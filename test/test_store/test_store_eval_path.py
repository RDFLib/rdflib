"""Tests for Store.eval_path() and the fallback mechanism in Graph.triples()."""

from __future__ import annotations

from typing import Iterator, Optional, Tuple

import pytest

from rdflib import Graph, URIRef
from rdflib.graph import _ContextType, _ObjectType, _SubjectType
from rdflib.namespace import RDF, RDFS
from rdflib.paths import Path, SequencePath, ZeroOrMore
from rdflib.plugins.stores.memory import Memory
from rdflib.store import Store

# --- Test 1: Base Store raises NotImplementedError ---


def test_store_eval_path_raises_not_implemented() -> None:
    """The base Store.eval_path() raises NotImplementedError."""
    store = Store()
    path = RDF.type / RDFS.subClassOf
    with pytest.raises(NotImplementedError):
        list(store.eval_path(path, subj=None, obj=None, context=None))


# --- Test 2: Fallback mechanism ---


def test_fallback_to_path_eval() -> None:
    """When the store does not implement eval_path, Graph.triples() falls
    back to Path.eval() and returns correct results."""
    g = Graph()
    a = URIRef("http://example.org/A")
    b = URIRef("http://example.org/B")
    c = URIRef("http://example.org/C")

    g.add((a, RDF.type, b))
    g.add((b, RDFS.subClassOf, c))

    path = RDF.type / RDFS.subClassOf
    results = set(g.triples((a, path, None)))
    assert (a, path, c) in results


def test_fallback_alternative_path() -> None:
    """Fallback works for AlternativePath."""
    g = Graph()
    a = URIRef("http://example.org/A")
    b = URIRef("http://example.org/B")
    c = URIRef("http://example.org/C")

    g.add((a, RDF.type, b))
    g.add((a, RDFS.subClassOf, c))

    path = RDF.type | RDFS.subClassOf
    results = {(s, o) for s, p, o in g.triples((a, path, None))}
    assert (a, b) in results
    assert (a, c) in results


def test_fallback_mulpath() -> None:
    """Fallback works for MulPath (transitive closure)."""
    g = Graph()
    a = URIRef("http://example.org/A")
    b = URIRef("http://example.org/B")
    c = URIRef("http://example.org/C")

    g.add((a, RDFS.subClassOf, b))
    g.add((b, RDFS.subClassOf, c))

    path = RDFS.subClassOf * ZeroOrMore  # type: ignore[operator]
    results = {(s, o) for s, p, o in g.triples((a, path, None))}
    # ZeroOrMore includes the start node itself and transitive closure
    assert (a, a) in results
    assert (a, b) in results
    assert (a, c) in results


# --- Test 3: Store-level dispatch ---


class PathAwareStore(Memory):
    """A mock store that implements eval_path with known results."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eval_path_called = False
        self.eval_path_args = None

    def eval_path(
        self,
        path: Path,
        subj: Optional[_SubjectType] = None,
        obj: Optional[_ObjectType] = None,
        context: Optional[_ContextType] = None,
    ) -> Iterator[Tuple[_SubjectType, _ObjectType]]:
        self.eval_path_called = True
        self.eval_path_args = (path, subj, obj)
        # Return a known result to verify dispatch
        yield (
            URIRef("http://example.org/store_subj"),
            URIRef("http://example.org/store_obj"),
        )


def test_store_dispatch_eval_path() -> None:
    """When the store implements eval_path, Graph.triples() uses it
    instead of Path.eval()."""
    store = PathAwareStore()
    g = Graph(store=store)

    path = RDF.type / RDFS.subClassOf
    results = list(g.triples((None, path, None)))

    assert store.eval_path_called
    assert len(results) == 1
    s, p, o = results[0]
    assert s == URIRef("http://example.org/store_subj")
    assert p == path
    assert o == URIRef("http://example.org/store_obj")


def test_store_dispatch_passes_correct_args() -> None:
    """eval_path receives the correct path, subject, and object."""
    store = PathAwareStore()
    g = Graph(store=store)

    subj = URIRef("http://example.org/s")
    obj = URIRef("http://example.org/o")
    path = RDF.type / RDFS.subClassOf

    list(g.triples((subj, path, obj)))

    assert store.eval_path_args == (path, subj, obj)


# --- Test 4: Partial support (NotImplementedError for specific path types) ---


class PartialPathStore(Memory):
    """A store that only supports SequencePath, raises NotImplementedError
    for other path types."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eval_path_called = False

    def eval_path(
        self,
        path: Path,
        subj: Optional[_SubjectType] = None,
        obj: Optional[_ObjectType] = None,
        context: Optional[_ContextType] = None,
    ) -> Iterator[Tuple[_SubjectType, _ObjectType]]:
        if not isinstance(path, SequencePath):
            raise NotImplementedError(f"Path type {type(path).__name__} not supported")
        self.eval_path_called = True
        yield (URIRef("http://example.org/seq_s"), URIRef("http://example.org/seq_o"))


def test_partial_support_supported_path() -> None:
    """A store that supports SequencePath returns its own results."""
    store = PartialPathStore()
    g = Graph(store=store)

    path = RDF.type / RDFS.subClassOf
    results = list(g.triples((None, path, None)))

    assert store.eval_path_called
    assert len(results) == 1
    assert results[0][0] == URIRef("http://example.org/seq_s")


def test_partial_support_unsupported_path_falls_back() -> None:
    """A store that doesn't support MulPath falls back to Path.eval()."""
    store = PartialPathStore()
    g = Graph(store=store)

    a = URIRef("http://example.org/A")
    b = URIRef("http://example.org/B")
    c = URIRef("http://example.org/C")
    g.add((a, RDFS.subClassOf, b))
    g.add((b, RDFS.subClassOf, c))

    path = RDFS.subClassOf * ZeroOrMore  # type: ignore[operator]
    results = {(s, o) for s, p, o in g.triples((a, path, None))}

    # Should have fallen back to Path.eval and gotten real results
    assert not store.eval_path_called
    assert (a, b) in results
    assert (a, c) in results
