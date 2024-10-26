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

import os.path
import unittest

import pytest

from pyswip import Atom, Variable
from pyswip.prolog import Prolog, NestedQueryError, format_prolog


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

        # Add something to the base
        Prolog.assertz("father(john,mich)")
        Prolog.assertz("father(john,gina)")
        Prolog.assertz("mother(jane,mich)")

        somequery = "father(john, Y)"
        otherquery = "mother(jane, X)"

        # This should not throw an exception
        for _ in Prolog.query(somequery):
            pass
        for _ in Prolog.query(otherquery):
            pass

        with self.assertRaises(NestedQueryError):
            for q in Prolog.query(somequery):
                for j in Prolog.query(otherquery):
                    # This should throw an error, because I opened the second
                    # query
                    pass

    def test_prolog_functor_in_list(self):
        Prolog.assertz("f([g(a,b),h(a,b,c)])")
        self.assertEqual([{"L": ["g(a, b)", "h(a, b, c)"]}], list(Prolog.query("f(L)")))
        Prolog.retract("f([g(a,b),h(a,b,c)])")

    def test_prolog_functor_in_functor(self):
        Prolog.assertz("f([g([h(a,1), h(b,1)])])")
        self.assertEqual(
            [{"G": ["g(['h(a, 1)', 'h(b, 1)'])"]}], list(Prolog.query("f(G)"))
        )
        Prolog.assertz("a([b(c(x), d([y, z, w]))])")
        self.assertEqual(
            [{"B": ["b(c(x), d(['y', 'z', 'w']))"]}], list(Prolog.query("a(B)"))
        )
        Prolog.retract("f([g([h(a,1), h(b,1)])])")
        Prolog.retract("a([b(c(x), d([y, z, w]))])")

    def test_prolog_strings(self):
        """
        See: https://github.com/yuce/pyswip/issues/9
        """
        Prolog.assertz('some_string_fact("abc")')
        self.assertEqual([{"S": b"abc"}], list(Prolog.query("some_string_fact(S)")))

    def test_quoted_strings(self):
        """
        See: https://github.com/yuce/pyswip/issues/90
        """
        self.assertEqual([{"X": b"a"}], list(Prolog.query('X = "a"')))
        Prolog.assertz('test_quoted_strings("hello","world")')
        self.assertEqual(
            [{"A": b"hello", "B": b"world"}],
            list(Prolog.query("test_quoted_strings(A,B)")),
        )

    def test_prolog_read_file(self):
        """
        See: https://github.com/yuce/pyswip/issues/10
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, "test_read.pl")
        Prolog.consult("test_read.pl", relative_to=__file__)
        list(Prolog.query(f'read_file("{path}", S)'))

    def test_retract(self):
        Prolog.dynamic("person/1")
        Prolog.asserta("person(jane)")
        result = list(Prolog.query("person(X)"))
        self.assertEqual([{"X": "jane"}], result)
        Prolog.retract("person(jane)")
        result = list(Prolog.query("person(X)"))
        self.assertEqual([], result)

    def test_placeholder_2(self):
        joe = Atom("joe")
        ids = [1, 2, 3]
        Prolog.assertz("user(%p,%p)", joe, ids)
        result = list(Prolog.query("user(%p, IDs)", joe))
        self.assertEqual([{'IDs': [1, 2, 3]}], result)


format_prolog_fixture = [
    ("", (), ""),
    ("no-args", (), "no-args"),
    ("before%pafter", ("text",), 'before"text"after'),
    ("before%pafter", (123,), "before123after"),
    ("before%pafter", (123.45,), "before123.45after"),
    ("before%pafter", (Atom("foo"),), "before'foo'after"),
    ("before%pafter", (Variable(name="Foo"),), "beforeFooafter"),
    (
        "before%pafter",
        (["foo", 38, 45.897, [1, 2, 3]],),
        'before["foo",38,45.897,[1,2,3]]after',
    ),
]


@pytest.mark.parametrize("fixture", format_prolog_fixture)
def test_convert_to_prolog(fixture):
    format, args, target = fixture
    assert format_prolog(format, args) == target
