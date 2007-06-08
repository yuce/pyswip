# -*- coding: utf-8 -*-

from pyswip import __VERSION__ as pyswip_VERSION
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
    print "".join(["/---", "----"*8, "\\"])
    for row in table:
        print "".join(["|", "|".join(" %s " % i for i in row), "|"])
    print "".join(["\\---", "----"*8, "/"])
    
def solve(problem):
    prolog.consult("sudoku.pl")
    p = str(puzzle2).replace("0", "_")
    result = list(prolog.query("L=%s,sudoku(L)" % p, catcherrors=False))
    if result:
        result = result[0]
        if pyswip_VERSION < "0.1.4":
            result = eval(result)
        return result["L"]
    else:
        return False
    
def main():
    s = solve(puzzle1)
    #if s:
    #    pretty_print(s)
    #else:
    #   print "This puzzle has no solutions [is it valid?]"

if __name__ == "__main__":
    prolog = Prolog()
    main()
