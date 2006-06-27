from rdflib.Namespace import Namespace
from rdflib import plugin,RDF,RDFS,URIRef
from rdflib.store import Store
from cStringIO import StringIO
from rdflib.Graph import Graph,ReadOnlyGraphAggregate,ConjunctiveGraph
import sys
from pprint import pprint

testGraph1N3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
:foo a rdfs:Class.
:bar :d :c.
:a :d :c.
"""


testGraph2N3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
@prefix log: <http://www.w3.org/2000/10/swap/log#>.
:foo a rdfs:Resource.
:bar rdfs:isDefinedBy [ a log:Formula ].
:a :d :e.
"""

testGraph3N3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix log: <http://www.w3.org/2000/10/swap/log#>.
@prefix : <http://test/> .
<> a log:N3Document.
"""

sparqlQ = \
"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
FROM NAMED <graph1>
FROM NAMED <graph2>
FROM NAMED <graph3>
FROM <http://www.w3.org/2000/01/rdf-schema#>

WHERE {?sub ?pred rdfs:Class }"""

sparqlQ2 =\
"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?class
WHERE { GRAPH ?graph { ?member a ?class } }"""

sparqlQ3 =\
"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX log: <http://www.w3.org/2000/10/swap/log#>
SELECT ?n3Doc
WHERE {?n3Doc a log:N3Document }"""


def testAggregateRaw():
    memStore = plugin.get('IOMemory',Store)()
    graph1 = Graph(memStore)
    graph2 = Graph(memStore)
    graph3 = Graph(memStore)

    for n3Str,graph in [(testGraph1N3,graph1),
                        (testGraph2N3,graph2),
                        (testGraph3N3,graph3)]:
        graph.parse(StringIO(n3Str),format='n3')

    G = ReadOnlyGraphAggregate([graph1,graph2,graph3])

    #Test triples
    assert len(list(G.triples((None,RDF.type,None))))                  == 4
    assert len(list(G.triples((URIRef("http://test/bar"),None,None)))) == 2
    assert len(list(G.triples((None,URIRef("http://test/d"),None))))   == 3

    #Test __len__
    assert len(G) == 8

    #Test __contains__
    assert (URIRef("http://test/foo"),RDF.type,RDFS.Resource) in G

    barPredicates = [URIRef("http://test/d"),RDFS.isDefinedBy]
    assert len(list(G.triples_choices((URIRef("http://test/bar"),barPredicates,None)))) == 2

def testAggregateSPARQL():
    memStore = plugin.get('IOMemory',Store)()
    graph1 = Graph(memStore,URIRef("graph1"))
    graph2 = Graph(memStore,URIRef("graph2"))
    graph3 = Graph(memStore,URIRef("graph3"))

    for n3Str,graph in [(testGraph1N3,graph1),
                        (testGraph2N3,graph2),
                        (testGraph3N3,graph3)]:
        graph.parse(StringIO(n3Str),format='n3')

    graph4 = Graph(memStore,RDFS.RDFSNS)
    graph4.parse(RDFS.RDFSNS)
    G = ConjunctiveGraph(memStore)
    rt =  G.query(sparqlQ)
    assert len(rt) > 1
    #print rt.serialize(format='xml')
    LOG_NS = Namespace(u'http://www.w3.org/2000/10/swap/log#')
    rt=G.query(sparqlQ2,initBindings={u'?graph' : URIRef("graph3")})
    #print rt.serialize(format='json')
    assert rt.serialize('python')[0] == LOG_NS.N3Document,str(rt)

def testDefaultGraph():
    memStore = plugin.get('IOMemory',Store)()
    graph1 = Graph(memStore,URIRef("graph1"))
    graph2 = Graph(memStore,URIRef("graph2"))
    graph3 = Graph(memStore,URIRef("graph3"))
    
    for n3Str,graph in [(testGraph1N3,graph1),
                        (testGraph2N3,graph2),
                        (testGraph3N3,graph3)]:
        graph.parse(StringIO(n3Str),format='n3')
    G = ConjunctiveGraph(memStore)
    #test that CG includes triples from all 3
    assert G.query(sparqlQ3),"CG as default graph should *all* triples"
    assert not graph2.query(sparqlQ3),"Graph as default graph should *not* include triples from other graphs"

if __name__ == '__main__':
    #testAggregateRaw()
    #testAggregateSPARQL()
    testDefaultGraph()