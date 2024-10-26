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

import inspect
from typing import Union, Callable, Optional

from pyswip.core import (
    PL_new_atom,
    PL_register_atom,
    PL_atom_wchars,
    PL_get_atom,
    PL_unregister_atom,
    PL_new_term_ref,
    PL_compare,
    PL_get_chars,
    PL_copy_term_ref,
    PL_unify_atom,
    PL_unify_string_chars,
    PL_unify_integer,
    PL_unify_bool,
    PL_unify_float,
    PL_unify_list,
    PL_unify_nil,
    PL_term_type,
    PL_put_term,
    PL_new_functor,
    PL_functor_name,
    PL_functor_arity,
    PL_get_functor,
    PL_new_term_refs,
    PL_get_arg,
    PL_cons_functor_v,
    PL_put_atom_chars,
    PL_put_integer,
    PL_put_functor,
    PL_put_nil,
    PL_cons_list,
    PL_get_long,
    PL_get_float,
    PL_is_list,
    PL_get_list,
    PL_register_foreign_in_module,
    PL_call,
    PL_new_module,
    PL_pred,
    PL_open_query,
    PL_next_solution,
    PL_cut_query,
    PL_close_query,
    PL_VARIABLE,
    PL_STRINGS_MARK,
    PL_TERM,
    PL_DICT,
    PL_ATOM,
    PL_STRING,
    PL_INTEGER,
    PL_FLOAT,
    PL_Q_NODEBUG,
    PL_Q_CATCH_EXCEPTION,
    PL_FA_NONDETERMINISTIC,
    CVT_VARIABLE,
    BUF_RING,
    REP_UTF8,
    CVT_ATOM,
    CVT_STRING,
    CFUNCTYPE,
    cleaned,
    cast,
    c_size_t,
    byref,
    c_void_p,
    atom_t,
    create_string_buffer,
    c_char_p,
    functor_t,
    c_int,
    c_long,
    c_double,
    foreign_t,
    term_t,
    control_t,
    module_t,
)


integer_types = (int,)


class InvalidTypeError(TypeError):
    def __init__(self, *args):
        type_ = args and args[0] or "Unknown"
        msg = f"Term is expected to be of type: '{type_}'"
        Exception.__init__(self, msg, *args)


class ArgumentTypeError(Exception):
    """
    Thrown when an argument has the wrong type.
    """

    def __init__(self, expected, got):
        msg = f"Expected an argument of type '{expected}' but got '{got}'"
        Exception.__init__(self, msg)


class Atom(object):
    __slots__ = "handle", "chars"

    def __init__(self, handleOrChars, chars=None):
        """Create an atom.
        ``handleOrChars``: handle or string of the atom.
        """

        if isinstance(handleOrChars, str):
            self.handle = PL_new_atom(handleOrChars)
            self.chars = handleOrChars
        else:
            self.handle = handleOrChars
            PL_register_atom(self.handle)
            if chars is None:
                slen = c_size_t()
                self.chars = PL_atom_wchars(self.handle, byref(slen))
            else:  # WA: PL_atom_wchars can fail to return correct string
                self.chars = chars

    def fromTerm(cls, term):
        """Create an atom from a Term or term handle."""

        if isinstance(term, Term):
            term = term.handle
        elif not isinstance(term, (c_void_p, integer_types)):
            raise ArgumentTypeError((str(Term), str(c_void_p)), str(type(term)))

        a = atom_t()
        if PL_get_atom(term, byref(a)):
            return cls(a.value, getAtomChars(term))

    fromTerm = classmethod(fromTerm)

    def __del__(self):
        if not cleaned:
            PL_unregister_atom(self.handle)

    def get_value(self):
        ret = self.chars
        if not isinstance(ret, str):
            ret = ret.decode()
        return ret

    value = property(get_value)

    def __str__(self):
        if self.chars is not None:
            return self.value
        else:
            return self.__repr__()

    def __repr__(self):
        return str(self.handle).join(["Atom('", "')"])

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        else:
            return self.handle == other.handle

    def __hash__(self):
        return self.handle


class Term(object):
    __slots__ = "handle", "chars", "__value", "a0"

    def __init__(self, handle=None, a0=None):
        if handle:
            # self.handle = PL_copy_term_ref(handle)
            self.handle = handle
        else:
            self.handle = PL_new_term_ref()
        self.chars = None
        self.a0 = a0

    def __invert__(self):
        return _not(self)

    def get_value(self):
        pass

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        else:
            return PL_compare(self.handle, other.handle) == 0

    def __hash__(self):
        return self.handle


