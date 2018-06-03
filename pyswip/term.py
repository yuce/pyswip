
import itertools
from ctypes import create_string_buffer, cast

from .swipl import Swipl, byref, c_int, c_char_p, c_long, c_double
from .const import \
    PL_ATOM, PL_INTEGER, PL_FLOAT, PL_STRING, PL_TERM, PL_NIL, PL_LIST_PAIR, PL_LIST, PL_VARIABLE, \
    atom_t, functor_t, CVT_VARIABLE, BUF_RING

__all__ = "FALSE", "NIL", "TRUE", \
          "Atom", "Functor", "Term", \
          "atom", "atoms", "functor", "functors", "norm_value"


class Atom:

    def __init__(self, handle, name=""):
        self.handle = handle
        self.name = name

    @classmethod
    def from_term(cls, t):
        a = atom_t()
        if Swipl.lib.get_atom(t, byref(a)):
            return cls.from_handle(a.value)
        raise Exception("Invalid atom")  # TODO: Proper exception

    @classmethod
    def from_handle(cls, handle):
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

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        if self.name == other.name:
            return True
        return False

    def __hash__(self):
        return hash(self.name)


def atom(name):
    return Atom(None, name=name)


def atoms(*names):
    return tuple(atom(name) for name in names)


NIL = atom("[]")
TRUE = atom("true")
FALSE = atom("false")


class Term:

    _router = {}

    @classmethod
    def decode(cls, t):
        term_type = Swipl.lib.term_type(t)
        fun = cls._router[term_type]
        return fun(t)

    @classmethod
    def decode_atom(cls, t):
        return Atom.from_term(t)

    @classmethod
    def decode_term(cls, t):
        lib = Swipl.lib
        if lib.is_compound(t):
            return Functor.from_term(t)
        return 6

    @classmethod
    def decode_integer(cls, t):
        i = c_long()
        Swipl.lib.get_long(t, byref(i))
        return i.value

    @classmethod
    def decode_float(cls, t):
        d = c_double()
        Swipl.lib.get_float(t, byref(d))
        return d.value

    @classmethod
    def decode_string(cls, t):
        slen = c_int()
        s = c_char_p()
        Swipl.lib.get_string_chars(t, byref(s), byref(slen))
        return s.value

    @classmethod
    def decode_nil(cls, t):
        return NIL

    @classmethod
    def decode_pair(cls, t):
        ls = cls.decode_list(t)
        if len(ls) == 1:
            return ls[0]
        if Swipl.lib.is_list(t):
            return ls
        return tuple(ls)

    @classmethod
    def decode_list(cls, t):
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
        s = create_string_buffer(b"\00" * 64)  # FIXME:
        ptr = cast(s, c_char_p)
        handle = lib.copy_term_ref(t)
        if lib.get_chars(handle, byref(ptr), CVT_VARIABLE | BUF_RING):
            self.chars = ptr.value


Term._router = {
    PL_ATOM: Atom.from_term,
    PL_TERM: Term.decode_term,
    PL_INTEGER: Term.decode_integer,
    PL_FLOAT: Term.decode_float,
    PL_STRING: Term.decode_string,
    PL_NIL: Term.decode_nil,
    PL_LIST_PAIR: Term.decode_pair,
    PL_LIST: Term.decode_list,
}


class Binding:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    @property
    def value(self):
        return {self.a: self.b}

    @property
    def norm_value(self):
        return {norm_value(self.a): norm_value(self.b)}


class Functor:

    funcs = {}

    def __init__(self, handle, name, arity=None, args=None, arg0=None):
        self.handle = handle
        self.name = name
        self.arity = arity
        self.args = args or []
        if arity is None:
            self.arity = len(self.args)
        self.arg0 = arg0

    @classmethod
    def from_term(cls, t):
        lib = Swipl.lib
        f = functor_t()
        if lib.get_functor(t, byref(f)):
            handle = f.value
            args = []
            arity = lib.functor_arity(handle)
            # arg handles are consecutive, args = arg0, arg0 + 1, ...
            a0 = lib.new_term_refs(arity)
            for i, arg_handle in enumerate(range(a0, a0 + arity)):
                if lib.get_arg(i + 1, t, arg_handle):
                    args.append(Term.decode(arg_handle))
            name = Atom.from_handle(lib.functor_name(handle))
            return cls(handle, name, arity=arity, args=args, arg0=a0)
        raise Exception("Invalid functor")  # TODO: proper exception

    @classmethod
    def add_callable(cls, name, arity, fun):
        cls.funcs["%s/%s" % (name, arity)] = fun

    @property
    def value(self):
        fun = self.funcs.get("%s/%s" % (self.name.value, self.arity))
        if fun is not None:
            return fun(*self.args)
        return self

    @property
    def norm_value(self):
        fun = self.funcs.get("%s/%s" % (self.name.value, self.arity))
        if fun is not None:
            return norm_value(fun(*self.args))
        return self

    def __repr__(self):
        return "Functor(%s(%s))" % (self.name.value, ", ".join(repr(a) for a in self.args))

    def __str__(self):
        return "%s(%s)" % (self.name.value, ", ".join(str(a) for a in self.args))

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name and \
               self.arity == other.arity and \
               self.args == other.args

    def __call__(self, *args, **kwargs):
        return Functor(None, name=self.name, args=list(args))


def functor(name, args=None, arity=None):
    return Functor(None, name=atom(name), arity=arity, args=args)


def functors(*names):
    return tuple(functor(name) for name in names)


def _unify(arg1, arg2):
    return Binding(arg1, arg2)


def _tuple(*args):
    return tuple(args)


Functor.add_callable("=", 2, _unify)
Functor.add_callable(",", 2, _tuple)


class Variable:

    def __init__(self, handle, name):
        self.handle = handle
        self.name = name


def norm_value(value):
    f = getattr(value, "norm_value", None)
    if hasattr(value, "norm_value"):
        return value.norm_value
    if isinstance(value, dict):
        return dict((norm_value(k), norm_value(v)) for k, v in value.items())
    elif isinstance(value, list):
        return [norm_value(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(itertools.chain.from_iterable(norm_value(item) for item in value))
    return value
