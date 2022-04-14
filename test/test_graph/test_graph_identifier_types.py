from test.data import likes, pizza, tarek

import pytest

from rdflib import FOAF, XSD, Namespace
from rdflib.graph import Graph
from rdflib.term import (
    BNode,
    IdentifiedNode,
    Literal,
    Node,
    RDFLibGenid,
    URIRef,
    Variable,
)


def test_graph_identifier_as_string():
    g = Graph(identifier="xxx")
    assert type(g.identifier) is URIRef  # rdflib.term.URIRef('xxx')
    assert issubclass(type(g.identifier), Node)
    assert issubclass(type(g.identifier), IdentifiedNode)


def test_graph_identifier_as_literal():
    g = Graph(identifier=Literal("xxx"))
    assert type(g.identifier) is Literal  # rdflib.term.Literal('xxx')
    assert issubclass(type(g.identifier), Node)
    assert not issubclass(type(g.identifier), IdentifiedNode)


def test_graph_identifier_as_bnode():
    g = Graph(identifier=BNode())
    assert (
        type(g.identifier) is BNode
    )  # rdflib.term.BNode('Ndc8ac01941254b299a66c31a5b49cdd3')
    assert issubclass(type(g.identifier), Node)
    assert issubclass(type(g.identifier), IdentifiedNode)


def test_graph_identifier_as_namespace():
    g = Graph(identifier=(tarek, likes, pizza))
    assert (
        type(g.identifier) is URIRef
    )  # rdflib.term.URIRef("(rdflib.term.URIRef('urn:example:tarek'),
    #                      rdflib.term.URIRef('urn:example:likes'),
    #                      rdflib.term.URIRef('urn:example:pizza'))")
    assert issubclass(type(g.identifier), Node)
    assert issubclass(type(g.identifier), IdentifiedNode)


def test_graph_identifier_as_graph():
    g = Graph()
    g = Graph(identifier=g)
    assert (
        type(g.identifier) is BNode
    )  # rdflib.term.BNode('N666b78c69a3d4544a079ab0919a84dda')
    assert issubclass(type(g.identifier), Node)
    assert issubclass(type(g.identifier), IdentifiedNode)


def test_graph_identifier_as_genid():
    g = Graph()
    g = Graph(identifier=RDFLibGenid("xxx"))
    assert type(g.identifier) is RDFLibGenid  # RDFLibGenid('xxx')
    assert issubclass(type(g.identifier), Node)
    assert issubclass(type(g.identifier), IdentifiedNode)


def test_graph_identifier_as_identifiednode():
    g = Graph()
    g = Graph(identifier=IdentifiedNode("xxx"))
    assert type(g.identifier) is IdentifiedNode  # 'xxx'
    assert issubclass(type(g.identifier), Node)
    assert issubclass(type(g.identifier), IdentifiedNode)


def test_graph_identifier_as_variable():
    g = Graph()
    g = Graph(identifier=Variable("x"))
    assert type(g.identifier) is Variable  # rdflib.term.Variable('x')
    assert issubclass(type(g.identifier), Node)
    assert not issubclass(type(g.identifier), IdentifiedNode)
