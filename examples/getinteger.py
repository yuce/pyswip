# -*- coding: utf-8 -*-

# Test Prolog to Python lists

from pyswip.prolog import Prolog
from pyswip.easy import getInteger, getFloat, registerForeign

def print_int(*a):
    i = getInteger(a[0])
    print i, type(i)
    return True
print_int.arity = 1

def print_float(*a):
    d = getFloat(a[0])
    print d, type(d)
    return True
print_float.arity = 1

def print_bool(*a):
    b = getBool(a[0])
    print b, type(b)
    return True
print_bool.arity = 1

for f in [print_int, print_float, print_bool]:
    registerForeign(f)
prolog = Prolog()
#list(prolog.query("X=42, print_int(X), Y=3.42, print_float(Y), Z=X=:=Y", catcherrors=False))

