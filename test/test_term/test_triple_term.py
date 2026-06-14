"""Tests for the RDF 1.2 TripleTerm class."""

from __future__ import annotations

import pickle

import pytest

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF
from rdflib.term import BNode, TripleTerm

EX = Namespace("http://example.org/")


# --- Construction ---


def test_construction_uriref_subject_and_object() -> None:
    """TripleTerm can be constructed with URIRef subject, predicate, and object."""
    tt = TripleTerm(EX.subject, EX.predicate, EX.object)
    assert tt.subject == EX.subject
    assert tt.predicate == EX.predicate
    assert tt.object == EX.object


def test_construction_bnode_subject() -> None:
    """TripleTerm can be constructed with a BNode subject."""
    bn = BNode()
    tt = TripleTerm(bn, EX.predicate, EX.object)
    assert tt.subject == bn
    assert isinstance(tt.subject, BNode)


def test_construction_literal_object() -> None:
    """TripleTerm can be constructed with a Literal object."""
    lit = Literal("hello", lang="en")
    tt = TripleTerm(EX.subject, EX.predicate, lit)
    assert tt.object == lit
    assert isinstance(tt.object, Literal)


def test_construction_bnode_object() -> None:
    """TripleTerm can be constructed with a BNode object."""
    bn = BNode()
    tt = TripleTerm(EX.subject, EX.predicate, bn)
    assert tt.object == bn
    assert isinstance(tt.object, BNode)


def test_construction_nested_triple_term_as_object() -> None:
    """TripleTerm can be constructed with another TripleTerm as object."""
    inner = TripleTerm(EX.s2, EX.p2, EX.o2)
    outer = TripleTerm(EX.subject, EX.predicate, inner)
    assert outer.object == inner
    assert isinstance(outer.object, TripleTerm)


# --- Invalid construction ---


def test_invalid_literal_as_subject() -> None:
    """Literal as subject raises TypeError."""
    with pytest.raises(TypeError, match="subject must be"):
        TripleTerm(Literal("bad"), EX.predicate, EX.object)  # type: ignore[arg-type]


def test_invalid_bnode_as_predicate() -> None:
    """BNode as predicate raises TypeError."""
    with pytest.raises(TypeError, match="predicate must be"):
        TripleTerm(EX.subject, BNode(), EX.object)  # type: ignore[arg-type]


def test_invalid_literal_as_predicate() -> None:
    """Literal as predicate raises TypeError."""
    with pytest.raises(TypeError, match="predicate must be"):
        TripleTerm(EX.subject, Literal("bad"), EX.object)  # type: ignore[arg-type]


def test_invalid_string_as_subject() -> None:
    """Plain string as subject raises TypeError."""
    with pytest.raises(TypeError, match="subject must be"):
        TripleTerm("http://example.org/s", EX.predicate, EX.object)  # type: ignore[arg-type]


def test_invalid_int_as_object() -> None:
    """Integer as object raises TypeError."""
    with pytest.raises(TypeError, match="object must be"):
        TripleTerm(EX.subject, EX.predicate, 42)  # type: ignore[arg-type]


# --- Equality ---


def test_equality_same_components() -> None:
    """TripleTerms with same components are equal."""
    tt1 = TripleTerm(EX.s, EX.p, EX.o)
    tt2 = TripleTerm(EX.s, EX.p, EX.o)
    assert tt1 == tt2


def test_equality_different_subject() -> None:
    """TripleTerms with different subjects are not equal."""
    tt1 = TripleTerm(EX.s1, EX.p, EX.o)
    tt2 = TripleTerm(EX.s2, EX.p, EX.o)
    assert tt1 != tt2


def test_equality_different_predicate() -> None:
    """TripleTerms with different predicates are not equal."""
    tt1 = TripleTerm(EX.s, EX.p1, EX.o)
    tt2 = TripleTerm(EX.s, EX.p2, EX.o)
    assert tt1 != tt2


def test_equality_different_object() -> None:
    """TripleTerms with different objects are not equal."""
    tt1 = TripleTerm(EX.s, EX.p, EX.o1)
    tt2 = TripleTerm(EX.s, EX.p, EX.o2)
    assert tt1 != tt2


def test_equality_not_equal_to_uriref() -> None:
    """TripleTerm is not equal to a URIRef."""
    tt = TripleTerm(EX.s, EX.p, EX.o)
    assert tt != EX.s


