# pyswip -- Python SWI-Prolog bridge
# Copyright (c) 2007-2018 Yüce Tekol
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
from typing import List, Dict

# 100 coins must sum to $5.00

from pyswip.prolog import Prolog


__all__ = ("solve",)

_PROLOG_FILE = "coins.pl"

Prolog.consult(_PROLOG_FILE, relative_to=__file__)


def solve(
    *, coin_count: int = 100, total_cents: int = 500, max_solutions: int = 1
) -> List[Dict[int, int]]:
    """
    Solves the coins problem.

    Finds and returns combinations of ``coin_count`` coins that makes ``total``cents.

    :param coin_count: Number of coins
    :param total_cents: Total cent value of coins
    """
    cents = [1, 5, 10, 50, 100]
    query = Prolog.query(
        "coins(%s, %s, Solution)", coin_count, total_cents, maxresult=max_solutions
    )
    return [
        {cent: count for cent, count in zip(cents, soln["Solution"])} for soln in query
    ]


def prolog_source() -> str:
    """
    Returns the Prolog source file that solves the coins problem.
    """
    from pathlib import Path

    path = Path(__file__).parent / _PROLOG_FILE
    with open(path) as f:
        return f.read()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--count", type=int, default=100)
    parser.add_argument("-t", "--total", type=int, default=500)
    parser.add_argument("-s", "--solutions", type=int, default=1)
    args = parser.parse_args()
    print(f"{args.count} coins must sum to ${args.total/100}:\n")
    solns = solve(
        coin_count=args.count, total_cents=args.total, max_solutions=args.solutions
    )
    for i, soln in enumerate(solns, start=1):
        text = " + ".join(
            f"{count}x{cent} cent(s)" for cent, count in soln.items() if count
        )
        print(f"{i}. {text}")


if __name__ == "__main__":
    main()
