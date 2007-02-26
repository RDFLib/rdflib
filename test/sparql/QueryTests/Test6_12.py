#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/04/02 07:29:46 $, by $Author: ivan $, $Revision: 1.1 $
#

from testSPARQL import ns_rdf
from testSPARQL import ns_rdfs
from testSPARQL import ns_dc
from testSPARQL import ns_dc0
from testSPARQL import ns_foaf
from testSPARQL import ns_ns
from testSPARQL import ns_book

from rdflib.Literal     import Literal
from rdflib.sparql.sparqlOperators import lt, ge
import datetime
from rdflib.sparql.graphPattern import GraphPattern

thresholdDate = datetime.date(2005,01,01)


rdfData ="""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:dc0="http://purl.org/dc/elements/1.0/"
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:foaf="http://xmlns.com/foaf/0.1/"
   xmlns:ns = "http://example.org/ns#"
   xmlns:book = "http://example.org/book"
>
        <rdf:Description rdf:ID="book2">
                <dc0:title>SPARQL Query Language Tutorial</dc0:title>
                <dc0:creator>Alice</dc0:creator>
        </rdf:Description>
        <rdf:Description rdf:ID="book1">
                <dc:title>SPARQL Protocol Tutorial</dc:title>
                <dc:creator>Bob</dc:creator>
        </rdf:Description>
</rdf:RDF>
"""

select      = ["?x","?y"]
patt1       = GraphPattern([("?book",ns_dc0["title"],"?x")])
patt2       = GraphPattern([("?book",ns_dc["title"],"?y")])
pattern     = [patt1,patt2]
optional    = []
tripleStore = None
expected = '''
  ?x: SPARQL Query Language Tutorial
  ?y: None

  ?x: None
  ?y: SPARQL Protocol Tutorial
'''



