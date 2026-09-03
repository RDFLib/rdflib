"""Tests for graph isomorphism with TripleTerms (RDF 1.2).

Tests that the compare module correctly handles TripleTerms
in graph isomorphism checks, including blank nodes inside triple terms.
"""

from rdflib import BNode, Graph, Literal, Namespace
from rdflib.compare import graph_diff, isomorphic, similar, to_canonical_graph
from rdflib.term import TripleTerm

EX = Namespace("http://example.org/")


class TestIsomorphicWithTripleTerms:
    """Test graph isomorphism with TripleTerms."""

    def test_isomorphic_graphs_with_triple_term_objects(self):
        """Two graphs with identical triple terms should be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        tt = TripleTerm(EX.Alice, EX.knows, EX.Bob)
        g1.add((EX.stmt1, EX.reifies, tt))
        g2.add((EX.stmt1, EX.reifies, tt))

        assert isomorphic(g1, g2)

    def test_non_isomorphic_graphs_different_triple_terms(self):
        """Graphs with different triple terms should not be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        tt1 = TripleTerm(EX.Alice, EX.knows, EX.Bob)
        tt2 = TripleTerm(EX.Alice, EX.knows, EX.Carol)

        g1.add((EX.stmt1, EX.reifies, tt1))
        g2.add((EX.stmt1, EX.reifies, tt2))

        assert not isomorphic(g1, g2)

    def test_isomorphic_with_bnode_in_triple_term_subject(self):
        """Graphs with BNodes in triple term subjects should be isomorphic
        if the BNode mapping is consistent."""
        g1 = Graph()
        g2 = Graph()

        # g1: _:a is used in triple term subject and also as a regular subject
        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))
        g1.add((b1, EX.type, EX.Person))

        # g2: different bnode, same structure
        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))
        g2.add((b2, EX.type, EX.Person))

        assert isomorphic(g1, g2)

    def test_non_isomorphic_with_inconsistent_bnode_in_triple_term(self):
        """Graphs where BNode in triple term doesn't match graph-level usage
        should not be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        # g1: same bnode in triple term and as subject
        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))
        g1.add((b1, EX.type, EX.Person))

        # g2: DIFFERENT bnodes - one in triple term, different one as subject
        b2 = BNode()
        b3 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))
        g2.add((b3, EX.type, EX.Person))

        assert not isomorphic(g1, g2)

    def test_isomorphic_with_bnode_in_triple_term_object(self):
        """Graphs with BNodes in triple term object position should be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(EX.Alice, EX.knows, b1)
        g1.add((EX.stmt1, EX.reifies, tt1))
        g1.add((b1, EX.name, Literal("Bob")))

        b2 = BNode()
        tt2 = TripleTerm(EX.Alice, EX.knows, b2)
        g2.add((EX.stmt1, EX.reifies, tt2))
        g2.add((b2, EX.name, Literal("Bob")))

        assert isomorphic(g1, g2)

    def test_isomorphic_with_nested_triple_terms(self):
        """Graphs with nested triple terms should be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        inner_tt = TripleTerm(EX.Alice, EX.name, Literal("Alice"))
        outer_tt = TripleTerm(EX.Bob, EX.believes, inner_tt)

        g1.add((EX.stmt1, EX.reifies, outer_tt))
        g2.add((EX.stmt1, EX.reifies, outer_tt))

        assert isomorphic(g1, g2)

    def test_isomorphic_nested_triple_term_with_bnodes(self):
        """Graphs with BNodes in nested triple terms should be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        inner_tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        outer_tt1 = TripleTerm(EX.Bob, EX.believes, inner_tt1)
        g1.add((EX.stmt1, EX.reifies, outer_tt1))
        g1.add((b1, EX.type, EX.Person))

        b2 = BNode()
        inner_tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        outer_tt2 = TripleTerm(EX.Bob, EX.believes, inner_tt2)
        g2.add((EX.stmt1, EX.reifies, outer_tt2))
        g2.add((b2, EX.type, EX.Person))

        assert isomorphic(g1, g2)


