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

from typing import Any, List, Optional, Tuple, Union

from .const import \
    PL_ATOM, PL_INTEGER, PL_FLOAT, PL_STRING, PL_TERM, PL_NIL, PL_LIST_PAIR, PL_LIST, PL_VARIABLE, \
    atom_t, functor_t, CVT_VARIABLE, BUF_DISCARDABLE
from .errors import ExistenceError, PrologError
from .swipl import Swipl, byref, c_int, c_char_p, c_long, c_double

__all__ = "FALSE", "NIL", "TRUE", \
          "Atom", "Compound", "Functor", "Term", \
          "atom", "atoms", "compound", "functor", "functors", "norm_value"


class Atom:

    def __init__(self, handle: Optional[int], name=""):
        self.handle = handle
        self.name = name

    @classmethod
    def from_term(cls, t: int):
        a = atom_t()
        if Swipl.lib.get_atom(t, byref(a)):
            return cls.from_handle(a.value)
        raise Exception("Invalid atom")  # TODO: Proper exception

    @classmethod
    def from_handle(cls, handle: int):
        lib = Swipl.lib
        lib.register_atom(handle)
        return cls(handle, lib.atom_chars(handle).decode("utf-8"))

    @property
    def value(self):
        # TODO: Move the following to a dict
        if self.name == '[]':
            return None
        elif self.name == 'true':
            return True
        elif self.name == 'false':
            return False
        return self.name

    norm_value = value

    def __repr__(self):
        return "Atom(%s)" % self.name

    def __str__(self):
        return self.name

    def __eq__(self, other: Any):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        if self.name == other.name:
            return True
        return False

    def __hash__(self):
        return hash(self.name)


def atom(name: str):
    return Atom(None, name=name)


def atoms(*names) -> List[Atom]:
    return [atom(name) for name in names]


NIL = atom("[]")
TRUE = atom("true")
FALSE = atom("false")


class Variable:

    def __init__(self, handle, name, value=None):
        self.handle = handle
        self.name = name
        self._value = value

    @property
    def value(self):
        return self._value

    @property
    def norm_value(self):
        return self._value

    @classmethod
    def from_term(cls, t):
        lib = Swipl.lib
        ptr = c_char_p()
        handle = lib.copy_term_ref(t)
        if lib.get_chars(handle, byref(ptr), CVT_VARIABLE | BUF_DISCARDABLE):
            return Variable(handle, name=ptr.value)
        raise PrologError("Invalid variable")

    def __repr__(self):
        return "Variable(%s=%s)" % (self.name, self._value)


class Binding:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    @property
    def value(self):
        return {self.a: self.b}

    @property
    def norm_value(self):
        nv = norm_value(self.b)
        # XXX: This is a hack and should be properly fixed --YT
        if isinstance(nv, tuple):
            nv = _flatten_tuple(nv)
        return {norm_value(self.a): nv}


class Functor:

    funcs = {}

    def __init__(self, handle, name, arity):
        self.handle = handle
        self.name = name
        self.arity = arity

    @classmethod
    def from_term(cls, t):
        lib = Swipl.lib
        f = functor_t()
        if lib.get_functor(t, byref(f)):
            handle = f.value
            arity = lib.functor_arity(handle)
            name = Atom.from_handle(lib.functor_name(handle))
            return cls(handle, name, arity=arity)
        raise Exception("Invalid functor")  # TODO: proper exception

    @classmethod
    def add_callable(cls, name, arity, fun):
        cls.funcs["%s/%s" % (name, arity)] = fun

    @property
    def value(self):
        return self.name.value

    norm_value = value

    def __repr__(self):
        return "Functor(%s/%s)" % (self.name.value, self.arity)

    def __str__(self):
        return "%s" % self.name.value

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name and \
               self.arity == other.arity

    def __call__(self, *args, **kwargs):
        f = Functor(None, self.name, len(args))
        return Compound(None, f, terms=args)


def _functor(name: str, arity=None) -> Functor:
    return Functor(None, name=atom(name), arity=arity)


def functors(*names) -> List[Functor]:
    return [_functor(name, 0) for name in names]


def _functor_unify(arg1, arg2) -> Binding:
    return Binding(arg1, arg2)


def _functor_tuple(arg1, arg2) -> Tuple:
    return arg1, arg2


def _functor_error(error_type, context):
    error = error_type.norm_value
    error.context = context
    return error


def _functor_existence_error(term_type, what):
    return ExistenceError(term_type, what)


Functor.add_callable("=", 2, _functor_unify)
Functor.add_callable(",", 2, _functor_tuple)
Functor.add_callable("error", 2, _functor_error)
Functor.add_callable("existence_error", 2, _functor_existence_error)