def test_equality_not_equal_to_literal() -> None:
    """TripleTerm is not equal to a Literal."""
    tt = TripleTerm(EX.s, EX.p, EX.o)
    assert tt != Literal("hello")


def test_equality_not_equal_to_none() -> None:
    """TripleTerm is not equal to None."""
    tt = TripleTerm(EX.s, EX.p, EX.o)
    assert tt != None  # noqa: E711


# --- Hashing ---


def test_hash_equal_triple_terms() -> None:
    """Equal TripleTerms have the same hash."""
    tt1 = TripleTerm(EX.s, EX.p, EX.o)
    tt2 = TripleTerm(EX.s, EX.p, EX.o)
    assert hash(tt1) == hash(tt2)


def test_hash_different_triple_terms() -> None:
    """Different TripleTerms have different hashes."""
    tt1 = TripleTerm(EX.s1, EX.p, EX.o)
    tt2 = TripleTerm(EX.s2, EX.p, EX.o)
    assert hash(tt1) != hash(tt2)


# --- Ordering ---


def test_ordering_same_type_by_subject() -> None:
    """TripleTerms are ordered component-wise; subject first."""
    tt1 = TripleTerm(EX.a, EX.p, EX.o)
    tt2 = TripleTerm(EX.b, EX.p, EX.o)
    assert tt1 < tt2
    assert tt2 > tt1


def test_ordering_same_type_by_predicate() -> None:
    """When subjects are equal, ordering is by predicate."""
    tt1 = TripleTerm(EX.s, EX.a, EX.o)
    tt2 = TripleTerm(EX.s, EX.b, EX.o)
    assert tt1 < tt2


def test_ordering_same_type_by_object() -> None:
    """When subject and predicate are equal, ordering is by object."""
    tt1 = TripleTerm(EX.s, EX.p, EX.a)
    tt2 = TripleTerm(EX.s, EX.p, EX.b)
    assert tt1 < tt2


def test_ordering_le_ge() -> None:
    """Test <= and >= operators."""
    tt1 = TripleTerm(EX.s, EX.p, EX.o)
    tt2 = TripleTerm(EX.s, EX.p, EX.o)
    tt3 = TripleTerm(EX.s2, EX.p, EX.o)
    assert tt1 <= tt2
    assert tt1 >= tt2
    assert tt1 <= tt3
    assert tt3 >= tt1


def test_ordering_cross_type_gt_uriref() -> None:
    """TripleTerm > URIRef in cross-type ordering."""
    tt = TripleTerm(EX.s, EX.p, EX.o)
    assert tt > EX.something


def test_ordering_cross_type_gt_literal() -> None:
    """TripleTerm > Literal in cross-type ordering."""
    tt = TripleTerm(EX.s, EX.p, EX.o)
    assert tt > Literal("hello")


def test_ordering_cross_type_gt_bnode() -> None:
    """TripleTerm > BNode in cross-type ordering."""
    tt = TripleTerm(EX.s, EX.p, EX.o)
    assert tt > BNode()


def test_ordering_cross_type_lt_none_is_false() -> None:
    """TripleTerm < None is False."""
    tt = TripleTerm(EX.s, EX.p, EX.o)
    assert not (tt < None)


def test_ordering_cross_type_gt_none_is_true() -> None:
    """TripleTerm > None is True."""
    tt = TripleTerm(EX.s, EX.p, EX.o)
    assert tt > None


# --- n3() output ---


def test_n3_basic() -> None:
    """n3() produces <<( <s> <p> <o> )>> format."""
    tt = TripleTerm(
        URIRef("http://example.org/s"),
        URIRef("http://example.org/p"),
        URIRef("http://example.org/o"),
    )
    expected = (
        "<<( <http://example.org/s> <http://example.org/p> <http://example.org/o> )>>"
    )
    assert tt.n3() == expected


def test_n3_with_literal_object() -> None:
    """n3() with a Literal object."""
    tt = TripleTerm(EX.s, EX.p, Literal("hello"))
    n3_str = tt.n3()
    assert n3_str.startswith("<<( ")
    assert n3_str.endswith(" )>>")
    assert '"hello"' in n3_str


def test_n3_with_bnode_subject() -> None:
    """n3() with a BNode subject."""
    bn = BNode("abc123")
    tt = TripleTerm(bn, EX.p, EX.o)
    n3_str = tt.n3()
    assert "_:abc123" in n3_str


