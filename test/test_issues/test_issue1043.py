import decimal
import unittest
import io
import sys

from rdflib import Graph, Namespace, XSD, RDFS, Literal


def test_issue_1043():
    expected = """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/number> rdfs:label 4e-08 .

"""

    g = Graph()
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)
    n = Namespace("http://example.org/")
    g.add((n.number, RDFS.label, Literal(0.00000004, datatype=XSD.decimal)))
    s = g.serialize(format="turtle")
    assert s == expected