class TestCanonicalGraphWithTripleTerms:
    """Test canonical graph generation with TripleTerms."""

    def test_canonical_graph_preserves_triple_terms(self):
        """Canonical graph should preserve triple terms."""
        g = Graph()
        tt = TripleTerm(EX.Alice, EX.knows, EX.Bob)
        g.add((EX.stmt1, EX.reifies, tt))

        cg = to_canonical_graph(g)
        triples = list(cg.triples((EX.stmt1, EX.reifies, None)))
        assert len(triples) == 1
        assert triples[0][2] == tt

    def test_canonical_graph_with_bnode_in_triple_term(self):
        """Canonical graph should remap BNodes inside triple terms."""
        g = Graph()
        b = BNode()
        tt = TripleTerm(b, EX.name, Literal("Alice"))
        g.add((EX.stmt1, EX.reifies, tt))
        g.add((b, EX.type, EX.Person))

        cg = to_canonical_graph(g)

        # The canonical graph should have the same structure
        assert len(cg) == 2

        # The BNode should be consistently remapped
        reify_triples = list(cg.triples((EX.stmt1, EX.reifies, None)))
        assert len(reify_triples) == 1
        canonical_tt = reify_triples[0][2]
        assert isinstance(canonical_tt, TripleTerm)

        # The BNode in the triple term should match the one used as subject
        type_triples = list(cg.triples((None, EX.type, EX.Person)))
        assert len(type_triples) == 1
        canonical_bnode = type_triples[0][0]
        assert canonical_tt.subject == canonical_bnode

    def test_canonical_graph_deterministic(self):
        """Two isomorphic graphs should produce the same canonical graph."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))
        g1.add((b1, EX.type, EX.Person))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))
        g2.add((b2, EX.type, EX.Person))

        cg1 = to_canonical_graph(g1)
        cg2 = to_canonical_graph(g2)

        # Both canonical graphs should be identical (same triples)
        assert set(cg1) == set(cg2)


class TestIsomorphicWithDirectionalLiterals:
    """Test graph isomorphism with directional language-tagged strings."""

    def test_isomorphic_with_directional_literals(self):
        """Graphs with same directional literals should be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        lit = Literal("مرحبا", lang="ar", direction="rtl")
        g1.add((EX.greeting, EX.text, lit))
        g2.add((EX.greeting, EX.text, lit))

        assert isomorphic(g1, g2)

    def test_non_isomorphic_different_directions(self):
        """Graphs with different directions should not be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        g1.add((EX.greeting, EX.text, Literal("hello", lang="en", direction="ltr")))
        g2.add((EX.greeting, EX.text, Literal("hello", lang="en", direction="rtl")))

        assert not isomorphic(g1, g2)

    def test_non_isomorphic_direction_vs_no_direction(self):
        """Graph with directional literal is not isomorphic to one without."""
        g1 = Graph()
        g2 = Graph()

        g1.add((EX.greeting, EX.text, Literal("hello", lang="en", direction="ltr")))
        g2.add((EX.greeting, EX.text, Literal("hello", lang="en")))

        assert not isomorphic(g1, g2)


class TestSimilarWithTripleTerms:
    """Test the similar() function with TripleTerms (exercises _squash_bnodes)."""

    def test_similar_graphs_with_triple_term_no_bnodes(self):
        """similar() should return True for identical graphs with triple terms."""
        g1 = Graph()
        g2 = Graph()

        tt = TripleTerm(EX.Alice, EX.knows, EX.Bob)
        g1.add((EX.stmt1, EX.reifies, tt))
        g2.add((EX.stmt1, EX.reifies, tt))

        assert similar(g1, g2)

    def test_similar_graphs_with_bnode_in_triple_term(self):
        """similar() should treat different BNodes inside TripleTerms as equivalent."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))
        g1.add((b1, EX.type, EX.Person))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))
        g2.add((b2, EX.type, EX.Person))

        assert similar(g1, g2)

    def test_not_similar_different_triple_terms(self):
        """similar() should return False for graphs with different triple terms."""
        g1 = Graph()
        g2 = Graph()

        tt1 = TripleTerm(EX.Alice, EX.knows, EX.Bob)
        tt2 = TripleTerm(EX.Alice, EX.knows, EX.Carol)
        g1.add((EX.stmt1, EX.reifies, tt1))
        g2.add((EX.stmt1, EX.reifies, tt2))

        assert not similar(g1, g2)

    def test_similar_with_bnode_in_triple_term_object(self):
        """similar() squashes BNodes in triple term object position."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(EX.Alice, EX.knows, b1)
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        tt2 = TripleTerm(EX.Alice, EX.knows, b2)
        g2.add((EX.stmt1, EX.reifies, tt2))

        assert similar(g1, g2)

    def test_similar_with_nested_triple_term_and_bnodes(self):
        """similar() squashes BNodes in nested TripleTerms."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        inner1 = TripleTerm(EX.Alice, EX.knows, b1)
        outer1 = TripleTerm(EX.Bob, EX.believes, inner1)
        g1.add((EX.stmt1, EX.reifies, outer1))

        b2 = BNode()
        inner2 = TripleTerm(EX.Alice, EX.knows, b2)
        outer2 = TripleTerm(EX.Bob, EX.believes, inner2)
        g2.add((EX.stmt1, EX.reifies, outer2))

        assert similar(g1, g2)

    def test_similar_embedded_only_bnodes(self):
        """similar() handles BNodes that appear only inside TripleTerms."""
        g1 = Graph()
        g2 = Graph()

        # BNodes only inside triple terms, never at graph level
        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))

        assert similar(g1, g2)


