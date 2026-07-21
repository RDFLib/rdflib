from __future__ import annotations

import math
import sys

from rdflib import Graph, Literal, URIRef, Variable
from rdflib.namespace import Namespace
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.processor import processUpdate
from rdflib.term import IdentifiedNode, Node


def triple_set(graph: Graph) -> set[tuple[Node, IdentifiedNode | Variable, Node]]:
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
