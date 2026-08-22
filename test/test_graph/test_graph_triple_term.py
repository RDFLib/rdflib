from __future__ import annotations

import pytest

from rdflib import RDF, BNode, Dataset, Graph, Namespace, TripleTerm
from rdflib.graph import QuotedGraph

EX = Namespace("http://example.org/")


def test_memory_store_add_query_contains_and_remove() -> None:
    graph = Graph()
    term = TripleTerm(EX.subject, EX.predicate, EX.object)
    triple = (EX.reifier, RDF.reifies, term)

    graph.add(triple)

    assert triple in graph
    assert list(graph.triples((EX.reifier, RDF.reifies, term))) == [triple]
    assert list(graph.triples((None, RDF.reifies, term))) == [triple]
    assert list(graph.triples((EX.reifier, None, None))) == [triple]

    graph.remove(triple)

    assert triple not in graph
    assert len(graph) == 0


def test_arbitrary_predicate_is_allowed() -> None:
    graph = Graph()
    term = TripleTerm(EX.subject, EX.predicate, EX.object)
    triple = (EX.resource, EX.references_proposition, term)

    graph.add(triple)

    assert triple in graph


def test_equal_triple_terms_are_the_same_store_key() -> None:
    graph = Graph()
    first = TripleTerm(EX.subject, EX.predicate, EX.object)
    second = TripleTerm(EX.subject, EX.predicate, EX.object)

    graph.add((EX.resource, EX.predicate, first))
    graph.add((EX.resource, EX.predicate, second))

    assert len(graph) == 1
    assert (EX.resource, EX.predicate, second) in graph


def test_nested_triple_term_with_bnodes() -> None:
    graph = Graph()
    inner = TripleTerm(BNode("subject"), EX.inner_predicate, BNode("object"))
    outer = TripleTerm(EX.outer_subject, EX.outer_predicate, inner)
    triple = (EX.resource, EX.references_proposition, outer)

    graph.add(triple)

    assert list(graph.objects(EX.resource, EX.references_proposition)) == [outer]
    assert list(graph.triples((None, None, outer))) == [triple]


@pytest.mark.parametrize("position", ["subject", "predicate"])
def test_graph_add_rejects_invalid_position(position: str) -> None:
    graph = Graph()
    term = TripleTerm(EX.embedded_subject, EX.embedded_predicate, EX.embedded_object)
    triple = (
        (term, EX.predicate, EX.object)
        if position == "subject"
        else (EX.subject, term, EX.object)
    )

    with pytest.raises(
        TypeError, match=f"TripleTerm cannot be used as an RDF {position}"
    ):
        graph.add(triple)

    assert len(graph) == 0


def test_triple_term_subject_pattern_returns_no_results() -> None:
    graph = Graph()
    term = TripleTerm(EX.embedded_subject, EX.embedded_predicate, EX.embedded_object)
    graph.add((EX.subject, EX.predicate, term))

    assert list(graph.triples((term, None, None))) == []


def test_graph_addn_accepts_object() -> None:
    graph = Graph()
    term = TripleTerm(EX.embedded_subject, EX.embedded_predicate, EX.embedded_object)
    triple = (EX.subject, EX.predicate, term)

    graph.addN([(*triple, graph)])

    assert triple in graph


@pytest.mark.parametrize("position", ["subject", "predicate"])
def test_graph_addn_rejects_invalid_position(position: str) -> None:
    graph = Graph()
    term = TripleTerm(EX.embedded_subject, EX.embedded_predicate, EX.embedded_object)
    triple = (
        (term, EX.predicate, EX.object)
        if position == "subject"
        else (EX.subject, term, EX.object)
    )

    with pytest.raises(
        TypeError, match=f"TripleTerm cannot be used as an RDF {position}"
    ):
        graph.addN([(*triple, graph)])

    assert len(graph) == 0


def test_dataset_add_and_addn() -> None:
    dataset = Dataset()
    direct = TripleTerm(EX.subject, EX.predicate, EX.object)
    nested = TripleTerm(EX.outer_subject, EX.outer_predicate, direct)

    dataset.add((EX.first, EX.references_proposition, direct))
    dataset.addN(
        [
            (
                EX.second,
                EX.references_proposition,
                nested,
                dataset.default_graph,
            )
        ]
    )

    assert (EX.first, EX.references_proposition, direct) in dataset.default_graph
    assert (EX.second, EX.references_proposition, nested) in dataset.default_graph


@pytest.mark.parametrize("method", ["add", "addN"])
@pytest.mark.parametrize("position", ["subject", "predicate"])
def test_dataset_rejects_invalid_position(method: str, position: str) -> None:
    dataset = Dataset()
    term = TripleTerm(EX.embedded_subject, EX.embedded_predicate, EX.embedded_object)
    triple = (
        (term, EX.predicate, EX.object)
        if position == "subject"
        else (EX.subject, term, EX.object)
    )

    with pytest.raises(
        TypeError, match=f"TripleTerm cannot be used as an RDF {position}"
    ):
        if method == "add":
            dataset.add(triple)
        else:
            dataset.addN([(*triple, dataset.default_graph)])

    assert len(dataset) == 0


def test_quoted_graph_accepts_triple_term_as_object() -> None:
    store = Graph().store
    graph = QuotedGraph(store, BNode("formula"))
    term = TripleTerm(EX.embedded_subject, EX.embedded_predicate, EX.embedded_object)

    graph.add((EX.subject, EX.predicate, term))

    assert (EX.subject, EX.predicate, term) in graph


@pytest.mark.parametrize("position", ["subject", "predicate"])
def test_quoted_graph_rejects_invalid_position(position: str) -> None:
    store = Graph().store
    graph = QuotedGraph(store, BNode("formula"))
    term = TripleTerm(EX.embedded_subject, EX.embedded_predicate, EX.embedded_object)
    triple = (
        (term, EX.predicate, EX.object)
        if position == "subject"
        else (EX.subject, term, EX.object)
    )

    with pytest.raises(
        TypeError, match=f"TripleTerm cannot be used as an RDF {position}"
    ):
        graph.add(triple)

    assert len(graph) == 0
