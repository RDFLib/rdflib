import unittest
from rdflib import Graph
from rdflib.store import Store
from rdflib.namespace import NamespaceManager


class TestAbstractStore(unittest.TestCase):
    def test_namespaces(self):
        """
        This tests that Store.namespaces is an empty generator.
        """
        store = Store()
        self.assertEqual(list(store.namespaces()), [])

    def test_namespaces_via_manager(self):
        """
        This tests that NamespaceManager.namespaces works correctly with an
        abstract Store.
        """
        namespace_manager = NamespaceManager(Graph(store=Store()))
        self.assertEqual(list(namespace_manager.namespaces()), [])


if __name__ == "__main__":
    unittest.main()
