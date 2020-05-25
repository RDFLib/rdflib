import unittest
from rdflib.graph import Graph, BatchAddGraph
from rdflib.term import URIRef


class TestBatchAddGraph(unittest.TestCase):
    def test_batch_size_zero_denied(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batch_size=0)

    def test_batch_size_none_denied(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batch_size=None)

    def test_batch_size_one_denied(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batch_size=1)

    def test_batch_size_negative_denied(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batch_size=-12)

    def test_exit_submits_partial_batch(self):
        trip = (URIRef("a"), URIRef("b"), URIRef("c"))
        g = Graph()
        with BatchAddGraph(g, batch_size=10) as cut:
            cut.add(trip)
        self.assertIn(trip, g)

    def test_add_more_than_batch_size(self):
        trips = [(URIRef("a"), URIRef("b%d" % i), URIRef("c%d" % i)) for i in range(12)]
        g = Graph()
        with BatchAddGraph(g, batch_size=10) as cut:
            for trip in trips:
                cut.add(trip)
        self.assertEqual(12, len(g))

    def test_add_quad_for_non_conjunctive_empty(self):
        """
        Graph drops quads that don't match our graph. Make sure we do the same
        """
        g = Graph(identifier="http://example.org/g")
        badg = Graph(identifier="http://example.org/badness")
        with BatchAddGraph(g) as cut:
            cut.add((URIRef("a"), URIRef("b"), URIRef("c"), badg))
        self.assertEqual(0, len(g))

    def test_add_quad_for_non_conjunctive_pass_on_context_matches(self):
        g = Graph()
        with BatchAddGraph(g) as cut:
            cut.add((URIRef("a"), URIRef("b"), URIRef("c"), g))
        self.assertEqual(1, len(g))

    def test_no_addN_on_exception(self):
        """
        Even if we've added triples so far, it may be that attempting to add the last
        batch is the cause of our exception, so we don't want to attempt again
        """
        g = Graph()
        trips = [(URIRef("a"), URIRef("b%d" % i), URIRef("c%d" % i)) for i in range(12)]

        try:
            with BatchAddGraph(g, batch_size=10) as cut:
                for i, trip in enumerate(trips):
                    cut.add(trip)
                    if i == 11:
                        raise Exception("myexc")
        except Exception as e:
            if str(e) != "myexc":
                pass
        self.assertEqual(10, len(g))

    def test_addN_batching_addN(self):
        class MockGraph(object):
            def __init__(self):
                self.counts = []

            def addN(self, quads):
                self.counts.append(sum(1 for _ in quads))

        g = MockGraph()
        quads = [
            (URIRef("a"), URIRef("b%d" % i), URIRef("c%d" % i), g) for i in range(12)
        ]

        with BatchAddGraph(g, batch_size=10, batch_addn=True) as cut:
            cut.addN(quads)
        self.assertEqual(g.counts, [10, 2])
