
from pyswip import *

p = Prolog()

assertz = Functor("assertz")
parent = Functor("parent", 2)
test1 = newModule("test1")
test2 = newModule("test2")

call(assertz(parent("john", "bob")), module=test1)
call(assertz(parent("jane", "bob")), module=test1)

call(assertz(parent("mike", "bob")), module=test2)
call(assertz(parent("gina", "bob")), module=test2)

print "knowledgebase test1"

X = Variable()
q = Query(parent(X, "bob"), module=test1)
while q.nextSolution():
    print X.value
q.closeQuery()

print "knowledgebase test2"

q = Query(parent(X, "bob"), module=test2)
while q.nextSolution():
    print X.value
q.closeQuery()

