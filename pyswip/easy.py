# -*- coding: utf-8 -*-

# pyswip.easy -- PySWIP helper functions
# (c) 2006-2007 Yüce TEKOL
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from pyswip.core import *


class InvalidTypeError(TypeError):
    def __init__(self, *args):
        type = args and args[0] or "Unknown"
        msg = "Term is expected to be of type: '%s'" % type
        Exception.__init__(self, msg, *args)


class Atom(object):
    __slots__ = "handle","chars"

    def __init__(self, handleOrChars):
        """Create an atom.
        ``handleOrChars``: handle or string of the atom.
        """
        if isinstance(handleOrChars, basestring):
            self.handle = PL_new_atom(handleOrChars)
            self.chars = handleOrChars
        else:
            self.handle = handleOrChars
            PL_register_atom(self.handle)
            self.chars = c_char_p(PL_atom_chars(self.handle)).value

    def fromTerm(cls, term):
        """Create an atom from a Term or term handle."""
        if isinstance(term, Term):
            term = term.handle

        a = atom_t()
        if PL_get_atom(term, addressof(a)):
            return cls(a.value)

    fromTerm = classmethod(fromTerm)

    def __del__(self):
        PL_unregister_atom(self.handle)

    value = property(lambda s:s.chars)

    def __str__(self):
        if self.chars is not None:
            return self.chars
        else:
            return self.__repr__()

    def __repr__(self):
        return str(self.handle).join(["Atom('", "')"])

class Term(object):
    __slots__ = "handle","chars","__value","a0"
    def __init__(self, handle=None, a0=None):
        if handle:
            #self.handle = PL_copy_term_ref(handle)
            self.handle = handle
        else:
            self.handle = PL_new_term_ref()
        self.chars = None
        self.a0 = a0

    def __invert__(self):
        return _not(self)

    def get_value(self):
        pass

class Variable(object):
    __slots__ = "handle","chars"

    def __init__(self, handle=None, name=None):
        self.chars = None
        if name:
            self.chars = name
        if handle:
            self.handle = handle
            s = create_string_buffer("\00"*64)  # FIXME:
            ptr = cast(s, c_char_p)
            if PL_get_chars(handle, byref(ptr), CVT_VARIABLE|BUF_RING):
                self.chars = ptr.value
        else:
            self.handle = PL_new_term_ref()
            #PL_put_variable(self.handle)

    def unify(self, value):
        if type(value) == str:
            fun = PL_unify_atom_chars
        elif type(value) == int:
            fun = PL_unify_integer
        elif type(value) == bool:
            fun = PL_unify_bool
        elif type(value) == float:
            fun = PL_unify_float
        elif type(value) == list:
            fun = PL_unify_list
        else:
            raise

        t = PL_new_term_ref()
        fun(t, value)
        self.handle = t

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
        return "Variable(%s)" % self.handle

    def put(self, term):
        #PL_put_variable(term)
        self.handle = term


class Functor(object):
    __slots__ = "handle","name","arity","args","__value","a0"
    func = {}

    def __init__(self, handleOrName, arity=1, args=None, a0=None):
        """Create a functor.
        ``handleOrName``: functor handle, a string or an atom.
        """

        self.args = args or []
        self.arity = arity
        self.a0 = a0

        if isinstance(handleOrName, basestring):
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
                self.__value = "Functor%d" % self.handle

    def fromTerm(cls, term):
        """Create a functor from a Term or term handle."""
        if isinstance(term, Term):
            term = term.handle

        f = functor_t()
        if PL_get_functor(term, addressof(f)):
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

    value = property(lambda s: s.__value)

    def __call__(self, *args):
        assert self.arity == len(args)
        a = PL_new_term_refs(len(args))
        for i, arg in enumerate(args):
            putTerm(a + i, arg)

        t = PL_new_term_ref()
        PL_cons_functor_v(t, self.handle, a)
        return Term(t)

    def __str__(self):
        if self.name is not None and self.arity is not None:
            return "%s(%d)" % (self.name,self.arity)
        else:
            return self.__repr__()

    def __repr__(self):
        return "".join(["Functor(", ",".join(str(x) for x in [self.handle,self.arity]+self.args), ")"])

def _unifier(arity, *args):
    assert arity == 2
    #if PL_is_variable(args[0]):
    #    args[0].unify(args[1])
    try:
        return {args[0].chars:args[1].value}
    except AttributeError:
        return {args[0].chars:args[1]}

_unify = Functor("=", 2)
Functor.func[_unify.handle] = _unifier
_not = Functor("not", 1)
_comma = Functor(",", 2)

def putTerm(term, value):
    if isinstance(value, Term):
        PL_put_term(term, value.handle)
    elif isinstance(value, basestring):
        PL_put_atom_chars(term, value)
    elif isinstance(value, int):
        PL_put_integer(term, value)
    elif isinstance(value, Variable):
        value.put(term)
    elif isinstance(value, list):
        putList(term, value)
    elif isinstance(value, Atom):
        print "ATOM"
    elif isinstance(value, Functor):
        PL_put_functor(term, value.handle)
    else:
        raise Exception("Not implemented")

