import unittest
from rdflib.graph import Graph, BatchAddGraph
from rdflib.term import URIRef


class TestBatchAddGraph(unittest.TestCase):
    def test_batchsize_zero(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batchsize=0)

    def test_batchsize_none(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batchsize=None)

    def test_batchsize_negative(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batchsize=-12)

    def test_exit_submits_partial_batch(self):
        trip = (URIRef('a'), URIRef('b'), URIRef('c'))
        g = Graph()
        with BatchAddGraph(g) as cut:
            cut.add(trip)
        self.assertIn(trip, g)
