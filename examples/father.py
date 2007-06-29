# -*- coding: utf-8 -*-

from pyswip import *

def main():
    p = Prolog()

    father = Functor("father", 2)
    mother = Functor("mother", 2)
    assertz = Functor("assertz", 1)

    #call(assertz(father("john", "mich")))
    #call(assertz(father("john", "gina")))
    #call(assertz(father("hank", "cloe")))
    #call(assertz(mother("jane", "mich")))
    #call(assertz(mother("jane", "gina")))

    p.assertz("father(john,mich)")
    p.assertz("father(john,gina)")
    p.assertz("mother(jane,mich)")

    X = Variable(); Y = Variable(); Z = Variable()

    listing = Functor("listing", 1)
    call(listing(father))

    #print list(p.query("listing(father))"))

    q = Query(father("john",Y), mother(Z,Y))
    while q.nextSolution():
        print Y.value, Z.value
        #print X.value, "is the father of", Y.value
        #print Z.value, "is the mother of", Y.value

    print "\nQuery with strings\n"
    for s in p.query("father(john,Y),mother(Z,Y)"):
        #print s["X"], "is the father of", s["Y"]
        #print s["Z"], "is the mother of", s["Y"] 
        print s["Y"], s["Z"]

    #print "running the query again"
    #q = Query(father(X, Y))
    #while q.nextSolution():
    #    print X.value, "is the father of", Y.value

if __name__ == "__main__":
    main()


