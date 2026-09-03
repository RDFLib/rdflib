"""Tests for skolemization and de-skolemization with TripleTerms."""

from __future__ import annotations

import re

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF
from rdflib.term import BNode, Literal, TripleTerm

EX = Namespace("http://example.org/")

SKOLEM_PATTERN = re.compile(r"^https://rdflib\.github\.io/\.well-known/genid/rdflib/")


def _is_skolem_uri(node: object) -> bool:
    return isinstance(node, URIRef) and SKOLEM_PATTERN.match(str(node)) is not None


def test_skolemize_bnode_in_triple_term() -> None:
    """Skolemize replaces BNodes in TripleTerm subject and object positions."""
    g = Graph()
    bn_s = BNode()
    bn_o = BNode()

    # TripleTerm with BNode subject only
    tt_subj = TripleTerm(bn_s, EX.predicate, EX.object)
    g.add((EX.r1, RDF.reifies, tt_subj))

    # TripleTerm with BNode object only
    tt_obj = TripleTerm(EX.subject, EX.predicate, bn_o)
    g.add((EX.r2, RDF.reifies, tt_obj))

    # TripleTerm with no BNodes (should be unchanged)
    tt_plain = TripleTerm(EX.subject, EX.predicate, EX.object)
    g.add((EX.r3, RDF.reifies, tt_plain))

    skolemized = g.skolemize()
    assert len(skolemized) == 3

    # Check BNode subject was skolemized
    r1_triples = list(skolemized.triples((EX.r1, RDF.reifies, None)))
    tt1 = r1_triples[0][2]
    assert isinstance(tt1, TripleTerm)
    assert _is_skolem_uri(tt1.subject)
    assert tt1.predicate == EX.predicate
    assert tt1.object == EX.object

    # Check BNode object was skolemized
    r2_triples = list(skolemized.triples((EX.r2, RDF.reifies, None)))
    tt2 = r2_triples[0][2]
    assert isinstance(tt2, TripleTerm)
    assert tt2.subject == EX.subject
    assert _is_skolem_uri(tt2.object)

    # Check no-BNode TripleTerm is unchanged
    r3_triples = list(skolemized.triples((EX.r3, RDF.reifies, None)))
    tt3 = r3_triples[0][2]
    assert isinstance(tt3, TripleTerm)
    assert tt3.subject == EX.subject
    assert tt3.object == EX.object


def test_deskolemize_reverses_skolemization() -> None:
    """De-skolemize restores BNodes inside TripleTerms after skolemization."""
    g = Graph()
    bn = BNode()
    tt = TripleTerm(bn, EX.predicate, EX.object)
    g.add((EX.reifier, RDF.reifies, tt))

    deskolemized = g.skolemize().de_skolemize()
    assert len(deskolemized) == 1

    triples = list(deskolemized.triples((EX.reifier, RDF.reifies, None)))
    obj = triples[0][2]
    assert isinstance(obj, TripleTerm)
    assert isinstance(obj.subject, BNode)
    assert obj.predicate == EX.predicate
    assert obj.object == EX.object

    # Also test BNode in object position roundtrips
    g2 = Graph()
    bn2 = BNode()
    tt2 = TripleTerm(EX.subject, EX.predicate, bn2)
    g2.add((EX.reifier, RDF.reifies, tt2))

    deskolemized2 = g2.skolemize().de_skolemize()
    triples2 = list(deskolemized2.triples((EX.reifier, RDF.reifies, None)))
    obj2 = triples2[0][2]
    assert isinstance(obj2, TripleTerm)
    assert isinstance(obj2.object, BNode)


def test_skolemize_nested_triple_term() -> None:
    """Skolemize/de-skolemize handles nested TripleTerms with BNodes."""
    g = Graph()
    bn = BNode()
    inner_tt = TripleTerm(bn, EX.innerPred, EX.innerObj)
    outer_tt = TripleTerm(EX.outerSubj, EX.outerPred, inner_tt)
    g.add((EX.reifier, RDF.reifies, outer_tt))

    # Skolemize
    skolemized = g.skolemize()
    triples = list(skolemized.triples((EX.reifier, RDF.reifies, None)))
    obj = triples[0][2]
    assert isinstance(obj, TripleTerm)
    inner = obj.object
    assert isinstance(inner, TripleTerm)
    assert _is_skolem_uri(inner.subject)
    assert inner.predicate == EX.innerPred

    # De-skolemize
    deskolemized = skolemized.de_skolemize()
    triples_d = list(deskolemized.triples((EX.reifier, RDF.reifies, None)))
    obj_d = triples_d[0][2]
    assert isinstance(obj_d, TripleTerm)
    inner_d = obj_d.object
    assert isinstance(inner_d, TripleTerm)
    assert isinstance(inner_d.subject, BNode)


def test_skolemize_shared_bnode_graph_and_triple_term() -> None:
    """A BNode used both as graph subject and inside a TripleTerm gets the same skolem URI."""
    g = Graph()
    bn = BNode()
    tt = TripleTerm(bn, EX.predicate, EX.object)
    g.add((bn, EX.name, Literal("Alice")))
    g.add((EX.reifier, RDF.reifies, tt))

    skolemized = g.skolemize()
    assert len(skolemized) == 2

    # Get the skolem URI from the graph-level triple
    name_triples = list(skolemized.triples((None, EX.name, Literal("Alice"))))
    skolem_node = name_triples[0][0]
    assert _is_skolem_uri(skolem_node)

    # Get the skolem URI from inside the TripleTerm
    reify_triples = list(skolemized.triples((EX.reifier, RDF.reifies, None)))
    tt_obj = reify_triples[0][2]
    assert isinstance(tt_obj, TripleTerm)
    assert _is_skolem_uri(tt_obj.subject)

    # Same BNode → same skolem URI
    assert skolem_node == tt_obj.subject
