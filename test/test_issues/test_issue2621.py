from __future__ import annotations

from typing import Any

import pytest

from rdflib import Dataset, Graph, Literal, Namespace
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib.query import Result

EX = Namespace("https://www.example.org/")
FALSY_LITERALS = [Literal(""), Literal(0), Literal(False)]


class _InMemorySPARQLUpdateStore(SPARQLUpdateStore):
    def __init__(self) -> None:
        super().__init__(
            query_endpoint="http://example.org/sparql",
            update_endpoint="http://example.org/update",
        )
        self._backing = Dataset()

    def _query(self, *args: Any, **kwargs: Any) -> Result:
        query = args[0]
        default_graph = kwargs.get("default_graph")
        if default_graph is not None:
            return self._backing.graph(default_graph).query(query)
        return self._backing.query(query)

    def _update(self, update: str) -> None:
        self._backing.update(update)


@pytest.mark.parametrize("falsy", FALSY_LITERALS)
def test_sparqlstore_triples_with_falsy_literal(falsy: Literal) -> None:
    store = _InMemorySPARQLUpdateStore()
    g = Graph(store=store, identifier=EX.g1)
    g.add((EX.a, EX.b, falsy))
    g.add((EX.a, EX.b, EX.c))

    assert list(g.triples((EX.a, EX.b, falsy))) == [(EX.a, EX.b, falsy)]
    assert list(g.triples((None, EX.b, falsy))) == [(EX.a, EX.b, falsy)]


@pytest.mark.parametrize("falsy", FALSY_LITERALS)
def test_sparqlstore_contexts_with_falsy_literal(falsy: Literal) -> None:
    store = _InMemorySPARQLUpdateStore()
    g1 = Graph(store=store, identifier=EX.g1)
    g2 = Graph(store=store, identifier=EX.g2)
    g1.add((EX.a, EX.b, falsy))
    g2.add((EX.a, EX.b, EX.c))

    assert list(store.contexts((EX.a, EX.b, falsy))) == [EX.g1]


@pytest.mark.parametrize("falsy", FALSY_LITERALS)
def test_sparqlupdatestore_remove_with_falsy_literal(falsy: Literal) -> None:
    store = _InMemorySPARQLUpdateStore()
    g = Graph(store=store, identifier=EX.g1)
    g.add((EX.a, EX.b, falsy))
    g.add((EX.a, EX.b, EX.c))

    g.remove((EX.a, EX.b, falsy))

    assert list(store._backing.graph(EX.g1).triples((None, None, None))) == [
        (EX.a, EX.b, EX.c)
    ]
