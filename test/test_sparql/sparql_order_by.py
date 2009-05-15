from rdflib.graph import ConjunctiveGraph
from rdflib import plugin
from rdflib.term import Literal
from rdflib.store import Store
from StringIO import StringIO
import unittest

test_data = """ 
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://example.org/bob>  foaf:name       "Bob" .
<http://example.org/dave>  foaf:name       "Dave" .
<http://example.org/alice>  foaf:name       "Alice" .
<http://example.org/charlie>  foaf:name       "Charlie" .
"""

test_query = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?name
WHERE { ?x foaf:name ?name . }
ORDER BY ?name
"""

class TestOrderBy(unittest.TestCase):

    def testOrderBy(self):
        graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
        graph.parse(StringIO(test_data), format="n3")
        results = graph.query(test_query)

        self.failUnless(False not in [r[0] == a for r, a in zip(results, ['Alice', 'Bob', 'Charlie', 'Dave'])])

if __name__ == "__main__":
    unittest.main()
