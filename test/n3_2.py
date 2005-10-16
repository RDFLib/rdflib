from rdflib import *
from rdflib.Graph import SubGraph,QuotedGraph
import sys
from pprint import pprint

implies = URIRef("http://www.w3.org/2000/10/swap/log#implies")
testN3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
{:a :b :c;a :foo} => {:a :d :c}.
_:foo a rdfs:Class.
:a :d :c."""


#Thorough test suite for formula-aware store
def testN3Store(backend,configString):
    g = Graph(backend=backend)
    g.open(configString)    
    g.parse(StringInputSource(testN3), format="n3") 
    try:
        for s,p,o in g.triples((None,implies,None)):
            formulaA = s
            formulaB = o

        assert type(formulaA)==QuotedGraph and type(formulaB)==QuotedGraph
        a = URIRef('http://test/a')
        b = URIRef('http://test/b')
        c = URIRef('http://test/c')
        d = URIRef('http://test/d')

        #test formula as terms
        assert len(list(g.triples((formulaA,implies,formulaB))))==1

        assert len(list(g.contexts()))==3
        
        assert type(list(g.triples((None,RDF.type,RDFS.Class)))[0][0]) == BNode
        assert len(list(g.triples((None,implies,None))))==1
        assert len(list(g.triples((None,RDF.type,None))))==1
        assert len(list(formulaA.triples((None,RDF.type,None))))==1
        assert len(list(formulaA.triples((None,None,None))))==2        
        assert len(list(formulaB.triples((None,None,None))))==1
        assert len(list(g.triples((None,None,None))))==3
        assert len(list(formulaB.triples((None,URIRef('http://test/d'),None))))==1
        assert len(list(g.triples((None,URIRef('http://test/d'),None))))==1

        #context tests
        #test contexts with triple argument
        assert len(list(g.contexts((a,d,c))))==2

        #Remove test cases
        g.remove((None,implies,None))
        assert len(list(g.triples((None,implies,None))))==0
        assert len(list(formulaA.triples((None,None,None))))==2
        assert len(list(formulaB.triples((None,None,None))))==1

        formulaA.remove((None,b,None))
        assert len(list(formulaA.triples((None,None,None))))==1
        formulaA.remove((None,RDF.type,None))
        assert len(list(formulaA.triples((None,None,None))))==0

        g.remove((None,RDF.type,RDFS.Class))


        #remove_context tests
        g.remove_context(formulaB.identifier)
        assert len(list(g.triples((None,RDF.type,None))))==0
        assert len(g)==1
        assert len(formulaB)==0
        
        g.remove((None,None,None))
        assert len(g)==0

        g.backend.destroy(configString)
    except:
        g.backend.destroy(configString)
        raise
    
