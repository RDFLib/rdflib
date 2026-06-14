"""Tests for the Graph.reify() method (RDF 1.2 reification)."""

from __future__ import annotations

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF
from rdflib.term import BNode, TripleTerm

EX = Namespace("http://example.org/")


def test_reify_returns_bnode_by_default() -> None:
    """reify() with no reifier argument returns a BNode."""
    g = Graph()
    reifier = g.reify(EX.alice, EX.knows, EX.bob)
    assert isinstance(reifier, BNode)


def test_reify_with_explicit_uriref_reifier() -> None:
    """reify() with an explicit URIRef reifier uses that URI."""
    g = Graph()
    reifier = g.reify(EX.alice, EX.knows, EX.bob, reifier=EX.reifier1)
    assert reifier == EX.reifier1


def test_reify_with_explicit_bnode_reifier() -> None:
    """reify() with an explicit BNode reifier uses that BNode."""
    g = Graph()
    bn = BNode("myreifier")
    reifier = g.reify(EX.alice, EX.knows, EX.bob, reifier=bn)
    assert reifier == bn


def test_reify_asserted_false_default() -> None:
    """By default (asserted=False), only the reifying triple is added."""
    g = Graph()
    g.reify(EX.alice, EX.knows, EX.bob)
    assert len(g) == 1
    assert (EX.alice, EX.knows, EX.bob) not in g


def test_reify_asserted_true() -> None:
    """With asserted=True, both the reifying triple and original are added."""
    g = Graph()
    g.reify(EX.alice, EX.knows, EX.bob, asserted=True)
    assert len(g) == 2
    assert (EX.alice, EX.knows, EX.bob) in g


def test_reifying_triple_uses_rdf_reifies() -> None:
    """The reifying triple uses RDF.reifies as predicate."""
    g = Graph()
    g.reify(EX.alice, EX.knows, EX.bob, reifier=EX.r1)
    triples = list(g.triples((EX.r1, RDF.reifies, None)))
    assert len(triples) == 1
    assert triples[0][1] == RDF.reifies


def test_reifying_triple_object_is_triple_term() -> None:
    """The object of the reifying triple is a TripleTerm."""
    g = Graph()
    g.reify(EX.alice, EX.knows, EX.bob, reifier=EX.r1)
    triples = list(g.triples((EX.r1, RDF.reifies, None)))
    obj = triples[0][2]
    assert isinstance(obj, TripleTerm)


def test_reifying_triple_term_components() -> None:
    """The TripleTerm in the reifying triple has correct components."""
    g = Graph()
    g.reify(EX.alice, EX.knows, EX.bob, reifier=EX.r1)
    triples = list(g.triples((EX.r1, RDF.reifies, None)))
    tt = triples[0][2]
    assert isinstance(tt, TripleTerm)
    assert tt.subject == EX.alice
    assert tt.predicate == EX.knows
    assert tt.object == EX.bob


def test_reifying_triple_with_literal_object() -> None:
    """Reification works when the original triple has a Literal object."""
    g = Graph()
    lit = Literal("Alice", lang="en")
    g.reify(EX.alice, EX.name, lit, reifier=EX.r1)
    triples = list(g.triples((EX.r1, RDF.reifies, None)))
    tt = triples[0][2]
    assert isinstance(tt, TripleTerm)
    assert tt.object == lit


def test_reify_return_value_is_reifier() -> None:
    """reify() returns the reifier node."""
    g = Graph()
    reifier = g.reify(EX.alice, EX.knows, EX.bob, reifier=EX.r1)
    assert reifier == EX.r1


def test_reify_return_value_auto_bnode() -> None:
    """reify() with no reifier returns the auto-generated BNode."""
    g = Graph()
    reifier = g.reify(EX.alice, EX.knows, EX.bob)
    triples = list(g.triples((reifier, RDF.reifies, None)))
    assert len(triples) == 1


def test_multiple_reifications_same_triple() -> None:
    """The same triple can be reified multiple times with different reifiers."""
    g = Graph()
    r1 = g.reify(EX.alice, EX.knows, EX.bob, reifier=EX.r1)
    r2 = g.reify(EX.alice, EX.knows, EX.bob, reifier=EX.r2)
    assert r1 != r2
    assert len(g) == 2
    assert len(list(g.triples((EX.r1, RDF.reifies, None)))) == 1
    assert len(list(g.triples((EX.r2, RDF.reifies, None)))) == 1


def test_reify_asserted_true_with_multiple_reifiers() -> None:
    """Multiple reifications with asserted=True only add the original once."""
    g = Graph()
    g.reify(EX.alice, EX.knows, EX.bob, reifier=EX.r1, asserted=True)
    g.reify(EX.alice, EX.knows, EX.bob, reifier=EX.r2, asserted=True)
    # 2 reifying triples + 1 original (deduplicated)
    assert len(g) == 3
    assert (EX.alice, EX.knows, EX.bob) in g
