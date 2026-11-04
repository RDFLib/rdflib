"""Blank node labels are scoped to the JSON-LD document that uses them."""

from rdflib import Graph, Literal, URIRef
from rdflib.term import BNode

NAME = URIRef("http://example.org/name")
KNOWS = URIRef("http://example.org/knows")


def test_same_label_in_two_documents_gives_two_nodes():
    graph = Graph()
    graph.parse(
        data='{"@id": "_:b0", "http://example.org/name": "a"}', format="json-ld"
    )
    graph.parse(
        data='{"@id": "_:b0", "http://example.org/name": "b"}', format="json-ld"
    )

    subjects = set(graph.subjects(NAME))

    assert len(subjects) == 2
    assert all(isinstance(subject, BNode) for subject in subjects)
    assert {graph.value(subject, NAME) for subject in subjects} == {
        Literal("a"),
        Literal("b"),
    }


def test_same_label_within_a_document_stays_one_node():
    graph = Graph().parse(
        data="""[
            {"@id": "_:b0", "http://example.org/name": "a"},
            {"@id": "_:b1", "http://example.org/knows": {"@id": "_:b0"}}
        ]""",
        format="json-ld",
    )

    assert next(graph.subjects(NAME, Literal("a"))) == next(graph.objects(None, KNOWS))