class Variable:
    __slots__ = "handle", "chars"

    def __init__(self, handle=None, name=None):
        self.chars = None
        if name:
            self.chars = name
        if handle:
            self.handle = handle
            s = create_string_buffer(b"\00" * 64)  # FIXME:
            ptr = cast(s, c_char_p)
            if PL_get_chars(handle, byref(ptr), CVT_VARIABLE | BUF_RING | REP_UTF8):
                self.chars = ptr.value
        else:
            self.handle = PL_new_term_ref()
            # PL_put_variable(self.handle)
        if (self.chars is not None) and not isinstance(self.chars, str):
            self.chars = self.chars.decode()

    def unify(self, value):
        if self.handle is None:
            t = PL_new_term_ref(self.handle)
        else:
            t = PL_copy_term_ref(self.handle)

        self._fun(value, t)
        self.handle = t

    def _fun(self, value, t):
        if type(value) == Atom:
            fun = PL_unify_atom
            value = value.handle
        elif isinstance(value, str):
            fun = PL_unify_string_chars
            value = value.encode()
        elif type(value) == int:
            fun = PL_unify_integer
        elif type(value) == bool:
            fun = PL_unify_bool
        elif type(value) == float:
            fun = PL_unify_float
        elif type(value) == list:
            fun = PL_unify_list
        else:
            raise TypeError(
                "Cannot unify {} with value {} due to the value unknown type {}".format(
                    self, value, type(value)
                )
            )

        if type(value) == list:
            a = PL_new_term_ref(self.handle)
            list_term = t
            for element in value:
                tail_term = PL_new_term_ref(self.handle)
                fun(list_term, a, tail_term)
                self._fun(element, a)
                list_term = tail_term
            PL_unify_nil(list_term)
        else:
            fun(t, value)

    def get_value(self):
        return getTerm(self.handle)

    value = property(get_value, unify)

    def unified(self):
        return PL_term_type(self.handle) == PL_VARIABLE

    def __str__(self):
        if self.chars is not None:
            return self.chars
        else:
            return self.__repr__()

    def __repr__(self):
        return f"Variable({self.handle})"

    def put(self, term):
        # PL_put_variable(term)
        PL_put_term(term, self.handle)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        else:
            return PL_compare(self.handle, other.handle) == 0

    def __hash__(self):
        return self.handle


class Functor(object):
    __slots__ = "handle", "name", "arity", "args", "__value", "a0"
    func = {}

    def __init__(self, handleOrName, arity=1, args=None, a0=None):
        """Create a functor.
        ``handleOrName``: functor handle, a string or an atom.
        """

        self.args = args or []
        self.arity = arity
        self.a0 = a0

        if isinstance(handleOrName, str):
            self.name = Atom(handleOrName)
            self.handle = PL_new_functor(self.name.handle, arity)
            self.__value = "Functor%d" % self.handle
        elif isinstance(handleOrName, Atom):
            self.name = handleOrName
            self.handle = PL_new_functor(self.name.handle, arity)
            self.__value = "Functor%d" % self.handle
        else:
            self.handle = handleOrName
            self.name = Atom(PL_functor_name(self.handle))
            self.arity = PL_functor_arity(self.handle)
            try:
                self.__value = self.func[self.handle](self.arity, *self.args)
            except KeyError:
                self.__value = str(self)

    def fromTerm(cls, term):
        """Create a functor from a Term or term handle."""

        if isinstance(term, Term):
            term = term.handle
        elif not isinstance(term, (c_void_p, integer_types)):
            raise ArgumentTypeError((str(Term), str(int)), str(type(term)))

        f = functor_t()
        if PL_get_functor(term, byref(f)):
            # get args
            args = []
            arity = PL_functor_arity(f.value)
            # let's have all args be consecutive
            a0 = PL_new_term_refs(arity)
            for i, a in enumerate(range(1, arity + 1)):
                if PL_get_arg(a, term, a0 + i):
                    args.append(getTerm(a0 + i))

            return cls(f.value, args=args, a0=a0)

    fromTerm = classmethod(fromTerm)

    @property
    def value(self):
        return self.__value

    def __call__(self, *args):
        assert self.arity == len(args)  # FIXME: Put a decent error message
        a = PL_new_term_refs(len(args))
        for i, arg in enumerate(args):
            putTerm(a + i, arg)

        t = PL_new_term_ref()
        PL_cons_functor_v(t, self.handle, a)
        return Term(t)

    def __str__(self):
        if self.name is not None and self.arity is not None:
            return "%s(%s)" % (self.name, ", ".join([str(arg) for arg in self.args]))
        else:
            return self.__repr__()

    def __repr__(self):
        return "".join(
            [
                "Functor(",
                ",".join(str(x) for x in [self.handle, self.arity] + self.args),
                ")",
            ]
        )

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        else:
            return PL_compare(self.handle, other.handle) == 0

    def __hash__(self):
        return self.handle


