"""
Test for empty xml:base values

xml:base='' should resolve to the given publicID per XML Base specification
and RDF/XML dependence on it
"""

from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef
from rdflib.namespace import RDF, FOAF
from io import StringIO

import unittest


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


baseUri = URIRef("http://example.com/")
baseUri2 = URIRef("http://example.com/foo/bar")


class TestEmptyBase(unittest.TestCase):
    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data), publicID=baseUri, format="xml")

    def test_base_ref(self):
        self.assertTrue(
            len(list(self.graph)), "There should be at least one statement in the graph"
        )
        self.assertTrue(
            (baseUri, RDF.type, FOAF.Document) in self.graph,
            "There should be a triple with %s as the subject" % baseUri,
        )


class TestRelativeBase(unittest.TestCase):
    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data2), publicID=baseUri2, format="xml")

    def test_base_ref(self):
        self.assertTrue(
            len(self.graph), "There should be at least one statement in the graph"
        )
        resolvedBase = URIRef("http://example.com/baz")
        self.assertTrue(
            (resolvedBase, RDF.type, FOAF.Document) in self.graph,
            "There should be a triple with %s as the subject" % resolvedBase,
        )


if __name__ == "__main__":
    unittest.main()
