"""
Test for empty xml:base values

xml:base='' should resolve to the given publicID per XML Base specification
and RDF/XML dependence on it
"""

from rdflib.graph import ConjunctiveGraph
from rdflib.namespace import FOAF, RDF
from rdflib.term import URIRef

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


class TestEmptyBase:
    def test_empty_base_ref(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(data=test_data, publicID=baseUri, format="xml")
        assert (
            len(list(self.graph)) > 0
        ), "There should be at least one statement in the graph"
        assert (
            baseUri,
            RDF.type,
            FOAF.Document,
        ) in self.graph, f"There should be a triple with {baseUri} as the subject"


class TestRelativeBase:
    def test_relative_base_ref(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(data=test_data2, publicID=baseUri2, format="xml")
        assert (
            len(self.graph) > 0
        ), "There should be at least one statement in the graph"
        resolvedBase = URIRef("http://example.com/baz")
        assert (
            resolvedBase,
            RDF.type,
            FOAF.Document,
        ) in self.graph, f"There should be a triple with {resolvedBase} as the subject"
