#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/04/02 07:30:02 $, by $Author: ivan $, $Revision: 1.1 $
#

from testSPARQL import ns_rdf
from testSPARQL import ns_rdfs
from testSPARQL import ns_dc0
from testSPARQL import ns_foaf
from testSPARQL import ns_ns
from testSPARQL import ns_book
from testSPARQL import ns_vcard
from testSPARQL import ns_person

from rdflib.Literal     import Literal
from rdflib.sparql.sparqlOperators import lt, ge
import datetime
from rdflib.sparql.graphPattern import GraphPattern

thresholdDate = datetime.date(2005,01,01)

rdfData = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:foaf="http://xmlns.com/foaf/0.1/"
   xmlns:ns = "http://example.org/ns#"
>
        <rdf:Description>
                <foaf:name>Alice</foaf:name>
                <foaf:mbox rdf:resource="mailto:alice@example.com"/>
        </rdf:Description>
</rdf:RDF>
"""

select      = []
pattern     = GraphPattern([("?x",ns_foaf["name"],"?name")])
optional    = []
construct   = GraphPattern([(ns_person["Alice"],ns_vcard["FN"],"?name")])
tripleStore = None



