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

"""
Sudoku example

You can run this module using::

    $ python3 -m pyswip.examples.sudoku
"""

from typing import List, Union, Literal, Optional, IO
from io import StringIO

from pyswip.prolog import Prolog

__all__ = "Matrix", "prolog_source", "sample_puzzle", "solve"

_DIMENSION = 9
_PROLOG_FILE = "sudoku.pl"


Prolog.consult(_PROLOG_FILE, relative_to=__file__)


class Matrix:
    """Represents a 9x9 Sudoku puzzle"""

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
        """
        Create a Matrix from the given string

        The following are valid characters in the string:

        * `.`: Blank column
        * `1-9`: Numbers

        The text must contain exactly 9 rows and 9 columns.
        Each row ends with a newline character.
        You can use blank lines and spaces/tabs between columns.

        :param text: The text to use for creating the Matrix

        >>> puzzle = Matrix.from_text('''
        ... . . 5 . 7 . 2 6 8
        ... . . 4 . . 2 . . .
        ... . . 1 . 9 . . . .
        ... . 8 . . . . 1 . .
        ... . 2 . 9 . . . 7 .
        ... . . 6 . . . . 3 .
        ... . . 2 . 4 . 7 . .
        ... . . . 5 . . 9 . .
        ... 9 5 7 . 3 . . . .
        ... ''')
        """
        lines = [row for line in text.strip().split("\n") if (row := line.strip())]
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

    def pretty_print(self, *, file: Optional[IO] = None) -> None:
        """
        Prints the matrix as a grid

        :param file: The file to use for printing

        >>> import sys
        >>> puzzle = sample_puzzle()
        >>> puzzle.pretty_print(file=sys.stdout)
        . . 5 . 7 . 2 6 8
        . . 4 . . 2 . . .
        . . 1 . 9 . . . .
        . 8 . . . . 1 . .
        . 2 . 9 . . . 7 .
        . . 6 . . . . 3 .
        . . 2 . 4 . 7 . .
        . . . 5 . . 9 . .
        9 5 7 . 3 . . . .
        """
        for row in self.matrix:
            row = " ".join(str(x or ".") for x in row)
            print(row, file=file)


def solve(matrix: Matrix) -> Union[Matrix, Literal[False]]:
    """
    Solves the given Sudoku puzzle

    :param matrix: The matrix that contains the Sudoku puzzle

    >>> puzzle = sample_puzzle()
    >>> print(puzzle)
    . . 5 . 7 . 2 6 8
    . . 4 . . 2 . . .
    . . 1 . 9 . . . .
    . 8 . . . . 1 . .
    . 2 . 9 . . . 7 .
    . . 6 . . . . 3 .
    . . 2 . 4 . 7 . .
    . . . 5 . . 9 . .
    9 5 7 . 3 . . . .
    <BLANKLINE>
    >>> print(solve(puzzle))
    3 9 5 4 7 1 2 6 8
    8 7 4 6 5 2 3 9 1
    2 6 1 3 9 8 5 4 7
    5 8 9 7 6 3 1 2 4
    1 2 3 9 8 4 6 7 5
    7 4 6 2 1 5 8 3 9
    6 1 2 8 4 9 7 5 3
    4 3 8 5 2 7 9 1 6
    9 5 7 1 3 6 4 8 2
    <BLANKLINE>
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
    """Returns the Prolog source file that solves Sudoku puzzles."""
    from pathlib import Path

    path = Path(__file__).parent / _PROLOG_FILE
    with open(path) as f:
        return f.read()


def sample_puzzle() -> Matrix:
    """Returns the sample Sudoku puzzle"""
    matrix = Matrix.from_text("""
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
    return matrix


def main():
    puzzle = sample_puzzle()
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
