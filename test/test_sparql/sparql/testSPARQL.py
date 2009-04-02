#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/04/02 07:29:30 $, by $Author: ivan $, $Revision: 1.1 $
#
"""

"""
import sys, os, time, datetime

from rdflib.constants   import RDFNS  as ns_rdf
from rdflib.constants   import RDFSNS as ns_rdfs
#from rdflib.sparql import ns_dc   as ns_dc
#from rdflib.sparql import ns_owl  as ns_owl

from rdflib.sparql.sparql import type_integer
from rdflib.sparql.sparql import type_double
from rdflib.sparql.sparql import type_float
from rdflib.sparql.sparql import type_decimal
from rdflib.sparql.sparql import type_dateTime

from rdflib.Namespace import Namespace

ns_foaf   = Namespace("http://xmlns.com/foaf/0.1/")
ns_ns     = Namespace("http://example.org/ns#")
ns_book   = Namespace("http://example.org/book")
ns_person = Namespace("http://example.org/person#")
ns_dt     = Namespace("http://example.org/datatype#")
ns_dc0    = Namespace("http://purl.org/dc/elements/1.0/")
ns_dc     = Namespace("http://purl.org/dc/elements/1.1/")
ns_vcard  = Namespace("http://www.w3.org/2001/vcard-rdf/3.0#")

