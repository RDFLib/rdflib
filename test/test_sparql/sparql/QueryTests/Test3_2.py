#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/04/02 07:29:46 $, by $Author: ivan $, $Revision: 1.1 $
#

from testSPARQL import ns_rdf
from testSPARQL import ns_rdfs
from testSPARQL import ns_dc
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
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:foaf="http://xmlns.com/foaf/0.1/"
   xmlns:ns = "http://example.org/ns#"
   xmlns:book = "http://example.org/book"
>
        <rdf:Description rdf:ID="book1">
                <dc:title>SPARQL Tutorial</dc:title>
                <ns:price rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">42</ns:price>
        </rdf:Description>
        <rdf:Description rdf:ID="book2">
                <dc:title>The Semantic Web</dc:title>
                <ns:price rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">23</ns:price>
        </rdf:Description>
        <rdf:Description rdf:ID="book3">
                <dc:title>The Semantic Web Old</dc:title>
                <dc:date rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2000-03-12</dc:date>
        </rdf:Description>
        <rdf:Description rdf:ID="book4">
                <dc:title>The Semantic Web New</dc:title>
                <dc:date rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2005-03-02</dc:date>
        </rdf:Description>
</rdf:RDF>
"""

select      = ["?title", "?price"]
pattern     = GraphPattern([("?x", ns_dc["title"],"?title"),("?x",ns_ns["price"],"?price")])
pattern.addConstraint(lt("?price",30))
optional    = []
tripleStore = None
expected = '''
  ?title: The Semantic Web
  ?price: 23
'''



