import pytest

from rdflib import OWL, XSD, BNode, Graph, Literal, Namespace, URIRef
from rdflib.extras.infixowl import Class, Individual, Property, Restriction, some

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


def test_restriction_str_and_hash(graph):

    r1 = (
        (Property(EXNS.someProp, baseType=OWL.DatatypeProperty))
        @ some
        @ (Class(EXNS.Foo))
    )

    assert str(r1) == "( ex:someProp SOME ex:Foo )"

    sg = Graph()
    sg.bind("ex", EXNS)

    r1.serialize(sg)

    assert r1.isPrimitive() is False

    r1hashfirstrun = r1.__hash__()

    r1hashsecondrun = r1.__hash__()

    assert r1hashfirstrun == r1hashsecondrun

    assert list(Property(EXNS.someProp, baseType=None).type) == [
        URIRef("http://www.w3.org/2002/07/owl#DatatypeProperty")
    ]


def test_restriction_range(graph):

    r1 = Restriction(
        onProperty=EXNS.hasParent,
        graph=graph,
        allValuesFrom=EXNS.Human,
    )
    r2 = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        allValuesFrom=EXNS.Human,
    )

    assert r1.__eq__(r2) is False

    assert r1.__eq__(Class(EXNS.NoClass)) is False


def test_restriction_onproperty(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        allValuesFrom=EXNS.Human,
    )

    r.onProperty = None

    r.onProperty = EXNS.someproperty


def test_restriction_inputs_bnode(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        allValuesFrom=EXNS.Human,
        identifier=BNode("harry"),
    )

    assert str(repr(r)) == "( ex:hasChild ONLY ex:Human )"

    assert graph.serialize(format="ttl") == (
        "@prefix ex: <http://example.org/vocab/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "\n"
        "ex:Human a owl:Class .\n"
        "\n"
        "[] a owl:Restriction ;\n"
        "    owl:allValuesFrom ex:Human ;\n"
        "    owl:onProperty ex:hasChild .\n"
        "\n"
    )


def test_restriction_inputs_with_identifier(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        allValuesFrom=EXNS.Human,
        identifier=EXNS.randomrestriction,
    )

    assert str(repr(r)) == "( ex:hasChild ONLY ex:Human )"

    assert graph.serialize(format="ttl") == (
        "@prefix ex: <http://example.org/vocab/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "\n"
        "ex:randomrestriction a owl:Restriction ;\n"
        "    owl:allValuesFrom ex:Human ;\n"
        "    owl:onProperty ex:hasChild .\n"
        "\n"
        "ex:Human a owl:Class .\n"
        "\n"
    )


def test_restriction_allvalues(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        allValuesFrom=EXNS.Human,
    )

    av = r.allValuesFrom
    assert av == Class(EXNS.Human)

    r.allValuesFrom = None

    r.allValuesFrom = Class(EXNS.Human)

    r.allValuesFrom = Class(EXNS.Parent)

    del r.allValuesFrom

    assert r.allValuesFrom is None


def test_restriction_somevalues(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        someValuesFrom=EXNS.Parent,
    )

    assert isinstance(r, Restriction)

    assert r.someValuesFrom is not None

    assert str(r.someValuesFrom) == "Class: ex:Parent "

    # Does not need to be Class
    r.someValuesFrom = EXNS.Parent

    r.someValuesFrom = None

    r.someValuesFrom = Class(EXNS.Human)

    del r.someValuesFrom

    assert r.someValuesFrom is None


def test_restriction_hasvalue(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        value=EXNS.Parent,
    )

    assert str(r.hasValue) == "Class: ex:Parent "

    # Needs to be Class to match initialisation
    r.hasValue = Class(EXNS.Parent)

    r.hasValue = None

    r.hasValue = EXNS.Parent

    r.hasValue = EXNS.Human

    del r.hasValue

    assert r.hasValue is None


def test_restriction_cardinality(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        cardinality=OWL.cardinality,
    )

    assert str(r.cardinality) == "Class: owl:cardinality "

    r.cardinality = OWL.cardinality

    r.cardinality = None

    r.cardinality = EXNS.foo

    del r.cardinality

    assert r.cardinality is None


def test_restriction_cardinality_value(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        cardinality=Literal("0", datatype=XSD.nonNegativeInteger),
    )

    assert graph.serialize(format="ttl") == (
        "@prefix ex: <http://example.org/vocab/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "\n"
        "[] a owl:Restriction ;\n"
        '    owl:cardinality "0"^^xsd:nonNegativeInteger ;\n'
        "    owl:onProperty ex:hasChild .\n"
        "\n"
    )

    assert r.cardinality is not None

    assert str(r) == "( ex:hasChild EQUALS 0 )"

    assert str(r.cardinality) == "Some Class "


@pytest.mark.xfail(reason="_set_cardinality fails to handle Literal")
def test_restriction_cardinality_set_value(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        cardinality=OWL.cardinality,
    )

    assert graph.serialize(format="ttl") == (
        "@prefix ex: <http://example.org/vocab/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "\n"
        "[] a owl:Restriction ;\n"
        "    owl:cardinality owl:cardinality ;\n"
        "    owl:onProperty ex:hasChild .\n"
        "\n"
    )

    assert r.cardinality is not None

    assert str(r) == "( ex:hasChild EQUALS http://www.w3.org/2002/07/owl#cardinality )"

    assert str(r.cardinality) == "Class: owl:cardinality "

    r.cardinality = Literal("0", datatype=XSD.nonNegativeInteger)

    assert (
        str(r) == '( ex:hasChild EQUALS owl:cardinality "0"^^xsd:nonNegativeInteger )'
    )


def test_restriction_maxcardinality(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        maxCardinality=OWL.maxCardinality,
    )

    assert str(r.maxCardinality) == "Class: owl:maxCardinality "

    r.maxCardinality = OWL.maxCardinality

    r.maxCardinality = None

    r.maxCardinality = EXNS.foo

    del r.maxCardinality

    assert r.maxCardinality is None


def test_restriction_mincardinality(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        minCardinality=OWL.minCardinality,
    )

    assert str(r.minCardinality) == "Class: owl:minCardinality "

    r.minCardinality = OWL.minCardinality

    r.minCardinality = None

    r.minCardinality = EXNS.foo

    del r.minCardinality

    assert r.minCardinality is None


def test_restriction_kind(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        minCardinality=OWL.minCardinality,
    )
    assert r.restrictionKind() == "minCardinality"


def test_deleted_restriction_kind(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
        minCardinality=OWL.minCardinality,
    )

    del r.minCardinality
    assert r.minCardinality is None

    assert r.restrictionKind() is None


@pytest.mark.xfail(reason="assert len(validRestrProps) fails to handle None")
def test_omitted_restriction_kind(graph):

    r = Restriction(
        onProperty=EXNS.hasChild,
        graph=graph,
    )
    assert r is not None
