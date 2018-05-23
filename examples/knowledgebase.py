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

    assertz = Functor("assertz")
    parent = Functor("parent", 2)
    test1 = newModule("test1")
    test2 = newModule("test2")

    call(assertz(parent("john", "bob")), module=test1)
    call(assertz(parent("jane", "bob")), module=test1)

    call(assertz(parent("mike", "bob")), module=test2)
    call(assertz(parent("gina", "bob")), module=test2)

    print("knowledgebase test1")

    X = Variable()
    q = Query(parent(X, "bob"), module=test1)
    while q.nextSolution():
        print(X.value)
    q.closeQuery()

    print("knowledgebase test2")

    q = Query(parent(X, "bob"), module=test2)
    while q.nextSolution():
        print(X.value)
    q.closeQuery()

if __name__ == "__main__":
    main()