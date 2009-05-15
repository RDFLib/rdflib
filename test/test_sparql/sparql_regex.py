from rdflib import plugin
from rdflib.graph import ConjunctiveGraph
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
WHERE { ?x foaf:name ?name .
        FILTER regex(?name, "a", "i") 
        }
"""

class TestRegex(unittest.TestCase):

    def testRegex(self):
        graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
        graph.parse(StringIO(test_data), format="n3")
        results = graph.query(test_query)
        self.failUnless(len([a for a in results if 'a' in a[0] or 'A' in a[0]]) == 3)

if __name__ == "__main__":
    unittest.main()
