# Copyright (c) 2007-2024 Yüce Tekol and PySwip Contributors
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

from typing import Union
from pathlib import Path

from pyswip.utils import resolve_path
from pyswip.core import (
    SWI_HOME_DIR,
    PL_STRING,
    REP_UTF8,
    PL_Q_NODEBUG,
    PL_Q_CATCH_EXCEPTION,
    PL_Q_NORMAL,
    PL_initialise,
    PL_open_foreign_frame,
    PL_new_term_ref,
    PL_chars_to_term,
    PL_call,
    PL_discard_foreign_frame,
    PL_new_term_refs,
    PL_put_chars,
    PL_predicate,
    PL_open_query,
    PL_next_solution,
    PL_copy_term_ref,
    PL_exception,
    PL_cut_query,
    PL_thread_self,
    PL_thread_attach_engine,
)


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
    args.append("-q")  # --quiet
    args.append("--nosignals")  # "Inhibit any signal handling by Prolog"
    if SWI_HOME_DIR:
        args.append("--home=%s" % SWI_HOME_DIR)

    result = PL_initialise(len(args), args)
    # result is a boolean variable (i.e. 0 or 1) indicating whether the
    # initialisation was successful or not.
    if not result:
        raise PrologError(
            "Could not initialize the Prolog environment."
            "PL_initialise returned %d" % result
        )

    swipl_fid = PL_open_foreign_frame()
    swipl_load = PL_new_term_ref()
    PL_chars_to_term(
        """
        asserta(pyrun(GoalString,BindingList) :-
            (read_term_from_atom(GoalString, Goal, [variable_names(BindingList)]),
            call(Goal))).
        """,
        swipl_load,
    )
    PL_call(swipl_load, None)
    PL_discard_foreign_frame(swipl_fid)


_initialize()


# NOTE: This import MUST be after _initialize is called!!
from pyswip.easy import getTerm  # noqa: E402


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
            Prolog._init_prolog_thread()
            swipl_fid = PL_open_foreign_frame()

            swipl_args = PL_new_term_refs(2)
            swipl_goalCharList = swipl_args
            swipl_bindingList = swipl_args + 1

            PL_put_chars(
                swipl_goalCharList, PL_STRING | REP_UTF8, -1, query.encode("utf-8")
            )

            swipl_predicate = PL_predicate("pyrun", 2, None)

            plq = catcherrors and (PL_Q_NODEBUG | PL_Q_CATCH_EXCEPTION) or PL_Q_NORMAL
            swipl_qid = PL_open_query(None, plq, swipl_predicate, swipl_args)

            Prolog._queryIsOpen = True  # From now on, the query will be considered open
            try:
                while maxresult and PL_next_solution(swipl_qid):
                    maxresult -= 1
                    swipl_list = PL_copy_term_ref(swipl_bindingList)
                    t = getTerm(swipl_list)
                    if normalize:
                        try:
                            v = t.value
                        except AttributeError:
                            v = {}
                            for r in [x.value for x in t]:
                                r = normalize_values(r)
                                v.update(r)
                        yield v
                    else:
                        yield t

                if PL_exception(swipl_qid):
                    term = getTerm(PL_exception(swipl_qid))

                    raise PrologError(
                        "".join(
                            [
                                "Caused by: '",
                                query,
                                "'. ",
                                "Returned: '",
                                str(term),
                                "'.",
                            ]
                        )
                    )

            finally:  # This ensures that, whatever happens, we close the query
                PL_cut_query(swipl_qid)
                PL_discard_foreign_frame(swipl_fid)
                Prolog._queryIsOpen = False

    @classmethod
    def _init_prolog_thread(cls):
        pengine_id = PL_thread_self()
        if pengine_id == -1:
            pengine_id = PL_thread_attach_engine(None)
        if pengine_id == -1:
            raise PrologError("Unable to attach new Prolog engine to the thread")
        elif pengine_id == -2:
            print("{WARN} Single-threaded swipl build, beware!")

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
    def consult(
        cls,
        path: Union[str, Path],
        *,
        catcherrors=False,
        relative_to: Union[str, Path] = "",
    ):
        path = resolve_path(path, relative_to)
        next(cls.query(str(path).join(["consult('", "')"]), catcherrors=catcherrors))

    @classmethod
    def query(cls, query, maxresult=-1, catcherrors=True, normalize=True):
        """Run a prolog query and return a generator.
        If the query is a yes/no question, returns {} for yes, and nothing for no.
        Otherwise returns a generator of dicts with variables as keys.

        >>> Prolog.assertz("father(michael,john)")
        >>> Prolog.assertz("father(michael,gina)")
        >>> bool(list(Prolog.query("father(michael,john)")))
        True
        >>> bool(list(Prolog.query("father(michael,olivia)")))
        False
        >>> print sorted(Prolog.query("father(michael,X)"))
        [{'X': 'gina'}, {'X': 'john'}]
        """
        return cls._QueryWrapper()(query, maxresult, catcherrors, normalize)


def normalize_values(values):
    from pyswip.easy import Atom, Functor

    if isinstance(values, Atom):
        return values.value
    if isinstance(values, Functor):
        normalized = str(values.name.value)
        if values.arity:
            normalized_args = [str(normalize_values(arg)) for arg in values.args]
            normalized = normalized + "(" + ", ".join(normalized_args) + ")"
        return normalized
    elif isinstance(values, dict):
        return {key: normalize_values(v) for key, v in values.items()}
    elif isinstance(values, (list, tuple)):
        return [normalize_values(v) for v in values]
    return values
