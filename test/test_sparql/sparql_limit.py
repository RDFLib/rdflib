from rdflib import ConjunctiveGraph, plugin
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
LIMIT 2
"""

class TestLimit(unittest.TestCase):

    def testLimit(self):
        graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
        graph.parse(StringIO(test_data), format="n3")
        results = graph.query(test_query,DEBUG=True)
        print len(results)
        self.failUnless(len(results) == 2)

if __name__ == "__main__":
    unittest.main()
