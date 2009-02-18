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

correct = """"name" : {"type": "literal", "xml:lang" : "None", "value" : "Bob"},
                   "x" : {"type": "uri", "value" : "http://example.org/bob"}
                }"""

test_header_query = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?name ?friend
WHERE { ?x foaf:name ?name .
        OPTIONAL { ?x foaf:knows ?friend . }
}
"""

# See Also: http://rdflib.net/pipermail/dev/2006-November/000112.html


class JSON(unittest.TestCase):

    def setUp(self):
        self.graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
        self.graph.parse(StringIO(test_data), format="n3")
        
    def testComma(self):
        """
        Verify the serialisation of the data as json contains an exact
        substring, with the comma in the correct place.
        """
        results = self.graph.query(test_query)
        result_json = results.serialize(format='json')
        self.failUnless(result_json.find(correct) > 0)

    def testHeader(self):
        """
        Verify that the "x", substring is omitted from the serialised output.
        """
        results = self.graph.query(test_header_query)
        result_json = results.serialize(format='json')
        self.failUnless(result_json.find('"x",') == -1)
        
if __name__ == "__main__":
    unittest.main()
