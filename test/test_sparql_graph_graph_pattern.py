from rdflib import Literal, URIRef, Namespace
from rdflib.Graph import Graph, ReadOnlyGraphAggregate
from StringIO import StringIO
import unittest

FOAF = Namespace("http://xmlns.com/foaf/0.1/")

#See: http://www.w3.org/TR/rdf-sparql-query/#queryDataset

test_graph_a = """
@prefix  foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix  rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix  rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .

_:a  foaf:name     "Alice" .
_:a  foaf:mbox     <mailto:alice@work.example> .
_:a  foaf:knows    _:b .

_:b  foaf:name     "Bob" .
_:b  foaf:mbox     <mailto:bob@work.example> .
_:b  foaf:nick     "Bobby" .
_:b  rdfs:seeAlso  <http://example.org/foaf/bobFoaf> .

<http://example.org/foaf/bobFoaf>
     rdf:type      foaf:PersonalProfileDocument ."""
     
test_graph_b = """
@prefix  foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix  rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix  rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .

_:z  foaf:mbox     <mailto:bob@work.example> .
_:z  rdfs:seeAlso  <http://example.org/foaf/bobFoaf> .
_:z  foaf:nick     "Robert" .

<http://example.org/foaf/bobFoaf>
     rdf:type      foaf:PersonalProfileDocument ."""     

test_query1 = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?src ?bobNick
FROM NAMED <http://example.org/foaf/aliceFoaf>
FROM NAMED <http://example.org/foaf/bobFoaf>
WHERE
  {
    GRAPH ?src
    { ?x foaf:mbox <mailto:bob@work.example> .
      ?x foaf:nick ?bobNick
    }
  }"""

test_query2= """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX data: <http://example.org/foaf/>

SELECT ?nick
FROM NAMED <http://example.org/foaf/aliceFoaf>
FROM NAMED <http://example.org/foaf/bobFoaf>
WHERE
  {
     GRAPH data:bobFoaf {
         ?x foaf:mbox <mailto:bob@work.example> .
         ?x foaf:nick ?nick }
  }"""

test_query3= """
PREFIX  data:  <http://example.org/foaf/>
PREFIX  foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX  rdfs:  <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?mbox ?nick ?ppd
FROM NAMED <http://example.org/foaf/aliceFoaf>
FROM NAMED <http://example.org/foaf/bobFoaf>
WHERE
{
  GRAPH data:aliceFoaf
  {
    ?alice foaf:mbox <mailto:alice@work.example> ;
           foaf:knows ?whom .
    ?whom  foaf:mbox ?mbox ;
           rdfs:seeAlso ?ppd .
    ?ppd  a foaf:PersonalProfileDocument .
  } .
  GRAPH ?ppd
  {
      ?w foaf:mbox ?mbox ;
         foaf:nick ?nick
  }
}"""

class TestGraphGraphPattern(unittest.TestCase):

    def setUp(self):
        self.graph1 = Graph(identifier=URIRef('http://example.org/foaf/aliceFoaf'))
        self.graph1.parse(StringIO(test_graph_a), format="n3")
        self.graph2 = Graph(identifier=URIRef('http://example.org/foaf/bobFoaf'))
        self.graph2.parse(StringIO(test_graph_b), format="n3")
        self.unionGraph = ReadOnlyGraphAggregate(graphs=[self.graph1,self.graph2])

    def test_8_3_1(self):
        rt=self.unionGraph.query(test_query1,DEBUG=False).serialize("python")
        self.failUnless(len(rt) == 2,"Expected 2 item solution set")
        for src,bobNick in rt:
            self.failUnless(src in [URIRef('http://example.org/foaf/aliceFoaf'),URIRef('http://example.org/foaf/bobFoaf')],
                            "Unexpected ?src binding :\n %s" % src)
            self.failUnless(bobNick in [Literal("Bobby"),Literal("Robert")],
                            "Unexpected ?bobNick binding :\n %s" % bobNick)
            
    def test_8_3_2(self):
        rt=self.unionGraph.query(test_query2,DEBUG=False).serialize("python")
        self.failUnless(len(rt) == 1,"Expected 1 item solution set")
        self.failUnless(rt[0]  == Literal("Robert"),"Unexpected ?nick binding :\n %s" % rt[0])            
        
#    def test_8_3_3(self):
#        rt=self.unionGraph.query(test_query3,DEBUG=False).serialize("python")
#        self.failUnless(len(rt) == 1,"Expected 1 item solution set")
#        for mbox,nick,ppd in rt:
#            self.failUnless(mbox == URIRef('mailto:bob@work.example'),
#                            "Unexpected ?mbox binding :\n %s" % mbox)
#            self.failUnless(nick  == Literal("Robert"),
#                            "Unexpected ?nick binding :\n %s" % nick)
#            self.failUnless(ppd == URIRef('http://example.org/foaf/bobFoaf'),
#                            "Unexpected ?ppd binding :\n %s" % ppd)

if __name__ == "__main__":
    unittest.main()

