import unittest
from io import StringIO

from pyswip.examples.hanoi import solve, prolog_source
from .utils import load_fixture


class HanoiTestCase(unittest.TestCase):

    def test_solve(self):
        fixture = load_fixture("hanoi_fixture.txt")
        sio = StringIO()
        solve(3, file=sio)
        self.assertEqual(fixture, sio.getvalue())

    def test_solve_simple(self):
        fixture = load_fixture("hanoi_simple_fixture.txt")
        sio = StringIO()
        solve(3, simple=True, file=sio)
        self.assertEqual(fixture, sio.getvalue())

    def test_prolog_source(self):
        source = prolog_source()
        self.assertIn("move(N, A, B, C)", source)
