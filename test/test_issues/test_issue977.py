import pytest

from rdflib import RDFS, Graph, Literal, URIRef


@pytest.fixture(scope="function")
def graph() -> Graph:
    graph = Graph()
    # Bind prefixes.
    graph.bind("isbn", "urn:isbn:")
    graph.bind("webn", "http://w3c.org/example/isbn/")
    # Populate graph.
    graph.add((URIRef("urn:isbn:1503280780"), RDFS.label, Literal("Moby Dick")))
    graph.add(
        (
            URIRef("http://w3c.org/example/isbn/1503280780"),
            RDFS.label,
            Literal("Moby Dick"),
        )
    )
    return graph


def test_namespace_manager(graph: Graph):
    assert "isbn", "urn:isbn:" in tuple(graph.namespaces())
    assert "webn", "http://w3c.org/example/isbn/" in tuple(graph.namespaces())


def test_turtle_serialization(graph: Graph):
    serialization = graph.serialize(None, format="turtle")
    print(f"Test Issue 977, serialization output:\n---\n{serialization}---")
    # Test serialization.
    assert "@prefix webn:" in serialization, "Prefix webn not found in serialization!"
    assert "@prefix isbn:" in serialization, "Prefix isbn not found in serialization!"
