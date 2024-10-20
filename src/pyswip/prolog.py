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

"""
Provides the basic Prolog interface.
"""

from typing import Union, Generator
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


__all__ = "PrologError", "NestedQueryError", "Prolog"


class PrologError(Exception):
    pass


class NestedQueryError(PrologError):
    """
    SWI-Prolog does not accept nested queries, that is, opening a query while the previous one was not closed.
    As this error may be somewhat difficult to debug in foreign code, it is automatically treated inside PySwip
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
    """Provides the entry point for the Prolog interface"""

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

            plq = PL_Q_NODEBUG | PL_Q_CATCH_EXCEPTION if catcherrors else PL_Q_NORMAL
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
    def asserta(cls, assertion: str, *, catcherrors: bool = False) -> None:
        """
        Assert a clause (fact or rule) into the database.

        ``asserta`` asserts the clause as the first clause of the predicate.

        See `asserta/1 <https://www.swi-prolog.org/pldoc/doc_for?object=asserta/1>`_ in SWI-Prolog documentation.

        :param assertion: Clause to insert into the head of the database
        :param catcherrors: Catches the exception raised during goal execution

        >>> Prolog.asserta("big(airplane)")
        >>> Prolog.asserta("small(mouse)")
        >>> Prolog.asserta('''bigger(A, B) :-
        ...    big(A),
        ...    small(B)''')
        """
        next(cls.query(assertion.join(["asserta((", "))."]), catcherrors=catcherrors))

    @classmethod
    def assertz(cls, assertion: str, *, catcherrors: bool = False) -> None:
        """
        Assert a clause (fact or rule) into the database.

        ``assertz`` asserts the clause as the last clause of the predicate.

        See `assertz/1 <https://www.swi-prolog.org/pldoc/doc_for?object=assertz/1>`_ in SWI-Prolog documentation.

        :param assertion: Clause to insert into the tail of the database
        :param catcherrors: Catches the exception raised during goal execution

        >>> Prolog.assertz("big(airplane)")
        >>> Prolog.assertz("small(mouse)")
        >>> Prolog.assertz('''bigger(A, B) :-
        ...    big(A),
        ...    small(B)''')
        """
        next(cls.query(assertion.join(["assertz((", "))."]), catcherrors=catcherrors))

    @classmethod
    def dynamic(cls, *terms: str, catcherrors: bool = False) -> None:
        """Informs the interpreter that the definition of the predicate(s) may change during execution

        See `dynamic/1 <https://www.swi-prolog.org/pldoc/doc_for?object=dynamic/1>`_ in SWI-Prolog documentation.

        :param terms: One or more predicate indicators
        :param catcherrors: Catches the exception raised during goal execution

        :raises ValueError: if no terms was given.

        >>> Prolog.dynamic("person/1")
        >>> Prolog.asserta("person(jane)")
        >>> list(Prolog.query("person(X)"))
        [{'X': 'jane'}]
        >>> Prolog.retractall("person(_)")
        >>> list(Prolog.query("person(X)"))
        []
        """
        if len(terms) < 1:
            raise ValueError("One or more terms must be given")
        params = ", ".join(terms)
        next(cls.query(f"dynamic(({params}))", catcherrors=catcherrors))

    @classmethod
    def retract(cls, term: str, *, catcherrors: bool = False) -> None:
        """
        Removes the fact or clause from the database

        See `retract/1 <https://www.swi-prolog.org/pldoc/doc_for?object=retract/1>`_ in SWI-Prolog documentation.

        :param term: The term to remove from the database
        :param catcherrors: Catches the exception raised during goal execution

        >>> Prolog.dynamic("person/1")
        >>> Prolog.asserta("person(jane)")
        >>> list(Prolog.query("person(X)"))
        [{'X': 'jane'}]
        >>> Prolog.retract("person(jane)")
        >>> list(Prolog.query("person(X)"))
        []
        """
        next(cls.query(term.join(["retract((", "))."]), catcherrors=catcherrors))

    @classmethod
    def retractall(cls, head: str, *, catcherrors: bool = False) -> None:
        """
        Removes all facts or clauses in the database where the ``head`` unifies.

        See `retractall/1 <https://www.swi-prolog.org/pldoc/doc_for?object=retractall/1>`_ in SWI-Prolog documentation.

        :param head: The term to unify with the facts or clauses in the database
        :param catcherrors: Catches the exception raised during goal execution

        >>> Prolog.dynamic("person/1")
        >>> Prolog.asserta("person(jane)")
        >>> Prolog.asserta("person(joe)")
        >>> list(Prolog.query("person(X)"))
        [{'X': 'joe'}, {'X': 'jane'}]
        >>> Prolog.retractall("person(_)")
        >>> list(Prolog.query("person(X)"))
        []
        """
        next(cls.query(head.join(["retractall((", "))."]), catcherrors=catcherrors))

    @classmethod
    def consult(
        cls,
        path: Union[str, Path],
        *,
        catcherrors: bool = False,
        relative_to: Union[str, Path] = "",
    ) -> None:
        """
        Reads the given Prolog source file

        The file is always reloaded when called.

        See `consult/1 <https://www.swi-prolog.org/pldoc/doc_for?object=consult/1>`_ in SWI-Prolog documentation.

        Tilde character (``~``) in paths are expanded to the user home directory

        >>> Prolog.consult("~/my_files/hanoi.pl")
        >>> # consults file /home/me/my_files/hanoi.pl

        ``relative_to`` keyword argument makes it easier to construct the consult path.
        This keyword is no-op, if the consult path is absolute.
        If the given ``relative_to`` path is a file, then the consult path is updated to become a sibling of that path.

        Assume you have the ``/home/me/project/facts.pl`` that you want to consult from the ``run.py`` file which exists in the same directory ``/home/me/project``.
        Using the built-in ``__file__`` constant which contains the path of the current Python file , it becomes very easy to do that:

        >>> Prolog.consult("facts.pl", relative_to=__file__)

        If the given `relative_path` is a directory, then the consult path is updated to become a child of that path.

        >>> project_dir = "~/projects"
        >>> Prolog.consult("facts1.pl", relative_to=project_dir)

        :param path: The path to the Prolog source file
        :param catcherrors: Catches the exception raised during goal execution
        :param relative_to: The path where the consulted file is relative to
        """
        path = resolve_path(path, relative_to)
        next(cls.query(str(path).join(["consult('", "')"]), catcherrors=catcherrors))

    @classmethod
    def query(
        cls,
        query: str,
        *,
        maxresult: int = -1,
        catcherrors: bool = True,
        normalize: bool = True,
    ) -> Generator:
        """Run a prolog query and return a generator

        If the query is a yes/no question, returns {} for yes, and nothing for no.
        Otherwise returns a generator of dicts with variables as keys.

        :param query: The query to execute in the Prolog engine
        :param maxresult: Maximum number of results to return
        :param catcherrors: Catches the exception raised during goal execution
        :param normalize: Return normalized values

        >>> Prolog.assertz("father(michael,john)")
        >>> Prolog.assertz("father(michael,gina)")
        >>> bool(list(Prolog.query("father(michael,john)")))
        True
        >>> bool(list(Prolog.query("father(michael,olivia)")))
        False
        >>> print(sorted(Prolog.query("father(michael,X)")))
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
