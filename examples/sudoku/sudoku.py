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

from pyswip.prolog import Prolog
from pyswip.easy import *


_ = 0
puzzle1 = [
            [_,6,_,1,_,4,_,5,_],
            [_,_,8,3,_,5,6,_,_],
            [2,_,_,_,_,_,_,_,1],
            [8,_,_,4,_,7,_,_,6],
            [_,_,6,_,_,_,3,_,_],
            [7,_,_,9,_,1,_,_,4],
            [5,_,_,_,_,_,_,_,2],
            [_,_,7,2,_,6,9,_,_],
            [_,4,_,5,_,8,_,7,_]
            ]


puzzle2 = [
            [_,_,1,_,8,_,6,_,4],
            [_,3,7,6,_,_,_,_,_],
            [5,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,5,_,_,_],
            [_,_,6,_,1,_,8,_,_],
            [_,_,_,4,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,3],
            [_,_,_,_,_,7,5,2,_],
            [8,_,2,_,9,_,7,_,_]
          ]


def pretty_print(table):
    print("".join(["/---", "----"*8, "\\"]))
    for row in table:
        print("".join(["|", "|".join(" %s " % (i or " ") for i in row), "|"]))
    print("".join(["\\---", "----"*8, "/"]))

    
def solve(problem):
    prolog.consult("sudoku.pl")
    p = str(problem).replace("0", "_")
    result = list(prolog.query("L=%s,sudoku(L)" % p, maxresult=1))
    if result:
        result = result[0]
        return result["L"]
    else:
        return False

    
def main():
    puzzle = puzzle1
    print("-- PUZZLE --")
    pretty_print(puzzle)
    print()
    print(" -- SOLUTION --")
    solution = solve(puzzle)
    if solution:
        pretty_print(solution)
    else:
        print("This puzzle has no solutions [is it valid?]")

        
if __name__ == "__main__":
    prolog = Prolog()
    main()
