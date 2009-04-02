from rdflib.term import URIRef, BNode, Literal, Variable
from rdflib.namespace import Namespace, RDF, RDFS
from rdflib import plugin
from rdflib.parser import StringInputSource
from rdflib.graph import Graph, ReadOnlyGraphAggregate, ConjunctiveGraph
import unittest,sys
from pprint import pprint

class TestSPARQLToldBNodes(unittest.TestCase):
    def setUp(self):
        NS = u"http://example.org/"
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringInputSource("""
           @prefix    : <http://example.org/> .
           @prefix rdf: <%s> .
           @prefix rdfs: <%s> .
           [ :prop :val ].
           [ a rdfs:Class ]."""%(RDF, RDFS)), format="n3")
    def testToldBNode(self):
        for s,p,o in self.graph.triples((None,RDF.type,None)):
            pass
        query = """SELECT ?obj WHERE { %s ?prop ?obj }"""%s.n3()
        print query
        rt = self.graph.query(query)
        self.failUnless(len(rt) == 1,"BGP should only match the 'told' BNode by name (result set size: %s)"%len(rt))
        bindings = {Variable('?subj'):s}
        query = """SELECT ?obj WHERE { ?subj ?prop ?obj }"""
        rt = self.graph.query(query,initBindings=bindings)
        self.failUnless(len(rt) == 1,"BGP should only match the 'told' BNode by name (result set size: %s, BNode: %s)"%(len(rt),s.n3()))        

if __name__ == '__main__':
    unittest.main()
