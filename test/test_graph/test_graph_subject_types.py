from test.data import likes, pizza, tarek, context0

import pytest

from rdflib import FOAF, RDF, RDFS, XSD, Namespace, logger
from rdflib.graph import Dataset, Graph, QuotedGraph
from rdflib.term import (
    BNode,
    IdentifiedNode,
    Literal,
    Node,
    RDFLibGenid,
    URIRef,
    Variable,
)


def test_literal_as_subject():
    g = Graph()
    g.add((Literal("tarek", lang="en"), likes, pizza))
    assert list(g)[0] == (
        Literal('tarek', lang='en'),
        URIRef('urn:example:likes'),
        URIRef('urn:example:pizza')
    )

def test_literal_as_subject_roundtrip():
    harry = Literal("Harry")
    likes = URIRef("urn:example:likes")
    pizza = URIRef("urn:example:pizza")
    g = Graph()
    g.add((harry, likes, pizza))
    assert g.serialize(format="n3") == """@prefix ns1: <urn:example:> .

"Harry" ns1:likes ns1:pizza .

"""
    g1 = Graph()
    g1.parse(data=g.serialize(format="turtle"), format="turtle")
    assert g1.serialize(format="n3") == """@prefix ns1: <urn:example:> .

"Harry" ns1:likes ns1:pizza .

"""

def test_quotedgraph_as_subject():
    g = Graph("default")
    qg = QuotedGraph(store=g.store, identifier=context0)
    qg.add((tarek, likes, pizza))
    g.add((qg, RDF.type, RDF.Statement))
    (s, p, o) = list(g)[0]
    assert [s.identifier, p, o] == [
        URIRef('urn:example:context-0'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement')
    ]
    assert list(s) == [
        (
            URIRef('urn:example:tarek'),
            URIRef('urn:example:likes'),
            URIRef('urn:example:pizza')
        )
    ]

@pytest.mark.xfail(reason="QuotedGraph as subject cannot be roundtripped")
def test_quotedgraph_as_subject_roundtrip():
    g = Graph("default")
    qg = QuotedGraph(store=g.store, identifier=context0)
    qg.add((tarek, likes, pizza))
    g.add((qg, RDF.type, RDF.Statement))
    (s, p, o) = list(g)[0]
    assert [s.identifier, p, o] == [
        URIRef('urn:example:context-0'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement')
    ]
    assert list(s) == [
        (
            URIRef('urn:example:tarek'),
            URIRef('urn:example:likes'),
            URIRef('urn:example:pizza')
        )
    ]
    g1 = Graph()
    g1.parse(data=g.serialize(format="n3"), format="n3")
    (s, p, o) = list(g1)[0]
    assert [s.identifier, p, o] == [
        URIRef('urn:example:context-0'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement')
    ]
    assert list(s) == [
        (
            URIRef('urn:example:tarek'),
            URIRef('urn:example:likes'),
            URIRef('urn:example:pizza')
        )
    ]


def test_variable_as_subject():
    g = Graph()
    g.add((Variable("tarek"), RDF.type, Literal("Variable")))
    assert list(g)[0] == (
        Variable('tarek'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        Literal('Variable')
    )


def test_variable_as_subject_roundtrip():
    g = Graph()
    g.add((Variable("tarek"), RDF.type, Literal("Variable")))
    assert list(g)[0] == (
        Variable('tarek'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        Literal('Variable')
    )
    g1 = Graph()
    g1.parse(data=g.serialize(format="n3"), format="n3")
    assert list(g1)[0] == (
        Variable('tarek'),
        URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        Literal('Variable')
    )
