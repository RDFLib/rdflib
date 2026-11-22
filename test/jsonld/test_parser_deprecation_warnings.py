from __future__ import annotations

import warnings

from rdflib import Dataset, Graph, URIRef
from rdflib.plugins.stores.auditable import AuditableStore
from rdflib.plugins.stores.memory import Memory

CONJUNCTIVE_GRAPH_WARNING = r"ConjunctiveGraph is deprecated, use Dataset instead\."

SUBJECT = URIRef("http://example.org/subject")
PREDICATE = URIRef("http://example.org/predicate")
OBJECT = URIRef("http://example.org/object")
TRIPLE = (SUBJECT, PREDICATE, OBJECT)

SIMPLE_JSONLD = """
{
  "@context": {"ex": "http://example.org/"},
  "@id": "http://example.org/subject",
  "ex:predicate": {"@id": "http://example.org/object"}
}
"""

NAMED_GRAPH_ID = URIRef("http://example.org/named-graph")
NAMED_GRAPH_JSONLD = """
{
  "@context": {"ex": "http://example.org/"},
  "@id": "http://example.org/named-graph",
  "@graph": {
    "@id": "http://example.org/subject",
    "ex:predicate": {"@id": "http://example.org/object"}
  }
}
"""


def parse_without_internal_conjunctive_graph_warning(graph: Graph, data: str) -> None:
    """Fail if JSON-LD parsing constructs the deprecated internal adapter."""
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "error",
            message=CONJUNCTIVE_GRAPH_WARNING,
            category=DeprecationWarning,
        )
        graph.parse(data=data, format="json-ld")


def test_graph_jsonld_parse_does_not_warn_about_conjunctive_graph() -> None:
    """Graph.parse must not construct the deprecated ConjunctiveGraph adapter."""
    graph = Graph()

    parse_without_internal_conjunctive_graph_warning(graph, SIMPLE_JSONLD)

    assert TRIPLE in graph


def test_dataset_jsonld_parse_does_not_warn_about_conjunctive_graph() -> None:
    """Direct Dataset parsing must use its default graph without the legacy warning."""
    dataset = Dataset()

    parse_without_internal_conjunctive_graph_warning(dataset, SIMPLE_JSONLD)

    assert TRIPLE in dataset.default_graph


def test_graph_jsonld_parse_preserves_target_context() -> None:
    """The context adapter must keep the original Graph identifier as its target."""
    identifier = URIRef("urn:test:target")
    graph = Graph(identifier=identifier)

    parse_without_internal_conjunctive_graph_warning(graph, SIMPLE_JSONLD)

    assert TRIPLE in graph
    assert TRIPLE not in Graph(
        store=graph.store,
        identifier=URIRef("urn:test:other"),
    )


def test_graph_jsonld_parse_preserves_named_graphs() -> None:
    """JSON-LD @graph data must still be routed to its declared named graph."""
    sink = Graph(identifier=URIRef("urn:test:target"))

    parse_without_internal_conjunctive_graph_warning(sink, NAMED_GRAPH_JSONLD)

    named_graph = Graph(store=sink.store, identifier=NAMED_GRAPH_ID)
    assert TRIPLE in named_graph
    assert TRIPLE not in sink


def test_graph_jsonld_parse_supports_context_aware_non_graph_aware_store() -> None:
    """Preserve stores supported by ConjunctiveGraph but rejected by Dataset."""
    store = AuditableStore(Memory())
    assert store.context_aware
    assert not store.graph_aware
    graph = Graph(store=store, identifier=URIRef("urn:test:auditable"))

    parse_without_internal_conjunctive_graph_warning(graph, SIMPLE_JSONLD)

    assert TRIPLE in graph
