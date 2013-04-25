from rdflib import URIRef, Graph, Namespace
import rdflib.plugins.sparql.paths  # this monkey-patches URIRef/Graph


FOAF = Namespace("http://xmlns.com/foaf/0.1/")

g = Graph()
g.load("foaf.rdf")

tim = URIRef("http://www.w3.org/People/Berners-Lee/card#i")

print "Timbl knows:"

for o in g.objects(tim, FOAF.knows / FOAF.name):
    print o
