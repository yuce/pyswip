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

from pyswip import *
from pyswip.core import *

def callbackWrapper(arity=1):
    #return CFUNCTYPE(*([foreign_t] + [term_t]*arity + [c_int, c_void_p]))
    return CFUNCTYPE(*([foreign_t] + [term_t]*arity))

def getAtomChars(t):
    """If t is an atom, return it as a string, otherwise return None.
    """
    s = c_char_p()
    if PL_get_atom_chars(t, addressof(s)):
        return s.value
    else:
        return None

def getList(t):
    """Return t as a list.
    """
    head = PL_new_term_ref()
    result = []
    v = c_char_p()
    while PL_get_list(t, head, t):
        PL_get_chars(head, addressof(v), CVT_ALL|CVT_WRITE)
        result.append(v.value)
        
    return result            

unifyInteger = PL_unify_integer

#PL_register_foreign("atom_checksum", 2, funtype(atom_checksum), PL_FA_VARARGS)
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

    return PL_register_foreign(name, arity, callbackWrapper(arity)(func), flags)
    
    
    