import pytest

from rdflib import OWL, Graph, Namespace
from rdflib.extras.infixowl import BooleanClass, Class, Individual

EXNS = Namespace("http://example.org/vocab/")


@pytest.fixture(scope="function")
def graph():
    g = Graph(identifier=EXNS.context0)
    g.bind("ex", EXNS)
    Individual.factoryGraph = g

    yield g

    del g


@pytest.mark.xfail(reason="assert len(props) == 1, repr(props), so AssertionError: []")
def test_booleanclass_operator_as_none(graph):

    fire = Class(EXNS.Fire)
    water = Class(EXNS.Water)

    id = EXNS.randoboolclass

    BooleanClass(identifier=id, operator=None, members=[fire, water], graph=graph)


@pytest.mark.xfail(reason="This is a previous boolean class description!'(  )")
def test_booleanclass_operator_as_none_with_intersection(graph):

    fire = Class(EXNS.Fire)
    water = Class(EXNS.Water)

    id = EXNS.randoboolclass

    graph.add((id, OWL.intersectionOf, EXNS.SomeClass))

    BooleanClass(identifier=id, operator=None, members=[fire, water], graph=graph)


def test_booleanclass_default_and_operator(graph):

    fire = Class(EXNS.Fire)
    water = Class(EXNS.Water)

    c = BooleanClass(identifier=EXNS.randoboolclass, members=[fire, water])

    assert c is not None

    assert str(c) == "( ex:Fire AND ex:Water )"


def test_booleanclass_with_or_operator(graph):

    fire = Class(EXNS.Fire)
    water = Class(EXNS.Water)

    c = BooleanClass(
        identifier=EXNS.randoboolclass, operator=OWL.unionOf, members=[fire, water]
    )

    assert c is not None

    assert str(c) == "( ex:Fire OR ex:Water )"


@pytest.mark.xfail(
    reason="BooleanClass.getIntersections() - TypeError: 'Callable' object is not callable"
)
def test_getintersections(graph):

    _ = BooleanClass.getIntersections()


@pytest.mark.xfail(
    reason="BooleanClass.getUnions() - TypeError: 'Callable' object is not callable"
)
def test_getunions(graph):

    _ = BooleanClass.getUnions()


def test_booleanclass_copy(graph):

    fire = Class(EXNS.Fire)
    water = Class(EXNS.Water)

    c = BooleanClass(identifier=EXNS.randoboolclass, members=[fire, water])

    d = c.copy()

    assert d is not None

    assert str(d) == "( ex:Fire AND ex:Water )"


def test_booleanclass_serialize(graph):

    fire = Class(EXNS.Fire)
    water = Class(EXNS.Water)

    c = BooleanClass(identifier=EXNS.randoboolclass, members=[fire, water])

    g1 = Graph()
    g1.bind("ex", EXNS, override=False)

    assert len(g1) == 0

    c.serialize(g1)

    assert len(g1) > 0

    assert g1.serialize(format="ttl") == (
        "@prefix ex: <http://example.org/vocab/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        "\n"
        "ex:randoboolclass a owl:Class ;\n"
        "    owl:intersectionOf ( ex:Fire ex:Water ) .\n"
        "\n"
        "ex:Fire a owl:Class .\n"
        "\n"
        "ex:Water a owl:Class .\n"
        "\n"
    )
