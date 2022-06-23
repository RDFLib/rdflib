"""Test that N-Triples formats do not have double newlines at the end
of the output.

https://github.com/RDFLib/rdflib/issues/1998
"""
import rdflib


def test_1998():
    g = rdflib.Graph()
    bob = rdflib.URIRef("http://example.org/people/Bob")
    g.add((bob, rdflib.RDF.type, rdflib.FOAF.Person))
    for nt_format in ("nt", "nt11"):
        output = g.serialize(format=nt_format)
        assert not output.endswith("\n\n")
