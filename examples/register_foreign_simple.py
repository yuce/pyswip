# -*- coding: utf-8 -*-

# Demonstrates registering a Python function as a Prolog predicate through SWI-Prolog's FFI.

from pyswip.prolog import Prolog
from pyswip.easy import registerForeign, getAtomChars

def hello(t):
    print "Hello,", t
hello.arity = 1

def main():
    registerForeign(hello)
    prolog = Prolog()
    prolog.assertz("father(michael,john)")
    prolog.assertz("father(michael,gina)")    
    list(prolog.query("father(michael,X), hello(X)"))

if __name__ =="__main__":
    main()
