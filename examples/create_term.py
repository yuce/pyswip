# -*- coding:utf-8 -*-

from pyswip.core import *
from pyswip.prolog import Prolog

def main():
    prolog = Prolog()
    
    a1 = PL_new_term_refs(2)
    a2 = a1 + 1
    t = PL_new_term_ref()
    ta = PL_new_term_ref()

    animal2 = PL_new_functor(PL_new_atom("animal"), 2)
    assertz = PL_new_functor(PL_new_atom("assertz"), 1)

    PL_put_atom_chars(a1, "gnu")
    PL_put_integer(a2, 50)
    #PL_cons_functor(t, animal2, a1, a2)
    PL_cons_functor_v(t, animal2, a1)
    PL_cons_functor_v(ta, assertz, t)
    PL_call(ta, None)
    
#    prolog.assertz("animal(gnu, 50)")
    print list(prolog.query("animal(X,Y)", catcherrors=True))
    
if __name__ == "__main__":
    main()