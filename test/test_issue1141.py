import unittest
from io import BytesIO

from rdflib import Graph
from rdflib.plugins.memory import IOMemory
from rdflib.plugins.stores.auditable import AuditableStore


class TestIssue1141(unittest.TestCase):
    """
    Tests is Turtle and TriG parsing works with a store with or without formula support
    """
    def test_issue_1141(self):
        file = b"@prefix : <http://example.com/> . :s :p :o ."

        for format in ("turtle", "trig"):
            # with formula
            graph = Graph()
            self.assertTrue(graph.store.formula_aware)
            graph.load(BytesIO(file), format=format)
            self.assertEqual(len(graph), 1)

            # without
            graph = Graph(store=AuditableStore(IOMemory()))
            self.assertFalse(graph.store.formula_aware)
            graph.load(BytesIO(file), format=format)
            self.assertEqual(len(graph), 1)
