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
list(p.query("""Y=[17,18, 'Hello, World!', atom, [3,4]], print_list(Y)""", catcherrors=False))
