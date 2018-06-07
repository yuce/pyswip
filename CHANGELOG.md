# CHANGELOG

+ 0.2.7

  * Works on FreeBSD.

+ 0.2.6

  * Fixed issue [#9](https://github.com/yuce/pyswip/issues/9).
  * Fixed issue [#10](https://github.com/yuce/pyswip/issues/10).


+ 0.2.5

  * Project cleanup
  * Updated the examples for Python 3.

+ 0.2.4

  * Maintenance release of PySwip
  * Added an error to avoid opening nested queries using PySwip (SWI-Prolog does
    not allow that). The error is NestedQueryError.
  * Added Tomasz Gryszkiewicz's patch for better finding the SWI-Prolog lib in 
    Darwin
  * Solved issue 4 "Patch for a dynamic method"
  * Solved issue 5 "Patch: hash and eq methods for Atom class"
  * Solved issue 3: "Problem with variables in lists"
  * Solved issue 17: "Can't find SWI-Prolog library in Homebrew's /usr/local"

+ 0.2.3

  * Maintenance release of PySwip
  * Solved issue "Segmentation fault when assertz-ing" (thanks to jpthompson23)
  * Solved issue "pyswip doesn't work on cygwin" 
  * Solved issue "Callbacks can cause segv's" (thanks to jpthompson23)
  * Solved issue "Improve library loading" 
  * Solved issue "sys.exit does not work when importing pyswip" 

+ 0.2.2

  * PySwip won't rely on the (id of the) functor handle of `=/2`.
  * Sebastian Höhn's patch to enable PySwip to work on MAC OS-X is incorporated.

+ 0.2.1

  * Importing `pyswip` automatically initializes SWI-Prolog.
  * Fixed a bug with querying lists with the new interface.

+ 0.2.0

  * All names are included with `from pyswip import ...`
  * New *Pythonic* interface
  * Prolog.query returns real Python datatypes
  * Markus Triska's Sudoku Solver
  * Prolog module support
  * Foreign functions retrieve Python datatypes.

+ 0.1.3

  * Renamed `pyswip/util.py` to `pyswip/prolog.py`.
  * New module `pyswip.easy`.
  * Now it is possible to register a Python function as a Prolog predicate
    through SWI-Prolog's Foreign Function Interface.
  * Additions to the core library.
  * Added example, *register foreign* which shows how to register a Python
    function as an SWI-Prolog predicate.
  * Added example, *Towers of Hanoi*

+ 0.1.2

  * Renamed `PrologRunner` to `Prolog`.
  * Removed `query` method of `Prolog`, `queryGenerator` is renamed as `query`.
  * Added `asserta`, `assertz` and `consult` methods to `Prolog`.
  * The necessary cleanup is done even if the `query` generator doesn't run to the end.
  * Errors during the execution of `query` is caught and `PrologError` is raised.
  * Many new additions to the core library.
  * Added `examples` directory.
  * Added examples, *coins* and *draughts*.
  
+ 0.1.1

  * Added `queryGenerator` to PrologRunner, `query` calls `queryGenerator`.
  * Added example `send more money`.