def _unifier(arity, *args):
    assert arity == 2
    try:
        return {args[0].value: args[1].value}
    except AttributeError:
        return {args[0].value: args[1]}


_unify = Functor("=", 2)
Functor.func[_unify.handle] = _unifier
_not = Functor("not", 1)
_comma = Functor(",", 2)


def putTerm(term, value):
    if isinstance(value, Term):
        PL_put_term(term, value.handle)
    elif isinstance(value, str):
        PL_put_atom_chars(term, value)
    elif isinstance(value, int):
        PL_put_integer(term, value)
    elif isinstance(value, Variable):
        value.put(term)
    elif isinstance(value, list):
        putList(term, value)
    elif isinstance(value, Functor):
        PL_put_functor(term, value.handle)
    else:
        raise Exception(f"Not implemented for type: {type(value)}")


def putList(l, ls):  # noqa: E741
    PL_put_nil(l)
    for item in reversed(ls):
        a = PL_new_term_ref()  # PL_new_term_refs(len(ls))
        putTerm(a, item)
        PL_cons_list(l, a, l)


def getAtomChars(t):
    """If t is an atom, return it as a string, otherwise raise InvalidTypeError."""
    s = c_char_p()
    if PL_get_chars(t, byref(s), CVT_ATOM | REP_UTF8):
        return s.value
    else:
        raise InvalidTypeError("atom")


def getAtom(t):
    """If t is an atom, return it , otherwise raise InvalidTypeError."""
    return Atom.fromTerm(t)


def getBool(t):
    """If t is of type bool, return it, otherwise raise InvalidTypeError."""
    b = c_int()
    if PL_get_long(t, byref(b)):
        return bool(b.value)
    else:
        raise InvalidTypeError("bool")


def getLong(t):
    """If t is of type long, return it, otherwise raise InvalidTypeError."""
    i = c_long()
    if PL_get_long(t, byref(i)):
        return i.value
    else:
        raise InvalidTypeError("long")


getInteger = getLong  # just an alias for getLong


def getFloat(t):
    """If t is of type float, return it, otherwise raise InvalidTypeError."""
    d = c_double()
    if PL_get_float(t, byref(d)):
        return d.value
    else:
        raise InvalidTypeError("float")


def getString(t):
    """If t is of type string, return it, otherwise raise InvalidTypeError."""
    s = c_char_p()
    if PL_get_chars(t, byref(s), REP_UTF8 | CVT_STRING):
        return s.value
    else:
        raise InvalidTypeError("string")


def getTerm(t):
    if t is None:
        return None
    with PL_STRINGS_MARK():
        p = PL_term_type(t)
        if p < PL_TERM:
            res = _getterm_router[p](t)
        elif PL_is_list(t):
            res = getList(t)
        elif p == PL_DICT:
            res = getDict(t)
        else:
            res = getFunctor(t)
        return res


def getDict(term):
    """
    Return term as a dictionary.
    """

    if isinstance(term, Term):
        term = term.handle
    elif not isinstance(term, (c_void_p, int)):
        raise ArgumentTypeError((str(Term), str(int)), str(type(term)))

    f = functor_t()
    if PL_get_functor(term, byref(f)):
        args = []
        arity = PL_functor_arity(f.value)
        a0 = PL_new_term_refs(arity)
        for i, a in enumerate(range(1, arity + 1)):
            if PL_get_arg(a, term, a0 + i):
                args.append(getTerm(a0 + i))
            else:
                raise Exception("Missing arg")

        it = iter(args[1:])
        d = {k.value: v for v, k in zip(it, it)}

        return d
    else:
        res = getFunctor(term)
        return res


def getList(x):
    """
    Return t as a list.
    """

    t = PL_copy_term_ref(x)
    head = PL_new_term_ref()
    result = []
    while PL_get_list(t, head, t):
        result.append(getTerm(head))
        head = PL_new_term_ref()

    return result


def getFunctor(t):
    """Return t as a functor"""
    return Functor.fromTerm(t)


def getVariable(t):
    return Variable(t)


