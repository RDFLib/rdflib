import unittest
from unittest.mock import Mock
from rdflib.graph import Graph, BatchAddGraph
from rdflib.term import URIRef


class TestBatchAddGraph(unittest.TestCase):
    def test_batchsize_zero_denied(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batchsize=0)

    def test_batchsize_none_denied(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batchsize=None)

    def test_batchsize_one_denied(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batchsize=1)

    def test_batchsize_negative_denied(self):
        with self.assertRaises(ValueError):
            BatchAddGraph(Graph(), batchsize=-12)

    def test_exit_submits_partial_batch(self):
        trip = (URIRef('a'), URIRef('b'), URIRef('c'))
        g = Graph()
        with BatchAddGraph(g, batchsize=10) as cut:
            cut.add(trip)
        self.assertIn(trip, g)

    def test_add_more_than_batchsize(self):
        trips = [(URIRef('a'), URIRef('b%d' % i), URIRef('c%d' % i))
                for i in range(12)]
        g = Graph()
        with BatchAddGraph(g, batchsize=10) as cut:
            for trip in trips:
                cut.add(trip)
        self.assertEqual(12, len(g))

    def test_add_quad_for_non_conjunctive_empty(self):
        '''
        Graph drops quads that don't match our graph. Make sure we do the same
        '''
        g = Graph(identifier='http://example.org/g')
        badg = Graph(identifier='http://example.org/badness')
        with BatchAddGraph(g) as cut:
            cut.add((URIRef('a'), URIRef('b'), URIRef('c'), badg))
        self.assertEqual(0, len(g))

    def test_add_quad_for_non_conjunctive_pass_on_context_matches(self):
        g = Graph()
        badg = Graph(identifier='http://example.org/badness')
        with BatchAddGraph(g) as cut:
            cut.add((URIRef('a'), URIRef('b'), URIRef('c'), g))
        self.assertEqual(1, len(g))

    def test_no_addN_on_exception(self):
        '''
        Even if we've added triples so far, it may be that attempting to add the last
        batch is the cause of our exception, so we don't want to attempt again
        '''
        g = Graph()
        trips = [(URIRef('a'), URIRef('b%d' % i), URIRef('c%d' % i))
                for i in range(12)]

        badg = Graph(identifier='http://example.org/badness')
        try:
            with BatchAddGraph(g, batchsize=10) as cut:
                for i, trip in enumerate(trips):
                    cut.add(trip)
                    if i == 11:
                        raise Exception('myexc')
        except Exception as e:
            if str(e) != 'myexc':
                pass
        self.assertEqual(10, len(g))
