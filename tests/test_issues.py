# -*- coding: utf-8 -*-

# Copyright 2007 Yuce Tekol <yucetekol@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import sys
import unittest


from pyswip.prolog import Prolog


class TestIssues(unittest.TestCase):

    p = Prolog()

    def test_issue_old_15(self):
        """
       	sys.exit does not work when importing pyswip

        https://code.google.com/p/pyswip/issues/detail?id=15
        """

        # We will use it to test several return codes
        python_exec = sys.executable

        def run_test_code(code):
            parameters = [python_exec,
                          '-c',
                          'import sys; import pyswip; sys.exit(%d)' % code,]
            result = subprocess.call(parameters)
            self.assertEqual(result, code)

        run_test_code(0)
        run_test_code(1)
        run_test_code(2)
        run_test_code(127)

    def test_issue_old_4(self):
        """
       	Patch for a dynamic method

        Ensures that the patch is working.

        https://code.google.com/p/pyswip/issues/detail?id=4
        """

        p = self.p

        p.dynamic('test_issue_4_d/1')
        p.assertz('test_issue_4_d(test1)')
        p.assertz('test_issue_4_d(test1)')
        p.assertz('test_issue_4_d(test2)')
        p.assertz('test_issue_4_d(test1)')
        results = list(p.query('test_issue_4_d(X)'))
        self.assertEqual(len(results), 4)

        p.retract('test_issue_4_d(test1)')
        results = list(p.query('test_issue_4_d(X)'))
        self.assertEqual(len(results), 3)

        p.retractall('test_issue_4_d(test1)')
        results = list(p.query('test_issue_4_d(X)'))
        self.assertEqual(len(results), 1)

    # def test_issue_old_3(self):
    #     """
    #    	Problem with variables in lists
    #
    #     https://code.google.com/p/pyswip/issues/detail?id=3
    #     """
    #
    #     from pyswip import Prolog, Functor, Variable, Atom
    #
    #     p = Prolog()
    #
    #     f = Functor('f', 1)
    #     A = Variable()
    #     B = Variable()
    #     C = Variable()
    #
    #     x = f([A, B, C])
    #     x = Functor.fromTerm(x)
    #     args = x.args[0]
    #
    #     self.assertFalse(args[0] == args[1], "Var A equals var B")
    #     self.assertFalse(args[0] == args[2], "Var A equals var C")
    #     self.assertFalse(args[1] == args[2], "Var B equals var C")
    #
    #     self.assertFalse(A == B, "Var A equals var B")
    #     self.assertFalse(B == C, "Var A equals var C")
    #     self.assertFalse(A == C, "Var B equals var C")
    #
    #     # A more complex test
    #     x = f([A, B, 'c'])
    #     x = Functor.fromTerm(x)
    #     args = x.args[0]
    #     self.assertEqual(type(args[0]), Variable)
    #     self.assertEqual(type(args[1]), Variable)
    #     self.assertEqual(type(args[2]), Atom)
    #
    #     # A test with repeated variables
    #     x = f([A, B, A])
    #     x = Functor.fromTerm(x)
    #     args = x.args[0]
    #     self.assertEqual(type(args[0]), Variable)
    #     self.assertEqual(type(args[1]), Variable)
    #     self.assertEqual(type(args[2]), Variable)
    #     self.assertTrue(args[0] == args[2], "The first and last var of "
    #                                         "f([A, B, A]) should be the same")