class TestGraphDiffWithTripleTerms:
    """Test graph_diff() with TripleTerms."""

    def test_graph_diff_identical_triple_terms(self):
        """graph_diff of identical graphs with triple terms should show all in common."""
        g1 = Graph()
        g2 = Graph()

        tt = TripleTerm(EX.Alice, EX.knows, EX.Bob)
        g1.add((EX.stmt1, EX.reifies, tt))
        g2.add((EX.stmt1, EX.reifies, tt))

        in_both, in_first, in_second = graph_diff(g1, g2)
        assert len(in_both) == 1
        assert len(in_first) == 0
        assert len(in_second) == 0

    def test_graph_diff_different_triple_terms(self):
        """graph_diff should separate graphs with different triple terms."""
        g1 = Graph()
        g2 = Graph()

        tt1 = TripleTerm(EX.Alice, EX.knows, EX.Bob)
        tt2 = TripleTerm(EX.Alice, EX.knows, EX.Carol)
        g1.add((EX.stmt1, EX.reifies, tt1))
        g2.add((EX.stmt1, EX.reifies, tt2))

        in_both, in_first, in_second = graph_diff(g1, g2)
        assert len(in_both) == 0
        assert len(in_first) == 1
        assert len(in_second) == 1

    def test_graph_diff_with_bnodes_in_triple_terms(self):
        """graph_diff should correctly handle BNodes inside triple terms."""
        g1 = Graph()
        g2 = Graph()

        # Isomorphic graphs with BNodes in triple terms
        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))
        g1.add((b1, EX.type, EX.Person))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))
        g2.add((b2, EX.type, EX.Person))

        in_both, in_first, in_second = graph_diff(g1, g2)
        assert len(in_both) == 2
        assert len(in_first) == 0
        assert len(in_second) == 0

    def test_graph_diff_partial_overlap_with_triple_terms(self):
        """graph_diff with shared and unique triples involving triple terms."""
        g1 = Graph()
        g2 = Graph()

        tt_shared = TripleTerm(EX.Alice, EX.knows, EX.Bob)
        tt_only_g1 = TripleTerm(EX.Alice, EX.likes, EX.Carol)
        tt_only_g2 = TripleTerm(EX.Alice, EX.likes, EX.Dave)

        g1.add((EX.stmt1, EX.reifies, tt_shared))
        g1.add((EX.stmt2, EX.reifies, tt_only_g1))

        g2.add((EX.stmt1, EX.reifies, tt_shared))
        g2.add((EX.stmt2, EX.reifies, tt_only_g2))

        in_both, in_first, in_second = graph_diff(g1, g2)
        assert len(in_both) == 1
        assert len(in_first) == 1
        assert len(in_second) == 1


