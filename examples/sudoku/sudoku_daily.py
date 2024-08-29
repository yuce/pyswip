# -*- coding: utf-8 -*-

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


# Sudoku auto-solver. Get today's sudoku at http://www.sudoku.org.uk/daily.asp
# and solve it

from __future__ import print_function
from pyswip.prolog import Prolog
from pyswip.easy import *

from html.parser import HTMLParser

import urllib.request as urllib_request


class DailySudokuPuzzle(HTMLParser):
    def __init__(self):
        self.puzzle = []
        self.__in_td = False
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == "td":
            for attr in attrs:
                if attr[0] == "class" and attr[1] == "InnerTDone":
                    self.__in_td = True
                    break
        elif tag == "input":
            if self.__in_td:
                self.puzzle.append(0)

    def handle_endtag(self, tag):
        if tag == "td":
            self.__in_td = False

    def handle_data(self, data):
        if self.__in_td:
            self.puzzle.append(int(data))


def pretty_print(table):
    print("".join(["/---", "----" * 8, "\\"]))
    for row in table:
        print("".join(["|", "|".join(" %s " % (i or " ") for i in row), "|"]))
    print("".join(["\\---", "----" * 8, "/"]))


def get_daily_sudoku(url):
    puzzle = DailySudokuPuzzle()
    f = urllib_request.urlopen(url)
    puzzle.feed(f.read().decode("latin-1"))
    puzzle = puzzle.puzzle
    return [puzzle[i * 9 : i * 9 + 9] for i in range(9)]


def solve(problem):
    prolog.consult("sudoku.pl")
    p = str(problem).replace("0", "_")
    result = list(prolog.query("Puzzle=%s,sudoku(Puzzle)" % p, maxresult=1))
    if result:
        result = result[0]
        return result["Puzzle"]
    else:
        return False


if __name__ == "__main__":
    URL = "http://www.sudoku.org.uk/daily.asp"

    prolog = Prolog()  # having this in `solve` bites! because of __del__
    print("Getting puzzle from:", URL)
    puzzle = get_daily_sudoku(URL)
    print("-- PUZZLE --")
    pretty_print(puzzle)
    print()
    print(" -- SOLUTION --")
    solution = solve(puzzle)
    if solution:
        pretty_print(solution)
    else:
        print("This puzzle has no solutions [is it valid?]")
