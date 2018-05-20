# PySWIP README

## What's New?

See the [CHANGELOG](CHANGELOG.md).

**This library is being refactored. Expect API breakage and incompatibility with previous versions.**

Thanks to all [contributors](CONTRIBUTORS.txt). If you have contributed to PySWIP in the past and your name does not appear on that list, please let [me](mailto:yucetekol@gmail.com) know so I can add your name.

## Introduction

PySWIP is a Python - SWI-Prolog bridge enabling to query [SWI-Prolog](http://www.swi-prolog.org) in your Python programs.
It features an (incomplete) SWI-Prolog foreign language interface, a utility class that makes it easy querying with Prolog and also a
Pythonic interface.

Since PySWIP uses SWI-Prolog as a shared library and ctypes to access it, it
doesn't require compilation to be installed.

## Requirements:

* Python 3.4 and higher.
    * PyPy is currently not supported.
* SWI-Prolog 7.6.x and higher (most probably other versions will also work).
* libpl as a shared library.
* Works on Linux and Win32, should work for all POSIX.

## Examples

### Using Prolog

```python
from pyswip import Prolog
prolog = Prolog()
prolog.assertz("father(michael,john)")
prolog.assertz("father(michael,gina)")
list(prolog.query("father(michael,X)")) == [{'X': 'john'}, {'X': 'gina'}]
for soln in prolog.query("father(X,Y)"):
    print(soln["X"], "is the father of", soln["Y"])
# michael is the father of john
# michael is the father of gina
```

An existing knowledge base stored in a Prolog file can also be consulted,
and queried. Assuming the filename "knowledge_base.pl" and the Python is 
being run in the same working directory, it is consulted like so:

    >>> from pyswip import Prolog
    >>> prolog = Prolog()
    >>> prolog.consult("knowledge_base.pl")

### Foreign Functions

```python
from pyswip import Prolog, registerForeign
def hello(t):
    print("Hello,", t)
hello.arity = 1
registerForeign(hello)
prolog = Prolog()
prolog.assertz("father(michael,john)")
prolog.assertz("father(michael,gina)")    
list(prolog.query("father(michael,X), hello(X)"))
```

### Pythonic interface (Experimental)

```python
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
# Outputs:
#    Hello, john
#    Hello, gina

```

The core functionality of ``Prolog.query`` is based on Nathan Denny's public domain prolog.py found at
http://www.ahsc.arizona.edu/~schcats/projects/docs/prolog-0.2.0.html

## Install

Please see ``INSTALL`` for detailed instructions.

## License

```
Copyright (c) 2007-2018 Yüce Tekol

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```