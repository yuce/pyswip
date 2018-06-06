<a href="https://travis-ci.org/yuce/pyswip"><img src="https://api.travis-ci.org/yuce/pyswip.svg?branch=master"></a>
<a href="https://coveralls.io/github/yuce/pyswip"><img src="https://coveralls.io/repos/github/yuce/pyswip/badge.svg?branch=master"></a>

# PySWIP

## What's New?

See the [CHANGELOG](CHANGELOG.md).

**This library is being cleaned up and refactored. Expect API breakage and incompatibility with previous versions.**

Thanks to all [contributors](CONTRIBUTORS.txt). If you have contributed to PySWIP in the past and your name does not appear on that list, please [let me know](mailto:yucetekol@gmail.com) so I can add your name.

## Introduction

PySWIP is a Python - SWI-Prolog bridge enabling to query [SWI-Prolog](http://www.swi-prolog.org) in your Python programs.
It features an (incomplete) SWI-Prolog foreign language interface, a utility class that makes it easy querying with Prolog and also a
Pythonic interface.

Since PySWIP uses SWI-Prolog as a shared library and ctypes to access it, it doesn't require compilation to be installed.

## Requirements:

* Python 2.7 or 3.4 and higher.
    * PyPy is currently not supported.
* SWI-Prolog 7.6.x and higher.
* `libswipl` as a shared library. *This is the default on most platforms.*
* Works on Linux, Windows and MacOS. Should work on other POSIX.

## Install

See [INSTALL](INSTALL.md) for instructions.

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
from __future__ import print_function
from pyswip import Prolog, registerForeign

def hello(t):
    print("Hello,", t)    
hello.arity = 1

registerForeign(hello)

prolog = Prolog()
prolog.assertz("father(michael,john)")
prolog.assertz("father(michael,gina)")    
print(list(prolog.query("father(michael,X), hello(X)")))
```

### Pythonic interface (Experimental)

```python
from __future__ import print_function
from pyswip import Functor, Variable, Query

assertz = Functor("assertz", 2)
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

## Contact

* `yucetekol@gmail.com`
* https://twitter.com/tklx


## Projects/Publications that Use or Reference PySWIP

**Do you have a project, video or publication that uses/mentions PySWIP? [Please let me know](mailto:yucetekol@gmail.com) or send a pull request.**

### Books

* [Beginning Artificial Intelligence with the Raspberry Pi](https://www.apress.com/gp/book/9781484227428)

### Publications

* [Assessment of Graph Databases as a Viable Materiel Solution for the Army's Dynamic Force Structure (DFS) Portal Implementation: Part 3, Risks, Mitigation Approach, and Roadmap](https://www.researchgate.net/publication/321977892_Assessment_of_Graph_Databases_as_a_Viable_Materiel_Solution_for_the_Army's_Dynamic_Force_Structure_DFS_Portal_Implementation_Part_3_Risks_Mitigation_Approach_and_Roadmap_Assessment_of_Graph_Databases_)
* [Tackling Complexity in High Performance Computing Applications](https://link.springer.com/article/10.1007/s10766-016-0422-9)
* [Social Human-Robot Interaction: A New Cognitive and Affective Interaction-Oriented Architecture](https://www.springer.com/gp/book/9783319474366)
* [A Planning Module for a ROS-Based Ubiquitous Robot Control System](https://dspace.library.uu.nl/bitstream/handle/1874/292669/2014-03-27%20MSc%20Thesis%20Pieterjan%20van%20Gastel.pdf) (PDF)
* [A pilot framework developed as a common platform integrating diverse elements of computer aided fixture design](https://www.tandfonline.com/doi/full/10.1080/00207543.2013.832000)
* [Integration von Prolog und ClioPatria in Python](http://www1.pub.informatik.uni-wuerzburg.de/pub/theses/2017-bodenlos-master.pdf) (PDF, German)
* [SELECTSCRIPT: A Query Language for Robotic World Models and Simulations](https://ieeexplore.ieee.org/document/7140077/)
* [A Concept for Declarative Information Acquisition in Smart Environments](https://d-nb.info/1122172583/34)
* [Implementation on ADHD Diagnostic Expert System based on DSM Diagnostic Criteria](http://jse.or.kr/AJMAHS/papers/v7n11/50.pdf) (PDF, Korean)
* [Wie sehen Krebsmolekule aus? Vergleich der Gute der Klassifizierung potenziell krebserregender Molekule durch induktiv logische und merkmalsbasierte Lernverfahren](http://www.cogsys.wiai.uni-bamberg.de/teaching/ss17/pj_bama/ProjektberichtRelLearningFinzelGrabeHillebrandHornigRicci.pdf) (PDF, German)
* [Companion Robots Behaving with Style: Towards Plasticity in Social Human-Robot Interaction](https://tel.archives-ouvertes.fr/tel-01679314/document) (PDF)

### Videos

* [AI - blocks world solver interactive planner](https://www.youtube.com/watch?v=p1m8htUEHrc)
* [PySwip, Prolog, JAVA SCRIPT and HTML](https://www.youtube.com/watch?v=Oj8xsW2vaLA) (Spanish)
* [GET OUT OF THE MAZE WITH PROLOG AND PYTHON](https://www.youtube.com/watch?v=MW3S0Jfa0LU) (Spanish)

### Projects

* [noworkflow](https://github.com/gems-uff/noworkflow) Supporting infrastructure to run scientific experiments without a scientific workflow management system. http://gems-uff.github.io/noworkflow
* [Super Pacman](https://github.com/kajornsakp/prologProject)
* [Pokemon Weak Detector](https://github.com/ReiiYuki/PokemonWeakDetector)
* [Food Recommendations in Hyderabad, India](https://github.com/cindyleowtt/prolog_food) Food Recommendation AI Expert System using a GUI hosted on Flask and a backend developed with PYSWIP and native Prolog
* [pyswip_envctrl](https://github.com/2rs2ts/pyswip_envctrl) An environment control module expert system written in PySWIP.
* [tic-tac-toe](https://github.com/ivpusic/tic-tac-toe) Tic-tac-toe game with AI in Prolog and GUI in Python (kivy framework + pyswip)
* [TBM1 - "Getting to Know My Home"](http://thewiki.rockinrobotchallenge.eu/index.php?title=TBM1_-_“Getting_to_Know_My_Home”)
* [A script that enables use of a Prolog natural language parsing component to control a Scribbler II robot over bluetooth](http://justinmangue.com/blog/scribpro-py/)
* [Cosmos](https://github.com/mcsoto/cosmos) A new logic programming language.
* [lib-annotated-attack-trees](https://github.com/yramirezc/lib-annotated-attack-trees) Scripts and resources for creating a library of annotated attack trees and using it to refine an annotated attack tree.
* [ClIDE](https://github.com/skeledrew/clide) Command-line Intelligent Development Environment
* [Artificial Intelligence INF1771 @ PUC-Rio](https://github.com/leotok/INF1771) Projects for the Artificial Intelligence class @ PUC-Rio
* [AutomobileAdvisor](https://github.com/liscju/AutomobileAdvisor) Projekt na systemy ekspertowe pomagający wybrać odpowiedni samochód dla danego klienta na podstawie preferencji (Polish)

### Blog Posts

* [Calling Prolog from Python](http://fernmac.blogspot.com.tr/2013/07/calling-prolog-from-python.html)
* [Python v. Prolog: Round 1: Fight!](http://www.kuliniewicz.org/blog/archives/2007/10/21/python-v-prolog-round-1-fight/)

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