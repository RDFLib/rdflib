import pytest

from rdflib import OWL, RDF, RDFS, Graph, Literal, Namespace
from rdflib.extras.infixowl import Class, EnumeratedClass, Individual

EXNS = Namespace("http://example.org/vocab/")


@pytest.fixture(scope="function")
def graph():
    g = Graph(identifier=EXNS.context0)
    g.bind("ex", EXNS)
    Individual.factoryGraph = g

    yield g

    del g


def test_enumerated_class(graph):
    """
    Members of enumerated datatype are literals ("November"^^xsd:string etc.),
    Members of enumerated class are individuals (some_prefix:November etc.)
    """

    from rdflib.collection import Collection
    from rdflib.util import first

    my_class = EXNS.my_class
    graph.add((my_class, RDF.type, OWL.Class))
    graph.add((my_class, RDFS.subClassOf, OWL.Thing))
    graph.add((my_class, RDF.value, Literal("my_class")))

    my_subclass = EXNS.my_subclass
    graph.add((my_subclass, RDF.type, OWL.Class))
    graph.add((my_subclass, RDF.value, Literal("my_subclass")))
    graph.add((my_subclass, RDFS.subClassOf, my_class))

    my_list = EnumeratedClass(
        EXNS.my_list, members=[EXNS.listitem1, EXNS.listitem2, EXNS.listitem3]
    )

    assert my_list.isPrimitive() is False

    col = Collection(
        graph, first(graph.objects(predicate=OWL.oneOf, subject=my_list.identifier))
    )

    lst = [graph.qname(item) for item in col]

    assert lst == ["ex:listitem1", "ex:listitem2", "ex:listitem3"]


def test_enumerated_class_serialize(graph):

    sg = Graph()

    contlist = [Class(EXNS.Africa, graph=graph), Class(EXNS.NorthAmerica, graph=graph)]
    ec = EnumeratedClass(members=contlist, graph=graph)

    ec.serialize(sg)

    assert len(sg) == 8

    assert sg.serialize(format="ttl") == (
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        "\n"
        "<http://example.org/vocab/Africa> a owl:Class .\n"
        "\n"
        "<http://example.org/vocab/NorthAmerica> a owl:Class .\n"
        "\n"
        "[] a owl:Class ;\n"
        "    owl:oneOf ( <http://example.org/vocab/Africa> "
        "<http://example.org/vocab/NorthAmerica> ) .\n"
        "\n"
    )
