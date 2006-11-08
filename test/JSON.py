from rdflib import ConjunctiveGraph, plugin
from rdflib.store import Store
from StringIO import StringIO
import unittest

test_data = """ 
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://example.org/alice>  foaf:name       "Alice" .
<http://example.org/alice>  foaf:knows      <http://example.org/bob> .
<http://example.org/bob>  foaf:name       "Bob" .
"""

test_query = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?name ?x ?friend
WHERE { ?x foaf:name ?name .
        OPTIONAL { ?x foaf:knows ?friend . }
}
"""

correct = """"name" : {"type": "literal", "xml:lang" : "None", "value" : "Bob"},\n                   "x" : {"type": "uri", "value" : "http://example.org/bob"}\n                }"""


# See Also: http://rdflib.net/pipermail/dev/2006-November/000112.html


class JSON(unittest.TestCase):

    def testOPTIONALSimple(self):
        graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
        graph.parse(StringIO(test_data), format="n3")
        results = graph.query(test_query)
        result_json = results.serialize(format='json')
        self.failUnless(result_json.find(correct) > 0)

if __name__ == "__main__":
    unittest.main()
