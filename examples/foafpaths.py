"""

SPARQL 1.1 defines path operators for combining/repeating predicates
in triple-patterns.

We overload some python operators on URIRefs to allow creating path
operators directly in python.

============ =========================================
Operator     Path
============ =========================================
``p1 / p2``  Path sequence
``p1 | p2``  Path alternative
``p1 * '*'`` chain of 0 or more p's
``p1 * '+'`` chain of 1 or more p's
``p1 * '?'`` 0 or 1 p
``~p1``      p1 inverted, i.e. (s p1 o) <=> (o ~p1 s)
``-p1``      NOT p1, i.e. any property but p1
============ =========================================


these can then be used in property position for ``s,p,o`` triple queries
for any graph method.

See the docs for :mod:`rdflib.paths` for the details.

This example shows how to get the name of friends with a single query.

"""

from rdflib import URIRef, Graph
from rdflib.namespace import FOAF

if __name__=='__main__':

    g = Graph()
    g.load("foaf.rdf")

    tim = URIRef("http://www.w3.org/People/Berners-Lee/card#i")

    print("Timbl knows:")

    for o in g.objects(tim, FOAF.knows / FOAF.name):
        print(o)
