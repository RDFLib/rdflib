from __future__ import annotations

import pickle

import pytest

import rdflib
from rdflib import BNode, Graph, Literal, Namespace, TripleTerm, URIRef, Variable
from rdflib.term import Node

EX = Namespace("http://example.org/")


def test_public_exports() -> None:
    assert rdflib.TripleTerm is TripleTerm
    assert "TripleTerm" in rdflib.__all__
    assert "TripleTerm" in rdflib.term.__all__


@pytest.mark.parametrize("subject", [EX.subject, BNode("subject")])
@pytest.mark.parametrize(
    "object_",
    [
        EX.object,
        BNode("object"),
        Literal("object"),
        TripleTerm(EX.inner_subject, EX.inner_predicate, EX.inner_object),
    ],
)
def test_construction_and_properties(subject: Node, object_: Node) -> None:
    term = TripleTerm(subject, EX.predicate, object_)  # type: ignore[arg-type]

    assert term.subject == subject
    assert term.predicate == EX.predicate
    assert term.object == object_
    assert isinstance(term, Node)
    assert not isinstance(term, str)
    assert not isinstance(term, tuple)


@pytest.mark.parametrize(
    ("attribute", "value"),
    [
        ("subject", EX.other),
        ("predicate", EX.other),
        ("object", EX.other),
        ("_triple", (EX.other, EX.predicate, EX.object)),
        ("_hash", 0),
        ("extra", EX.other),
    ],
)
def test_immutable(attribute: str, value: object) -> None:
    term = TripleTerm(EX.subject, EX.predicate, EX.object)

    with pytest.raises(AttributeError, match="TripleTerm is immutable"):
        setattr(term, attribute, value)


def test_attributes_cannot_be_deleted() -> None:
    term = TripleTerm(EX.subject, EX.predicate, EX.object)

    with pytest.raises(AttributeError, match="TripleTerm is immutable"):
        del term._triple


@pytest.mark.parametrize(
    "subject",
    [Literal("subject"), Variable("subject"), "subject", 1],
)
def test_invalid_subject(subject: object) -> None:
    with pytest.raises(
        TypeError,
        match=f"TripleTerm subject must be URIRef or BNode, got {type(subject).__name__}",
    ):
        TripleTerm(subject, EX.predicate, EX.object)  # type: ignore[arg-type]


def test_triple_term_is_invalid_as_embedded_subject() -> None:
    inner = TripleTerm(EX.subject, EX.predicate, EX.object)

    with pytest.raises(TypeError, match="TripleTerm subject must be URIRef or BNode"):
        TripleTerm(inner, EX.predicate, EX.object)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "predicate",
    [BNode("predicate"), Literal("predicate"), Variable("predicate"), "predicate"],
)
def test_invalid_predicate(predicate: object) -> None:
    with pytest.raises(
        TypeError,
        match=f"TripleTerm predicate must be URIRef, got {type(predicate).__name__}",
    ):
        TripleTerm(EX.subject, predicate, EX.object)  # type: ignore[arg-type]


@pytest.mark.parametrize("object_", [Variable("object"), Graph(), "object", 1])
def test_invalid_object(object_: object) -> None:
    with pytest.raises(
        TypeError,
        match=f"TripleTerm object must be URIRef, BNode, Literal, or TripleTerm, got {type(object_).__name__}",
    ):
        TripleTerm(EX.subject, EX.predicate, object_)  # type: ignore[arg-type]


def test_structural_equality_and_hashing() -> None:
    first = TripleTerm(EX.subject, EX.predicate, Literal("object", lang="en"))
    second = TripleTerm(EX.subject, EX.predicate, Literal("object", lang="EN"))
    different = TripleTerm(EX.subject, EX.predicate, Literal("different"))

    assert first == second
    assert hash(first) == hash(second)
    assert first != different
    assert len({first, second, different}) == 2
    assert first != (EX.subject, EX.predicate, Literal("object", lang="en"))


def test_nested_structural_equality_and_hashing() -> None:
    first = TripleTerm(
        EX.outer_subject,
        EX.outer_predicate,
        TripleTerm(BNode("shared"), EX.inner_predicate, BNode("object")),
    )
    second = TripleTerm(
        EX.outer_subject,
        EX.outer_predicate,
        TripleTerm(BNode("shared"), EX.inner_predicate, BNode("object")),
    )

    assert first == second
    assert hash(first) == hash(second)


def test_deterministic_recursive_ordering() -> None:
    nested = TripleTerm(EX.inner_subject, EX.inner_predicate, EX.inner_object)
    terms = [
        TripleTerm(EX.b, EX.p, EX.o),
        TripleTerm(EX.a, EX.q, EX.o),
        TripleTerm(EX.a, EX.p, nested),
        TripleTerm(BNode("subject"), EX.p, EX.o),
        TripleTerm(EX.a, EX.p, Literal("object")),
        TripleTerm(EX.a, EX.p, EX.o),
    ]

    assert sorted(terms) == [
        terms[3],
        terms[5],
        terms[4],
        terms[2],
        terms[1],
        terms[0],
    ]


def test_ordering_interoperates_with_existing_node_ranks() -> None:
    term = TripleTerm(EX.subject, EX.predicate, EX.object)
    existing_nodes = [BNode("b"), Variable("v"), URIRef(EX.node), Literal("literal")]

    for node in existing_nodes:
        assert node < term
        assert term > node
        assert not node > term
        assert not term < node

    assert term > None
    assert not term < None
    assert sorted([term, *existing_nodes])[-1] == term  # type: ignore[type-var]


def test_n3() -> None:
    term = TripleTerm(EX.subject, EX.predicate, Literal("object", lang="en"))

    assert term.n3() == (
        '<<( <http://example.org/subject> <http://example.org/predicate> "object"@en )>>'
    )


def test_n3_propagates_namespace_manager_recursively() -> None:
    graph = Graph()
    graph.bind("ex", EX)
    inner = TripleTerm(EX.inner_subject, EX.inner_predicate, EX.inner_object)
    outer = TripleTerm(EX.outer_subject, EX.outer_predicate, inner)

    assert outer.n3(graph.namespace_manager) == (
        "<<( ex:outer_subject ex:outer_predicate "
        "<<( ex:inner_subject ex:inner_predicate ex:inner_object )>> )>>"
    )


def test_repr_and_str() -> None:
    term = TripleTerm(EX.subject, EX.predicate, EX.object)
    expected = (
        "TripleTerm(rdflib.term.URIRef('http://example.org/subject'), "
        "rdflib.term.URIRef('http://example.org/predicate'), "
        "rdflib.term.URIRef('http://example.org/object'))"
    )

    assert repr(term) == expected
    assert str(term) == expected


def test_pickle_round_trip_with_nested_term_and_bnodes() -> None:
    term = TripleTerm(
        BNode("outer"),
        EX.outer_predicate,
        TripleTerm(EX.inner_subject, EX.inner_predicate, BNode("inner")),
    )

    restored = pickle.loads(pickle.dumps(term, protocol=pickle.HIGHEST_PROTOCOL))

    assert restored == term
    assert hash(restored) == hash(term)
    assert isinstance(restored.object, TripleTerm)
    assert restored.object.object == BNode("inner")
