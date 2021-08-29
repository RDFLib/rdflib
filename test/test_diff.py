from typing import Set, Tuple
import unittest
from unittest.case import expectedFailure
import rdflib
from rdflib.compare import graph_diff
from rdflib.namespace import RDF, FOAF
from rdflib import Graph
from rdflib.term import Node, BNode, Literal
from .testutils import GraphHelper

"""Test for graph_diff - much more extensive testing
would certainly be possible"""

_TripleT = Tuple[Node, Node, Node]
_TripleSetT = Set[_TripleT]


class TestDiff(unittest.TestCase):
    """Unicode literals for graph_diff test
    (issue 151)"""

    def testA(self):
        """with bnode"""
        g = rdflib.Graph()
        g.add((rdflib.BNode(), rdflib.URIRef("urn:p"), rdflib.Literal("\xe9")))

        diff = graph_diff(g, g)

    def testB(self):
        """Curiously, this one passes, even before the fix in issue 151"""

        g = rdflib.Graph()
        g.add((rdflib.URIRef("urn:a"), rdflib.URIRef("urn:p"), rdflib.Literal("\xe9")))

        diff = graph_diff(g, g)

    @expectedFailure
    def test_subsets(self) -> None:
        """
        This test verifies that `graph_diff` returns the correct values
        for two graphs, `g0` and `g1` where the triples in `g0` is a
        subset of the triples in `g1`.

        The expectation is that graph_diff reports that there are no
        triples only in `g0`, and that there are triples that occur in both
        `g0` and `g1`, and that there are triples only in `g1`.
        """
        g0_ts: _TripleSetT = set()
        bnode = BNode()
        g0_ts.update(
            {
                (bnode, FOAF.name, Literal("Golan Trevize")),
                (bnode, RDF.type, FOAF.Person),
            }
        )
        g0 = Graph()
        g0 += g0_ts

        g1_ts: _TripleSetT = set()
        bnode = BNode()
        g1_ts.update(
            {
                *g0_ts,
                (bnode, FOAF.name, Literal("Janov Pelorat")),
                (bnode, RDF.type, FOAF.Person),
            }
        )
        g1 = Graph()
        g1 += g1_ts

        result = graph_diff(g0, g1)
        in_both, in_first, in_second = GraphHelper.triple_sets(result)
        self.assertFalse(in_first)
        self.assertTrue(in_second)
        self.assertTrue(in_both)


if __name__ == "__main__":
    unittest.main()
