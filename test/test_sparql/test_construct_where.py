import pytest

from rdflib import Graph, Literal, URIRef

DATA = """
@prefix : <urn:ex:> .
:a :p 1 .
:b :p 2 .
:c :p 3 .
"""


@pytest.mark.parametrize(
    ("modifiers", "expected_count"),
    [
        ("", 3),
        ("LIMIT 1", 1),
        ("OFFSET 1", 2),
        ("ORDER BY ?s", 3),
        ("ORDER BY ?s LIMIT 2 OFFSET 1", 2),
        ("VALUES ?s { <urn:ex:a> <urn:ex:b> }", 2),
        ("LIMIT 1 VALUES ?s { <urn:ex:a> <urn:ex:b> }", 1),
    ],
)
def test_construct_where_with_solution_modifiers(
    modifiers: str, expected_count: int
) -> None:
    """
    The template of a short form CONSTRUCT WHERE query is its basic graph
    pattern, also when solution modifiers apply.
    This is issue https://github.com/RDFLib/rdflib/issues/1785
    """
    graph = Graph().parse(data=DATA, format="turtle")

    result = graph.query(f"CONSTRUCT WHERE {{ ?s ?p ?o }} {modifiers}")

    assert result.graph is not None
    assert len(result.graph) == expected_count
    assert set(result.graph) <= set(graph)


def test_construct_where_with_order_by_and_limit() -> None:
    graph = Graph().parse(data=DATA, format="turtle")

    result = graph.query("CONSTRUCT WHERE { ?s ?p ?o } ORDER BY DESC(?s) LIMIT 1")

    assert result.graph is not None
    assert set(result.graph) == {
        (URIRef("urn:ex:c"), URIRef("urn:ex:p"), Literal(3)),
    }


def test_construct_where_template_has_every_triple_of_the_pattern() -> None:
    graph = Graph().parse(
        data=DATA + "<urn:ex:a> <urn:ex:q> 10 .\n<urn:ex:b> <urn:ex:q> 20 .",
        format="turtle",
    )

    result = graph.query(
        "CONSTRUCT WHERE { ?s <urn:ex:p> ?o . ?s <urn:ex:q> ?x } ORDER BY ?s LIMIT 1"
    )

    assert result.graph is not None
    assert set(result.graph) == {
        (URIRef("urn:ex:a"), URIRef("urn:ex:p"), Literal(1)),
        (URIRef("urn:ex:a"), URIRef("urn:ex:q"), Literal(10)),
    }


@pytest.mark.parametrize(
    "where",
    [
        "{ ?s ?p ?o }",
        "{ ?s ?p ?o } LIMIT 1",
        "{ ?s ?p ?o OPTIONAL { ?o ?q ?x } }",
    ],
)
def test_construct_with_empty_template(where: str) -> None:
    """
    An empty template constructs an empty graph, whatever the WHERE clause.
    """
    graph = Graph().parse(data=DATA, format="turtle")

    result = graph.query(f"CONSTRUCT {{ }} WHERE {where}")

    assert result.graph is not None
    assert len(result.graph) == 0
