"""
The JSON-LD serializer shortens an IRI only to a name that expands back to it.

With ``@vocab`` or a prefix, ``http://example.org/name`` can be written as
``name`` or ``ex:name``. If the context defines that name as a term for a
different IRI, or as a keyword alias, a reader expands it to something else.
IRI Compaction (JSON-LD 1.1 Processing Algorithms and API, section 6.2.2,
steps 5.1 and 7.3) uses such a name only when it is not a term. The outputs
of these cases were also checked with pyld during review.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from rdflib import RDF, Graph, Literal, Namespace
from rdflib.compare import isomorphic
from rdflib.plugins.shared.jsonld.context import Context
from rdflib.term import Node

EX = Namespace("http://example.org/")
OTHER = Namespace("http://other.org/")
A = Namespace("http://a.example/")
VOCAB_CONTEXT = {"@vocab": str(EX), "name": str(OTHER.name)}
# A prefix redefined later in the context: "ex:" now means OTHER.
REDEFINED_PREFIX = [{"ex": str(EX)}, {"ex": str(OTHER)}]
# A term "p" for the vocabulary itself, which also makes it a prefix.
PREFIX_NAMED_LIKE_A_NAME = {"@vocab": str(A), "p": str(A)}
KEYWORD_ALIASES = {"@vocab": str(EX), "type": "@type", "id": "@id"}


@pytest.mark.parametrize(
    ("context", "iri", "expected"),
    [
        pytest.param(VOCAB_CONTEXT, EX.name, str(EX.name), id="name-is-a-term"),
        pytest.param(VOCAB_CONTEXT, EX.age, "age", id="name-is-free"),
        pytest.param(VOCAB_CONTEXT, OTHER.name, "name", id="the-term-itself"),
        pytest.param(REDEFINED_PREFIX, EX.name, str(EX.name), id="stale-prefix"),
        pytest.param(REDEFINED_PREFIX, OTHER.name, "ex:name", id="current-prefix"),
        pytest.param(PREFIX_NAMED_LIKE_A_NAME, A.p, "p:p", id="name-is-a-prefix"),
        pytest.param(KEYWORD_ALIASES, EX.type, str(EX.type), id="keyword-alias"),
        pytest.param(
            {"@vocab": str(EX), "name": None}, EX.name, str(EX.name), id="null-term"
        ),
        pytest.param({"@vocab": str(EX)}, EX["a:b"], str(EX["a:b"]), id="colon"),
        pytest.param({"@vocab": str(EX)}, EX["@type"], str(EX["@type"]), id="keyword"),
        pytest.param({"@vocab": str(EX)}, EX[""], str(EX[""]), id="the-vocabulary"),
    ],
)
def test_to_symbol_returns_a_name_that_expands_back(
    context: Any, iri: str, expected: str
) -> None:
    ctx = Context(context)

    symbol = ctx.to_symbol(iri)

    assert symbol == expected
    assert ctx.expand(symbol) == str(iri)


@pytest.mark.parametrize(
    ("context", "triple"),
    [
        pytest.param(VOCAB_CONTEXT, (EX.s, EX.name, Literal("x")), id="property"),
        pytest.param(REDEFINED_PREFIX, (EX.s, EX.name, Literal("x")), id="prefix"),
        pytest.param(KEYWORD_ALIASES, (EX.s, EX.id, Literal("x")), id="keyword-alias"),
        pytest.param(VOCAB_CONTEXT, (EX.s, RDF.type, EX.name), id="type"),
        pytest.param(
            VOCAB_CONTEXT,
            (EX.s, EX.p, Literal("x", datatype=EX.name)),
            id="datatype",
        ),
        pytest.param(
            {**VOCAB_CONTEXT, "ref": {"@id": str(EX.ref), "@type": "@vocab"}},
            (EX.s, EX.ref, EX.name),
            id="vocab-coerced-value",
        ),
        # Terms for the same IRI that read a value differently.
        pytest.param(
            {"@vocab": str(EX), "name": {"@reverse": str(EX.name)}},
            (EX.s, EX.name, EX.o),
            id="reverse-term",
        ),
        pytest.param(
            {"@vocab": str(EX), "name": {"@id": str(EX.name), "@language": "en"}},
            (EX.s, EX.name, Literal("x")),
            id="language-term",
        ),
    ],
)
def test_a_value_named_like_a_term_round_trips(
    context: Any, triple: tuple[Node, Node, Node]
) -> None:
    g = Graph()
    g.add(triple)

    data = g.serialize(format="json-ld", context=context)
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert isomorphic(g, g2), json.loads(data)