def test_n3_with_namespace_manager() -> None:
    """n3() with a namespace_manager uses prefixed names."""
    g = Graph()
    g.bind("ex", EX)
    tt = TripleTerm(EX.s, EX.p, EX.o)
    n3_str = tt.n3(namespace_manager=g.namespace_manager)
    assert "ex:" in n3_str
    assert n3_str.startswith("<<( ")
    assert n3_str.endswith(" )>>")


def test_n3_nested_triple_term() -> None:
    """n3() with a nested TripleTerm as object."""
    inner = TripleTerm(EX.s2, EX.p2, EX.o2)
    outer = TripleTerm(EX.s, EX.p, inner)
    n3_str = outer.n3()
    # Should contain nested <<( ... )>>
    assert n3_str.count("<<(") == 2
    assert n3_str.count(")>>") == 2


# --- repr() ---


def test_repr() -> None:
    """repr() produces a readable representation."""
    tt = TripleTerm(EX.s, EX.p, EX.o)
    r = repr(tt)
    assert r.startswith("TripleTerm(")
    assert "rdflib.term.URIRef" in r
    assert "http://example.org/s" in r


# --- Pickling ---


def test_pickle_roundtrip() -> None:
    """TripleTerm survives pickle/unpickle."""
    tt = TripleTerm(EX.s, EX.p, EX.o)
    pickled = pickle.dumps(tt)
    unpickled = pickle.loads(pickled)
    assert tt == unpickled
    assert tt.subject == unpickled.subject
    assert tt.predicate == unpickled.predicate
    assert tt.object == unpickled.object


def test_pickle_roundtrip_with_literal() -> None:
    """TripleTerm with Literal object survives pickle/unpickle."""
    lit = Literal("hello", lang="en")
    tt = TripleTerm(EX.s, EX.p, lit)
    pickled = pickle.dumps(tt)
    unpickled = pickle.loads(pickled)
    assert tt == unpickled
    assert unpickled.object == lit


def test_pickle_roundtrip_with_bnode() -> None:
    """TripleTerm with BNode subject survives pickle/unpickle."""
    bn = BNode("fixed_id")
    tt = TripleTerm(bn, EX.p, EX.o)
    pickled = pickle.dumps(tt)
    unpickled = pickle.loads(pickled)
    assert tt == unpickled


def test_pickle_roundtrip_nested() -> None:
    """Nested TripleTerm survives pickle/unpickle."""
    inner = TripleTerm(EX.s2, EX.p2, EX.o2)
    outer = TripleTerm(EX.s, EX.p, inner)
    pickled = pickle.dumps(outer)
    unpickled = pickle.loads(pickled)
    assert outer == unpickled
    assert isinstance(unpickled.object, TripleTerm)


# --- Use in a Graph ---


def test_use_in_graph_as_object() -> None:
    """TripleTerm can be added to a Graph as an object."""
    g = Graph()
    tt = TripleTerm(EX.s, EX.p, EX.o)
    g.add((EX.reifier, RDF.reifies, tt))
    assert len(g) == 1
    triples = list(g.triples((EX.reifier, RDF.reifies, None)))
    assert len(triples) == 1
    assert triples[0][2] == tt


def test_use_in_graph_multiple_triple_terms() -> None:
    """Multiple TripleTerms can coexist in a Graph."""
    g = Graph()
    tt1 = TripleTerm(EX.s1, EX.p1, EX.o1)
    tt2 = TripleTerm(EX.s2, EX.p2, EX.o2)
    g.add((EX.r1, RDF.reifies, tt1))
    g.add((EX.r2, RDF.reifies, tt2))
    assert len(g) == 2


def test_use_in_graph_deduplication() -> None:
    """Adding the same triple with same TripleTerm object twice doesn't duplicate."""
    g = Graph()
    tt = TripleTerm(EX.s, EX.p, EX.o)
    g.add((EX.reifier, RDF.reifies, tt))
    g.add((EX.reifier, RDF.reifies, tt))
    assert len(g) == 1


def test_use_in_graph_equal_triple_terms_deduplicate() -> None:
    """Adding equal TripleTerms (different instances) doesn't duplicate."""
    g = Graph()
    tt1 = TripleTerm(EX.s, EX.p, EX.o)
    tt2 = TripleTerm(EX.s, EX.p, EX.o)
    g.add((EX.reifier, RDF.reifies, tt1))
    g.add((EX.reifier, RDF.reifies, tt2))
    assert len(g) == 1
