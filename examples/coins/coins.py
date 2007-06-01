# -*- coding: utf-8 -*-

# 100 coins must sum to $5.00

from pyswip.prolog import Prolog

def main():
    prolog = Prolog()
    prolog.consult("coins.pl")
    #count = int(raw_input("How many coins (default: 100)? ") or 100)
    #total = int(raw_input("What should be the total (default: 500)? ") or 500)
    #for i, soln in enumerate(prolog.query("coins(S, %d, %d)." % (count,total))):
    #    # [1,5,10,50,100]
    #    S = zip(eval(soln["S"]), [1, 5, 10, 50, 100])
    #    print i,
    #    for c, v in S:
    #        print "%dx%d" % (c,v),
    #    print
    count = 100
    total = 500
    list(prolog.query("coins(S, %d, %d)." % (count,total)))
        
if __name__ == "__main__":
    main()
