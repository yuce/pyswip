import unittest

from pyswip.examples.coins import solve, prolog_source

class CoinsTestCase(unittest.TestCase):

    def test_solve(self):
        fixture = [{1: 3, 5: 0, 10: 30, 50: 0, 100: 0}]
        soln = solve(coin_count=33, total_cents=303, max_solutions=1)
        self.assertEqual(fixture, soln)

    def test_prolog_source(self):
        source = prolog_source()
        self.assertIn("label(Solution)", source)
