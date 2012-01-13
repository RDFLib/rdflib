from rdflib import Literal, ConjunctiveGraph, Namespace, BNode

import rdflib
from rdflib import plugin

plugin.register(
    'sparql', rdflib.query.Processor,
    'rdfextras.sparql.processor', 'Processor')
plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')

DC = Namespace(u"http://purl.org/dc/elements/1.1/")
FOAF = Namespace(u"http://xmlns.com/foaf/0.1/")

graph = ConjunctiveGraph()
s = BNode()
graph.add((s, FOAF['givenName'], Literal('Alice')))
b = BNode()
graph.add((b, FOAF['givenName'], Literal('Bob')))
graph.add((b, DC['date'], Literal("2005-04-04T04:04:04Z")))

print(graph.query("""\
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dc:  <http://purl.org/dc/elements/1.1/>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?name
WHERE { ?x foaf:givenName  ?name .
        OPTIONAL { ?x dc:date ?date } .
        FILTER ( bound(?date) ) 
      }
""").serialize('python'))
