# -*- coding: utf-8 -*-

from pyswip import Prolog, Functor, Variable, call

_ = Variable

puzzle1 = [
            [_(),6,_(),1,_(),4,_(),5,_()],
            [_(),_(),8,3,_(),5,6,_(),_()],
            [2,_(),_(),_(),_(),_(),_(),_(),1],
            [8,_(),_(),4,_(),7,_(),_(),6],
            [_(),_(),6,_(),_(),_(),3,_(),_()],
            [7,_(),_(),9,_(),1,_(),_(),4],
            [5,_(),_(),_(),_(),_(),_(),_(),2],
            [_(),_(),7,2,_(),6,9,_(),_()],
            [_(),4,_(),5,_(),8,_(),7,_()]
            ]

puzzle2 = [
            [_(),_(),1,_(),8,_(),6,_(),4],
            [_(),3,7,6,_(),_(),_(),_(),_()],
            [5,_(),_(),_(),_(),_(),_(),_(),_()],
            [_(),_(),_(),_(),_(),5,_(),_(),_()],
            [_(),_(),6,_(),1,_(),8,_(),_()],
            [_(),_(),_(),4,_(),_(),_(),_(),_()],
            [_(),_(),_(),_(),_(),_(),_(),_(),3],
            [_(),_(),_(),_(),_(),7,5,2,_()],
            [8,_(),2,_(),9,_(),7,_(),_()]
          ]

def pretty_print(table):
    def get_col(c):
        try:
            if c.handle:
                return c.value
            else:
                return " "
        except:
            return c
        
    print "".join(["/---", "----"*8, "\\"])
    for row in table:
        print "".join(["|", "|".join(" %s " % get_col(i) for i in row), "|"])
    print "".join(["\\---", "----"*8, "/"])        
    
def solve(problem):
    prolog.consult("sudoku.pl")
    sudoku = Functor("sudoku")
    if call(sudoku(problem)):
        return problem
    else:
        return False
    
def main():
    puzzle = puzzle1
    print "-- PUZZLE --"
    pretty_print(puzzle)    
    print
    print " -- SOLUTION --"
    solution = solve(puzzle)
    if solution:
        pretty_print(solution)
    else:
        print "This puzzle has no solutions [is it valid?]"

if __name__ == "__main__":
    prolog = Prolog()
    main()
