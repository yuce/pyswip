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

import functools
import inspect
import re
from typing import Union, Generator, Callable, Optional, Tuple
from pathlib import Path

from pyswip.utils import resolve_path
from pyswip.core import (
    SWI_HOME_DIR,
    PL_STRING,
    REP_UTF8,
    PL_Q_NODEBUG,
    PL_Q_CATCH_EXCEPTION,
    PL_Q_NORMAL,
    PL_FA_NONDETERMINISTIC,
    CFUNCTYPE,
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
    PL_register_foreign_in_module,
    foreign_t,
    term_t,
    control_t,
)


__all__ = "PrologError", "NestedQueryError", "Prolog"


RE_PLACEHOLDER = re.compile(r"%s")


class PrologError(Exception):
    pass


class NestedQueryError(PrologError):
    """
    SWI-Prolog does not accept nested queries, that is, opening a query while the previous one was not closed.
    As this error may be somewhat difficult to debug in foreign code, it is automatically treated inside PySwip
    """

    pass


def __initialize():
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


__initialize()


# NOTE: These imports MUST come after _initialize is called!!
from pyswip.easy import getTerm, Atom, Variable  # noqa: E402


class Prolog:
    """Provides the entry point for the Prolog interface"""

    # We keep track of open queries to avoid nested queries.
    _queryIsOpen = False
    _cwraps = []

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
    def asserta(cls, format: str, *args, catcherrors: bool = False) -> None:
        """
        Assert a clause (fact or rule) into the database.

        ``asserta`` asserts the clause as the first clause of the predicate.

        See `asserta/1 <https://www.swi-prolog.org/pldoc/doc_for?object=asserta/1>`_ in SWI-Prolog documentation.

        :param format:
            The format to be used to generate the clause.
            The placeholders (``%s``) are replaced by the ``args`` if one ore more arguments are given.
        :param args:
            Arguments to replace the placeholders in the ``format`` string
        :param catcherrors:
            Catches the exception raised during goal execution

        .. Note::
            Currently, If no arguments given, the format string is used as the raw clause, even if it contains a placeholder.
            This behavior is kept for for compatibility reasons.
            It may be removed in future versions.

        >>> Prolog.asserta("big(airplane)")
        >>> Prolog.asserta("small(mouse)")
        >>> Prolog.asserta('''bigger(A, B) :-
        ...    big(A),
        ...    small(B)''')
        >>> nums = list(range(5))
        >>> Prolog.asserta("numbers(%s)", nums)
        """
        next(
            cls.query(format.join(["asserta((", "))."]), *args, catcherrors=catcherrors)
        )

    @classmethod
    def assertz(cls, format: str, *args, catcherrors: bool = False) -> None:
        """
        Assert a clause (fact or rule) into the database.

        ``assertz`` asserts the clause as the last clause of the predicate.

        See `assertz/1 <https://www.swi-prolog.org/pldoc/doc_for?object=assertz/1>`_ in SWI-Prolog documentation.

        :param format:
            The format to be used to generate the clause.
            The placeholders (``%s``) are replaced by the ``args`` if one ore more arguments are given.
        :param catcherrors:
            Catches the exception raised during goal execution

        .. Note::
            Currently, If no arguments given, the format string is used as the raw clause, even if it contains a placeholder.
            This behavior is kept for for compatibility reasons.
            It may be removed in future versions.

        >>> Prolog.assertz("big(airplane)")
        >>> Prolog.assertz("small(mouse)")
        >>> Prolog.assertz('''bigger(A, B) :-
        ...    big(A),
        ...    small(B)''')
        >>> nums = list(range(5))
        >>> Prolog.assertz("numbers(%s)", nums)
        """
        next(
            cls.query(format.join(["assertz((", "))."]), *args, catcherrors=catcherrors)
        )

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
        params = ",".join(terms)
        next(cls.query(f"dynamic(({params}))", catcherrors=catcherrors))

    @classmethod
    def retract(cls, format: str, *args, catcherrors: bool = False) -> None:
        """
        Removes the fact or clause from the database

        See `retract/1 <https://www.swi-prolog.org/pldoc/doc_for?object=retract/1>`_ in SWI-Prolog documentation.

        :param format:
            The format to be used to generate the term.
            The placeholders (``%s``) are replaced by the ``args`` if one ore more arguments are given.
        :param catcherrors:
            Catches the exception raised during goal execution

        .. Note::
            Currently, If no arguments given, the format string is used as the raw term, even if it contains a placeholder.
            This behavior is kept for for compatibility reasons.
            It may be removed in future versions.


        >>> Prolog.dynamic("person/1")
        >>> Prolog.asserta("person(jane)")
        >>> list(Prolog.query("person(X)"))
        [{'X': 'jane'}]
        >>> Prolog.retract("person(jane)")
        >>> list(Prolog.query("person(X)"))
        []
        >>> Prolog.dynamic("numbers/1")
        >>> nums = list(range(5))
        >>> Prolog.asserta("numbers(10)")
        >>> Prolog.asserta("numbers(%s)", nums)
        >>> list(Prolog.query("numbers(X)"))
        [{'X': [0, 1, 2, 3, 4]}, {'X': 10}]
        >>> Prolog.retract("numbers(%s)", nums)
        >>> list(Prolog.query("numbers(X)"))
        [{'X': 10}]
        """
        next(
            cls.query(format.join(["retract((", "))."]), *args, catcherrors=catcherrors)
        )

    @classmethod
    def retractall(cls, format: str, *args, catcherrors: bool = False) -> None:
        """
        Removes all facts or clauses in the database where the ``head`` unifies.

        See `retractall/1 <https://www.swi-prolog.org/pldoc/doc_for?object=retractall/1>`_ in SWI-Prolog documentation.

        :param format: The term to unify with the facts or clauses in the database
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
        next(
            cls.query(
                format.join(["retractall((", "))."]), *args, catcherrors=catcherrors
            )
        )

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
        format: str,
        *args,
        maxresult: int = -1,
        catcherrors: bool = True,
        normalize: bool = True,
    ) -> Generator:
        """Run a prolog query and return a generator

        If the query is a yes/no question, returns {} for yes, and nothing for no.
        Otherwise returns a generator of dicts with variables as keys.

        :param format:
            The format to be used to generate the query.
            The placeholders (``%s``) are replaced by the ``args`` if one ore more arguments are given.
        :param args:
            Arguments to replace the placeholders in the ``format`` string
        :param maxresult:
            Maximum number of results to return
        :param catcherrors:
            Catches the exception raised during goal execution
        :param normalize:
            Return normalized values

        .. Note::
            Currently, If no arguments given, the format string is used as the raw query, even if it contains a placeholder.
            This behavior is kept for for compatibility reasons.
            It may be removed in future versions.

        >>> Prolog.assertz("father(michael,john)")
        >>> Prolog.assertz("father(michael,gina)")
        >>> bool(list(Prolog.query("father(michael,john)")))
        True
        >>> bool(list(Prolog.query("father(michael,olivia)")))
        False
        >>> print(sorted(Prolog.query("father(michael,X)")))
        [{'X': 'gina'}, {'X': 'john'}]
        """
        if args:
            query = format_prolog(format, args)
        else:
            query = format
        return cls._QueryWrapper()(query, maxresult, catcherrors, normalize)

    @classmethod
    @functools.cache
    def _callback_wrapper(cls, arity, nondeterministic):
        ps = [foreign_t] + [term_t] * arity
        if nondeterministic:
            return CFUNCTYPE(*(ps + [control_t]))
        return CFUNCTYPE(*ps)

    @classmethod
    @functools.cache
    def _foreign_wrapper(cls, fun, nondeterministic=False):
        def wrapper(*args):
            if nondeterministic:
                args = [getTerm(arg) for arg in args[:-1]] + [args[-1]]
            else:
                args = [getTerm(arg) for arg in args]
            r = fun(*args)
            return True if r is None else r

        return wrapper

    @classmethod
    def register_foreign(
        cls,
        func: Callable,
        /,
        name: str = "",
        arity: Optional[int] = None,
        *,
        module: str = "",
        nondeterministic: bool = False,
    ):
        """
        Registers a Python callable as a Prolog predicate

        :param func:
            Callable to be registered. The callable should return a value in ``foreign_t``, ``True`` or ``False`` or ``None``.
            Returning ``None`` is equivalent to returning ``True``.
        :param name:
            Name of the callable. If the name is not specified, it is derived from ``func.__name__``.
        :param arity:
            Number of parameters of the callable. If not specified, it is derived from the callable signature.
        :param module:
            Name of the module to register the predicate. By default, the current module.
        :param nondeterministic:
            Set the foreign callable as nondeterministic
        """
        if not callable(func):
            raise ValueError("func is not callable")
        module = module or None
        flags = PL_FA_NONDETERMINISTIC if nondeterministic else 0
        if arity is None:
            arity = len(inspect.signature(func).parameters)
            if nondeterministic:
                arity -= 1
        if not name:
            name = func.__name__

        cwrap = cls._callback_wrapper(arity, nondeterministic)
        # TODO: check func
        fwrap = cls._foreign_wrapper(func, nondeterministic)
        fwrap = cwrap(fwrap)
        cls._cwraps.append(fwrap)
        return PL_register_foreign_in_module(module, name, arity, fwrap, flags)


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


def make_prolog_str(value) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, list):
        inner = ",".join(make_prolog_str(v) for v in value)
        return f"[{inner}]"
    elif isinstance(value, Atom):
        # TODO: escape atom nome
        return f"'{value.chars}'"
    elif isinstance(value, Variable):
        # TODO: escape variable name
        return value.chars
    return str(value)


def format_prolog(fmt: str, args: Tuple) -> str:
    frags = RE_PLACEHOLDER.split(fmt)
    if len(args) != len(frags) - 1:
        raise ValueError("Number of arguments must match the number of placeholders")
    fs = []
    for i in range(len(args)):
        fs.append(frags[i])
        fs.append(make_prolog_str(args[i]))
    fs.append(frags[-1])
    return "".join(fs)
