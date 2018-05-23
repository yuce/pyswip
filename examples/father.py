# -*- coding: utf-8 -*-

# pyswip -- Python SWI-Prolog bridge
# Copyright (c) 2007-2018 Yüce Tekol
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#  
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pyswip import *


def main():
    p = Prolog()

    father = Functor("father", 2)
    mother = Functor("mother", 2)
    assertz = Functor("assertz", 1)

    p.assertz("father(john,mich)")
    p.assertz("father(john,gina)")
    p.assertz("mother(jane,mich)")

    X = Variable(); Y = Variable(); Z = Variable()

    listing = Functor("listing", 1)
    call(listing(father))

    q = Query(father("john",Y), mother(Z,Y))
    while q.nextSolution():
        print(Y.value, Z.value)
    q.closeQuery()    # Newer versions of SWI-Prolog do not allow nested queries

    print("\nQuery with strings\n")
    for s in p.query("father(john,Y),mother(Z,Y)"):
        print(s["Y"], s["Z"])

if __name__ == "__main__":
    main()


