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

import subprocess
import sys
import unittest


class TestIssues(unittest.TestCase):
    """Each test method is named after the issue it is testing. The docstring
    contains the link for the issue and the issue's description.
    """

    def test_issue_13_17_and_6(self):
        """
        Improve library loading.

        This issue used to manifest as an inability to load SWI-Prolog's
        SO/DLL. If this test fails, it will usually kill Python, so the test is
        very simple.

        This test is here but it should be run on several platforms to ensure it
        works.

        http://code.google.com/p/pyswip/issues/detail?id=13
        http://code.google.com/p/pyswip/issues/detail?id=6
        https://code.google.com/p/pyswip/issues/detail?id=17
        """

        # won't be very useful if it is not tested in several
        # OSes

    def test_issue_1(self):
        """
        Segmentation fault when assertz-ing

        Notes: This issue manifests only in 64bit stacks (note that a full 64
        bit stack is needed. If running 32 in 64bit, it will not happen.)

        http://code.google.com/p/pyswip/issues/detail?id=1
        """

        # The simple code below should be enough to trigger the issue. As with
        # issue 13, if it does not work, it will segfault Python.
        from pyswip import Prolog

        Prolog.assertz("randomTerm(michael,john)")

    def test_issue_8(self):
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

        Prolog.assertz("parent(michael,john)")
        Prolog.assertz("parent(michael,gina)")
        p = Prolog.query("parent(michael,X), hello(X)")
        result = list(p)  # Will run over the iterator

        self.assertEqual(len(callsToHello), 2)  # ['john', 'gina']
        self.assertEqual(len(result), 2)  # [{'X': 'john'}, {'X': 'gina'}]

    def test_issue_15(self):
        """
        sys.exit does not work when importing pyswip

        https://code.google.com/p/pyswip/issues/detail?id=15
        """

        # We will use it to test several return codes
        pythonExec = sys.executable

        def runTestCode(code):
            parameters = [
                pythonExec,
                "-c",
                "import sys; import pyswip; sys.exit(%d)" % code,
            ]
            result = subprocess.call(parameters)
            self.assertEqual(result, code)

        runTestCode(0)
        runTestCode(1)
        runTestCode(2)
        runTestCode(127)

    def test_issue_5(self):
        """
        Patch: hash and eq methods for Atom class.

        Ensures that the patch is working.

        https://code.google.com/p/pyswip/issues/detail?id=5
        """

        from pyswip import Atom, Variable

        a = Atom("test")
        b = Atom("test2")
        c = Atom("test")  # Should be equal to a

        self.assertNotEqual(a, b)
        self.assertNotEqual(c, b)
        self.assertEqual(a, c)

        atomSet = set()
        atomSet.add(a)
        atomSet.add(b)
        atomSet.add(c)  # This is equal to a
        self.assertEqual(len(atomSet), 2)
        self.assertEqual(atomSet, set([a, b]))

        # The same semantics should be valid for other classes
        A = Variable()
        B = Variable()
        C = Variable(A.handle)  # This is equal to A

        self.assertNotEqual(A, B)
        self.assertNotEqual(C, B)
        self.assertEqual(A, C)
        varSet = set()
        varSet.add(A)
        varSet.add(B)
        varSet.add(C)  # This is equal to A
        self.assertEqual(len(varSet), 2)
        self.assertEqual(varSet, {A, B})

    def test_dynamic(self):
        """
        Patch for a dynamic method

        Ensures that the patch is working.

        https://code.google.com/p/pyswip/issues/detail?id=4
        """

        from pyswip import Prolog

        Prolog.dynamic("test_issue_4_d/1")
        Prolog.assertz("test_issue_4_d(test1)")
        Prolog.assertz("test_issue_4_d(test1)")
        Prolog.assertz("test_issue_4_d(test1)")
        Prolog.assertz("test_issue_4_d(test2)")
        results = list(Prolog.query("test_issue_4_d(X)"))
        self.assertEqual(len(results), 4)

        Prolog.retract("test_issue_4_d(test1)")
        results = list(Prolog.query("test_issue_4_d(X)"))
        self.assertEqual(len(results), 3)

        Prolog.retractall("test_issue_4_d(test1)")
        results = list(Prolog.query("test_issue_4_d(X)"))
        self.assertEqual(len(results), 1)

    def test_issue_3(self):
        """
        Problem with variables in lists

        https://code.google.com/p/pyswip/issues/detail?id=3
        """

        from pyswip import Prolog, Functor, Variable, Atom

        _ = Prolog()

        f = Functor("f", 1)
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
        x = f([A, B, "c"])
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
        self.assertTrue(
            args[0] == args[2],
            "The first and last var of " "f([A, B, A]) should be the same",
        )

    def test_issue_62(self):
        """
        Problem with non-ascii atoms and strings

        https://github.com/yuce/pyswip/issues/62
        """
        from pyswip import Prolog

        Prolog.consult("test_unicode.pl", catcherrors=True, relative_to=__file__)
        atoms = list(Prolog.query("unicode_atom(B)."))

        self.assertEqual(len(atoms), 3, "Query should return exactly three atoms")

        strings = list(Prolog.query("unicode_string(B)."))

        self.assertEqual(len(strings), 1, "Query should return exactly one string")
        self.assertEqual(strings[0]["B"], b"\xd1\x82\xd0\xb5\xd1\x81\xd1\x82")

    def test_functor_return(self):
        """
        pyswip should generate string representations of query results
        that are at least meaningful, preferably equal to what
        SWI-Prolog would generate. This test checks if this is true for
        `Functor` instance results.

        Not a formal issue, but see forum topic:
        https://groups.google.com/forum/#!topic/pyswip/Mpnfq4DH-mI
        """

        import pyswip.prolog as pl

        p = pl.Prolog()
        p.consult("test_functor_return.pl", catcherrors=True, relative_to=__file__)
        query = "sentence(Parse_tree, [the,bat,eats,a,cat], [])"
        expectedTree = "s(np(d(the), n(bat)), vp(v(eats), np(d(a), n(cat))))"

        # This should not throw an exception
        results = list(p.query(query))
        self.assertEqual(len(results), 1, "Query should return exactly one result")

        ptree = results[0]["Parse_tree"]
        self.assertEqual(ptree, expectedTree)

        # A second test, based on what was posted in the forum
        p.assertz("friend(john,son(miki))")
        p.assertz("friend(john,son(kiwi))")
        p.assertz("friend(john,son(wiki))")
        p.assertz("friend(john,son(tiwi))")
        p.assertz("father(son(miki),kur)")
        p.assertz("father(son(kiwi),kur)")
        p.assertz("father(son(wiki),kur)")

        soln = [s["Y"] for s in p.query("friend(john,Y), father(Y,kur)", maxresult=1)]
        self.assertEqual(soln[0], "son(miki)")
