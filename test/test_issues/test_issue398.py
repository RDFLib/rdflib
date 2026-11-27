import pytest

from rdflib import ConjunctiveGraph, Dataset, Graph, URIRef


def test_conjunctive_graph_contains_checks_context() -> None:
    """Empty context graphs are falsy and must not fall back to the union graph."""
    s = URIRef("http://example.org/a")
    p = URIRef("http://example.org/b")
    o = URIRef("http://example.org/c")
    ctx1 = URIRef("http://example.org/ctx1")
    ctx2 = URIRef("http://example.org/ctx2")

    with pytest.warns(DeprecationWarning):
        cg = ConjunctiveGraph()
    cg.get_context(ctx1).add((s, p, o))

    assert (s, p, o, ctx1) in cg  # type: ignore[operator]
    assert (s, p, o, Graph(identifier=ctx1)) in cg
    assert (s, p, o, ctx2) not in cg  # type: ignore[operator]
    assert (s, p, o, Graph(identifier=ctx2)) not in cg
    assert list(cg.triples((s, p, o), context=Graph(identifier=ctx2))) == []


def test_dataset_contains_checks_context_when_in_default_graph() -> None:
    """Empty context graphs must not fall back to Dataset.default_graph."""
    s = URIRef("http://example.org/a")
    p = URIRef("http://example.org/b")
    o = URIRef("http://example.org/c")
    ctx2 = URIRef("http://example.org/ctx2")

    ds = Dataset()
    ds.default_graph.add((s, p, o))

    assert (s, p, o) in ds
    assert (s, p, o, ctx2) not in ds
    assert (s, p, o, Graph(identifier=ctx2)) not in ds
    assert list(ds.triples((s, p, o), context=Graph(identifier=ctx2))) == []
