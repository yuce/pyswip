# -*- coding: utf-8 -*-


# prolog.py -- Prolog class
# Copyright (c) 2007-2012 Yüce Tekol
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from .swipl import Swipl, c_char_p
from .const import PL_Q_NODEBUG, PL_Q_CATCH_EXCEPTION, PL_Q_NORMAL
from .term import Term


class PrologError(Exception):
    pass


class NestedQueryError(PrologError):
    """
    SWI-Prolog does not accept nested queries, that is, opening a query while
    the previous one was not closed.

    As this error may be somewhat difficult to debug in foreign code, it is
    automatically treated inside pySWIP
    """
    pass


class _Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Prolog(metaclass=_Singleton):

    # We keep track of open queries to avoid nested queries.
    # _queryIsOpen = False

    def __init__(self, lib_path="", swi_home=""):
        if not lib_path:
            lib_path, swi_home = self._discover_lib()
        self._initialize(lib_path, swi_home)

    @classmethod
    def _discover_lib(self):
        from .discover  import _findSwipl
        return _findSwipl()

    @classmethod
    def _initialize(self, lib_path, swi_home):
        from .swipl import open_lib
        open_lib(lib_path)

        args = [
            "./",
            "-q",  # quiet
            "-nosignals", # Inhibit signal handling by SWI
        ]
        if swi_home:
            args.append("--home=%s" % swi_home)

        lib = Swipl.lib
        result = lib.initialise(len(args),args)
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

    def asserta(self, assertion, catcherrors=False):
        return next(self.query(assertion.join(["asserta((", "))."]), catcherrors=catcherrors))

    def assertz(self, assertion, catcherrors=False):
        return next(self.query(assertion.join(["assertz((", "))."]), catcherrors=catcherrors))

    # @classmethod
    # def dynamic(cls, term, catcherrors=False):
    #     next(cls.query(term.join(["dynamic((", "))."]), catcherrors=catcherrors))
    #
    # @classmethod
    # def retract(cls, term, catcherrors=False):
    #     next(cls.query(term.join(["retract((", "))."]), catcherrors=catcherrors))
    #
    # @classmethod
    # def retractall(cls, term, catcherrors=False):
    #     next(cls.query(term.join(["retractall((", "))."]), catcherrors=catcherrors))
    #

    def consult(self, filename, catcherrors=True):
        return next(self.query(filename.join(["consult('", "')"]), catcherrors=catcherrors))

    @classmethod
    def query(cls, query, maxresult=-1, catcherrors=True, normalize=True):
        return _QueryWrapper()(query, maxresult, catcherrors, normalize)


class _QueryWrapper(object):

    @classmethod
    def __call__(cls, query, maxresult, catcherrors, normalize):
        lib = Swipl.lib

        with Frame():
            swipl_head = lib.new_term_ref()
            swipl_args = lib.new_term_refs(2)
            swipl_goal_char_list = swipl_args
            swipl_binding_list = swipl_args + 1
            lib.put_list_chars(swipl_goal_char_list, query)
            swipl_predicate = lib.predicate(c_char_p(b"pyrun"), 2, None)
            plq = catcherrors and (PL_Q_NODEBUG|PL_Q_CATCH_EXCEPTION) or PL_Q_NORMAL
            swipl_qid = lib.open_query(None, plq, swipl_predicate, swipl_args)

            # Prolog._queryIsOpen = True # From now on, the query will be considered open
            try:
                while maxresult and lib.next_solution(swipl_qid):
                    maxresult -= 1
                    bindings = []
                    swipl_list = lib.copy_term_ref(swipl_binding_list)
                    # t = getTerm(swipl_list)
                    t = Term.decode(swipl_list)
                    if normalize:
                        yield t.norm_value
                    #     try:
                    #         v = t.value
                    #     except AttributeError:
                    #         v = {}
                    #         for r in [x.value for x in t]:
                    #             v.update(r)
                    #     yield v
                    else:
                        yield t

                if lib.exception(swipl_qid):
                    raise PrologError("error: %s", swipl_qid)
                    # term = getTerm(lib.exception(swipl_qid))
                    #
                    # raise PrologError("".join(["Caused by: '", query, "'. ",
                    #                             "Returned: '", str(term), "'."]))

            finally:
                lib.cut_query(swipl_qid)
                # Prolog._queryIsOpen = False


class Frame:

    def __init__(self):
        self.swipl_fid = None

    def __enter__(self):
        self.swipl_fid = Swipl.lib.open_foreign_frame()

    def __exit__(self, exc_type, exc_val, exc_tb):
        Swipl.lib.discard_foreign_frame(self.swipl_fid)
        self.swipl_fid = None