class TestEmbeddedOnlyBNodes:
    """Test BNodes that appear exclusively inside TripleTerms and never at graph level.

    This exercises the embedded-only BNode coloring logic: _record_triple_term_context,
    the embedded_only vs graph_level_bnodes partitioning, and embedded_color_groups.
    """

    def test_isomorphic_embedded_only_bnode_in_subject(self):
        """Graphs with BNodes only inside triple term subject (never at graph level)
        should be isomorphic when structurally identical."""
        g1 = Graph()
        g2 = Graph()

        # BNode only appears inside the TripleTerm, not as a direct triple subject/object
        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))

        assert isomorphic(g1, g2)

    def test_isomorphic_embedded_only_bnode_in_object(self):
        """Graphs with BNodes only inside triple term object (never at graph level)
        should be isomorphic when structurally identical."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(EX.Alice, EX.knows, b1)
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        tt2 = TripleTerm(EX.Alice, EX.knows, b2)
        g2.add((EX.stmt1, EX.reifies, tt2))

        assert isomorphic(g1, g2)

    def test_canonical_graph_embedded_only_bnode(self):
        """Canonical graph should produce deterministic output for embedded-only BNodes."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))

        cg1 = to_canonical_graph(g1)
        cg2 = to_canonical_graph(g2)

        assert set(cg1) == set(cg2)

    def test_canonical_graph_embedded_only_bnode_has_canonical_id(self):
        """Embedded-only BNodes should receive cb-prefixed canonical identifiers."""
        g = Graph()
        b = BNode()
        tt = TripleTerm(b, EX.name, Literal("Alice"))
        g.add((EX.stmt1, EX.reifies, tt))

        cg = to_canonical_graph(g)
        triples = list(cg.triples((EX.stmt1, EX.reifies, None)))
        assert len(triples) == 1
        canonical_tt = triples[0][2]
        assert isinstance(canonical_tt, TripleTerm)
        assert isinstance(canonical_tt.subject, BNode)
        assert str(canonical_tt.subject).startswith("cb")

    def test_embedded_only_bnode_with_additional_graph_triples(self):
        """Embedded-only BNodes work correctly alongside graph-level non-bnode triples."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))
        g1.add((EX.Alice, EX.type, EX.Person))
        g1.add((EX.Bob, EX.knows, EX.Alice))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))
        g2.add((EX.Alice, EX.type, EX.Person))
        g2.add((EX.Bob, EX.knows, EX.Alice))

        assert isomorphic(g1, g2)


class TestMultipleEmbeddedOnlyBNodes:
    """Test multiple distinct embedded-only BNodes in separate TripleTerms.

    This exercises the embedded_color_groups logic that groups embedded-only
    BNodes by their structural context.
    """

    def test_isomorphic_two_embedded_only_bnodes_same_context(self):
        """Two embedded-only BNodes in identical structural contexts should be
        isomorphic (same predicate/position)."""
        g1 = Graph()
        g2 = Graph()

        # Two triples each with an embedded-only bnode in subject of TripleTerm
        # Same predicate and same surrounding terms = same context group
        b1a = BNode()
        b1b = BNode()
        tt1a = TripleTerm(b1a, EX.name, Literal("Alice"))
        tt1b = TripleTerm(b1b, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1a))
        g1.add((EX.stmt2, EX.reifies, tt1b))

        b2a = BNode()
        b2b = BNode()
        tt2a = TripleTerm(b2a, EX.name, Literal("Alice"))
        tt2b = TripleTerm(b2b, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2a))
        g2.add((EX.stmt2, EX.reifies, tt2b))

        assert isomorphic(g1, g2)

    def test_isomorphic_two_embedded_only_bnodes_different_contexts(self):
        """Two embedded-only BNodes in different structural contexts (different
        predicates in the TripleTerm) should still be isomorphic when structure matches.
        """
        g1 = Graph()
        g2 = Graph()

        b1a = BNode()
        b1b = BNode()
        # Different predicates inside the TripleTerms = different context groups
        tt1a = TripleTerm(b1a, EX.name, Literal("Alice"))
        tt1b = TripleTerm(b1b, EX.age, Literal(30))
        g1.add((EX.stmt1, EX.reifies, tt1a))
        g1.add((EX.stmt2, EX.reifies, tt1b))

        b2a = BNode()
        b2b = BNode()
        tt2a = TripleTerm(b2a, EX.name, Literal("Alice"))
        tt2b = TripleTerm(b2b, EX.age, Literal(30))
        g2.add((EX.stmt1, EX.reifies, tt2a))
        g2.add((EX.stmt2, EX.reifies, tt2b))

        assert isomorphic(g1, g2)

    def test_non_isomorphic_embedded_only_bnodes_swapped_positions(self):
        """Two graphs with embedded-only BNodes where one graph has BNode in subject
        and the other has BNode in object should NOT be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        # BNode in subject position of the TripleTerm
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        # BNode in object position of the TripleTerm
        tt2 = TripleTerm(EX.Alice, EX.name, b2)
        g2.add((EX.stmt1, EX.reifies, tt2))

        assert not isomorphic(g1, g2)

    def test_non_isomorphic_embedded_only_bnodes_different_predicates(self):
        """Two graphs with embedded-only BNodes in same position but different
        surrounding predicates should NOT be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.label, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))

        assert not isomorphic(g1, g2)

    def test_canonical_graph_distinguishes_embedded_only_bnodes(self):
        """Canonical graph assigns distinct labels to embedded-only BNodes in
        different structural contexts."""
        g = Graph()

        b1 = BNode()
        b2 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        tt2 = TripleTerm(b2, EX.age, Literal(30))
        g.add((EX.stmt1, EX.reifies, tt1))
        g.add((EX.stmt2, EX.reifies, tt2))

        cg = to_canonical_graph(g)
        assert len(cg) == 2

        # Extract canonical triple terms
        reify1 = list(cg.triples((EX.stmt1, EX.reifies, None)))
        reify2 = list(cg.triples((EX.stmt2, EX.reifies, None)))
        assert len(reify1) == 1
        assert len(reify2) == 1

        ctt1 = reify1[0][2]
        ctt2 = reify2[0][2]
        assert isinstance(ctt1, TripleTerm)
        assert isinstance(ctt2, TripleTerm)

        # The two BNodes in different contexts should get different canonical IDs
        assert ctt1.subject != ctt2.subject

    def test_isomorphic_multiple_embedded_bnodes_in_one_triple_term(self):
        """A TripleTerm with BNodes in both subject and object should be
        handled correctly for isomorphism."""
        g1 = Graph()
        g2 = Graph()

        b1s = BNode()
        b1o = BNode()
        tt1 = TripleTerm(b1s, EX.knows, b1o)
        g1.add((EX.stmt1, EX.reifies, tt1))
        # Give structure so they can be distinguished
        g1.add((b1s, EX.type, EX.Person))
        g1.add((b1o, EX.type, EX.Animal))

        b2s = BNode()
        b2o = BNode()
        tt2 = TripleTerm(b2s, EX.knows, b2o)
        g2.add((EX.stmt1, EX.reifies, tt2))
        g2.add((b2s, EX.type, EX.Person))
        g2.add((b2o, EX.type, EX.Animal))

        assert isomorphic(g1, g2)

    def test_non_isomorphic_multiple_embedded_bnodes_swapped_types(self):
        """Two graphs where BNodes in subject/object of TripleTerm have swapped
        types at graph level should NOT be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        b1s = BNode()
        b1o = BNode()
        tt1 = TripleTerm(b1s, EX.knows, b1o)
        g1.add((EX.stmt1, EX.reifies, tt1))
        g1.add((b1s, EX.type, EX.Person))
        g1.add((b1o, EX.type, EX.Animal))

        b2s = BNode()
        b2o = BNode()
        tt2 = TripleTerm(b2s, EX.knows, b2o)
        g2.add((EX.stmt1, EX.reifies, tt2))
        # Swapped: subject is Animal, object is Person
        g2.add((b2s, EX.type, EX.Animal))
        g2.add((b2o, EX.type, EX.Person))

        assert not isomorphic(g1, g2)


