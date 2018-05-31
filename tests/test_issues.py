# -*- coding: utf-8 -*-


# pyswip -- Python SWI-Prolog bridge
# Copyright (c) 2007-2012 Yüce Tekol
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


"""Regression tests for issues."""


import sys
import unittest
import subprocess

from pyswip.prolog import Prolog


class TestIssues(unittest.TestCase):

    p = Prolog()

    def test_issue_old_8(self):
        """
        Callbacks can cause segv's

        https://code.google.com/p/pyswip/issues/detail?id=8
        """

        from pyswip import Prolog, registerForeign

        callsToHello = []
        def hello(t):
            callsToHello.append(t)
        hello.arity = 1

        registerForeign(hello)

        prolog = Prolog()
        prolog.assertz("parent(michael,john)")
        prolog.assertz("parent(michael,gina)")
        p = prolog.query("parent(michael,X), hello(X)")
        result = list(p)   # Will run over the iterator
        
        self.assertEqual(len(callsToHello), 2)  # ['john', 'gina']
        self.assertEqual(len(result), 2) # [{'X': 'john'}, {'X': 'gina'}]

    def test_issue_old_15(self):
        """
       	sys.exit does not work when importing pyswip

        https://code.google.com/p/pyswip/issues/detail?id=15
        """

        # We will use it to test several return codes
        pythonExec = sys.executable
        def runTestCode(code):
            parameters = [pythonExec,
                          '-c',
                          'import sys; import pyswip; sys.exit(%d)' % code,]
            result = subprocess.call(parameters)
            self.assertEqual(result, code)

        runTestCode(0)
        runTestCode(1)
        runTestCode(2)
        runTestCode(127)

    def test_issue_old_4(self):
        """
       	Patch for a dynamic method

        Ensures that the patch is working.

        https://code.google.com/p/pyswip/issues/detail?id=4
        """

        from pyswip import Prolog
        
        Prolog.dynamic('test_issue_4_d/1')
        Prolog.assertz('test_issue_4_d(test1)')
        Prolog.assertz('test_issue_4_d(test1)')
        Prolog.assertz('test_issue_4_d(test1)')
        Prolog.assertz('test_issue_4_d(test2)')
        results = list(Prolog.query('test_issue_4_d(X)'))
        self.assertEqual(len(results), 4)
        
        Prolog.retract('test_issue_4_d(test1)')
        results = list(Prolog.query('test_issue_4_d(X)'))
        self.assertEqual(len(results), 3)
        
        Prolog.retractall('test_issue_4_d(test1)')
        results = list(Prolog.query('test_issue_4_d(X)'))
        self.assertEqual(len(results), 1)

    def test_issue_old_3(self):
        """
       	Problem with variables in lists

        https://code.google.com/p/pyswip/issues/detail?id=3
        """

        from pyswip import Prolog, Functor, Variable, Atom
         
        p = Prolog()
         
        f = Functor('f', 1)
        A = Variable()
        B = Variable()
        C = Variable()
         
        x = f([A, B, C])
        x = Functor.fromTerm(x)
        args = x.args[0]

        self.assertFalse(args[0] == args[1], "Var A equals var B")
        self.assertFalse(args[0] == args[2], "Var A equals var C")
        self.assertFalse(args[1] == args[2], "Var B equals var C")

        self.assertFalse(A == B, "Var A equals var B")
        self.assertFalse(B == C, "Var A equals var C")
        self.assertFalse(A == C, "Var B equals var C")

        # A more complex test
        x = f([A, B, 'c'])
        x = Functor.fromTerm(x)
        args = x.args[0]
        self.assertEqual(type(args[0]), Variable)
        self.assertEqual(type(args[1]), Variable)
        self.assertEqual(type(args[2]), Atom)

        # A test with repeated variables
        x = f([A, B, A])
        x = Functor.fromTerm(x)
        args = x.args[0]
        self.assertEqual(type(args[0]), Variable)
        self.assertEqual(type(args[1]), Variable)
        self.assertEqual(type(args[2]), Variable)
        self.assertTrue(args[0] == args[2], "The first and last var of "
                                            "f([A, B, A]) should be the same")


        
if __name__ == "__main__":
    unittest.main()
    