_getterm_router = {
    PL_VARIABLE: getVariable,
    PL_ATOM: getAtom,
    PL_STRING: getString,
    PL_INTEGER: getInteger,
    PL_FLOAT: getFloat,
    PL_TERM: getTerm,
}

arities = {}


def _callbackWrapper(arity=1, nondeterministic=False):
    res = arities.get((arity, nondeterministic))
    if res is None:
        if nondeterministic:
            res = CFUNCTYPE(*([foreign_t] + [term_t] * arity + [control_t]))
        else:
            res = CFUNCTYPE(*([foreign_t] + [term_t] * arity))
        arities[(arity, nondeterministic)] = res
    return res


funwraps = {}


def _foreignWrapper(fun, nondeterministic=False):
    res = funwraps.get(fun)
    if res is None:

        def wrapper(*args):
            if nondeterministic:
                args = [getTerm(arg) for arg in args[:-1]] + [args[-1]]
            else:
                args = [getTerm(arg) for arg in args]
            r = fun(*args)
            return (r is None) and True or r

        res = wrapper
        funwraps[fun] = res
    return res


cwraps = []


def registerForeign(
    func: Callable, name: str = "", arity: Optional[int] = None, flags: int = 0
):
    """
    Registers a Python callable as a Prolog predicate

    :param func: Callable to be registered. The callable should return a value in ``foreign_t``, ``True`` or ``False``.
    :param name: Name of the callable. If the name is not specified, it is derived from ``func.__name__``.
    :param arity: Number of parameters of the callable. If not specified, it is derived from the callable signature.
    :param flags: Only supported flag is ``PL_FA_NONDETERMINISTIC``.

    See: `PL_register_foreign <https://www.swi-prolog.org/pldoc/man?CAPI=PL_register_foreign>`_.

    .. Note::
        This function is deprecated.
        Use :py:meth:`Prolog.register_foreign` instead.
    """
    if not callable(func):
        raise ValueError("func is not callable")
    nondeterministic = bool(flags & PL_FA_NONDETERMINISTIC)
    if arity is None:
        # backward compatibility
        if hasattr(func, "arity"):
            arity = func.arity
        else:
            arity = len(inspect.signature(func).parameters)
            if nondeterministic:
                arity -= 1
    if not name:
        name = func.__name__

    cwrap = _callbackWrapper(arity, nondeterministic)
    fwrap = _foreignWrapper(func, nondeterministic)
    fwrap2 = cwrap(fwrap)
    cwraps.append(fwrap2)
    return PL_register_foreign_in_module(None, name, arity, fwrap2, flags)


newTermRef = PL_new_term_ref


def newTermRefs(count):
    a = PL_new_term_refs(count)
    return list(range(a, a + count))


def call(*terms, **kwargs):
    """Call term in module.
    ``term``: a Term or term handle
    """
    for kwarg in kwargs:
        if kwarg not in ["module"]:
            raise KeyError

    module = kwargs.get("module", None)

    t = terms[0]
    for tx in terms[1:]:
        t = _comma(t, tx)

    return PL_call(t.handle, module)


def newModule(name: Union[str, Atom]) -> module_t:
    """
    Returns a module with the given name.

    The module is created if it does not exist.

    .. NOTE::
        This function is deprecated. Use ``module`` instead.

    :param name: Name of the module
    """
    return module(name)


def module(name: Union[str, Atom]) -> module_t:
    """
    Returns a module with the given name.

    The module is created if it does not exist.

    :param name: Name of the module
    """
    if isinstance(name, str):
        name = Atom(name)
    return PL_new_module(name.handle)


class Query(object):
    qid = None
    fid = None

    def __init__(self, *terms, **kwargs):
        for key in kwargs:
            if key not in ["flags", "module"]:
                raise Exception(f"Invalid kwarg: {key}", key)

        flags = kwargs.get("flags", PL_Q_NODEBUG | PL_Q_CATCH_EXCEPTION)
        module = kwargs.get("module", None)

        t = terms[0]
        for tx in terms[1:]:
            t = _comma(t, tx)

        f = Functor.fromTerm(t)
        p = PL_pred(f.handle, module)
        Query.qid = PL_open_query(module, flags, p, f.a0)

    def nextSolution():
        return PL_next_solution(Query.qid)

    nextSolution = staticmethod(nextSolution)

    def cutQuery():
        PL_cut_query(Query.qid)

    cutQuery = staticmethod(cutQuery)

    def closeQuery():
        if Query.qid is not None:
            PL_close_query(Query.qid)
            Query.qid = None

    closeQuery = staticmethod(closeQuery)
