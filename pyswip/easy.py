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

PYSWIP_UNIFY = 274700

class InvalidTypeError(TypeError):
    def __init__(self, *args):
        type = args and args[0] or "Unknown"
        msg = "Term is expected to be of type: '%s'" % type
        Exception.__init__(self, msg, *args)
        

class Atom(object):
    __slots__ = "handle","chars"
    def __init__(self, handle, term=None):
        self.handle = handle
        PL_register_atom(handle)
        s = c_char_p()
        if term and PL_get_atom_chars(term, addressof(s)):
            self.chars = s.value
        else:
            self.chars = None
        
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
    __slots__ = "handle","chars","__value"
    def __init__(self, handle=None):
        if handle:
            self.handle = PL_copy_term_ref(handle)
        else:
            self.handle = PL_new_term_ref()
        self.chars = None
        
    def get_value(self):
        pass
    
class Variable(object):
    __slots__ = "handle","chars"
    def __init__(self, handle, term=None):
        self.handle = handle
        s = c_char_p()
        if term and PL_get_chars(term, addressof(s)):
            self.chars = s.value
        else:
            self.chars = None
            
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
        
        fun(self.handle, value)
            
    def __str__(self):
        if self.chars is not None:
            return self.chars
        else:
            return self.__repr__            
        
    def __repr__(self):
        return "Variable(%d)" % self.handle

class Functor(object):
    __slots__ = "handle","name","arity","args","__value"
    func = {}
    def __init__(self, handle, term=None):
        self.handle = handle
        self.name = None
        self.arity = None
        self.args = []
        a = atom_t()
        i = c_int()
        if term and PL_get_name_arity(term, addressof(a), addressof(i)):
            self.name = Atom(a.value, term=term)
            c = c_char_p()
            PL_get_chars(term, addressof(c), CVT_ALL | CVT_WRITE | BUF_RING)
            #print "c=", c.value
            self.arity = i.value
            #print "name", self.name
            #print "Arity", self.arity, type(self.arity)
            args = self.args
            for i in range(1, self.arity + 1):
                arg = PL_new_term_ref()
                if PL_get_arg(i, term, arg):
                    args.append(getTerm(arg))
            try:
                #print self.handle, type(self.handle)
                self.__value = self.func[self.handle](self.arity, *self.args)
            except KeyError:
                self.__value = {}
                
    value = property(lambda s: s.__value)
        
    def __str__(self):
        if self.name is not None and self.arity is not None:
            return "%s(%d)" % (self.name,self.arity)
        else:            
            return self.__repr__()
    
    def __repr__(self):
        #return str(self.handle).join(["Atom('", "')"])
        return "".join(["Functor(", ",".join(str(x) for x in [self.handle,self.arity]+self.args), ")"])
    
def _unifier(arity, *args):
    assert arity == 2
    #print args, [type(arg) for arg in args]
    #if PL_is_variable(args[0]):
    #    args[0].unify(args[1])
    try:
        return {args[0].chars:args[1].value}
    except AttributeError:
        return {args[0].chars:args[1]}

Functor.func[274700] = _unifier

def _callbackWrapper(arity=1):
    return CFUNCTYPE(*([foreign_t] + [term_t]*arity))

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
    a = atom_t()
    if PL_get_atom(t, addressof(a)):
        return Atom(a.value, term=t)
    else:
        raise InvalidTypeError("atom")    

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
    #print "getTerm", p
    if p < PL_TERM:
        return _getterm_router[p](t)
    elif PL_is_list(t):
        return getList(t)
    else:
        return getFunctor(t)

def getList(t):
    """Return t as a list.
    """
    head = PL_new_term_ref()
    result = []
    while PL_get_list(t, head, t):
        result.append(getTerm(head))
        
    return result

def getFunctor(t):
    """Return t as a functor
    """
    f = functor_t()
    if PL_get_functor(t, addressof(f)):
        return Functor(f.value, term=t)
    else:
        raise InvalidTypeError("functor")
    
def getVariable(t):
    return Variable(t)

_getterm_router = {
                    PL_VARIABLE:getVariable, PL_ATOM:getAtom, PL_STRING:getString,
                    PL_INTEGER:getInteger, PL_FLOAT:getFloat,
                    PL_TERM:getTerm
                    }

unifyInteger = PL_unify_integer

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

    return PL_register_foreign(name, arity, _callbackWrapper(arity)(func), flags)
    
    
    