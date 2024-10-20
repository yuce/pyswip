# -*- coding: utf-8 -*-

# pyswip -- Python SWI-Prolog bridge
# Copyright (c) 2007-2024 Yüce Tekol
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

import sys
from typing import List, Union, Literal
from io import StringIO

from pyswip.prolog import Prolog


__all__ = "Matrix", "solve", "prolog_source"

_DIMENSION = 9
_SOURCE_PATH = "sudoku.pl"


Prolog.consult(_SOURCE_PATH, relative_to=__file__)


class Matrix:
    def __init__(self, matrix: List[List[int]]) -> None:
        if not matrix:
            raise ValueError("matrix must be given")
        if len(matrix) != _DIMENSION:
            raise ValueError("Matrix dimension must be 9")
        self._dimension = len(matrix)
        self._validate(self._dimension, matrix)
        self.matrix = matrix

    @classmethod
    def from_text(cls, text: str) -> "Matrix":
        lines = text.strip().split("\n")
        dimension = len(lines)
        rows = []
        for i, line in enumerate(lines):
            cols = line.split()
            if len(cols) != dimension:
                raise ValueError(
                    f"All rows must have {dimension} columns, line {i+1} has {len(cols)}"
                )
            rows.append([0 if x == "." else int(x) for x in cols])
        return cls(rows)

    @classmethod
    def _validate(cls, dimension: int, matrix: List[List[int]]):
        if len(matrix) != dimension:
            raise ValueError(f"Matrix must have {dimension} rows, it has {len(matrix)}")
        for i, row in enumerate(matrix):
            if len(row) != dimension:
                raise ValueError(
                    f"All rows must have {dimension} columns, row {i+1} has {len(row)}"
                )

    def __len__(self) -> int:
        return self._dimension

    def __str__(self) -> str:
        sio = StringIO()
        self.pretty_print(file=sio)
        return sio.getvalue()

    def __repr__(self) -> str:
        return str(self.matrix)

    def pretty_print(self, *, file=sys.stdout) -> None:
        for row in self.matrix:
            row = " ".join(str(x or ".") for x in row)
            print(row, file=file)


def solve(matrix: Matrix) -> Union[Matrix, Literal[False]]:
    """
    Solves the given Sudoku puzzle

    Parameters:
        matrix (Matrix): The matrix that contains the Sudoku puzzle

    Returns:
        Matrix: Solution matrix
        False: If no solutions was found
    """
    p = repr(matrix).replace("0", "_")
    result = list(Prolog.query(f"L={p},sudoku(L)", maxresult=1))
    if not result:
        return False
    result = result[0].get("L")
    if not result:
        return False
    return Matrix(result)


def prolog_source() -> str:
    from pathlib import Path

    path = Path(__file__).parent / _SOURCE_PATH
    with open(path) as f:
        return f.read()


def main():
    puzzle = Matrix.from_text("""
. . 5 . 7 . 2 6 8
. . 4 . . 2 . . .
. . 1 . 9 . . . .
. 8 . . . . 1 . .
. 2 . 9 . . . 7 .
. . 6 . . . . 3 .
. . 2 . 4 . 7 . .
. . . 5 . . 9 . .
9 5 7 . 3 . . . .    
    """)
    print("\n-- PUZZLE --")
    puzzle.pretty_print()
    print("\n-- SOLUTION --")
    solution = solve(puzzle)
    if solution:
        solution.pretty_print()
    else:
        print("This puzzle has no solutions. Is it valid?")


if __name__ == "__main__":
    main()
