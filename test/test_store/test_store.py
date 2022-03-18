from rdflib import Graph
from rdflib.store import NodePickler, Store
from rdflib.namespace import NamespaceManager


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
    The ``node_pickler`` property of a `rdflib.store.Store` works correctly.
    """
    store = Store()
    assert isinstance(store.node_pickler, NodePickler)
    # Tested twice as the property is a singleton and will do something
    # different on the first invocation and second.
    assert isinstance(store.node_pickler, NodePickler)
