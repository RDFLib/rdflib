"""
Test for empty xml:base values

xml:base='' should resolve to the given publicID per XML Base specification 
and RDF/XML dependence on it
"""

from rdflib import ConjunctiveGraph, Literal, URIRef, Namespace, RDF
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

baseUri = URIRef('http://example.com/')

class TestEmptyBase(unittest.TestCase):
    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data),publicID=baseUri)

    def test_base_ref(self):        
        self.failUnless(len(self.graph) == 1,"There should be at least one statement in the graph")
        self.failUnless((baseUri,RDF.type,FOAF.Document) in self.graph,"There should be a triple with %s as the subject" % baseUri)

if __name__ == "__main__":
    unittest.main()

