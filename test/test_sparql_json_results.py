from rdflib import ConjunctiveGraph
from StringIO import StringIO
import unittest


test_data = """
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://example.org/alice> a foaf:Person;
    foaf:name "Alice";
    foaf:knows <http://example.org/bob> .

<http://example.org/bob> a foaf:Person;
    foaf:name "Bob" .
"""


PROLOGUE = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
"""


opt_query = PROLOGUE+"""
SELECT ?name ?x ?friend
WHERE { ?x foaf:name ?name .
        OPTIONAL { ?x foaf:knows ?friend . }
}
"""

opt_correct = """"name" : {"type": "literal", "xml:lang" : "None", "value" : "Bob"}
                   ,
                   "x" : {"type": "uri", "value" : "http://example.org/bob"}
                }"""


wild_query = PROLOGUE+"""
SELECT * WHERE { ?x foaf:name ?name . }
"""

wild_correct = """"name" : {"type": "literal", "xml:lang" : "None", "value" : "Bob"}
                   ,
                   "x" : {"type": "uri", "value" : "http://example.org/bob"}
                }"""


union_query  = PROLOGUE+"""
SELECT DISTINCT ?uri ?name WHERE {
            { <http://example.org/alice> foaf:name ?name . } UNION { <http://example.org/bob> foaf:name ?name . }
}
"""

union_correct = """{
                   "name" : {"type": "literal", "xml:lang" : "None", "value" : "Alice"}
                },
               {
                   "name" : {"type": "literal", "xml:lang" : "None", "value" : "Bob"}
                }"""


class TestSparqlJsonResults(unittest.TestCase):

    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data), format="n3")

    def _query_result_contains(self, query, correct):
        results = self.graph.query(query)
        result_json = results.serialize(format='json')
        self.failUnless(result_json.find(correct) > 0)

    def testOPTIONALSimple(self):
        self._query_result_contains(opt_query, opt_correct)

    def testWildcard(self):
        self._query_result_contains(wild_query, wild_correct)

    def testUnion(self):
        self._query_result_contains(union_query, union_correct)


if __name__ == "__main__":
    unittest.main()

