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
LIMIT 2
"""

test_data2 = """
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix :   <http://example.org/book/> .
@prefix ns: <http://example.org/ns#> .

:book1 dc:title "SPARQL Tutorial" .
:book1 ns:price 35 .
:book2 dc:title "Python Tutorial" .
:book2 ns:price 25 .
:book3 dc:title "Java Tutorial" .
:book3 ns:price 15 .
:book3 dc:title "COBOL Tutorial" .
:book3 ns:price 5 .
"""

test_query2 ="""
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX ns: <http://example.org/ns#>

SELECT ?title ?price
WHERE {
 ?x ns:price ?price .
 FILTER (?price < 20) .
 ?x dc:title ?title .
}
LIMIT 1"""

class TestLimit(unittest.TestCase):

    def testLimit(self):
        graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
        graph.parse(StringIO(test_data), format="n3")
        results = graph.query(test_query,DEBUG=True)
        print len(results)
        self.failUnless(len(results) == 2)
        
    def testLimit2(self):
           graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
           graph.parse(StringIO(test_data2), format="n3")
           results = list(graph.query(test_query2,DEBUG=True))
           print graph.query(test_query2).serialize(format='xml')
           self.failUnless(len(results) == 1)
           for title,price in results:    
               self.failUnless(title in [Literal("Java Tutorial"),
                                         Literal("COBOL Tutorial")])    

if __name__ == "__main__":
    unittest.main()
