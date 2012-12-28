# -*- coding: utf-8 -*-


"""Regression tests for issues."""


import sys
import unittest
import subprocess


class TestIssues(unittest.TestCase):
    """Each test method is named after the issue it is testing. The docstring
       contains the link for the issue and the issue's description.
    """

    def test_issue_13_and_6(self):
        """
        Improve library loading.

        This issue used to manifest as an inability to load SWI-Prolog's
        SO/DLL. If this test fails, it will usually kill Python, so the test is
        very simple.

        This test is here but it should be run on several platforms to ensure it
        works.

        http://code.google.com/p/pyswip/issues/detail?id=13
        http://code.google.com/p/pyswip/issues/detail?id=6
        """

        import pyswip.core # This implicitly tests library loading code. It
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
        prolog = Prolog()
        prolog.assertz("randomTerm(michael,john)")

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

        prolog = Prolog()
        prolog.assertz("parent(michael,john)")
        prolog.assertz("parent(michael,gina)")
        p = prolog.query("parent(michael,X), hello(X)")
        result = list(p)   # Will run over the iterator
        
        self.assertEquals(len(callsToHello), 2)  # ['john', 'gina']
        self.assertEquals(len(result), 2) # [{'X': 'john'}, {'X': 'gina'}]

    def test_issue_15(self):
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
            self.assertEquals(result, code)

        runTestCode(0)
        runTestCode(1)
        runTestCode(2)
        runTestCode(127)


if __name__ == "__main__":
    unittest.main()
    
