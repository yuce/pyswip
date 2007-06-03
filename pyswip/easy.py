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
    def __init__(self, handle, term=None):
        self.handle = handle
        PL_register_atom(handle)
        s = c_char_p()
        if term and PL_get_atom_chars(term, addressof(s)):
            self.chars = s.value
        else:
            self.chars = ""
        
    def __del__(self):
        PL_unregister_atom(self.handle)
    
    def __str__(self):
        return self.chars
    
    def __repr__(self):
        return str(self.handle).join(["Atom('", "')"])
        

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

def getList(t):
    """Return t as a list.
    """
    head = PL_new_term_ref()
    result = []
    while PL_get_list(t, head, t):
        result.append(_getList_router[PL_term_type(head)](head))        
        
    return result

def _get_atom(t):
    if PL_is_string(t):
        return getString(t)
    else:
        return getAtom(t)

_getList_router = {PL_VARIABLE:None, PL_ATOM:getAtom, PL_STRING:getString,
                    PL_INTEGER:getInteger, PL_FLOAT:getFloat,
                    PL_TERM:getList}

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
    
    
    