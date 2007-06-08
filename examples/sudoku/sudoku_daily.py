# -*- coding: utf-8 -*-

# Sudoku auto-solver. Get today's sudoku at http://www.sudoku.org.uk/daily.asp
# and solve it

import urllib
from HTMLParser import HTMLParser, HTMLParseError
from pyswip.prolog import Prolog
from pyswip.easy import *

URL = "http://www.sudoku.org.uk/daily.asp"

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
    print "".join(["/---", "----"*8, "\\"])
    for row in table:
        print "".join(["|", "|".join(" %s " % (i or " ") for i in row), "|"])
    print "".join(["\\---", "----"*8, "/"])        

def get_daily_sudoku(url):
    puzzle = DailySudokuPuzzle()
    f = urllib.urlopen(url)
    try:
        puzzle.feed(f.read())
    except HTMLParseError:
        pass
    puzzle = puzzle.puzzle
    return [puzzle[i*9:i*9+9] for i in range(9)]

def solve(problem):
    prolog.consult("sudoku.pl")
    p = str(problem).replace("0", "_")
    result = list(prolog.query("Puzzle=%s,sudoku(Puzzle)" % p, catcherrors=False))
    if result:
        result = result[0]
        return result["Puzzle"]
    else:
        return False    
    
if __name__ == "__main__":
    prolog = Prolog()  # having this in `solve` bites! because of __del__
    
    print "Getting puzzle from:", URL
    
    puzzle = get_daily_sudoku(URL)
    print "-- PUZZLE --"
    pretty_print(puzzle)
    
    print
    print " -- SOLUTION --"
    solution = solve(puzzle)
    if solution:
        pretty_print(solution)
    else:
        print "This puzzle has no solutions [is it valid?]"

