"""Tests for to_quads() and the Graph/ConjunctiveGraph/Dataset add_many() methods."""

from __future__ import annotations

from rdflib import ConjunctiveGraph, Dataset, Graph, URIRef
from rdflib.graph import to_quads

subj = URIRef("urn:s")
pred = URIRef("urn:p")
obj = URIRef("urn:o")


class TestToQuads:
    def test_triple_uses_default_context(self) -> None:
        ctx = Graph(identifier=URIRef("urn:ctx"))
        result = list(to_quads([(subj, pred, obj)], ctx))
        assert result == [(subj, pred, obj, ctx)]

    def test_quad_is_yielded_unchanged(self) -> None:
        ctx = Graph(identifier=URIRef("urn:ctx"))
        other = Graph(identifier=URIRef("urn:other"))
        result = list(to_quads([(subj, pred, obj, other)], ctx))
        assert result == [(subj, pred, obj, other)]

    def test_mixed_triples_and_quads(self) -> None:
        ctx = Graph(identifier=URIRef("urn:ctx"))
        other = Graph(identifier=URIRef("urn:other"))
        items = [(subj, pred, obj), (subj, pred, obj, other)]
        result = list(to_quads(items, ctx))
        assert result == [(subj, pred, obj, ctx), (subj, pred, obj, other)]

    def test_empty_input(self) -> None:
        ctx = Graph(identifier=URIRef("urn:ctx"))
        assert list(to_quads([], ctx)) == []

    def test_multiple_triples_all_get_default_context(self) -> None:
        ctx = Graph(identifier=URIRef("urn:ctx"))
        s2, p2, o2 = URIRef("urn:s2"), URIRef("urn:p2"), URIRef("urn:o2")
        result = list(to_quads([(subj, pred, obj), (s2, p2, o2)], ctx))
        assert result == [(subj, pred, obj, ctx), (s2, p2, o2, ctx)]

    def test_result_is_lazy_generator(self) -> None:
        """to_quads should return a generator, not a list."""
        ctx = Graph(identifier=URIRef("urn:ctx"))
        import types

        result = to_quads([(subj, pred, obj)], ctx)
        assert isinstance(result, types.GeneratorType)


class TestGraphAddMany:
    def test_triple_uses_self_as_context(self) -> None:
        g = Graph(identifier=URIRef("urn:g"))
        g.add_many([(subj, pred, obj)])
        assert (subj, pred, obj) in g

    def test_quad_with_matching_context_is_added(self) -> None:
        g = Graph(identifier=URIRef("urn:g"))
        g.add_many([(subj, pred, obj, g)])
        assert (subj, pred, obj) in g

    def test_quad_with_non_matching_context_is_skipped(self) -> None:
        g = Graph(identifier=URIRef("urn:g"))
        other = Graph(identifier=URIRef("urn:other"))
        g.add_many([(subj, pred, obj, other)])
        assert (subj, pred, obj) not in g

    def test_mixed_triple_and_matching_quad(self) -> None:
        g = Graph(identifier=URIRef("urn:g"))
        s2, p2, o2 = URIRef("urn:s2"), URIRef("urn:p2"), URIRef("urn:o2")
        g.add_many([(subj, pred, obj), (s2, p2, o2, g)])
        assert (subj, pred, obj) in g
        assert (s2, p2, o2) in g

    def test_returns_self(self) -> None:
        g = Graph()
        assert g.add_many([(subj, pred, obj)]) is g

    def test_empty_input(self) -> None:
        g = Graph()
        g.add_many([])
        assert len(g) == 0


class TestConjunctiveGraphAddMany:
    def test_triple_goes_to_default_context(self) -> None:
        cg = ConjunctiveGraph()
        cg.add_many([(subj, pred, obj)])
        assert (subj, pred, obj) in cg.default_context

    def test_quad_goes_to_named_context(self) -> None:
        cg = ConjunctiveGraph()
        ctx = cg.get_context(URIRef("urn:ctx"))
        cg.add_many([(subj, pred, obj, ctx)])
        assert (subj, pred, obj) in ctx
        assert (subj, pred, obj) not in cg.default_context

    def test_mixed_triple_and_quad(self) -> None:
        cg = ConjunctiveGraph()
        ctx = cg.get_context(URIRef("urn:ctx"))
        s2, p2, o2 = URIRef("urn:s2"), URIRef("urn:p2"), URIRef("urn:o2")
        cg.add_many([(subj, pred, obj), (s2, p2, o2, ctx)])
        assert (subj, pred, obj) in cg.default_context
        assert (s2, p2, o2) in ctx

    def test_returns_self(self) -> None:
        cg = ConjunctiveGraph()
        assert cg.add_many([(subj, pred, obj)]) is cg

    def test_empty_input(self) -> None:
        cg = ConjunctiveGraph()
        cg.add_many([])
        assert len(cg) == 0


class TestDatasetAddMany:
    def test_triple_goes_to_default_context(self) -> None:
        ds = Dataset()
        ds.add_many([(subj, pred, obj)])
        assert (subj, pred, obj) in ds.default_context

    def test_quad_goes_to_named_context(self) -> None:
        ds = Dataset()
        ctx = ds.graph(URIRef("urn:ctx"))
        ds.add_many([(subj, pred, obj, ctx)])
        assert (subj, pred, obj) in ctx
        assert (subj, pred, obj) not in ds.default_context

    def test_returns_self(self) -> None:
        ds = Dataset()
        assert ds.add_many([(subj, pred, obj)]) is ds
