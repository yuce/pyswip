# -*- coding: utf-8 -*-
# based on http://gollem.science.uva.nl/SWI-Prolog/Manual/foreigninclude.html#sec:9.6.17

from pyswip import *
from pyswip.util import Prolog

def atom_checksum(a0, arity, context):
    s = c_char_p("\x00"*PYSWIP_MAXSTR)
    if PL_get_atom_chars(a0, addressof(s)):
        sum = 0
        for c in s.value:
            sum += ord(c)&0xFF;
        return PL_unify_integer(a0 + 1, sum&0xFF)
    else:
        return 0
    
funtype = CFUNCTYPE(foreign_t, term_t, c_int, c_void_p)

p = Prolog()
PL_register_foreign("atom_checksum", 2, funtype(atom_checksum), PL_FA_VARARGS)
print list(p.query("X='Python', atom_checksum(X, Y)", catcherrors=True))
