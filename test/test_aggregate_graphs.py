import unittest
from rdflib.namespace import Namespace, RDF, RDFS
from rdflib import plugin
from rdflib.term import URIRef
from rdflib.store import Store
from cStringIO import StringIO
from rdflib.graph import Graph
from rdflib.graph import ReadOnlyGraphAggregate
from rdflib.graph import ConjunctiveGraph

testGraph1N3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
:foo a rdfs:Class.
:bar :d :c.
:a :d :c.
"""


testGraph2N3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
@prefix log: <http://www.w3.org/2000/10/swap/log#>.
:foo a rdfs:Resource.
:bar rdfs:isDefinedBy [ a log:Formula ].
:a :d :e.
"""

testGraph3N3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix log: <http://www.w3.org/2000/10/swap/log#>.
@prefix : <http://test/> .
<> a log:N3Document.
"""

sparqlQ = \
"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
FROM NAMED <http://example.com/graph1>
FROM NAMED <http://example.com/graph2>
FROM NAMED <http://example.com/graph3>
FROM <http://www.w3.org/2000/01/rdf-schema#>

WHERE {?sub ?pred rdfs:Class }"""

sparqlQ2 =\
"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?class
WHERE { GRAPH ?graph { ?member a ?class } }"""

sparqlQ3 =\
"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX log: <http://www.w3.org/2000/10/swap/log#>
SELECT ?n3Doc
WHERE {?n3Doc a log:N3Document }"""

class GraphAggregates1(unittest.TestCase):
    def setUp(self):
        memStore = plugin.get('IOMemory',Store)()
        self.graph1 = Graph(memStore)
        self.graph2 = Graph(memStore)
        self.graph3 = Graph(memStore)

        for n3Str,graph in [(testGraph1N3,self.graph1),
                            (testGraph2N3,self.graph2),
                            (testGraph3N3,self.graph3)]:
            graph.parse(StringIO(n3Str),format='n3')
    
        self.G = ReadOnlyGraphAggregate([self.graph1,self.graph2,self.graph3])

    def testAggregateRaw(self):
        #Test triples
        assert len(list(self.G.triples((None,RDF.type,None))))                  == 4
        assert len(list(self.G.triples((URIRef("http://test/bar"),None,None)))) == 2
        assert len(list(self.G.triples((None,URIRef("http://test/d"),None))))   == 3
    
        #Test __len__
        assert len(self.G) == 8
        
        #assert context iteration
        for g in self.G.contexts():
            assert isinstance(g,Graph)
    
        #Test __contains__
        assert (URIRef("http://test/foo"),RDF.type,RDFS.Resource) in self.G
    
        barPredicates = [URIRef("http://test/d"),RDFS.isDefinedBy]
        assert len(list(self.G.triples_choices((URIRef("http://test/bar"),barPredicates,None)))) == 2
    
class GraphAggregates2(unittest.TestCase):

    known_issue = True
    sparql = True

    def setUp(self):
        memStore = plugin.get('IOMemory',Store)()
        self.graph1 = Graph(memStore,URIRef("http://example.com/graph1"))
        self.graph2 = Graph(memStore,URIRef("http://example.com/graph2"))
        self.graph3 = Graph(memStore,URIRef("http://example.com/graph3"))
    
        for n3Str,graph in [(testGraph1N3,self.graph1),
                            (testGraph2N3,self.graph2),
                            (testGraph3N3,self.graph3)]:
            graph.parse(StringIO(n3Str),format='n3')
    
        self.graph4 = Graph(memStore,RDFS)
        self.graph4.parse(RDFS.uri)
        self.G = ConjunctiveGraph(memStore)

if __name__ == '__main__':
    unittest.main()
