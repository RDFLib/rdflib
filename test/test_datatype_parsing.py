# -*- coding: UTF-8 -*-
import unittest
from pprint import pprint
from rdflib import ConjunctiveGraph, URIRef, Literal, RDFS, Namespace
from rdflib.Literal import _XSD_NS
from StringIO import StringIO
from sets import Set

testContent = """
@prefix    :        <http://example.org/things#> .
@prefix xsd:        <http://www.w3.org/2001/XMLSchema#> .
:xi2 :p  "1"^^xsd:integer .
:xd3 :p  "1"^^xsd:double .
"""
    
exNS = Namespace("http://example.org/things#")

double1 = Literal('1',datatype=_XSD_NS.double)

class TestSparqlOPT_FILTER(unittest.TestCase):
    def setUp(self):
        self.graph = ConjunctiveGraph()
        self.graph.load(StringIO(testContent), format='n3')
    def test_OPT_FILTER(self):
        xd3Objs = [o for o in self.graph.objects(subject=exNS.xd3,predicate=exNS.p)]
        self.failUnless(xd3Objs[0].datatype == _XSD_NS.double,
                "Expecting %r, got instead : %r"%(double1,xd3Objs[0]))

if __name__ == "__main__":
    unittest.main()