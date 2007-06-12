# -*- coding: utf-8 -*-

# Adapted from:
# http://gollem.science.uva.nl/SWI-Prolog/Manual/foreigninclude.html#PL_register_foreign()

from pyswip import *

def main():
    prolog = Prolog()
    
    animal = Functor("animal", 2)
    assertz = Functor("assertz", 1)
    
    #call(assertz(animal("gnu", 50)))
    #call(assertz(animal("gnu", 76)))
    
    X = Variable()
    q = Query(animal("gnu", X))
    while q.nextSolution():
        print X.value
    

if __name__ == "__main__":
    main()
