from rdflib.graph import ConjunctiveGraph
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


test_material = {}

test_material['optional'] = (PROLOGUE+"""
    SELECT ?name ?x ?friend
    WHERE { ?x foaf:name ?name .
            OPTIONAL { ?x foaf:knows ?friend . }
    }
    """,
    """"name" : {"type": "literal", "xml:lang" : "None", "value" : "Bob"},
                   "x" : {"type": "uri", "value" : "http://example.org/bob"}
                }"""
    )

test_material['select_vars'] = (PROLOGUE+"""
    SELECT ?name ?friend
    WHERE { ?x foaf:name ?name .
            OPTIONAL { ?x foaf:knows ?friend . }
    }""",
    """"vars" : [
             "name",
             "friend"
         ]"""
    )

test_material['wildcard'] = (PROLOGUE+"""
    SELECT * WHERE { ?x foaf:name ?name . }
    """,
    """"name" : {"type": "literal", "xml:lang" : "None", "value" : "Bob"},
                   "x" : {"type": "uri", "value" : "http://example.org/bob"}
                }"""
    )

test_material['wildcard_vars'] = (PROLOGUE+"""
    SELECT * WHERE { ?x foaf:name ?name . }
    """,
    """"vars" : [
             "name",
             "x"
         ]"""
    )

test_material['union'] = (PROLOGUE+"""
    SELECT DISTINCT ?name WHERE {
                { <http://example.org/alice> foaf:name ?name . } UNION { <http://example.org/bob> foaf:name ?name . }
    }
    """,
    """{
                   "name" : {"type": "literal", "xml:lang" : "None", "value" : "Bob"}
                },
               {
                   "name" : {"type": "literal", "xml:lang" : "None", "value" : "Alice"}
                }"""
    )

test_material['union3'] = (PROLOGUE+"""
    SELECT DISTINCT ?name WHERE {
                { <http://example.org/alice> foaf:name ?name . }
                UNION { <http://example.org/bob> foaf:name ?name . }
                UNION { <http://example.org/nobody> foaf:name ?name . }
    }
            """, '"Alice"'
    )


def make_method(testname):
    def test(self):
        query, correct = test_material[testname]
        self._query_result_contains(query, correct)
    test.__name__ = 'test%s' % testname.title()
    return test


class TestSparqlJsonResults(unittest.TestCase):

    known_issue = True

    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data), format="n3")

    def _query_result_contains(self, query, correct):
        results = self.graph.query(query)
        result_json = results.serialize(format='json')
        self.failUnless(result_json.find(correct) >= 0,
                "Expected:\n %s \n- to contain:\n%s" % (result_json, correct))

    testOptional = make_method('optional')

    testWildcard = make_method('wildcard')

    testUnion = make_method('union')

    testUnion3 = make_method('union3')

    testSelectVars = make_method('select_vars')
    
    testWildcardVars = make_method('wildcard_vars')
    
if __name__ == "__main__":
    unittest.main()

