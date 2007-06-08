# -*- coding: utf-8 -*-

# Test Prolog to Python lists

from pyswip.prolog import *
from pyswip.easy import *

def print_list(*a):
    for i, item in enumerate(getList(a[0])):
        print i, item, type(item)
    return True

print_list.arity = 1

registerForeign(print_list)
p = Prolog()
print list(p.query("""Y=[17,18, 'Hello, World!', atom, [3,4]]""", catcherrors=False))
print list(p.query("Z=[Y=[1,2]]", catcherrors=False))
#print p.assertz("father(mich,john)")
print list(p.query("assertz(father(mich,john))"))
print list(p.query("assertz(father(mich,gina))"))
#print list(p.query("father(X,Y)"))
for r in p.query("father(X,Y)"):
    print ">", r
#print list(p.query("father(mich,gina)"))
#print list(p.query("T=f(X, g(X)), X=a"))
