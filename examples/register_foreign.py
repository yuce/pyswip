
from pyswip import Prolog, registerForeign, Atom

def atom_checksum(*a):
    if isinstance(a[0], Atom):
        r = sum(ord(c)&0xFF for c in str(a[0]))
        a[1].value = r&0xFF
        return True
    else:
        return False

p = Prolog()
registerForeign(atom_checksum, arity=2)
print list(p.query("X='Python', atom_checksum(X, Y)", catcherrors=False))
