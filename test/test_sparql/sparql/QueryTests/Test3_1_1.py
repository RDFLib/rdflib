#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/04/02 07:29:46 $, by $Author: ivan $, $Revision: 1.1 $
#
"""
   Datatype test. Note that this is not 100% kosher. The problem is that the Literal of rdflib does not check the
   datatypes. In theory, if the data contains:

           x ns:p 42.

   instead of:

       x ns:p 42^^http://www.w3.org/2001/XMLSchema#integer

    the query should return no results, because the first object is of datatype string. However, Literal does not
        implement this...

"""
rdfData ="""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:rdfs ="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:rdf  ="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:dc   ="http://purl.org/dc/elements/1.1/"
   xmlns:foaf ="http://xmlns.com/foaf/0.1/"
   xmlns:ns   ="http://example.org/ns#"
   xmlns:dt   ="http://example.org/datatype#"
>
        <rdf:Description>
                <ns:p rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">42</ns:p>
                <ns:p rdf:datatype="http://example.org/datatype#specialDatatype">abc</ns:p>
                <ns:p>2005-02-27</ns:p>
                <ns:p xml:lang="en">cat</ns:p>
        </rdf:Description>
</rdf:RDF>
"""

from testSPARQL import ns_rdf
from testSPARQL import ns_rdfs
from testSPARQL import ns_dc
from testSPARQL import ns_foaf
from testSPARQL import ns_ns

from rdflib.Literal import Literal
import datetime
from rdflib.sparql.graphPattern import GraphPattern

select      = ["?v"]
pattern     = GraphPattern([("?v","?p",42)])
optional    = []
tripleStore = None
expected = '''
?v : (some bnode id)
'''


