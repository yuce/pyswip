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


import sys

from pyswip.core import *


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


def _initialize():
    args = []
    args.append("./")
    args.append("-q")         # --quiet
    args.append("--nosignals") # "Inhibit any signal handling by Prolog"
    if SWI_HOME_DIR is not None:
        args.append("--home=%s" % SWI_HOME_DIR)

    result = PL_initialise(len(args),args)
    # result is a boolean variable (i.e. 0 or 1) indicating whether the
    # initialisation was successful or not.
    if not result:
        raise PrologError("Could not initialize the Prolog environment."
                          "PL_initialise returned %d" % result)

    swipl_fid = PL_open_foreign_frame()
    swipl_load = PL_new_term_ref()
    PL_chars_to_term("asserta(pyrun(GoalString,BindingList) :- "
                     "(atom_chars(A,GoalString),"
                     "atom_to_term(A,Goal,BindingList),"
                     "call(Goal))).", swipl_load)
    PL_call(swipl_load, None)
    PL_discard_foreign_frame(swipl_fid)
_initialize()


# NOTE: This import MUST be after _initialize is called!!
from pyswip.easy import getTerm


class Prolog:
    """Easily query SWI-Prolog.
    This is a singleton class
    """

    # We keep track of open queries to avoid nested queries.
    _queryIsOpen = False

    class _QueryWrapper(object):

        def __init__(self):
            if Prolog._queryIsOpen:
                raise NestedQueryError("The last query was not closed")

        def __call__(self, query, maxresult, catcherrors, normalize):
            swipl_fid = PL_open_foreign_frame()

            swipl_head = PL_new_term_ref()
            swipl_args = PL_new_term_refs(2)
            swipl_goalCharList = swipl_args
            swipl_bindingList = swipl_args + 1

            PL_put_list_chars(swipl_goalCharList, query)

            swipl_predicate = PL_predicate("pyrun", 2, None)

            plq = catcherrors and (PL_Q_NODEBUG|PL_Q_CATCH_EXCEPTION) or PL_Q_NORMAL
            swipl_qid = PL_open_query(None, plq, swipl_predicate, swipl_args)

            Prolog._queryIsOpen = True # From now on, the query will be considered open
            try:
                while maxresult and PL_next_solution(swipl_qid):
                    maxresult -= 1
                    bindings = []
                    swipl_list = PL_copy_term_ref(swipl_bindingList)
                    t = getTerm(swipl_list)
                    if normalize:
                        try:
                            v = t.value
                        except AttributeError:
                            v = {}
                            for r in [x.value for x in t]:
                                v.update(r)
                        yield v
                    else:
                        yield t

                if PL_exception(swipl_qid):
                    term = getTerm(PL_exception(swipl_qid))

                    raise PrologError("".join(["Caused by: '", query, "'. ",
                                               "Returned: '", str(term), "'."]))

            finally: # This ensures that, whatever happens, we close the query
                PL_cut_query(swipl_qid)
                PL_discard_foreign_frame(swipl_fid)
                Prolog._queryIsOpen = False

    @classmethod
    def asserta(cls, assertion, catcherrors=False):
        next(cls.query(assertion.join(["asserta((", "))."]), catcherrors=catcherrors))

    @classmethod
    def assertz(cls, assertion, catcherrors=False):
        next(cls.query(assertion.join(["assertz((", "))."]), catcherrors=catcherrors))

    @classmethod
    def dynamic(cls, term, catcherrors=False):
        next(cls.query(term.join(["dynamic((", "))."]), catcherrors=catcherrors))

    @classmethod
    def retract(cls, term, catcherrors=False):
        next(cls.query(term.join(["retract((", "))."]), catcherrors=catcherrors))

    @classmethod
    def retractall(cls, term, catcherrors=False):
        next(cls.query(term.join(["retractall((", "))."]), catcherrors=catcherrors))

    @classmethod
    def consult(cls, filename, catcherrors=False):
        next(cls.query(filename.join(["consult('", "')"]), catcherrors=catcherrors))

    @classmethod
    def query(cls, query, maxresult=-1, catcherrors=True, normalize=True):
        """Run a prolog query and return a generator.
        If the query is a yes/no question, returns {} for yes, and nothing for no.
        Otherwise returns a generator of dicts with variables as keys.

        >>> prolog = Prolog()
        >>> prolog.assertz("father(michael,john)")
        >>> prolog.assertz("father(michael,gina)")
        >>> bool(list(prolog.query("father(michael,john)")))
        True
        >>> bool(list(prolog.query("father(michael,olivia)")))
        False
        >>> print sorted(prolog.query("father(michael,X)"))
        [{'X': 'gina'}, {'X': 'john'}]
        """
        return cls._QueryWrapper()(query, maxresult, catcherrors, normalize)

