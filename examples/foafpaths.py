"""

SPARQL 1.1 defines path operators

We overload some python operators on URIRefs to allow creating path
operators directly in python. 

p1 / p2 => Path sequence
p1 | p2 => Path alternative
p1 * '*' => chain of 0 or more p's
p1 * '+' => chain of 1 or more p's
p1 * '?' => 0 or 1 p 
~p1 => p1 is inverted order (s p1 o) <=> (o ~p1 s)
-p1 => NOT p1, i.e. any property by p1

these can then be used in property position for s,p,o triple queries
for graph objects

See the docs for rdflib.plugins.sparql.path for the details

"""

from rdflib import URIRef, Graph, Namespace


FOAF = Namespace("http://xmlns.com/foaf/0.1/")

g = Graph()
g.load("foaf.rdf")

tim = URIRef("http://www.w3.org/People/Berners-Lee/card#i")

print "Timbl knows:"

for o in g.objects(tim, FOAF.knows / FOAF.name):
    print o
