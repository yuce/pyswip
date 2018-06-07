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

"""
Run several complex examples using pySwip. The main goal of these tests is
ensure stability in several platforms.
"""

import unittest

# from pyswip import *
from pyswip.prolog import Prolog


class TestExamples(unittest.TestCase):
    """
    Each test method is named after one example in $PYSWIP/examples.

    WARNING: Since it is not possible to unload things from the Prolog base, the
    examples have to be 'orthogonal'.
    """

    p = Prolog()

    def test_create_term(self):
        """
        Simple example of term creation.
        """

        from pyswip.swipl import Swipl

        lib = Swipl.lib
        p = self.p

        a1 = lib.new_term_refs(2)
        a2 = a1 + 1
        t = lib.new_term_ref()
        ta = lib.new_term_ref()

        animal2 = lib.new_functor(lib.new_atom("animal"), 2)
        assertz = lib.new_functor(lib.new_atom("assertz"), 1)

        lib.put_atom_chars(a1, "gnu")
        lib.put_integer(a2, 50)
        lib.cons_functor_v(t, animal2, a1)
        lib.cons_functor_v(ta, assertz, t)
        lib.call(ta, None)

        result = list(p.query("animal(X,Y)", catcherrors=True))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {'X': 'gnu', 'Y': 50})

    def test_knowledgebase(self):
        """
        Tests usage of modules.
        """

        p = Prolog()
         
        assertz = Functor("assertz")
        parent = Functor("parent", 2)
        test1 = newModule("test1")
        test2 = newModule("test2")
         
        call(assertz(parent("john", "bob")), module=test1)
        call(assertz(parent("jane", "bob")), module=test1)
         
        call(assertz(parent("mike", "bob")), module=test2)
        call(assertz(parent("gina", "bob")), module=test2)
         
        # Test knowledgebase module test1
 
        result = set()
        X = Variable()
        q = Query(parent(X, "bob"), module=test1)
        while q.nextSolution():
            result.add(X.value.value)    # X.value is an Atom
        q.closeQuery()
        self.assertEqual(result, set(["john", "jane"]))
         
        # Test knowledgebase module test2
         
        result = set()
        q = Query(parent(X, "bob"), module=test2)
        while q.nextSolution():
            result.add(X.value.value)
        q.closeQuery()
        self.assertEqual(result, set(["mike", "gina"]))

    def test_father(self):
        """
        Tests basic inferences.
        """

        p = Prolog()
     
        father = Functor("father", 2)
        mother = Functor("mother", 2)
     
        p.assertz("father(john,mich)")
        p.assertz("father(john,gina)")
        p.assertz("mother(jane,mich)")
     
        X = Variable()
        Y = Variable()
        Z = Variable()
  
        result = []
        q = Query(father("john", Y), mother(Z, Y))
        while q.nextSolution():
            y = Y.value.value
            z = Z.value.value
            result.append({'Y': y, 'Z': z})
        q.closeQuery()
   
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {'Y': 'mich', 'Z': 'jane'})

        # Repeat the same query but using strings
        result = []
        for s in p.query("father(john,Y),mother(Z,Y)"):
            result.append(s)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {'Y': 'mich', 'Z': 'jane'})
     
    def test_coins(self):
        """
        Runs the coins example (uses clp library of SWI-Prolog).
        """

        prolog = Prolog()
        prolog.consult(example_path("coins/coins.pl"))
        count = 100
        total = 500
        coins = Functor("coins", 3)
        S = Variable()
        q = Query(coins(S, count, total))
 
        solutions = []
        while q.nextSolution():
            solutions.append(S.value)
        q.closeQuery()
 
        self.assertEqual(len(solutions), 105)

        # Now do the same test, but using the prolog.query interface
        solutions = list(prolog.query("coins(S, %d, %d)." % (count,total)))
        self.assertEqual(len(solutions), 105)

    def test_draughts(self):
        """
        Runs the draughts example (uses clp library of SWI-Prolog).
        """
        
        p = self.p
        p.consult(example_path("draughts/puzzle1.pl"))
        solutions = list(p.query("solve(B)."))
        self.assertEqual(len(solutions), 37)
        
    def test_hanoi(self):
        """
        Runs the hanoi example.
        """
 
        N = 3  # Number of disks
 
        result = []

        @Prolog.register
        def notify(t):
            result.append((t[0].value, t[1].value))

        p = self.p
        p.consult(example_path("hanoi/hanoi.pl"))
        list(p.query("hanoi(%d)" % N))
        self.assertEqual(len(result), 7)
        self.assertEqual(result[0], ('left', 'right'))
        self.assertEqual(result[1], ('left', 'center'))
        self.assertEqual(result[2], ('right', 'center'))
        
    def test_sendmoremoney(self):
        """
        Runs the sendmoremoney example::

            S E N D
            M O R E
          + -------
          M O N E Y
         
        So, what should be the values of S, E, N, D, M, O, R, Y
        if they are all distinct digits.
        """
        
        letters = "S E N D M O R Y".split()
        prolog = Prolog()
        sendmore = Functor("sendmore")
        prolog.consult(example_path("sendmoremoney/money.pl"))

        X = Variable()
        call(sendmore(X))
        r = X.value
        val = {}
        for i, letter in enumerate(letters):
            val[letter] = r[i]

        self.assertEqual(len(val), 8)
        
        send = val['S']*1e3 + val['E']*1e2 + val['N']*1e1 + val['D']*1e0
        more = val['M']*1e3 + val['O']*1e2 + val['R']*1e1 + val['E']*1e0
        money = val['M']*1e4 + val['O']*1e3 + val['N']*1e2 + val['E']*1e1 + val['Y']*1e0
        self.assertEqual(money, send + more)
 
    def test_sudoku(self):
        """
        Runs the sudoku example (uses clp library of SWI-Prolog).
        """
        
        _ = 0
        puzzle1 = [
            [_,6,_,1,_,4,_,5,_],
            [_,_,8,3,_,5,6,_,_],
            [2,_,_,_,_,_,_,_,1],
            [8,_,_,4,_,7,_,_,6],
            [_,_,6,_,_,_,3,_,_],
            [7,_,_,9,_,1,_,_,4],
            [5,_,_,_,_,_,_,_,2],
            [_,_,7,2,_,6,9,_,_],
            [_,4,_,5,_,8,_,7,_]
            ]
         
        puzzle2 = [
            [_,_,1,_,8,_,6,_,4],
            [_,3,7,6,_,_,_,_,_],
            [5,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,5,_,_,_],
            [_,_,6,_,1,_,8,_,_],
            [_,_,_,4,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,3],
            [_,_,_,_,_,7,5,2,_],
            [8,_,2,_,9,_,7,_,_]
                  ]
            
        p = self.p
        p.consult(example_path("sudoku/sudoku.pl"))

        for i, problem in enumerate((puzzle1, puzzle2)):
            problem = str(problem).replace("0", "_")
            result = list(p.query("L=%s,sudoku(L)" % problem, maxresult=1))
            if result:
                # Does a simple check on the result
                result = result[0]
                for j, line in enumerate(result["L"]):
                    self.assertEqual(len(set(line)), 9,
                                     "Failure in line %d: %s" % (j, line))
            else:
                self.fail("Failed while running example number %d" % i)


def example_path(path):
    import os.path
    return os.path.normpath(os.path.join(os.path.split(os.path.abspath(__file__))[0], "..", "examples", path))
