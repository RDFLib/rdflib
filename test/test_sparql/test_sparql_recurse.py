from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef, Literal
from rdflib.namespace import RDFS
from rdflib.sparql.algebra import RenderSPARQLAlgebra
from StringIO import StringIO
import unittest, sys
import nose

testContent = """
@prefix foaf:  <http://xmlns.com/foaf/0.1/> .
@prefix dc: <http://purl.org/dc/elements/1.1/>.
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
<http://del.icio.us/rss/chimezie/logic> 
  a foaf:Document;
  dc:date "2006-10-01T12:35:00"^^xsd:dateTime.
<http://del.icio.us/rss/chimezie/paper> 
  a foaf:Document;
  dc:date "2005-05-25T08:15:00"^^xsd:dateTime.
<http://del.icio.us/rss/chimezie/illustration> 
  a foaf:Document;
  dc:date "1990-01-01T12:45:00"^^xsd:dateTime."""
    
BASIC_KNOWS_DATA = '''
@prefix foaf:  <http://xmlns.com/foaf/0.1/> .

<ex:person.1> foaf:name "person 1";
              foaf:knows <ex:person.2>.
<ex:person.2> foaf:knows <ex:person.3>.
<ex:person.3> foaf:name "person 3".
'''

KNOWS_QUERY = '''
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?x ?name
{
  ?x foaf:knows ?y .
  OPTIONAL { ?y foaf:name ?name }
}
RECUR ?y TO ?x
'''

SUBCLASS_DATA = '''
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
<ex:ob> a <ex:class.1> .
<ex:class.1> rdfs:subClassOf <ex:class.2> .
<ex:class.2> rdfs:subClassOf <ex:class.3> .
'''

SUBCLASS_QUERY = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?x ?t 
{ ?x rdf:type ?t }
RECUR ?t TO ?x
{ ?x rdfs:subClassOf ?t }
'''

ANSWER1 = URIRef('http://del.icio.us/rss/chimezie/paper')

class RecursionTests(unittest.TestCase):
    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.load(StringIO(testContent), format='n3')

    def test_simple_recursion(self):
        graph = ConjunctiveGraph()
        graph.load(StringIO(BASIC_KNOWS_DATA), format='n3')
        results = graph.query(KNOWS_QUERY,
                              DEBUG=False).serialize(format='python')
        results = set([tuple(result) for result in results])
        person1 = URIRef('ex:person.1')
        person2 = URIRef('ex:person.2')
        nose.tools.assert_equal(
          results,
          set([(person1, None), (person1, Literal('person 3')),
               (person2, Literal('person 3'))]))

    def test_secondary_recursion(self):
        graph = ConjunctiveGraph()
        graph.load(StringIO(SUBCLASS_DATA), format='n3')
        results = graph.query(SUBCLASS_QUERY,
                              DEBUG=False).serialize(format='python')
        results = set([tuple(result) for result in results])
        ob = URIRef('ex:ob')
        class1 = URIRef('ex:class.1')
        class2 = URIRef('ex:class.2')
        class3 = URIRef('ex:class.3')
        nose.tools.assert_equal(
          results,
          set([(ob, class1), (ob, class2), (ob, class3)]))

if __name__ == "__main__":
    unittest.main()
