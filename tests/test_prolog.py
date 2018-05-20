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


"""
Tests the Prolog class.
"""


import unittest
import doctest

import pyswip.prolog as pl   # This implicitly tests library loading code


class TestProlog(unittest.TestCase):
    """
    Unit tests for prolog module (contains only Prolog class).
    """

    def test_nested_queries(self):
        """
        SWI-Prolog cannot have nested queries called by the foreign function
        interface, that is, if we open a query and are getting results from it,
        we cannot open another query before closing that one.

        Since this is a user error, we just ensure that a appropriate error
        message is thrown.
        """
        
        p = pl.Prolog()

        # Add something to the base
        p.assertz("father(john,mich)")
        p.assertz("father(john,gina)")
        p.assertz("mother(jane,mich)")

        somequery = "father(john, Y)"
        otherquery = "mother(jane, X)"

        # This should not throw an exception
        for _ in p.query(somequery):
            pass
        for _ in p.query(otherquery):
            pass
        
        with self.assertRaises(pl.NestedQueryError):
            for q in p.query(somequery):
                for j in p.query(otherquery):
                    # This should throw an error, because I opened the second
                    # query
                    pass


if __name__ == "__main__":
    unittest.main()
    
