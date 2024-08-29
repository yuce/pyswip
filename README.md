<a href="https://pypi.python.org/pypi/pyswip"><img src="https://img.shields.io/pypi/v/pyswip.svg?maxAge=2592&updated=2"></a>
<img src="https://img.shields.io/github/actions/workflow/status/yuce/pyswip/tests.yaml">
<a href="https://coveralls.io/github/yuce/pyswip"><img src="https://coveralls.io/repos/github/yuce/pyswip/badge.svg?branch=master"></a>

# PySwip

---

## Installing the Latest Version

The latest SWI-Prolog supported by Ubuntu 22.04 are 9.0.4.
We generally want to support LTS releases of Ubuntu.
You can use the following to install PySwip from the master branch:

```
pip install git+https://github.com/yuce/pyswip@master#egg=pyswip
```

## The End of Python 2 Support

Python 2 has reached end of life on January 1st, 2020 as documented [here](https://www.python.org/doc/sunset-python-2/).
So, PySwip 0.2.10 is the last version which officially supports Python 2.

---

## What's New?

See the [CHANGELOG](CHANGELOG.md).

---

**WARNING! PySwip has no Windows installers!
If you are a Windows user, see [INSTALL](https://github.com/yuce/pyswip/blob/master/INSTALL.md#windows).
There are some "free download" sites that claim to be hosting PySwip installers.
DO NOT TRUST THEM!**

---

Thanks to all [contributors](CONTRIBUTORS.txt).

## Introduction

PySwip is a Python - SWI-Prolog bridge enabling to query [SWI-Prolog](http://www.swi-prolog.org) in your Python programs.
It features an (incomplete) SWI-Prolog foreign language interface, a utility class that makes it easy querying with Prolog and also a Pythonic interface.

Since PySwip uses SWI-Prolog as a shared library and ctypes to access it, it doesn't require compilation to be installed.

## Requirements:

* Python 3.8 and higher.
  * PyPy is currently not supported.
* SWI-Prolog 9.0.4 and higher.
* `libswipl` as a shared library. *This is the default on most platforms.*
* Works on Linux, Windows, MacOS and FreeBSD. Should work on other POSIX.

## Install

**IMPORTANT: Make sure the SWI-Prolog architecture is the same as the Python architecture.
If you are using a 64bit build of Python, use a 64bit build of SWI-Prolog, etc.**

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

## Projects/Publications that Use or Reference PySwip

**Do you have a project, video or publication that uses/mentions PySwip? [file an issue](https://github.com/yuce/pyswip/issues/new?title=Powered%20by%20PySwip) or send a pull request.**

If you would like to reference PySwip in a LaTeX document, you can use the provided [BibTeX file](pyswip.bibtex).

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
* [A Concept for Declarative Information Acquisition in Smart Environments](https://d-nb.info/1122172583/34) (PDF)
* [Implementation on ADHD Diagnostic Expert System based on DSM Diagnostic Criteria](http://jse.or.kr/AJMAHS/papers/v7n11/50.pdf) (PDF, Korean)
* [Wie sehen Krebsmolekule aus? Vergleich der Gute der Klassifizierung potenziell krebserregender Molekule durch induktiv logische und merkmalsbasierte Lernverfahren](http://www.cogsys.wiai.uni-bamberg.de/teaching/ss17/pj_bama/ProjektberichtRelLearningFinzelGrabeHillebrandHornigRicci.pdf) (PDF, German)
* [Companion Robots Behaving with Style: Towards Plasticity in Social Human-Robot Interaction](https://tel.archives-ouvertes.fr/tel-01679314/document) (PDF)
* [Semi-automatically Augmenting Attack Trees using an Annotated Attack Tree Library](https://www.researchgate.net/publication/327985985_Semi-automatically_Augmenting_Attack_Trees_Using_an_Annotated_Attack_Tree_Library)
* [A Learning Framework for Tool Creation by a Robot](http://www.araa.asn.au/acra/acra2015/papers/pap145.pdf) (PDF)
* [Conceptual Maps as the First Step in an Ontology Construction Method](https://ieeexplore.ieee.org/abstract/document/5629027)
* [Fact-Based Expert System for Supplier Selection with ERP Data](https://link.springer.com/chapter/10.1007/978-981-15-1041-0_3)
* [Interactive Text Graph Mining with a Prolog-based Dialog Engine](https://link.springer.com/chapter/10.1007/978-3-030-39197-3_1)
* [The Detection Of Conflicts In The Requirements Specification Based On An Ontological Model And A Production Rule System](https://www.researchgate.net/publication/337655252_The_detection_of_conflicts_in_the_requirements_specification_based_on_an_ontological_model_and_a_production_rule_system)
* [Dependency-based Text Graphs for Keyphrase and Summary Extraction with Applications to Interactive Content Retrieval](https://arxiv.org/pdf/1909.09742.pdf) (PDF)
* [Information Retrieval Based on Knowledge-Enhanced Word Embedding Through Dialog: A Case Study](https://www.atlantis-press.com/journals/ijcis/125936225/view)
* [Exploring the world of declarative programming](https://fedoramagazine.org/exploring-the-world-of-declarative-programming/)
* [Development of a Prototype of a Medical Application Using a Type-2 Fuzzy Inference System](https://www.researchgate.net/publication/377771997_Development_of_a_Prototype_of_a_Medical_Application_Using_a_Type-2_Fuzzy_Inference_System)
* [Learning Where and When to Reason in Neuro-Symbolic Inference](https://openreview.net/pdf?id=en9V5F8PR) (PDF)
* [MMDect: Metamorphic Malware Detection Using Logic Programming](http://platon.etsii.urjc.es/~jarias/tfg/23-Luciana.pdf) (PDF)
* [Continuous QoS-compliant orchestration in the Cloud-Edge continuum](https://onlinelibrary.wiley.com/doi/10.1002/spe.3334) ([Code](https://github.com/di-unipi-socc/FogArm))

### Videos

* [AI - Blocks world solver interactive planner](https://www.youtube.com/watch?v=p1m8htUEHrc)
* [PySwip, Prolog, Javascript and HTML](https://www.youtube.com/watch?v=Oj8xsW2vaLA) (Spanish)
* [Get out of the maze with Prolog and Python](https://www.youtube.com/watch?v=MW3S0Jfa0LU) (Spanish)
* [Les robots deviennent (vraiment) intelligents ! (NAO discute avec Kylo Ren)](https://www.youtube.com/watch?v=JlfnpyIly-Y)
* [Connect Python and Prolog | Using Pyswip Module | Using Prolog as Backend](https://www.youtube.com/watch?v=1jwAHIz8WXc)
* [How to connect Prolog and Python Using Pyswip Module](https://www.youtube.com/watch?v=R_dpVolI7bg)
* [Praktikum Sistem Pakar 01 - Pengenalan Prolog, SWI-Prolog, PySwip](https://www.youtube.com/watch?v=wY5C48NMDp4) (Indonesian)
* [Curso Básico de Prolog: 4 - Interconectando Python con Prolog a través de PySwip](https://www.youtube.com/watch?v=5xDqp_lYlcM) (Spanish)

### Projects

* [noworkflow](https://github.com/gems-uff/noworkflow) Supporting infrastructure to run scientific experiments without a scientific workflow management system. http://gems-uff.github.io/noworkflow
* [Super Pacman](https://github.com/kajornsakp/prologProject)
* [Pokemon Weak Detector](https://github.com/ReiiYuki/PokemonWeakDetector)
* [Food Recommendations in Hyderabad, India](https://github.com/cindyleowtt/prolog_food) Food Recommendation AI Expert System using a GUI hosted on Flask and a backend developed with PYSWIP and native Prolog.
* [pyswip_envctrl](https://github.com/2rs2ts/pyswip_envctrl) An environment control module expert system written in PySwip.
* [tic-tac-toe](https://github.com/ivpusic/tic-tac-toe) Tic-tac-toe game with AI in Prolog and GUI in Python (kivy framework + pyswip).
* [TBM1 - "Getting to Know My Home"](http://thewiki.rockinrobotchallenge.eu/index.php?title=TBM1_-_“Getting_to_Know_My_Home”)
* [Prolog natural language parsing component to control a Scribbler II robot over bluetooth](http://justinmangue.com/blog/scribpro-py/)
* [Cosmos](https://github.com/mcsoto/cosmos) A new logic programming language.
* [lib-annotated-attack-trees](https://github.com/yramirezc/lib-annotated-attack-trees) Scripts and resources for creating a library of annotated attack trees and using it to refine an annotated attack tree.
* [ClIDE](https://github.com/skeledrew/clide) Command-line Intelligent Development Environment
* [Artificial Intelligence INF1771 @ PUC-Rio](https://github.com/leotok/INF1771) Projects for the Artificial Intelligence class @ PUC-Rio
* [AutomobileAdvisor](https://github.com/liscju/AutomobileAdvisor) Projekt na systemy ekspertowe pomagający wybrać odpowiedni samochód dla danego klienta na podstawie preferencji (Polish)
* [Prolog Tetris AI](https://sourceforge.net/projects/prologtetrisai/)
* [Jupyter SWI Prolog](https://github.com/targodan/jupyter-swi-prolog) A Jupyter Kernel for SWI-Prolog.
* [Blocks World Planner](https://github.com/davideiacobs/BlocksWorldPlanner) A program that allows users to solve the blocks world problem interacting only using the natural language.
* [DeepTalk](https://github.com/ptarau/DeepTalk) A Python+Prolog based Dialog Engine using the Python package text_graph_crafts that extracts the highest ranked sentences answering a query.
* [DeepRank](https://github.com/ptarau/DeepRank) The system uses dependency links for building Text Graphs, that with help of a centrality algorithm like PageRank, extract relevant keyphrases, summaries and relations from text documents.
* [Prolog Tic-tac-toe](https://github.com/guyzyl/prolog-tic-tac-toe) A full-stack tic-tac-toe game with AI in Prolog, backend in Python3 (+Flask) and frontend in Vue.js 3.
* [MIDSI Project](https://github.com/devdaniellima/midsi) Solution for data discovery in projects applicable to the
  Semantic Web, enabling the loading of ontologies and inference of results using the WSML language.
* [Popper](https://github.com/logic-and-learning-lab/Popper) An inductive logic programming system.
* [Trabajo Final](https://github.com/NicolasLeidi/Trabajo-Final) Ingeniería para Sistemas de Información - Nicolás Leidi

### Blog Posts

* [Calling Prolog from Python](http://fernmac.blogspot.com.tr/2013/07/calling-prolog-from-python.html)
* [Python v. Prolog: Round 1: Fight!](http://www.kuliniewicz.org/blog/archives/2007/10/21/python-v-prolog-round-1-fight/)
* [Path Follower: Arduino+Rasp on ROS](http://blog.giacomocerquone.com/path-follower-maze-solving-car-arduino/) and its [Project code](https://github.com/giacomocerquone/robotics-MazeSolver)
* [10 minutes to make a GUI for your SWI-Prolog App via Python](http://pbrown.me/blog/quick_gui/)
* [Playing with Prolog – Prolog’s Role in the LLM Era, Part 3](https://eugeneasahara.com/2024/08/12/playing-with-prolog-prologs-role-in-the-llm-era-part-3/)
* [Prolog - Gateway to Logic Programming](https://sut-ai.github.io/supplementary/notebooks/logic_programming/)

## Companies using PySwip

* [Magazino GmbH](https://www.magazino.eu/?lang=en) Magazino develops and builds intelligent, mobile robots for intralogistics.

## License

```
Copyright (c) 2007-2024 Yüce Tekol and PySwip contributors

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
