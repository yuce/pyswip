# -*- coding: utf-8 -*-

# 100 coins must sum to $5.00

from pyswip import Prolog, Functor, Variable, Query

def main():
    prolog = Prolog()
    prolog.consult("coins.pl")
    count = int(raw_input("How many coins (default: 100)? ") or 100)
    total = int(raw_input("What should be the total (default: 500)? ") or 500)
    coins = Functor("coins", 3)
    S = Variable()
    q = Query(coins(S, count, total))
    i = 0
    while q.nextSolution():
        ## [1,5,10,50,100]
        s = zip(S.value, [1, 5, 10, 50, 100])
        print i,
        for c, v in s:
            print "%dx%d" % (c,v),
        print
        i += 1
    q.closeQuery()
        
if __name__ == "__main__":
    main()
