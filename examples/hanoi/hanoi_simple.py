# -*- coding: utf-8 -*-

from pyswip.prolog import Prolog
from pyswip.easy import getList, registerForeign

N = 3  # Number of disks

def main():
    def notify(t):
        print "move disk from %s pole to %s pole." % tuple(getList(t))
        return True
    notify.arity = 1
        
    prolog = Prolog()
    registerForeign(notify)
    prolog.consult("hanoi.pl")
    list(prolog.query("hanoi(%d)" % N))
    
if __name__ == "__main__":
    main()