class Compound:

    def __init__(self, handle: Optional[int], functor: Union[str, Functor], terms=None, arg0=None):
        self.handle = handle
        self.terms = tuple(terms) if terms else tuple()
        self.arg0 = arg0
        if isinstance(functor, Functor):
            self.functor = functor
        elif isinstance(functor, str):
            self.functor = _functor(functor, len(self.terms))
        else:
            raise Exception("Invalid functor: %s" % functor)

    @classmethod
    def from_term(cls, t):
        lib = Swipl.lib
        f = Functor.from_term(t)
        # arg handles are consecutive, args = arg0, arg0 + 1, ...
        a0 = lib.new_term_refs(f.arity)
        terms = []
        for i, arg_handle in enumerate(range(a0, a0 + f.arity)):
            if lib.get_arg(i + 1, t, arg_handle):
                terms.append(Term.decode(arg_handle))
        return cls(t, functor=f, terms=terms, arg0=a0)

    @property
    def value(self):
        fun = Functor.funcs.get("%s/%s" % (self.functor.value, len(self.terms)))
        if fun is None:
            return self
        return fun(*self.terms)

    @property
    def norm_value(self):
        fun = Functor.funcs.get("%s/%s" % (self.functor.value, len(self.terms)))
        if fun is None:
            return self
        return norm_value(fun(*self.terms))

    def __repr__(self):
        return "Compound(%s(%s))" % (repr(self.functor), ", ".join(repr(t) for t in self.terms))

    def __str__(self):
        return "%s(%s)" % (str(self.functor), ", ".join(str(t) for t in self.terms))

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        return self.functor == other.functor and \
            self.terms == other.terms


def compound(functor, *terms):
    return Compound(None, functor=functor, terms=terms)


class Term:

    _router = {}

    @classmethod
    def decode(cls, t: int):
        term_type = Swipl.lib.term_type(t)
        fun = cls._router[term_type]
        return fun(t)

    @classmethod
    def decode_atom(cls, t: int) -> Atom:
        return Atom.from_term(t)

    @classmethod
    def decode_term(cls, t: int) -> Compound:
        lib = Swipl.lib
        if lib.is_compound(t):
            return Compound.from_term(t)
        raise PrologError("Cannot decode term: %s", t)

    @classmethod
    def decode_integer(cls, t: int) -> int:
        i = c_long()
        Swipl.lib.get_long(t, byref(i))
        return i.value

    @classmethod
    def decode_float(cls, t: int) -> float:
        d = c_double()
        Swipl.lib.get_float(t, byref(d))
        return d.value

    @classmethod
    def decode_string(cls, t: int) -> str:
        slen = c_int()
        s = c_char_p()
        Swipl.lib.get_string_chars(t, byref(s), byref(slen))
        return s.value

    @classmethod
    def decode_nil(cls, t: int) -> Atom:
        return NIL

    @classmethod
    def decode_pair(cls, t: int) -> Union[List, Tuple]:
        ls = cls.decode_list(t)
        if len(ls) == 1:
            return ls[0]
        if Swipl.lib.is_list(t):
            return ls
        return tuple(ls)

    @classmethod
    def decode_list(cls, t: int) -> List:
        lib = Swipl.lib
        t = lib.copy_term_ref(t)
        head = lib.new_term_ref()
        result = []
        while lib.get_list(t, head, t):
            result.append(Term.decode(head))
        return result

    @classmethod
    def decode_functor(cls, t):
        return Functor.from_term(t)


Term._router = {
    PL_VARIABLE: Variable.from_term,
    PL_ATOM: Atom.from_term,
    PL_TERM: Term.decode_term,
    PL_INTEGER: Term.decode_integer,
    PL_FLOAT: Term.decode_float,
    PL_STRING: Term.decode_string,
    PL_NIL: Term.decode_nil,
    PL_LIST_PAIR: Term.decode_pair,
    PL_LIST: Term.decode_list,
}


def norm_value(value):
    if hasattr(value, "norm_value"):
        return value.norm_value
    if isinstance(value, dict):
        return dict((norm_value(k), norm_value(v)) for k, v in value.items())
    elif isinstance(value, list):
        return [norm_value(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(norm_value(item) for item in value)
    return value


def _flatten_tuple(t):
    if not isinstance(t, tuple):
        return t
    ls = []
    for item in t:
        if isinstance(item, tuple):
            ls.extend(_flatten_tuple(item))
        else:
            ls.append(item)
    return tuple(ls)


functor = _functor
