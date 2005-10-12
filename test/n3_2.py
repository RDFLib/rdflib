from rdflib import *
from rdflib.Graph import Context
import sys
from pprint import pprint

implies = URIRef("http://www.w3.org/2000/10/swap/log#implies")

configString="user=root,password=1618,host=localhost,db=rdflib_db"
testN3="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
{:a :b :c;a :foo} => {:a :d :c}.
_:foo a rdfs:Class.
:a :d :ce."""


#Thorough test suite for formula-aware store
def testN3Store(backend):
    g = Graph(backend=backend)
    g.open(configString)    
    g.parse(StringInputSource(testN3), format="n3") 
    try:
        for s,p,o in g.triples((None,implies,None)):
            formulaA = s
            formulaB = o

        a = URIRef('http://test/a')
        b = URIRef('http://test/b')
        c = URIRef('http://test/c')
        d = URIRef('http://test/d')

        assert len(list(g.contexts()))==3
        
        #triples test cases
        assert type(list(g.triples((None,RDF.type,RDFS.Class)))[0][0]) == BNode
        assert len(list(g.triples((None,implies,None))))==1
        assert len(list(g.triples((None,RDF.type,None))))==3
        assert len(list(g.triples((None,RDF.type,None),formulaA)))==1
        assert len(list(g.triples((None,None,None),formulaA)))==2        
        assert len(list(g.triples((None,None,None),formulaB)))==1
        assert len(list(g.triples((None,None,None))))==5
        assert len(list(g.triples((None,URIRef('http://test/d'),None),formulaB)))==1
        assert len(list(g.triples((None,URIRef('http://test/d'),None))))==1

        #Remove test cases
        g.remove((None,implies,None))
        assert len(list(g.triples((None,implies,None))))==0
        assert len(list(g.triples((None,None,None),formulaA)))==2
        assert len(list(g.triples((None,None,None),formulaB)))==1

        g.remove((None,b,None),formulaA)
        assert len(list(g.triples((None,None,None),formulaA)))==1
        g.remove((None,RDF.type,None),formulaA)
        assert len(list(g.triples((None,None,None),formulaA)))==0

        g.remove((None,RDF.type,RDFS.Class))

        #remove_context tests
        formulaBContext=Context(g,formulaB)
        g.remove_context(formulaB)
        #g.remove((None,None,None),formulaB)
        assert len(list(g.triples((None,RDF.type,None))))==2
        assert len(g)==3
        assert len(formulaBContext)==0
        
        g.remove((None,None,None))
        assert len(g)==0

        g.backend.destroy(configString)
    except:
        g.backend.destroy(configString)
        raise
    
# contexts tests
# 1) all contexts 2) same triple in two contexts
# remove context tests
# 1) clear quoted context
