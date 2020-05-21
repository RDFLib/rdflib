import unittest

from rdflib import Graph, URIRef


class TestIssue1055(unittest.TestCase):

    def test_issue_1055(self):
        exp_tuple1 = (URIRef('http://example.com/foo'), URIRef('http://example.com/p1'),
               URIRef('http://example.com/bar1'))
        exp_tuple2 = (URIRef('http://example.com/foo'), URIRef('http://example.com/p2'),
               URIRef('http://example.com/bar2'))

        g = Graph()
        g.add((URIRef('http://example.com/foo'), URIRef('http://example.com/p1'),
               URIRef('http://example.com/bar1')))
        g.add((URIRef('http://example.com/foo'), URIRef('http://example.com/p2'),
               URIRef('http://example.com/bar2')))
        g.add((URIRef('http://example.com/foo2'), URIRef('http://example.com/p3'),
               URIRef('http://example.com/bar3')))
        newGraph = g.subgraph((URIRef('http://example.com/foo'), None, None))
        triple_generator = newGraph.triples((URIRef('http://example.com/foo'), None, None))
        act_tuples = sorted([next(triple_generator), next(triple_generator)])
        self.assertEqual(exp_tuple1, act_tuples[0])
        self.assertEqual(exp_tuple2, act_tuples[1])


if __name__ == "__main__":
    unittest.main()
