from pyswip.core import *
from pyswip.easy import *
from pyswip.prolog import *

import math

def print_solution(x):
    print("--------------------------")
    if type(x) == list:
        for x in soln["X"]:
            print(x)
    else:
        print(x)
    print("--------------------------")

def predecessors(x, l):
    if isinstance(x, int) and isinstance(l, Variable) and x > 0:
        l.unify(list(range(x)))
        return True
    elif isinstance(x, Variable) and isinstance(l, list):
        for i in range(len(l)):
            if l[i] != i:
                return False
        x.unify(i+1)
        return True
    else:
        return False

predecessors.arity = 2

def tareksFather(tarek, father):
    father_name = "hocine"
    tarek_name = "tarek"
    if isinstance(tarek, Variable) and isinstance(father, Variable):
        tarek.unify(tarek_name)
        father.unify(father_name)
        return True
    if isinstance(tarek, Variable) and isinstance(father, str) and father == "hocine":
        tarek.unify(tarek_name)
        return True
    elif isinstance(tarek, str) and isinstance(father, Variable) and tarek == "tarek":
        father.unify(father_name)
        return True
    elif isinstance(tarek, str) and isinstance(father, str):
        return tarek == tarek_name and father == father_name
    else:
        return False

tareksFather.arity = 2

def isTrue(t):
    if isinstance(t, Variable):
        t.unify(True)
        return True
    return t == True

isTrue.arity = 1

def isPi(x):
    if isinstance(x, float):
        return x == math.pi
    if isinstance(x, Variable):
        x.unify(math.pi)
        return True
    return False

isPi.arity = 1

prolog = Prolog()

registerForeign(predecessors)
registerForeign(tareksFather)
registerForeign(isTrue)
registerForeign(isPi)


for soln in prolog.query("predecessors(3, X)"):
    print_solution(soln["X"])

for soln in prolog.query("tareksFather(X, Y)"):
    print_solution(soln["X"])
    print_solution(soln["Y"])

for soln in prolog.query("isTrue(X)"):
    print_solution(soln["X"])


for soln in prolog.query("isPi(X)"):
    print_solution(soln["X"])

