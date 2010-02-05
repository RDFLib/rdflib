from rdflib.graph import ConjunctiveGraph
from StringIO import StringIO
import re
import unittest

test_data = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/word>
    rdfs:label "Word"@en;
    rdf:value 1;
    rdfs:seeAlso [] .

"""

PROLOGUE = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
"""

query = PROLOGUE+"""
SELECT ?s ?o WHERE { ?s ?p ?o . }
"""

expected_fragments = [
    #u"""<sparql:sparql xmlns="http://www.w3.org/2005/sparql-results#"><sparql:head>""",

    u"""</sparql:head><sparql:results distinct="false" ordered="false">""",

    u"""<sparql:binding name="s"><sparql:uri>http://example.org/word</sparql:uri></sparql:binding>""",

    u"""<sparql:binding name="o"><sparql:bnode>""",

    u"""<sparql:binding name="o"><sparql:literal datatype="http://www.w3.org/2001/XMLSchema#integer">1</sparql:literal></sparql:binding>""",

    u"""<sparql:result><sparql:binding name="s"><sparql:uri>http://example.org/word</sparql:uri></sparql:binding><sparql:binding name="o"><sparql:literal xml:lang="en">Word</sparql:literal></sparql:binding></sparql:result>"""
]


# TODO:
#   - better canonicalization of results to compare with (4Suite-XML has support for this)
#   - test expected 'variable'-elems in head


class TestSparqlXmlResults(unittest.TestCase):

    sparql = True

    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.parse(StringIO(test_data), format="n3")

    def testSimple(self):
        self._query_result_contains(query, expected_fragments)

    def _query_result_contains(self, query, fragments):
        results = self.graph.query(query)
        result_xml = results.serialize(format='xml')
        result_xml = normalize(result_xml) # TODO: poor mans c14n..
        print result_xml
        for frag in fragments:
            print frag
            self.failUnless(frag in result_xml)


def normalize(s, exp=re.compile(r'\s+', re.MULTILINE)):
    return exp.sub(' ', s)


if __name__ == "__main__":
    unittest.main()


