
# PySWIP setup script

import sys
import os
import os.path
from distutils.core import setup

setup(name="pyswip",
		version="0.2.1",
		url="http://code.google.com/p/pyswip/",
		download_url="http://code.google.com/p/pyswip/downloads/list",
		author="Yuce Tekol",
		author_email="yucetekol@gmail.com",
		description="PySWIP enables querying SWI-Prolog in your Python programs.",
        long_description="""
PySWIP 0.2.1
==========

PySWIP is a GPL'd Python - SWI-Prolog bridge enabling to query SWI-Prolog in your Python programs. It features an (incomplete) SWI-Prolog foreign language interface, a utility class that makes it easy querying with Prolog and also a Pythonic interface.


Since PySWIP uses SWI-Prolog as a shared library and ctypes to access it, it doesn't require compilation to be installed.

Note that this version of PySWIP is slightly incompatible with prior versions.

Requirements:
-------------

* Python 2.3 and higher.
* ctypes 1.0 and higher.
* SWI-Prolog 5.6.x and higher (most probably other versions will also work).
* libpl as a shared library.
* Works on Linux and Win32, should work for all POSIX.

News
----

* Prolog.query returns real Python datatypes.
* New Pythonic interface (See the last example).
* Several new examples, including Markus Triska's *Sudoku Solver*.
* Prolog module support.
* Foreign functions retrieve Python datatypes.

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

Since version 0.1.3 of PySWIP, it is possible to register a Python function as a Prolog predicate through SWI-Prolog's foreign language interface.

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

Since version 0.2, PySWIP contains a 'Pythonic' interface which allows writing predicates in pure Python.

Example (Pythonic interface):
-----------------------------

    from pyswip import Prolog, Functor, Variable, Query

    assertz = Functor("assertz", 2)
    father = Functor("father", 2)

    call(assertz(father("michael","john")))
    call(assertz(father("michael","gina")))

    X = Variable()
    q = Query(father("michael",X))
    while q.nextSolution():
        print "Hello,", X.value

Outputs:
    Hello, john
    Hello, gina
""",
		license="GPL",
		packages=["pyswip"],
		classifiers=[
			'Development Status :: 3 - Alpha',
			'Intended Audience :: Developers',
			'Intended Audience :: Science/Research',
			'License :: OSI Approved :: GNU General Public License (GPL)',
			'Operating System :: OS Independent',
			'Programming Language :: Python',
			'Topic :: Scientific/Engineering :: Artificial Intelligence',
			'Topic :: Software Development :: Libraries :: Python Modules'
			],
		)

