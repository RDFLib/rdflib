"""
Test for empty xml:base values

xml:base='' should resolve to the given publicID per XML Base specification 
and RDF/XML dependence on it
"""

from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef
from rdflib.namespace import Namespace
from rdflib.namespace import RDF
from StringIO import StringIO
import unittest

FOAF = Namespace('http://xmlns.com/foaf/0.1/')

test_data = """
<rdf:RDF 
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xml:base="">
    <rdf:Description rdf:about="">
      <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Document"/>
    </rdf:Description>
</rdf:RDF>"""

test_data2 = """
<rdf:RDF 
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xml:base="../">
    <rdf:Description rdf:about="baz">
      <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Document"/>
    </rdf:Description>
</rdf:RDF>"""


baseUri  = URIRef('http://example.com/')
baseUri2 = URIRef('http://example.com/foo/bar')

class TestEmptyBase(unittest.TestCase):
    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data),publicID=baseUri)

    def test_base_ref(self):        
        self.failUnless(len(self.graph) == 1,"There should be at least one statement in the graph")
        self.failUnless((baseUri,RDF.type,FOAF.Document) in self.graph,"There should be a triple with %s as the subject" % baseUri)

class TestRelativeBase(unittest.TestCase):
    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data2),publicID=baseUri2)

    def test_base_ref(self):        
        self.failUnless(len(self.graph) == 1,"There should be at least one statement in the graph")
        resolvedBase = URIRef('http://example.com/baz')
        self.failUnless((resolvedBase,RDF.type,FOAF.Document) in self.graph,"There should be a triple with %s as the subject" % resolvedBase)

if __name__ == "__main__":
    unittest.main()

