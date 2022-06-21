import pytest

from rdflib import OWL, RDF, RDFS, Graph, Namespace
from rdflib.extras.infixowl import ClassNamespaceFactory, Individual, Property, some

EXNS = Namespace("http://example.org/vocab/")

EXCL = ClassNamespaceFactory(EXNS)


@pytest.fixture(scope="function")
def graph():
    g = Graph(identifier=EXNS.context0)
    g.bind("ex", EXNS)
    Individual.factoryGraph = g

    yield g

    del g


def test_logic_structuring(graph):

    isPartOf = Property(EXNS.isPartOf)  # noqa: N806
    graph.add((isPartOf.identifier, RDF.type, OWL.TransitiveProperty))

    hasLocation = Property(EXNS.hasLocation, subPropertyOf=[isPartOf])  # noqa: N806
    graph.add((hasLocation.identifier, RDFS.subPropertyOf, isPartOf.identifier))

    leg = EXCL.Leg
    knee = EXCL.Knee
    joint = EXCL.Joint
    kneeJoint = EXCL.KneeJoint  # noqa: N806
    legStructure = EXCL.LegStructure  # noqa: N806

    kneeJoint.equivalentClass = [joint & (isPartOf @ some @ knee)]

    structure = EXCL.Structure

    legStructure.equivalentClass = [structure & (isPartOf @ some @ leg)]

    structure += leg
    structure += joint

    locatedInLeg = hasLocation @ some @ leg  # noqa: N806
    locatedInLeg += knee

    assert graph.serialize(format="ttl") == (
        "@prefix ex: <http://example.org/vocab/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "\n"
        "ex:KneeJoint a owl:Class ;\n"
        "    owl:equivalentClass [ a owl:Class ;\n"
        "            owl:intersectionOf ( ex:Joint [ a owl:Restriction ;\n"
        "                        owl:onProperty ex:isPartOf ;\n"
        "                        owl:someValuesFrom ex:Knee ] ) ] .\n"
        "\n"
        "ex:LegStructure a owl:Class ;\n"
        "    owl:equivalentClass [ a owl:Class ;\n"
        "            owl:intersectionOf ( ex:Structure [ a owl:Restriction ;\n"
        "                        owl:onProperty ex:isPartOf ;\n"
        "                        owl:someValuesFrom ex:Leg ] ) ] .\n"
        "\n"
        "ex:Joint a owl:Class ;\n"
        "    rdfs:subClassOf ex:Structure .\n"
        "\n"
        "ex:Knee a owl:Class ;\n"
        "    rdfs:subClassOf [ a owl:Restriction ;\n"
        "            owl:onProperty ex:hasLocation ;\n"
        "            owl:someValuesFrom ex:Leg ] .\n"
        "\n"
        "ex:hasLocation a owl:ObjectProperty ;\n"
        "    rdfs:subPropertyOf ex:isPartOf .\n"
        "\n"
        "ex:Leg a owl:Class ;\n"
        "    rdfs:subClassOf ex:Structure .\n"
        "\n"
        "ex:Structure a owl:Class .\n"
        "\n"
        "ex:isPartOf a owl:ObjectProperty,\n"
        "        owl:TransitiveProperty .\n"
        "\n"
    )
