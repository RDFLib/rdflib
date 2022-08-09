from test.data import context0, pizza

import pytest

from rdflib import OWL, RDFS, BNode, Graph, Literal, Namespace, URIRef
from rdflib.extras.infixowl import Class, Individual

EXNS = Namespace("http://example.org/vocab/")


@pytest.fixture(scope="function")
def graph():
    g = Graph(identifier=EXNS.context0)
    g.bind("ex", EXNS)
    Individual.factoryGraph = g

    yield g

    del g


def test_infixowl_individual_type(graph):

    b = Individual(OWL.Restriction, graph)
    b.type = RDFS.Resource
    assert len(list(b.type)) == 1

    del b.type
    assert len(list(b.type)) == 0


def test_infixowl_individual_label(graph):

    b = Individual(OWL.Restriction, graph)
    b.label = Literal("boo")

    assert len(list(b.label)) == 3

    del b.label
    assert hasattr(b, "label") is False


def test_individual_type_settergetter(graph):

    b = Individual(OWL.Restriction, graph)

    b.type = OWL.Restriction

    b.type = None

    b.type = OWL.Class

    b.type = [OWL.Class, OWL.Restriction]

    assert graph.serialize(format="ttl") == (
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "\n"
        "owl:Restriction a owl:Class,\n"
        "        owl:Restriction .\n"
        "\n"
    )

    b.replace(Class(identifier=context0))

    assert graph.serialize(format="ttl") == (
        "@prefix ns1: <urn:example:> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "\n"
        "ns1:context-0 a owl:Class .\n"
        "\n"
    )


def test_individual_identity__settergetter(graph):

    b = Individual(OWL.Restriction, graph)

    assert b.identifier == URIRef("http://www.w3.org/2002/07/owl#Restriction")

    b.identifier = URIRef("http://www.w3.org/2002/07/owl#Restriction")

    b.identifier = pizza

    assert b.identifier == pizza

    b.identifier = URIRef("http://www.w3.org/2002/07/owl#Restriction")

    bnodeid = BNode("harry")

    b.identifier = bnodeid

    assert b.identifier == bnodeid


def test_individual_sameas__settergetter(graph):

    b = Individual(OWL.Restriction, graph)

    assert list(b.sameAs) == []

    b.sameAs = pizza

    assert list(b.sameAs) == [pizza]

    bnodeid = BNode("harry")

    b.sameAs = [pizza, bnodeid]

    assert list(b.sameAs) == [pizza, bnodeid]
