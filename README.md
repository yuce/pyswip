PySWIP README
=============

:Version: 
    0.2.3

:Maintainer:
    Rodrigo Starr <rodrigo.starr@gmail.com>

:Author:
    Yuce Tekol <yucetekol@gmail.com>
    Rodrigo Starr <rodrigo.starr@gmail.com>

:Project Website:
   http://code.google.com/p/pyswip
    

Introduction
------------

PySWIP is a Python - SWI-Prolog bridge enabling to query SWI-Prolog in your
Python programs. It features an (incomplete) SWI-Prolog foreign language
interface, a utility class that makes it easy querying with Prolog and also a
Pythonic interface.

Since PySWIP uses SWI-Prolog as a shared library and ctypes to access it, it
doesn't require compilation to be installed.

Note that this version of PySWIP is slightly incompatible with 0.1.x versions.

Requirements:
-------------

* Python 2.3 and higher.
* ctypes 1.0 and higher.
* SWI-Prolog 5.6.x and higher (most probably other versions will also work).
* libpl as a shared library.
* Works on Linux and Win32, should work for all POSIX.

Example (Using Prolog):
-----------------------

    >>> from pyswip import Prolog
    >>> prolog = Prolog()
    >>> prolog.assertz("father(michael,john)")
    >>> prolog.assertz("father(michael,gina)")
    >>> list(prolog.query("father(michael,X)"))
    [{'X': 'john'}, {'X': 'gina'}]
    >>> for soln in prolog.query("father(X,Y)"):
    ...     print soln["X"], "is the father of", soln["Y"]
    ...
    michael is the father of john
    michael is the father of gina

Since version 0.1.3 of PySWIP, it is possible to register a Python function as a
Prolog predicate through SWI-Prolog's foreign language interface.

Example (Foreign Functions):
----------------------------
    
    from pyswip import Prolog, registerForeign

    def hello(t):
        print "Hello,", t
    hello.arity = 1

    registerForeign(hello)

    prolog = Prolog()
    prolog.assertz("father(michael,john)")
    prolog.assertz("father(michael,gina)")    
    list(prolog.query("father(michael,X), hello(X)"))

Outputs:
    Hello, john
    Hello, gina

Since version 0.2, PySWIP contains a 'Pythonic' interface which allows writing
predicates in pure Python (*Note that interface is experimental.*)

Example (Pythonic interface):
-----------------------------

    from pyswip import Functor, Variable, Query

    assertz = Functor("assertz", 2)
    father = Functor("father", 2)

    call(assertz(father("michael","john")))
    call(assertz(father("michael","gina")))

    X = Variable()
    q = Query(father("michael",X))
    while q.nextSolution():
        print "Hello,", X.value
    q.closeQuery()

Outputs:
    Hello, john
    Hello, gina

The core functionality of ``Prolog.query`` is based on Nathan Denny's public
domain prolog.py found at
http://www.ahsc.arizona.edu/~schcats/projects/docs/prolog-0.2.0.html

Install
-------

Please see ``INSTALL`` for detailed instructions.

