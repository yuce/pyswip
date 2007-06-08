# -*- coding: utf-8 -*-

#   S E N D
#   M O R E
# + -------
# M O N E Y
#
# So, what should be the values of S, E, N, D, M, O, R, Y
# if they are all distinct digits.

from pyswip.prolog import Prolog

letters = "S E N D M O R Y".split()
prolog = Prolog()
prolog.consult("money.pl")
for result in prolog.query("sendmore(X)"):
    r = result["X"]
    for i, letter in enumerate(letters):
        print letter, "=", r[i]

print "That's all..."
