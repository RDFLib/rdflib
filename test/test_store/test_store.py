from __future__ import annotations

from collections.abc import Generator

from rdflib import Dataset, Graph, URIRef
from rdflib.graph import QuotedGraph, _ContextType, _TriplePatternType, _TripleType
from rdflib.namespace import NamespaceManager
from rdflib.plugins.stores.memory import Memory
from rdflib.store import NodePickler, Store


def test_quads_preserves_custom_triples_override() -> None:
    hidden_predicate = URIRef("urn:hidden")

    class FilteredMemory(Memory):
        def triples(
            self,
            triple_pattern: _TriplePatternType,
            context: _ContextType | None = None,
        ) -> Generator[
            tuple[_TripleType, Generator[_ContextType | None, None, None]], None, None
        ]:
            for triple, contexts in super().triples(triple_pattern, context):
                if triple[1] != hidden_predicate:
                    yield triple, contexts

    store = FilteredMemory()
    dataset = Dataset(store=store)
    named = dataset.graph(URIRef("urn:named"))
    triple = (URIRef("urn:s"), URIRef("urn:p"), URIRef("urn:o"))
    dataset.add(triple)
    named.add(triple)
    named.add((triple[0], hidden_predicate, triple[2]))
    named.add((URIRef("urn:other"), triple[1], triple[2]))

    assert set(store.quads((triple[0], None, None))) == {
        (*triple, dataset.default_graph),
        (*triple, named),
    }
    assert set(dataset.quads((triple[0], None, None))) == {
        (*triple, dataset.default_graph.identifier),
        (*triple, named.identifier),
    }


def test_quads_requested_context_does_not_leak_memberships() -> None:
    dataset = Dataset()
    first = dataset.graph(URIRef("urn:first"))
    second = dataset.graph(URIRef("urn:second"))
    triple = (URIRef("urn:s"), URIRef("urn:p"), URIRef("urn:o"))
    first.add(triple)
    second.add(triple)

    assert list(dataset.store.quads(triple, context=first)) == [(*triple, first)]
    assert list(dataset.store.quads(triple, second)) == [(*triple, second)]
    assert list(dataset.quads((*triple, first))) == [(*triple, first.identifier)]


def test_quads_preserves_quoted_graph_selection() -> None:
    store = Memory()
    asserted = Graph(store=store, identifier=URIRef("urn:asserted"))
    quoted = QuotedGraph(store=store, identifier=URIRef("urn:quoted"))
    triple = (URIRef("urn:s"), URIRef("urn:p"), URIRef("urn:o"))
    quoted_triple = (URIRef("urn:quoted-subject"), triple[1], triple[2])
    asserted.add(triple)
    quoted.add(quoted_triple)

    assert list(store.quads((None, None, None))) == [(*triple, asserted)]
    assert list(store.quads((None, None, None), context=quoted)) == [
        (*quoted_triple, quoted)
    ]


def test_quad_count_counts_graph_memberships() -> None:
    dataset = Dataset()
    triple = (URIRef("urn:s"), URIRef("urn:p"), URIRef("urn:o"))
    dataset.add(triple)
    dataset.graph(URIRef("urn:named")).add(triple)

    assert dataset.store.quad_count() == 2
    assert len(dataset.store) == 1


def test_quad_count_context_unaware_store() -> None:
    graph = Graph(store="SimpleMemory")
    assert graph.store.quad_count() == 0
    graph.add((URIRef("urn:s"), URIRef("urn:p"), URIRef("urn:o")))

    assert graph.store.quad_count() == 1
    assert len(graph) == 1


def test_namespaces() -> None:
    """
    This tests that Store.namespaces is an empty generator.
    """
    store = Store()
    assert list(store.namespaces()) == []


def test_namespaces_via_manager() -> None:
    """
    This tests that NamespaceManager.namespaces works correctly with an
    abstract Store.
    """
    namespace_manager = NamespaceManager(Graph(store=Store()))
    assert list(namespace_manager.namespaces()) == []


def test_propery_node_pickler() -> None:
    """
    The `node_pickler` property of a `rdflib.store.Store` works correctly.
    """
    store = Store()
    assert isinstance(store.node_pickler, NodePickler)
    # Tested twice as the property is a singleton and will do something
    # different on the first invocation and second.
    assert isinstance(store.node_pickler, NodePickler)
