# -*- coding: utf-8 -*-

# Copyright 2007 Yuce Tekol <yucetekol@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .const import PL_Q_NODEBUG, PL_Q_CATCH_EXCEPTION, PL_Q_NORMAL
from .swipl import CFUNCTYPE, Swipl, c_char_p, foreign_t, term_t
from .term import Term

__all__ = "Prolog", "PrologError"

from inspect import signature

def _fun_arg_count(f):
    return len(signature(f).parameters)


class PrologError(Exception):
    pass


class _Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Prolog(metaclass=_Singleton):

    callbacks = {}
    register_after = []

    def __init__(self, lib_path="", swi_bin_path=""):
        if not lib_path:
            lib_path = self._discover_lib()
        if not swi_bin_path:
            swi_bin_path = self._discover_swi_bin_path()
        if not lib_path:
            raise PrologError("")
        self._initialize(lib_path, swi_bin_path)

    @classmethod
    def _discover_lib(cls):
        from ctypes.util import find_library
        return find_library("swipl")

    @classmethod
    def _discover_swi_bin_path(cls):
        import os
        import sys

        # first check whether SWI_HOME_DIR is already defined
        path = os.environ.get("SWI_HOME_DIR")
        if path:
            return path

        # check the PATH environment variable to find the swipl binary
        paths = os.environ.get("PATH")
        if not paths:
            return ""
        swipl_bin = "swipl"
        if sys.platform.startswith("win"):
            swipl_bin = "swipl.exe"
        for path in paths.split(os.pathsep):
            path = os.path.join(path, swipl_bin)
            if os.path.exists(path):
                # Found the swipl binary, return its path
                return path
        return ""

    @classmethod
    def _initialize(cls, lib_path, swi_bin_path):
        from .swipl import open_lib
        open_lib(lib_path)

        args = [
            swi_bin_path,
            "-q",  # quiet
            "-nosignals", # Inhibit signal handling by SWI
        ]

        lib = Swipl.lib
        result = lib.initialise(len(args), args)
        # result is a boolean variable (i.e. 0 or 1) indicating whether the
        # initialisation was successful or not.
        if not result:
            raise PrologError("Could not initialize the Prolog environment."
                              "PL_initialise returned %d" % result)

        with Frame():
            swipl_load = lib.new_term_ref()
            lib.chars_to_term(
                """
                asserta(pyrun(GoalString, BindingList) :- (
                    atom_chars(A, GoalString),
                    atom_to_term(A, Goal, BindingList),
                    call(Goal))).
                """, swipl_load)
            lib.call(swipl_load, None)

        if cls.register_after:
            for item in cls.register_after:
                Swipl.lib.register_foreign(*item)
            cls.register_after = []

    def asserta(self, assertion, catcherrors=False):
        return next(self.query(assertion.join(["asserta((", "))."]), catcherrors=catcherrors))

    def assertz(self, assertion, catcherrors=False):
        return next(self.query(assertion.join(["assertz((", "))."]), catcherrors=catcherrors))

    @classmethod
    def dynamic(cls, term, catcherrors=False):
        next(cls.query(term.join(["dynamic((", "))."]), catcherrors=catcherrors))

    @classmethod
    def retract(cls, term, catcherrors=False):
        next(cls.query(term.join(["retract((", "))."]), catcherrors=catcherrors))

    @classmethod
    def retractall(cls, term, catcherrors=False):
        next(cls.query(term.join(["retractall((", "))."]), catcherrors=catcherrors))

    def consult(self, filename, catcherrors=True):
        return next(self.query(filename.join(["consult('", "')"]), catcherrors=catcherrors))

    @classmethod
    def query(cls, query, maxresult=-1, catcherrors=True, normalize=True):
        return _QueryWrapper()(query, maxresult, catcherrors, normalize)

    @classmethod
    def register(cls, fun, name=None, arity=None, flags=0):
        if name is None:
            name = fun.__name__
        if arity is None:
            arity = _fun_arg_count(fun)

        key = "%s/%s" % (name, arity)
        if key in cls.callbacks:
            return True
        cwrapper = CFUNCTYPE(*([foreign_t] + [term_t] * arity))
        wrapped = cwrapper(_foreign_wrapper(fun))
        cls.callbacks[key] = wrapped

        if Swipl.lib is None:
            # Prolog wasn't initialized yet, defer registry
            cls.register_after.append((name, arity, wrapped, flags))
            return True
        else:
            return Swipl.lib.register_foreign(name, arity, wrapped, flags) == 1


class _QueryWrapper(object):

    @classmethod
    def __call__(cls, query, maxresult, catcherrors, normalize):
        lib = Swipl.lib

        with Frame():
            swipl_args = lib.new_term_refs(2)
            swipl_goal_char_list = swipl_args
            swipl_binding_list = swipl_args + 1
            lib.put_list_chars(swipl_goal_char_list, query)
            swipl_predicate = lib.predicate(c_char_p(b"pyrun"), 2, None)
            plq = catcherrors and (PL_Q_NODEBUG|PL_Q_CATCH_EXCEPTION) or PL_Q_NORMAL
            swipl_qid = lib.open_query(None, plq, swipl_predicate, swipl_args)

            try:
                while maxresult and lib.next_solution(swipl_qid):
                    maxresult -= 1
                    swipl_list = lib.copy_term_ref(swipl_binding_list)
                    t = Term.decode(swipl_list)
                    if normalize:
                        if isinstance(t, list):
                            ls = [x.norm_value for x in t]
                            if len(ls) > 0 and isinstance(ls[0], dict):
                                d = ls[0]
                                for x in ls[1:]:
                                    d.update(x)
                                yield d
                            else:
                                yield ls
                        else:
                            yield t.norm_value
                    else:
                        yield t

                if lib.exception(swipl_qid):
                    raise PrologError("error with qid: %s" % swipl_qid)
                    # term = Term.decode(lib.exception(swipl_qid))
                    # raise PrologError("".join(["Caused by: '", query, "'. ",
                    #                             "Returned: '", str(term), "'."]))

            finally:
                lib.cut_query(swipl_qid)


class Frame:

    def __init__(self):
        self.swipl_fid = None

    def __enter__(self):
        self.swipl_fid = Swipl.lib.open_foreign_frame()

    def __exit__(self, exc_type, exc_val, exc_tb):
        Swipl.lib.discard_foreign_frame(self.swipl_fid)
        self.swipl_fid = None


def _foreign_wrapper(fun):
    def wrapper(*args):
        args = [Term.decode(arg) for arg in args]
        r = fun(*args)
        return True if r is None else r
    return wrapper
