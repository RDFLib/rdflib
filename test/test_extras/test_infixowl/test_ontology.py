import pytest

from rdflib import OWL, RDF, XSD, Graph, Literal, Namespace, URIRef
from rdflib.extras.infixowl import Ontology

EXNS = Namespace("http://example.org/vocab/")


@pytest.fixture(scope="function")
def graph():
    g = Graph(identifier=EXNS.context0)
    g.bind("ex", EXNS)

    yield g

    del g


def test_ontology_instantiation(graph):

    name = Literal("TestOntology", lang="en")

    pizza = URIRef("http://example.org/ontologies/pizza.owl")

    wine = URIRef("http://example.org/ontologies/wine.owl")

    c = Ontology(
        identifier=name,
        imports=[pizza, wine],
        comment=Literal("Test Ontology"),
        graph=graph,
    )

    assert c is not None

    # Not yet
    with pytest.raises(AttributeError):
        c.set_version(Literal("1.0", datatype=XSD.string))

    c.setVersion(Literal("1.0", datatype=XSD.string))

    assert list(c.imports) == [pizza, wine]

    with pytest.raises(
        TypeError, match="'generator' object does not support item deletion"
    ):
        del c.imports[wine]
        assert list(c.imports) == [pizza]

    c.imports = None

    assert list(c.imports) == [pizza, wine]

    assert graph.serialize(format="ttl") == (
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "\n"
        '"TestOntology"@en a owl:Ontology ;\n'
        '    rdfs:comment "Test Ontology" ;\n'
        "    owl:imports <http://example.org/ontologies/pizza.owl>,\n"
        "        <http://example.org/ontologies/wine.owl> ;\n"
        '    owl:versionInfo "1.0"^^xsd:string .\n'
        "\n"
    )


def test_ontology_instantiation_exists_in_graph(graph):

    name = Literal("TestOntology", lang="en")

    graph.add((URIRef(name), RDF.type, OWL.Ontology))

    c = Ontology(
        identifier=name,
        graph=graph,
    )

    assert c is not None

    assert graph.serialize(format="ttl") == (
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "\n"
        "<TestOntology> a owl:Ontology .\n"
        "\n"
        '"TestOntology"@en a owl:Ontology .\n'
        "\n"
    )
