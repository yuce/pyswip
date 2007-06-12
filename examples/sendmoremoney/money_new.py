# -*- coding: utf-8 -*-

#   S E N D
#   M O R E
# + -------
# M O N E Y
#
# So, what should be the values of S, E, N, D, M, O, R, Y
# if they are all distinct digits.

from pyswip import Prolog, Functor, Variable, call

def main():
    letters = "S E N D M O R Y".split()
    prolog = Prolog()
    sendmore = Functor("sendmore")
    prolog.consult("money.pl")
    
    X = Variable()
    call(sendmore(X))
    r = X.value
    for i, letter in enumerate(letters):
        print letter, "=", r[i]
        
    print "That's all..."

if __name__ == "__main__":
    main()

