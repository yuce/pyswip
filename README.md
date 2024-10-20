<a href="https://pypi.python.org/pypi/pyswip"><img src="https://img.shields.io/pypi/v/pyswip.svg?maxAge=2592&updated=2"></a>
<img src="https://img.shields.io/github/actions/workflow/status/yuce/pyswip/tests.yaml">
<a href="https://coveralls.io/github/yuce/pyswip"><img src="https://coveralls.io/repos/github/yuce/pyswip/badge.svg?branch=master"></a>
<a href="https://pyswip.readthedocs.io/en/latest/"><img src="https://readthedocs.org/projects/pyswip/badge/?version=latest"></a>


# PySwip

<div align="center">
    <img src="https://pyswip.org/images/pyswip_logo_sm_256colors.gif" alt="PySwip logo">
</div>

## What's New?

See the [Change Log](https://pyswip.org/change-log.html).

## Install

If you have SWI-Prolog installed, it's just:
```
pip install pyswip
```

See [Get Started](https://pyswip.readthedocs.io/en/latest/get_started.html) for detailed instructions.

## Introduction

PySwip is a Python-Prolog interface that enables querying [SWI-Prolog](https://www.swi-prolog.org) in your Python programs.
It features an SWI-Prolog foreign language interface, a utility class that makes it easy querying with Prolog and also a Pythonic interface.

Since PySwip uses SWI-Prolog as a shared library and ctypes to access it, it doesn't require compilation to be installed.

PySwip was brought to you by the PySwip community.
Thanks to all [contributors](CONTRIBUTORS.txt).

## Examples

### Using Prolog

```python
from pyswip import Prolog
Prolog.assertz("father(michael,john)")
Prolog.assertz("father(michael,gina)")
list(Prolog.query("father(michael,X)")) == [{'X': 'john'}, {'X': 'gina'}]
for soln in Prolog.query("father(X,Y)"):
    print(soln["X"], "is the father of", soln["Y"])
# michael is the father of john
# michael is the father of gina
```

An existing knowledge base stored in a Prolog file can also be consulted, and queried.
Assuming the filename "knowledge_base.pl" and the Python is being run in the same working directory, it is consulted like so:

```python
from pyswip import Prolog
Prolog.consult("knowledge_base.pl")
```

### Foreign Functions

```python
from pyswip import Prolog, registerForeign

def hello(t):
    print("Hello,", t)
hello.arity = 1

registerForeign(hello)

Prolog.assertz("father(michael,john)")
Prolog.assertz("father(michael,gina)")
print(list(Prolog.query("father(michael,X), hello(X)")))
```

### Pythonic interface (Experimental)

```python
from pyswip import Functor, Variable, Query, call

assertz = Functor("assertz", 1)
father = Functor("father", 2)
call(assertz(father("michael","john")))
call(assertz(father("michael","gina")))
X = Variable()

q = Query(father("michael",X))
while q.nextSolution():
    print("Hello,", X.value)
q.closeQuery()

# Outputs:
#    Hello, john
#    Hello, gina
```

The core functionality of `Prolog.query` is based on Nathan Denny's public domain prolog.py.

## Help!

* [Support Forum](https://groups.google.com/forum/#!forum/pyswip)
* [Stack Overflow](https://stackoverflow.com/search?q=pyswip)

## PySwip Community Home

PySwip was used in scientific articles, dissertations, and student projects over the years.
Head out to [PySwip Community](https://pyswip.org/community.html) for more information and community links.

**Do you have a project, video or publication that uses/mentions PySwip?**
**[file an issue](https://github.com/yuce/pyswip/issues/new?title=Powered%20by%20PySwip) or send a pull request.**

If you would like to reference PySwip in a LaTeX document, you can use the provided [BibTeX file](https://pyswip.org/pyswip.bibtex).
You can also use the following information to refer to PySwip:
* Author: Yüce Tekol and PySwip contributors
* Title: PySwip VERSION
* URL: https://pyswip.org

## License

PySwip is licensed under the [MIT license](LICENSE).
