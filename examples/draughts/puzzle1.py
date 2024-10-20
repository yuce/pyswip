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
    Prolog.consult("puzzle1.pl", relative_to=__file__)

    for soln in Prolog.query("solve(B)."):
        B = soln["B"]

        # [NW,N,NE,W,E,SW,S,SE]
        print("%d %d %d" % tuple(B[:3]))
        print("%d   %d" % tuple(B[3:5]))
        print("%d %d %d" % tuple(B[5:]))

        cont = input("Press 'n' to finish: ")
        if cont.lower() == "n":
            break


if __name__ == "__main__":
    main()
