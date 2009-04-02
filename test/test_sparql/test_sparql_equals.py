# -*- coding: UTF-8 -*-
from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef
from StringIO import StringIO
import unittest

class TestSparqlEquals(unittest.TestCase):

    PREFIXES = {
        'rdfs': "http://www.w3.org/2000/01/rdf-schema#"
    }

    def setUp(self):
        testContent = """
            @prefix rdfs: <%(rdfs)s> .
            <http://example.org/doc/1> rdfs:label "Document 1"@en .
            <http://example.org/doc/2> rdfs:label "Document 2"@en .
            <http://example.org/doc/3> rdfs:label "Document 3"@en .
        """ % self.PREFIXES
        self.graph = graph = ConjunctiveGraph()
        self.graph.load(StringIO(testContent), format='n3')

    def test_uri_equals(self):
        uri = URIRef("http://example.org/doc/1")
        query = ("""
            PREFIX rdfs: <%(rdfs)s>

            SELECT ?uri WHERE {
                ?uri rdfs:label ?label .
                FILTER( ?uri = <"""+uri+"""> )
            }
        """) % self.PREFIXES
        res = self.graph.query(query)
        expected = [uri]
        self.assertEqual(res.selected,expected)

if __name__ == "__main__":
    unittest.main()