class TestDeeplyNestedTripleTermsWithEmbeddedBNodes:
    """Test deeply nested TripleTerms with embedded-only BNodes.

    Exercises recursion in _get_bnodes_from_term, _remap_triple_term,
    and _record_triple_term_context for nested structures.
    """

    def test_isomorphic_deeply_nested_embedded_only_bnode(self):
        """BNode in object of a nested TripleTerm (embedded-only) should be
        handled correctly for isomorphism."""
        g1 = Graph()
        g2 = Graph()

        # Nested: outer has BNode in inner object position (embedded-only)
        b1 = BNode()
        inner1 = TripleTerm(EX.Alice, EX.knows, b1)
        outer1 = TripleTerm(EX.Bob, EX.believes, inner1)
        g1.add((EX.stmt1, EX.reifies, outer1))

        b2 = BNode()
        inner2 = TripleTerm(EX.Alice, EX.knows, b2)
        outer2 = TripleTerm(EX.Bob, EX.believes, inner2)
        g2.add((EX.stmt1, EX.reifies, outer2))

        assert isomorphic(g1, g2)

    def test_canonical_graph_deeply_nested_embedded_only_bnode(self):
        """Canonical graph deterministically handles nested embedded-only BNodes."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        inner1 = TripleTerm(EX.Alice, EX.knows, b1)
        outer1 = TripleTerm(EX.Bob, EX.believes, inner1)
        g1.add((EX.stmt1, EX.reifies, outer1))

        b2 = BNode()
        inner2 = TripleTerm(EX.Alice, EX.knows, b2)
        outer2 = TripleTerm(EX.Bob, EX.believes, inner2)
        g2.add((EX.stmt1, EX.reifies, outer2))

        cg1 = to_canonical_graph(g1)
        cg2 = to_canonical_graph(g2)
        assert set(cg1) == set(cg2)

    def test_non_isomorphic_nested_different_inner_predicate(self):
        """Nested TripleTerms with different inner predicates should not be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        inner1 = TripleTerm(EX.Alice, EX.knows, b1)
        outer1 = TripleTerm(EX.Bob, EX.believes, inner1)
        g1.add((EX.stmt1, EX.reifies, outer1))

        b2 = BNode()
        inner2 = TripleTerm(EX.Alice, EX.likes, b2)  # Different predicate
        outer2 = TripleTerm(EX.Bob, EX.believes, inner2)
        g2.add((EX.stmt1, EX.reifies, outer2))

        assert not isomorphic(g1, g2)

    def test_isomorphic_double_nested_triple_term_with_bnode(self):
        """Double-nested TripleTerm with BNode in deepest object position."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        innermost1 = TripleTerm(EX.Alice, EX.knows, b1)
        middle1 = TripleTerm(EX.Bob, EX.believes, innermost1)
        outer1 = TripleTerm(EX.Carol, EX.reports, middle1)
        g1.add((EX.stmt1, EX.reifies, outer1))

        b2 = BNode()
        innermost2 = TripleTerm(EX.Alice, EX.knows, b2)
        middle2 = TripleTerm(EX.Bob, EX.believes, innermost2)
        outer2 = TripleTerm(EX.Carol, EX.reports, middle2)
        g2.add((EX.stmt1, EX.reifies, outer2))

        assert isomorphic(g1, g2)

    def test_nested_embedded_only_bnode_alongside_graph_level_bnodes(self):
        """Graph with both graph-level BNodes and embedded-only BNodes in nested
        TripleTerms should be correctly isomorphic."""
        g1 = Graph()
        g2 = Graph()

        # Graph-level bnode
        gb1 = BNode()
        g1.add((gb1, EX.type, EX.Statement))
        # Embedded-only bnode in nested triple term
        eb1 = BNode()
        inner1 = TripleTerm(EX.Alice, EX.knows, eb1)
        outer1 = TripleTerm(EX.Bob, EX.believes, inner1)
        g1.add((gb1, EX.reifies, outer1))

        gb2 = BNode()
        g2.add((gb2, EX.type, EX.Statement))
        eb2 = BNode()
        inner2 = TripleTerm(EX.Alice, EX.knows, eb2)
        outer2 = TripleTerm(EX.Bob, EX.believes, inner2)
        g2.add((gb2, EX.reifies, outer2))

        assert isomorphic(g1, g2)


class TestNonIsomorphicEmbeddedOnlyBNodesStructuralContext:
    """Test that embedded-only BNodes in different structural positions are
    correctly discriminated.

    This is the key behavioral test for _record_triple_term_context and the
    embedded_color_groups grouping logic.
    """

    def test_non_isomorphic_different_graph_predicates(self):
        """Embedded-only BNodes under different graph-level predicates should
        produce non-isomorphic graphs if structure differs."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        # Different graph-level predicate
        g2.add((EX.stmt1, EX.describes, tt2))

        assert not isomorphic(g1, g2)

    def test_non_isomorphic_different_graph_subjects(self):
        """Same TripleTerm structure but under different graph subjects should not
        be isomorphic."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt2, EX.reifies, tt2))

        assert not isomorphic(g1, g2)

    def test_non_isomorphic_bnode_position_subject_vs_object(self):
        """A BNode in TripleTerm subject vs object position should not be isomorphic
        even when both are embedded-only."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        # BNode in subject position
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        # BNode in object position
        tt2 = TripleTerm(EX.person, EX.name, b2)
        g2.add((EX.stmt1, EX.reifies, tt2))

        assert not isomorphic(g1, g2)

    def test_non_isomorphic_same_position_different_surrounding_terms(self):
        """Embedded-only BNodes with same position but different non-BNode terms
        in the TripleTerm should produce non-isomorphic graphs."""
        g1 = Graph()
        g2 = Graph()

        b1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))

        b2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Bob"))
        g2.add((EX.stmt1, EX.reifies, tt2))

        assert not isomorphic(g1, g2)

    def test_isomorphic_same_context_different_bnodes(self):
        """Embedded-only BNodes with identical structural context should be
        isomorphic regardless of BNode identity."""
        g1 = Graph()
        g2 = Graph()

        # Both have the exact same structure - only bnode identity differs
        b1 = BNode("x")
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((EX.stmt1, EX.reifies, tt1))
        g1.add((EX.stmt1, EX.type, EX.Reification))

        b2 = BNode("y")
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((EX.stmt1, EX.reifies, tt2))
        g2.add((EX.stmt1, EX.type, EX.Reification))

        assert isomorphic(g1, g2)

    def test_non_isomorphic_embedded_only_mixed_with_graph_level(self):
        """Graph where one BNode is graph-level and another is embedded-only
        vs graph where both appear at graph level."""
        g1 = Graph()
        g2 = Graph()

        # g1: b1 is embedded-only, b_graph is graph-level
        b1 = BNode()
        b_graph1 = BNode()
        tt1 = TripleTerm(b1, EX.name, Literal("Alice"))
        g1.add((b_graph1, EX.reifies, tt1))
        g1.add((b_graph1, EX.type, EX.Statement))

        # g2: both BNodes appear at graph level (b2 also used as subject)
        b2 = BNode()
        b_graph2 = BNode()
        tt2 = TripleTerm(b2, EX.name, Literal("Alice"))
        g2.add((b_graph2, EX.reifies, tt2))
        g2.add((b_graph2, EX.type, EX.Statement))
        g2.add((b2, EX.type, EX.Person))  # Extra triple makes it non-iso

        assert not isomorphic(g1, g2)
