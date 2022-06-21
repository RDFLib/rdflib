import pytest

from rdflib import OWL, BNode, Graph, Namespace, URIRef
from rdflib.extras.infixowl import (
    BooleanClass,
    Class,
    ComponentTerms,
    Individual,
    Property,
    some,
)

EXNS = Namespace("http://example.org/vocab/")
PZNS = Namespace(
    "http://www.co-ode.org/ontologies/pizza/2005/10/18/classified/pizza.owl#"
)


@pytest.fixture(scope="function")
def graph():
    g = Graph(identifier=EXNS.context0)
    g.bind("ex", EXNS)
    Individual.factoryGraph = g

    yield g

    del g


def test_componentterms_restriction():

    name = EXNS.Man
    assert isinstance(name, URIRef)

    r = (
        (Property(EXNS.someProp, baseType=OWL.DatatypeProperty))
        @ some
        @ (Class(EXNS.Foo))
    )

    r.value = BNode("foo")

    ct = ComponentTerms(r)
    assert str(list(ct)) in ["[Class: ns1:Foo ]", "[Class: ex:Foo ]"]


def test_componentterms_booleanclass(graph):

    fire = Class(EXNS.Fire)
    water = Class(EXNS.Water)

    id = EXNS.randoboolclass

    bc = BooleanClass(identifier=id, members=[fire, water], graph=graph)

    ct = ComponentTerms(bc)

    assert str(list(ct)) == "[Class: ex:Fire , Class: ex:Water ]"


def test_componentterms_booleanclass_bnodeid(graph):

    fire = Class(EXNS.Fire)
    water = Class(EXNS.Water)

    id = BNode("randoboolclass")

    bc = BooleanClass(identifier=id, members=[fire, water], graph=graph)

    ct = ComponentTerms(bc)

    assert str(list(ct)) == "[Class: ex:Fire , Class: ex:Water ]"