def putList(l, ls):
    PL_put_nil(l)
    a = PL_new_term_ref()  #PL_new_term_refs(len(ls))
    for item in reversed(ls):
        putTerm(a, item)
        PL_cons_list(l, a, l)
    #PL_get_head(h, h)

# deprecated
def getAtomChars(t):
    """If t is an atom, return it as a string, otherwise raise InvalidTypeError.
    """
    s = c_char_p()
    if PL_get_atom_chars(t, addressof(s)):
        return s.value
    else:
        raise InvalidTypeError("atom")

def getAtom(t):
    """If t is an atom, return it , otherwise raise InvalidTypeError.
    """
    return Atom.fromTerm(t)

def getBool(t):
    """If t is of type bool, return it, otherwise raise InvalidTypeError.
    """
    b = c_int()
    if PL_get_long(t, addressof(b)):
        return bool(b.value)
    else:
        raise InvalidTypeError("bool")

def getLong(t):
    """If t is of type long, return it, otherwise raise InvalidTypeError.
    """
    i = c_long()
    if PL_get_long(t, addressof(i)):
        return i.value
    else:
        raise InvalidTypeError("long")

getInteger = getLong  # just an alias for getLong

def getFloat(t):
    """If t is of type float, return it, otherwise raise InvalidTypeError.
    """
    d = c_double()
    if PL_get_float(t, addressof(d)):
        return d.value
    else:
        raise InvalidTypeError("float")

def getString(t):
    """If t is of type string, return it, otherwise raise InvalidTypeError.
    """
    slen = c_int()
    s = c_char_p()
    if PL_get_string_chars(t, addressof(s), addressof(slen)):
        return s.value
    else:
        raise InvalidTypeError("string")

def getTerm(t):
    p = PL_term_type(t)
    if p < PL_TERM:
        return _getterm_router[p](t)
    elif PL_is_list(t):
        return getList(t)
    else:
        return getFunctor(t)

def getList(x):
    """Return t as a list.
    """
    t = PL_copy_term_ref(x)
    head = PL_new_term_ref()
    result = []
    while PL_get_list(t, head, t):
        result.append(getTerm(head))

    return result

def getFunctor(t):
    """Return t as a functor
    """
    return Functor.fromTerm(t)

def getVariable(t):
    return Variable(t)

_getterm_router = {
                    PL_VARIABLE:getVariable, PL_ATOM:getAtom, PL_STRING:getString,
                    PL_INTEGER:getInteger, PL_FLOAT:getFloat,
                    PL_TERM:getTerm
                    }

def _callbackWrapper(arity=1):
    return CFUNCTYPE(*([foreign_t] + [term_t]*arity))

def _foreignWrapper(fun):
    def wrapper(*args):
        args = [getTerm(arg) for arg in args]
        r = fun(*args)
        return (r is None) and True or r
    return wrapper

def registerForeign(func, name=None, arity=None, flags=0):
    """Register a Python predicate
    ``func``: Function to be registered. The function should return a value in
    ``foreign_t``, ``True`` or ``False``.
    ``name`` : Name of the function. If this value is not used, ``func.func_name``
    should exist.
    ``arity``: Arity (number of arguments) of the function. If this value is not
    used, ``func.arity`` should exist.
    """
    if arity is None:
        arity = func.arity

    if name is None:
        name = func.func_name

    return PL_register_foreign(name, arity,
            _callbackWrapper(arity)(_foreignWrapper(func)), flags)

newTermRef = PL_new_term_ref

def newTermRefs(count):
    a = PL_new_term_refs(count)
    return range(a, a + count)

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

def newModule(name):
    """Create a new module.
    ``name``: An Atom or a string
    """
    if isinstance(name, basestring):
        name = Atom(name)

    return PL_new_module(name.handle)

class Query(object):
    qid = None
    fid = None

    def __init__(self, *terms, **kwargs):
        for key in kwargs:
            if key not in ["flags", "module"]:
                raise Exception("Invalid kwarg: %s" % key, key)

        flags = kwargs.get("flags", PL_Q_NODEBUG|PL_Q_CATCH_EXCEPTION)
        module = kwargs.get("module", None)

        t = terms[0]
        for tx in terms[1:]:
            t = _comma(t, tx)

        f = Functor.fromTerm(t)
        p = PL_pred(f.handle, module)
        Query.qid = PL_open_query(module, flags, p, f.a0)

#    def __del__(self):
#        self.closeQuery()

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


def _test():
    #from pyswip.prolog import Prolog
    #p = Prolog()

    #p = _prolog

    assertz = Functor("assertz")
    a = Functor("a_")
    b = Functor("b_")

    call(assertz(a(10)))
    call(assertz(a([1,2,3])))
    call(assertz(a(11)))
    call(assertz(b(11)))
    call(assertz(b(12)))

    X = Variable()

    #q = Query(a(X), ~b(X))
    #q = Query(b(X), a(X))
    #while q.nextSolution():
    #    print X.value
    #print call(a(X),b(X))
    #print call(_comma(~a(X),a(X)))
    #q = Query(_comma(a(X), b(X)))
    q = Query(a(X))
    while q.nextSolution():
        print ">", X.value

if __name__ == "__main__":
    _test()

