# test for https://github.com/RDFLib/rdflib/issues/457

import io
from xml.etree import ElementTree

import rdflib
from rdflib.plugins.stores.sparqlstore import CastToTerm

s = """<ns0:literal xmlns:ns0="http://www.w3.org/2005/sparql-results#" />"""
node = ElementTree.parse(io.BytesIO(s)).getroot()
term = CastToTerm(node)
assert term  == rdflib.Literal(''), repr(term)

