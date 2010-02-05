from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef, Literal
from rdflib.namespace import RDFS
from rdflib.sparql.algebra import RenderSPARQLAlgebra
from StringIO import StringIO
import unittest

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
    
QUERY1 = u"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX   dc: <http://purl.org/dc/elements/1.1/>
PREFIX  xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?doc
WHERE { 
  ?doc a foaf:Document;
       dc:date ?date. 
    FILTER (?date < xsd:dateTime("2006-01-01T00:00:00") && 
            ?date > xsd:dateTime("1995-06-15T00:00:00")) }"""

QUERY2 = u"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX   dc: <http://purl.org/dc/elements/1.1/>
PREFIX  xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?doc
WHERE { 
  ?doc a foaf:Document;
       dc:date ?date. 
    FILTER (?date < "2006-01-01T00:00:00" && 
            ?date > "1995-06-15T00:00:00") }"""

QUERY3 = u"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX   dc: <http://purl.org/dc/elements/1.1/>
PREFIX  xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?doc
WHERE { 
  ?doc a foaf:Document;
       dc:date ?date. 
    FILTER (?date < "2006-01-01T00:00:00"^^xsd:dateTime && 
            ?date > "1995-06-15T00:00:00"^^xsd:dateTime ) }"""

ANSWER1 = URIRef('http://del.icio.us/rss/chimezie/paper')

class DateFilterTest(unittest.TestCase):
    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.load(StringIO(testContent), format='n3')
    def test_DATE_FILTER1(self):
        for query in [QUERY1,QUERY2,QUERY3]:
            print query
            #pQuery = Parse(query)
            #print RenderSPARQLAlgebra(pQuery)
            results = self.graph.query(query,
                                       DEBUG=False).serialize(format='python')
            results = list(results)
            self.failUnless(
                len(results) and results == [ANSWER1],
                "expecting : %s .  Got: %s"%([ANSWER1],repr(results)))

if __name__ == "__main__":
    unittest.main()
