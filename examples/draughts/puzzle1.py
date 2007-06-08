# -*- coding: utf-8 -*-

# This example is adapted from http://eclipse.crosscoreop.com/examples/puzzle1.pl.txt

# "Twelve draught pieces are arranged in a square frame with four on
# each side.  Try placing them so there are 5 on each side.  (Kordemsky)
#
# "Maybe this problem is not described very well but I wanted to stick
# with the original text from Kordemsky.  The problem may be stated in
# terms of guards on the wall of a square fort.  If a guard stands on a
# side wall then he may only watch that particular wall whereas a guard
# at a corner may watch two walls.  If twelve guards are positioned such
# that there are two on each side wall and one at each corner then there
# are four guards watching each wall.  How can they be rearranged such
# that there are five watching each wall?"

from pyswip.prolog import Prolog

def main():
    prolog = Prolog()
    prolog.consult("puzzle1.pl")
    for soln in prolog.query("solve(B)."):
        #B = eval(soln["B"])
        B = soln["B"]
        # [NW,N,NE,W,E,SW,S,SE]
        print "%d %d %d" % tuple(B[:3])
        print "%d   %d"   % tuple(B[3:5])
        print "%d %d %d" % tuple(B[5:])
        
        cont = raw_input("Press 'n' to finish: ")
        if cont.lower() == "n": break
        
if __name__ == "__main__":
    main()
