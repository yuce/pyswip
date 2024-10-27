import unittest

from pyswip.examples.sudoku import Matrix, solve, prolog_source
from .utils import load_fixture


class MatrixTestCase(unittest.TestCase):
    FIXTURE = load_fixture("sudoku.txt")

    def test_matrix_from_text(self):
        got = Matrix.from_text(self.FIXTURE)
        target = [
            [0, 6, 0, 1, 0, 4, 0, 5, 0],
            [0, 0, 8, 3, 0, 5, 6, 0, 0],
            [2, 0, 0, 0, 0, 0, 0, 0, 1],
            [8, 0, 0, 4, 0, 7, 0, 0, 6],
            [0, 0, 6, 0, 0, 0, 3, 0, 0],
            [7, 0, 0, 9, 0, 1, 0, 0, 4],
            [5, 0, 0, 0, 0, 0, 0, 0, 2],
            [0, 0, 7, 2, 0, 6, 9, 0, 0],
            [0, 4, 0, 5, 0, 8, 0, 7, 0],
        ]
        self.assertListEqual(target, got.matrix)

    def test_solve_success(self):
        puzzle = Matrix.from_text(self.FIXTURE)
        solution = solve(puzzle)
        target = [
            [9, 6, 3, 1, 7, 4, 2, 5, 8],
            [1, 7, 8, 3, 2, 5, 6, 4, 9],
            [2, 5, 4, 6, 8, 9, 7, 3, 1],
            [8, 2, 1, 4, 3, 7, 5, 9, 6],
            [4, 9, 6, 8, 5, 2, 3, 1, 7],
            [7, 3, 5, 9, 6, 1, 8, 2, 4],
            [5, 8, 9, 7, 1, 3, 4, 6, 2],
            [3, 1, 7, 2, 4, 6, 9, 8, 5],
            [6, 4, 2, 5, 9, 8, 1, 7, 3],
        ]
        self.assertEqual(target, solution.matrix)

    def test_solve_failure(self):
        fixture = "8 " + self.FIXTURE[2:]
        puzzle = Matrix.from_text(fixture)
        solution = solve(puzzle)
        self.assertFalse(solution)

    def test_prolog_source(self):
        text = prolog_source()
        self.assertIn("Prolog Sudoku Solver", text)
