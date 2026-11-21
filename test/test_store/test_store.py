from rdflib import Dataset, Graph, URIRef
from rdflib.namespace import NamespaceManager
from rdflib.store import NodePickler, Store


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
