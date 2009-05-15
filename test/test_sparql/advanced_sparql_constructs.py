import unittest
from rdflib import plugin
from rdflib.namespace import Namespace,RDF,RDFS
from rdflib.term import URIRef
from rdflib.store import Store
from cStringIO import StringIO
from rdflib.graph import Graph,ReadOnlyGraphAggregate,ConjunctiveGraph
import sys
from pprint import pprint

testGraph1N3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
:foo :relatedTo [ a rdfs:Class ];
     :parentOf ( [ a rdfs:Class ] ).
:bar :relatedTo [ a rdfs:Resource ];
     :parentOf ( [ a rdfs:Resource ] ).
     
( [ a rdfs:Resource ] ) :childOf :bar.     
( [ a rdfs:Class ] )    :childOf :foo.
"""

sparqlQ1 = \
"""
BASE <http://test/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?node WHERE { ?node :relatedTo [ a rdfs:Class ] }"""


sparqlQ2 = \
"""
BASE <http://test/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?node WHERE { ?node :parentOf ( [ a rdfs:Class ] ) }"""


sparqlQ3 = \
"""
BASE <http://test/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?node WHERE { ( [ a rdfs:Resource ] ) :childOf ?node }"""

sparqlQ4 = \
"""
PREFIX owl:  <http://www.w3.org/2002/07/owl#> 

SELECT DISTINCT ?class 
FROM <http://www.w3.org/2002/07/owl#>
WHERE { ?thing a ?class }"""

class AdvancedTests(unittest.TestCase):
    def setUp(self):
        memStore = plugin.get('IOMemory',Store)()
        self.testGraph = Graph(memStore)
        self.testGraph.parse(StringIO(testGraph1N3),format='n3')
        
    def testNamedGraph(self):
        from sets import Set
        OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
        rt =  self.testGraph.query(sparqlQ4)
        self.assertEquals(Set(rt.serialize('python')),Set([OWL_NS.OntologyProperty,OWL_NS.Class,OWL_NS.Ontology,OWL_NS.AnnotationProperty,RDF.Property,RDFS.Class]))

    def testScopedBNodes(self):
        rt =  self.testGraph.query(sparqlQ1)
        self.assertEquals(rt.serialize('python')[0],URIRef("http://test/foo"))

    def testCollectionContentWithinAndWithout(self):
        rt =  self.testGraph.query(sparqlQ3)
        self.assertEquals(rt.serialize('python')[0],URIRef("http://test/bar"))

    def testCollectionAsObject(self):
        rt =  self.testGraph.query(sparqlQ2)
        self.assertEquals(rt.serialize('python')[0],URIRef("http://test/foo"))
        self.assertEquals(1,len(rt))

if __name__ == '__main__':
    suite = unittest.makeSuite(AdvancedTests)
    unittest.TextTestRunner(verbosity=3).run(suite)
