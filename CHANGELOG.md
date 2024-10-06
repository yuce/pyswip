# CHANGELOG

### 0.3.0 (Not Released)

* Improve list representations, unicode support and multiple threading usage, see: [97](https://github.com/yuce/pyswip/pull/97). Contributed by Guglielmo Gemignani.
* Added PL_STRINGS_MARK to getAtomChars, fixes [102](https://github.com/yuce/pyswip/issues/102). Contributed by Vince Jankovics.
* Backwards compatibility for Python 2 64bit, see: [104](https://github.com/yuce/pyswip/pull/104). Contributed by Tobias Grubenmann.
* Improved handling of lists, nested lists, strings, and atoms. see: [112](https://github.com/yuce/pyswip/pull/112). Contributed by Tobias Grubenmann.
* Fixes for changed constants, see: [125](https://github.com/yuce/pyswip/pull/125). Contributed by Arvid Norlander.
* Refactored SWI-Prolog discovery [commit](https://github.com/yuce/pyswip/commit/d399f0d049ff17200b1b7e1cd878faf3e48502dc)
* Dictionary support, see: [commit](https://github.com/yuce/pyswip/commit/59016e0841f56177d1b18ec08fd9b67792bd0a97). Contributed by Max Peltzer.
* Check `PILLIBSWIPL` environment variable for the `libswipl` library path [145](https://github.com/yuce/pyswip/pull/145). Contributed by Jan Wielemaker.
* Avoid AttributeError with PL_version_info in swipl <= 8.4.2 [154](https://github.com/yuce/pyswip/pull/154). Contributed by Jan DestyNova.
* Added hardcoded path for `libswipl.so` [43](https://github.com/yuce/pyswip/pull/43). Contributed by Kumar Abhinav.
* Fixed not finding swipl lib file when there are multiple options [153](https://github.com/yuce/pyswip/pull/153). Contributed by AdiHarif.

### 0.2.10

* Synchronized type constants with SWI-Prolog.h
  update for broken compatibility changes in SWI-Prolog.h up to 0.8.3.
* Fix incorrect REP_* constants.  
* Fixed issue [#92](https://github.com/yuce/pyswip/issues/92) (C assert)
* Fixed issue [#90](https://github.com/yuce/pyswip/issues/90) (quoted string)
* Fixed Variables in foreign functions not unifiable. Contributed by Michael Kasch.
* Added support multibyte strings and atoms. Contributed by Nikolai Merinov.
* Updated core.py and easy.py for unifying strings properly. Contributed by rohanshekhar.
* Fixed issue [#71](https://github.com/yuce/pyswip/issues/71). Contributed by prologrules.
* Fixed compatibility with SWI-Prolog 8.2.0. Contributed by Stuart Reynolds.
* Fixed compatibility with MacOS. Contributed by prologrules and Dylan Lukes.

### 0.2.9

* Added non deterministic foreign function support. Contributed by rmanhaeve.
* Fixed issue [#67](https://github.com/yuce/pyswip/pull/67). Contributed by Galileo Sartor.

### 0.2.8

* Fixed issue [#35](https://github.com/yuce/pyswip/issues/35). Contributed by Robert Simione.

### 0.2.7

* Works on FreeBSD.

### 0.2.6

* Fixed issue [#9](https://github.com/yuce/pyswip/issues/9).
* Fixed issue [#10](https://github.com/yuce/pyswip/issues/10).

### 0.2.5

* Project cleanup
* Updated the examples for Python 3.

### 0.2.4

* Maintenance release of PySwip
* Added an error to avoid opening nested queries using PySwip (SWI-Prolog does
  not allow that). The error is NestedQueryError.
* Added Tomasz Gryszkiewicz's patch for better finding the SWI-Prolog lib in 
  Darwin
* Solved issue 4 "Patch for a dynamic method"
* Solved issue 5 "Patch: hash and eq methods for Atom class"
* Solved issue 3: "Problem with variables in lists"
* Solved issue 17: "Can't find SWI-Prolog library in Homebrew's /usr/local"

### 0.2.3

* Maintenance release of PySwip
* Solved issue "Segmentation fault when assertz-ing" (thanks to jpthompson23)
* Solved issue "pyswip doesn't work on cygwin" 
* Solved issue "Callbacks can cause segv's" (thanks to jpthompson23)
* Solved issue "Improve library loading" 
* Solved issue "sys.exit does not work when importing pyswip" 

### 0.2.2

* PySwip won't rely on the (id of the) functor handle of `=/2`.
* Sebastian Höhn's patch to enable PySwip to work on MAC OS-X is incorporated.

### 0.2.1

* Importing `pyswip` automatically initializes SWI-Prolog.
* Fixed a bug with querying lists with the new interface.

### 0.2.0

* All names are included with `from pyswip import ...`
* New *Pythonic* interface
* Prolog.query returns real Python datatypes
* Markus Triska's Sudoku Solver
* Prolog module support
* Foreign functions retrieve Python datatypes.

### 0.1.3

* Renamed `pyswip/util.py` to `pyswip/prolog.py`.
* New module `pyswip.easy`.
* Now it is possible to register a Python function as a Prolog predicate
  through SWI-Prolog's Foreign Function Interface.
* Additions to the core library.
* Added example, *register foreign* which shows how to register a Python
  function as an SWI-Prolog predicate.
* Added example, *Towers of Hanoi*

### 0.1.2

* Renamed `PrologRunner` to `Prolog`.
* Removed `query` method of `Prolog`, `queryGenerator` is renamed as `query`.
* Added `asserta`, `assertz` and `consult` methods to `Prolog`.
* The necessary cleanup is done even if the `query` generator doesn't run to the end.
* Errors during the execution of `query` is caught and `PrologError` is raised.
* Many new additions to the core library.
* Added `examples` directory.
* Added examples, *coins* and *draughts*.
  
### 0.1.1

* Added `queryGenerator` to PrologRunner, `query` calls `queryGenerator`.
* Added example `send more money`.
