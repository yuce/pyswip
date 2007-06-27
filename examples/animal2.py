# -*- coding: utf-8 -*-

# Adapted from:
# http://gollem.science.uva.nl/SWI-Prolog/Manual/foreigninclude.html#PL_register_foreign()

from pyswip import *

def main():
    prolog = Prolog()

    animal = Functor("animal", 2)
    assertz = Functor("assertz", 1)

    X = Variable()
    call(assertz(animal("gnu", 50)))
    call(assertz(animal("gnu", [1,2,3])))
    #call(assertz(animal("gnu", animal(10,20))))
    call(assertz(animal("gnu", 70)))
    call(assertz(animal("gnu", 80)))
    call(assertz(animal("gnu", [4,5,6])))

    q = Query(animal("gnu", X))
    while q.nextSolution():
        print X.value

    q = Query(animal("gnu", X))
    while q.nextSolution():
        print X.value

    #listing = Functor("listing", 1)
    #q = Query(listing(animal))
    #while q.nextSolution():
    #    pass

if __name__ == "__main__":
    main()
