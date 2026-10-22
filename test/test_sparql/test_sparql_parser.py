from __future__ import annotations

import math
import sys
from decimal import Decimal

import pytest

from rdflib import Graph, Literal, URIRef, Variable
from rdflib.namespace import XSD, Namespace
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.processor import processUpdate
from rdflib.term import Node


def triple_set(graph: Graph) -> set[tuple[Node, Node, Node]]:
    return set(graph.triples((None, None, None)))


class TestSPARQLParser:
    def test_insert_recursionlimit(self) -> None:
        # These values are experimentally determined
        # to cause the RecursionError reported in
        # https://github.com/RDFLib/rdflib/issues/1336
        resource_count = math.ceil(sys.getrecursionlimit() / (33 - 3))
        self.do_insert(resource_count)

    def test_insert_large(self) -> None:
        self.do_insert(200)

    def do_insert(self, resource_count: int) -> None:
        EGV = Namespace("http://example.org/vocab#")  # noqa: N806
        EGI = Namespace("http://example.org/instance#")  # noqa: N806
        prop0, prop1, prop2 = EGV["prop0"], EGV["prop1"], EGV["prop2"]
        g0 = Graph()
        for index in range(resource_count):
            resource = EGI[f"resource{index}"]
            g0.add((resource, prop0, Literal(index)))
            g0.add((resource, prop1, Literal("example resource")))
            g0.add((resource, prop2, Literal(f"resource #{index}")))

        g0ntriples = g0.serialize(format="ntriples")
        g1 = Graph()

        assert triple_set(g0) != triple_set(g1)

        processUpdate(g1, f"INSERT DATA {{ {g0ntriples!s} }}")

        assert triple_set(g0) == triple_set(g1)

    def test_nested_service(self) -> None:
        query = """
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX bd: <http://www.bigdata.com/rdf#>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?item ?pic
        WHERE
        {
            SERVICE <https://query.wikidata.org/sparql> {
                ?item wdt:P31 wd:Q146 .
                ?item wdt:P18 ?pic
                SERVICE wikibase:label {
                    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
                }
            }
        }"""
        parsed_query = translateQuery(parseQuery(query))
        outer_service = parsed_query.algebra.p.p
        assert outer_service.name == "ServiceGraphPattern"
        assert outer_service.term == URIRef("https://query.wikidata.org/sparql")
        inner_parts = outer_service.graph.part
        inner_services = [p for p in inner_parts if p.name == "ServiceGraphPattern"]
        assert len(inner_services) == 1
        assert inner_services[0].term == URIRef("http://wikiba.se/ontology#label")

        # Each pattern keeps its own text, from its SERVICE keyword to its closing brace
        inner_start = query.index("SERVICE wikibase:label")
        inner_end = query.index("}", inner_start) + 1
        outer_start = query.index("SERVICE <https://query.wikidata.org/sparql>")
        outer_end = query.index("}", inner_end) + 1
        assert inner_services[0].service_string == query[inner_start:inner_end]
        assert outer_service.service_string == query[outer_start:outer_end]


# A raw TAB is allowed inside every SPARQL string literal form, see
# https://github.com/RDFLib/rdflib/issues/3586
RAW_TAB_STRING_LITERALS = [
    pytest.param("'a\tb'", id="STRING_LITERAL1"),
    pytest.param('"a\tb"', id="STRING_LITERAL2"),
    pytest.param("'''a\tb'''", id="STRING_LITERAL_LONG1"),
    pytest.param('"""a\tb"""', id="STRING_LITERAL_LONG2"),
]


@pytest.mark.parametrize("string_literal", RAW_TAB_STRING_LITERALS)
def test_query_raw_tab_in_string_literal(string_literal: str) -> None:
    subject = URIRef("http://example.org/s")
    graph = Graph()
    graph.add((subject, URIRef("http://example.org/p"), Literal("a\tb")))

    result = graph.query(f"SELECT ?s WHERE {{ ?s ?p {string_literal} }}")

    assert result.bindings == [{Variable("s"): subject}]


@pytest.mark.parametrize("string_literal", RAW_TAB_STRING_LITERALS)
def test_update_raw_tab_in_string_literal(string_literal: str) -> None:
    graph = Graph()

    graph.update(
        f"INSERT DATA {{ <http://example.org/s> <http://example.org/p> {string_literal} }}"
    )

    assert list(graph.objects()) == [Literal("a\tb")]


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        pytest.param(
            "SELECT ?x WHERE { VALUES ?x { -2.5 } }",
            Literal("-2.5", datatype=XSD.decimal),
            id="values",
        ),
        pytest.param(
            "SELECT ?x WHERE { ?x <urn:p> -2.5 }",
            URIRef("urn:s"),
            id="triple-object",
        ),
        pytest.param(
            "SELECT ?x WHERE { VALUES ?x { -1.234567890123456789012345678901234567890 } }",
            Literal("-1.234567890123456789012345678901234567890", datatype=XSD.decimal),
            id="values-40-digits",
        ),
        pytest.param(
            "SELECT ?x WHERE { VALUES ?x { -0.0 } }",
            Literal("-0.0", datatype=XSD.decimal),
            id="values-negative-zero",
        ),
    ],
)
def test_negative_decimal_literal(query: str, expected: Node) -> None:
    graph = Graph()
    graph.add((URIRef("urn:s"), URIRef("urn:p"), Literal(Decimal("-2.5"))))

    assert list(graph.query(query)) == [(expected,)]
