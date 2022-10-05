from dataclasses import dataclass, field
from test.utils import (
    COLLAPSED_BNODE,
    BNodeHandling,
    GHQuad,
    GHTriple,
    GraphHelper,
    MarksType,
    MarkType,
)
from typing import TYPE_CHECKING, Collection, Set, Tuple, Type, Union, cast

import pytest
from _pytest.mark.structures import ParameterSet

import rdflib
from rdflib import Graph
from rdflib.compare import graph_diff
from rdflib.graph import ConjunctiveGraph, Dataset
from rdflib.namespace import FOAF, RDF, Namespace
from rdflib.term import BNode, Literal

if TYPE_CHECKING:
    from rdflib.graph import _TripleType

"""Test for graph_diff - much more extensive testing
would certainly be possible"""

_TripleSetType = Set["_TripleType"]


class TestDiff:
    """Unicode literals for graph_diff test
    (issue 151)"""

    def test_a(self):
        """with bnode"""
        g = rdflib.Graph()
        g.add((rdflib.BNode(), rdflib.URIRef("urn:p"), rdflib.Literal("\xe9")))

        graph_diff(g, g)

    def test_b(self):
        """Curiously, this one passes, even before the fix in issue 151"""

        g = rdflib.Graph()
        g.add((rdflib.URIRef("urn:a"), rdflib.URIRef("urn:p"), rdflib.Literal("\xe9")))

        graph_diff(g, g)

    @pytest.mark.xfail()
    def test_subsets(self) -> None:
        """
        This test verifies that `graph_diff` returns the correct values
        for two graphs, `g0` and `g1` where the triples in `g0` is a
        subset of the triples in `g1`.

        The expectation is that graph_diff reports that there are no
        triples only in `g0`, and that there are triples that occur in both
        `g0` and `g1`, and that there are triples only in `g1`.
        """
        g0_ts: _TripleSetType = set()
        bnode = BNode()
        g0_ts.update(
            {
                (bnode, FOAF.name, Literal("Golan Trevize")),
                (bnode, RDF.type, FOAF.Person),
            }
        )
        g0 = Graph()
        g0 += g0_ts

        g1_ts: _TripleSetType = set()
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
        assert in_first == set()
        assert len(in_second) > 0
        assert len(in_both) > 0


_ElementSetType = Union[Collection[GHTriple], Collection[GHQuad]]

_ElementSetTypeOrStr = Union[_ElementSetType, str]


@dataclass
class GraphDiffCase:
    graph_type: Type[Graph]
    format: str
    lhs: str
    rhs: str
    expected_result: Tuple[
        _ElementSetTypeOrStr, _ElementSetTypeOrStr, _ElementSetTypeOrStr
    ]
    marks: MarkType = field(default_factory=lambda: cast(MarksType, list()))

    def as_element_set(self, value: _ElementSetTypeOrStr) -> _ElementSetType:
        if isinstance(value, str):
            graph = self.graph_type()
            graph.parse(data=value, format=self.format)
            if isinstance(graph, ConjunctiveGraph):
                return GraphHelper.quad_set(graph, BNodeHandling.COLLAPSE)
            else:
                return GraphHelper.triple_set(graph, BNodeHandling.COLLAPSE)
        return value

    def expected_in_both_set(self) -> _ElementSetType:
        return self.as_element_set(self.expected_result[0])

    def expected_in_lhs_set(self) -> _ElementSetType:
        return self.as_element_set(self.expected_result[1])

    def expected_in_rhs_set(self) -> _ElementSetType:
        return self.as_element_set(self.expected_result[2])

    def as_params(self) -> ParameterSet:
        return pytest.param(self, marks=self.marks)


EGSCHEME = Namespace("example:")


@pytest.mark.parametrize(
    "test_case",
    [
        GraphDiffCase(
            Graph,
            format="turtle",
            lhs="""
            @prefix eg: <example:> .
            _:a _:b _:c .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            rhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            expected_result=(
                """
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
                {(COLLAPSED_BNODE, COLLAPSED_BNODE, COLLAPSED_BNODE)},
                "",
            ),
        ),
        GraphDiffCase(
            Graph,
            format="turtle",
            lhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            rhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            expected_result=(
                """
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
                "",
                "",
            ),
        ),
        GraphDiffCase(
            Dataset,
            format="trig",
            lhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            rhs="""
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
            expected_result=(
                """
            @prefix eg: <example:> .
            eg:o0 eg:p0 eg:s0 .
            eg:o1 eg:p1 eg:s1 .
            """,
                "",
                "",
            ),
            marks=pytest.mark.xfail(
                reason="quads are not supported", raises=ValueError
            ),
        ).as_params(),
    ],
)
def test_assert_sets_equal(test_case: GraphDiffCase):
    """
    GraphHelper.sets_equals and related functions work correctly in both
    positive and negative cases.
    """
    lhs_graph: Graph = test_case.graph_type()
    lhs_graph.parse(data=test_case.lhs, format=test_case.format)

    rhs_graph: Graph = test_case.graph_type()
    rhs_graph.parse(data=test_case.rhs, format=test_case.format)

    in_both, in_lhs, in_rhs = graph_diff(lhs_graph, rhs_graph)
    in_both_set = GraphHelper.triple_or_quad_set(in_both, BNodeHandling.COLLAPSE)
    in_lhs_set = GraphHelper.triple_or_quad_set(in_lhs, BNodeHandling.COLLAPSE)
    in_rhs_set = GraphHelper.triple_or_quad_set(in_rhs, BNodeHandling.COLLAPSE)

    assert test_case.expected_in_both_set() == in_both_set
    assert test_case.expected_in_lhs_set() == in_lhs_set
    assert test_case.expected_in_rhs_set() == in_rhs_set

    # Diff should be symetric
    in_rboth, in_rlhs, in_rrhs = graph_diff(rhs_graph, lhs_graph)
    in_rboth_set = GraphHelper.triple_or_quad_set(in_rboth, BNodeHandling.COLLAPSE)
    in_rlhs_set = GraphHelper.triple_or_quad_set(in_rlhs, BNodeHandling.COLLAPSE)
    in_rrhs_set = GraphHelper.triple_or_quad_set(in_rrhs, BNodeHandling.COLLAPSE)

    assert test_case.expected_in_both_set() == in_rboth_set
    assert test_case.expected_in_rhs_set() == in_rlhs_set
    assert test_case.expected_in_lhs_set() == in_rrhs_set
