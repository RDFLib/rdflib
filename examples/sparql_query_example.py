from rdflib import Literal, ConjunctiveGraph, Namespace, BNode

import rdflib

# Note that this example uses SPARQL and assumes you have rdfextras installed
# after installation, no other steps are nescessary, the SPARQL implementation
# should be found automatically. 

DC = Namespace(u"http://purl.org/dc/elements/1.1/")
FOAF = Namespace(u"http://xmlns.com/foaf/0.1/")

graph = ConjunctiveGraph()
s = BNode()
graph.add((s, FOAF['givenName'], Literal('Alice')))
b = BNode()
graph.add((b, FOAF['givenName'], Literal('Bob')))
graph.add((b, DC['date'], Literal("2005-04-04T04:04:04Z")))

q="""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dc:  <http://purl.org/dc/elements/1.1/>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?name
WHERE { ?x foaf:givenName  ?name .
        OPTIONAL { ?x dc:date ?date } .
        FILTER ( bound(?date) ) 
      }
"""

for x in graph.query(q):
    print x
