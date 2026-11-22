"""
JSON-LD gives a JSON number its datatype by value, not by how it is written.

Object to RDF Conversion (JSON-LD 1.1 Processing Algorithms and API, section
8.2.2): a number with a non-zero fractional part, or with an absolute value
of 10^21 or more, is an ``xsd:double``; any other number is an
``xsd:integer``. JSON has one number type, so ``1.0`` is the integer 1.

The parser typed numbers by their Python type, so ``1.0`` became a double.
The serializer wrote the double ``1.0`` as the JSON number ``1.0``, which a
conforming reader reads back as the integer 1.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from rdflib import XSD, Graph, Literal, Namespace
from rdflib.collection import Collection
from rdflib.compare import isomorphic
from rdflib.plugins.parsers.jsonld import to_rdf

EX = Namespace("http://example.org/")
CONTEXT = {"@vocab": str(EX)}

NUMBERS = [
    pytest.param("1", Literal(1), id="integer"),
    pytest.param("1.0", Literal(1), id="integral-decimal"),
    pytest.param("1.5e3", Literal(1500), id="integral-exponent"),
    pytest.param("-0.0", Literal(0), id="negative-zero"),
    pytest.param("2.5", Literal(2.5), id="fraction"),
    pytest.param("1e21", Literal(1e21), id="exponent-at-10^21"),
    pytest.param("1000000000000000000000", Literal(1e21), id="integer-at-10^21"),
]


def _parse(value: Any) -> Graph:
    doc = {"@id": str(EX.s), str(EX.p): value}
    g = Graph()
    g.parse(data=json.dumps(doc), format="json-ld")
    return g


def _strict_json(data: str) -> Any:
    """Parse JSON that must not use NaN or Infinity, which JSON lacks."""

    def reject(constant: str) -> None:
        raise ValueError(f"not JSON: {constant}")

    return json.loads(data, parse_constant=reject)


@pytest.mark.parametrize(("number", "literal"), NUMBERS)
def test_a_json_number_is_typed_by_its_value(number: str, literal: Literal) -> None:
    (parsed,) = _parse(json.loads(number)).objects()

    assert parsed == literal


@pytest.mark.parametrize(("number", "literal"), NUMBERS)
def test_a_number_value_object_is_typed_by_its_value(
    number: str, literal: Literal
) -> None:
    (parsed,) = _parse({"@value": json.loads(number)}).objects()

    assert parsed == literal


@pytest.mark.parametrize(("number", "literal"), NUMBERS)
def test_a_number_list_member_is_typed_by_its_value(
    number: str, literal: Literal
) -> None:
    g = _parse({"@list": [json.loads(number)]})

    (head,) = g.objects(EX.s, EX.p)
    assert list(Collection(g, head)) == [literal]


def test_an_integer_beyond_a_double_is_infinity() -> None:
    """A JSON number too large for a double, as a JavaScript reader reads it.

    Passed as a Python value, as the standard json module would also give it.
    """
    g = Graph()
    to_rdf({"@id": str(EX.s), str(EX.p): -(10**309)}, g)

    (parsed,) = g.objects()
    assert parsed == Literal(float("-inf"))


def test_an_explicitly_typed_number_keeps_its_type() -> None:
    """Guard: a datatype given in the document is used as before."""
    (parsed,) = _parse({"@value": 1.0, "@type": str(XSD.double)}).objects()

    assert isinstance(parsed, Literal)
    assert parsed.datatype == XSD.double


@pytest.mark.parametrize(
    "literal",
    [
        pytest.param(Literal(1.0), id="integral-double"),
        pytest.param(Literal(0.0), id="zero-double"),
        pytest.param(Literal(10**21), id="integer-at-10^21"),
        pytest.param(Literal(2**53), id="integer-beyond-2^53"),
        pytest.param(Literal(2**64 + 1), id="integer-beyond-64-bits"),
        pytest.param(Literal(-(2**63) - 1), id="negative-beyond-64-bits"),
        pytest.param(Literal("abc", datatype=XSD.integer), id="ill-typed-integer"),
        pytest.param(Literal(True, datatype=XSD.integer), id="boolean-as-integer"),
        pytest.param(Literal(float("nan")), id="nan"),
        pytest.param(Literal(float("inf")), id="infinity"),
    ],
)
def test_a_value_a_reader_would_retype_is_written_with_its_type(
    literal: Literal,
) -> None:
    g = Graph()
    g.add((EX.s, EX.p, literal))

    data = g.serialize(format="json-ld", context=CONTEXT)
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    value = _strict_json(data)["p"]
    assert value == {"@type": str(literal.datatype), "@value": str(literal)}
    assert isomorphic(g, g2)


@pytest.mark.parametrize(
    ("literal", "native"),
    [
        pytest.param(Literal(2.5), 2.5, id="fractional-double"),
        pytest.param(Literal(5), 5, id="integer"),
        pytest.param(Literal(2**53 - 1), 2**53 - 1, id="largest-interoperable-integer"),
        pytest.param(Literal(True), True, id="boolean"),
        pytest.param(Literal("x"), "x", id="string"),
    ],
)
def test_a_value_a_reader_types_the_same_is_still_native(
    literal: Literal, native: Any
) -> None:
    """Guard: these are read back with their own datatype."""
    g = Graph()
    g.add((EX.s, EX.p, literal))

    data = g.serialize(format="json-ld", context=CONTEXT)
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert _strict_json(data)["p"] == native
    assert isomorphic(g, g2)
