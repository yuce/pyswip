
from pyswip.prolog import Prolog
from pyswip.easy import getAtomChars, unifyInteger, registerForeign

def atom_checksum(*a):
    s = getAtomChars(a[0])
    if s is not None:
        r = sum(ord(c)&0xFF for c in s)
        return unifyInteger(a[1], r&0xFF)
    else:
        return False
atom_checksum.arity = 2

p = Prolog()
registerForeign(atom_checksum)
print list(p.query("X='Python', atom_checksum(X, Y)"))
