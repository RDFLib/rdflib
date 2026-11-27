"""
Object to RDF Conversion (JSON-LD 1.1 Processing Algorithms and API, section
8.2.2) turns a native JSON value into a string before it applies a datatype: a
boolean into ``true`` or ``false`` (step 9); a number with a non-zero
fractional part or an absolute value of 10^21 or more, or any number under
``xsd:double``, into an ``xsd:double`` (step 10); and any other number into an
``xsd:integer`` (step 11).

The parser built the literal from the Python value instead, so the value did
not follow the datatype: ``1`` under ``xsd:float`` was a literal ``"1"^^xsd:float``
whose value is the integer 1, and ``true`` under ``xsd:string`` held the Python
``True``. Such a literal differs from the same literal read from N-Triples or
Turtle, and code that relies on the value, such as pySHACL's ``sh:datatype``
check, rejects it.

The expected literals are those pyld 3.3.0 produces for the same documents,
read with rdflib's N-Triples parser.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

import pytest

from rdflib import XSD, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection

NS = Namespace("http://example.org/ns/")
UNIT = "http://example.org/unit"

# (JSON value, datatype, the object pyld writes in N-Triples, type of the value)
TYPED_NATIVE_VALUES = [
    pytest.param(1, XSD.float, f'"1"^^<{XSD.float}>', float, id="integer-as-float"),
    pytest.param(
        2.5, XSD.float, f'"2.5E0"^^<{XSD.float}>', float, id="double-as-float"
    ),
    pytest.param(
        1, XSD.double, f'"1.0E0"^^<{XSD.double}>', float, id="integer-as-double"
    ),
    pytest.param(
        1.0, XSD.double, f'"1.0E0"^^<{XSD.double}>', float, id="whole-double-as-double"
    ),
    # Under xsd:double a whole number is still written as a double (step 10),
    # which keeps the sign of negative zero.
    pytest.param(
        -0.0,
        XSD.double,
        f'"-0.0E0"^^<{XSD.double}>',
        float,
        id="negative-zero-as-double",
    ),
    pytest.param(
        1, XSD.decimal, f'"1"^^<{XSD.decimal}>', Decimal, id="integer-as-decimal"
    ),
    pytest.param(True, XSD.string, f'"true"^^<{XSD.string}>', str, id="true-as-string"),
    pytest.param(
        False, XSD.string, f'"false"^^<{XSD.string}>', str, id="false-as-string"
    ),
    pytest.param(
        1, UNIT, f'"1"^^<{UNIT}>', type(None), id="integer-as-unknown-datatype"
    ),
    # Guards: these already had a value of the right type.
    pytest.param(1, XSD.integer, f'"1"^^<{XSD.integer}>', int, id="integer-as-integer"),
    pytest.param(
        1.0, XSD.integer, f'"1"^^<{XSD.integer}>', int, id="whole-double-as-integer"
    ),
    pytest.param(
        7,
        XSD.nonNegativeInteger,
        f'"7"^^<{XSD.nonNegativeInteger}>',
        int,
        id="integer-as-nonNegativeInteger",
    ),
    pytest.param(
        True, XSD.boolean, f'"true"^^<{XSD.boolean}>', bool, id="true-as-boolean"
    ),
    pytest.param("1", XSD.float, f'"1"^^<{XSD.float}>', float, id="string-as-float"),
]


def _from_ntriples(obj: str) -> Literal:
    (o,) = Graph().parse(data=f"<{NS.s}> <{NS.p}> {obj} .", format="nt").objects()
    assert isinstance(o, Literal)
    return o


def _parse(doc: dict[str, Any]) -> Graph:
    g = Graph()
    g.parse(data=json.dumps(doc), format="json-ld")
    return g


def _object(g: Graph) -> Literal:
    (o,) = g.objects(NS.s, NS.p)
    assert isinstance(o, Literal)
    return o


@pytest.mark.parametrize(
    ("value", "datatype", "expected", "python_type"), TYPED_NATIVE_VALUES
)
def test_a_value_under_a_datatype_term_is_the_literal_of_its_lexical_form(
    value: Any, datatype: URIRef, expected: str, python_type: type
) -> None:
    doc = {
        "@context": {"p": {"@id": str(NS.p), "@type": str(datatype)}},
        "@id": str(NS.s),
        "p": value,
    }

    parsed = _object(_parse(doc))

    assert parsed == _from_ntriples(expected)
    assert type(parsed.value) is python_type


@pytest.mark.parametrize(
    ("value", "datatype", "expected", "python_type"), TYPED_NATIVE_VALUES
)
def test_a_typed_value_object_is_the_literal_of_its_lexical_form(
    value: Any, datatype: URIRef, expected: str, python_type: type
) -> None:
    doc = {"@id": str(NS.s), str(NS.p): {"@value": value, "@type": str(datatype)}}

    parsed = _object(_parse(doc))

    assert parsed == _from_ntriples(expected)
    assert type(parsed.value) is python_type


@pytest.mark.parametrize(
    ("value", "datatype", "expected", "python_type"), TYPED_NATIVE_VALUES
)
def test_a_value_in_a_list_under_a_datatype_term_is_the_literal_of_its_lexical_form(
    value: Any, datatype: URIRef, expected: str, python_type: type
) -> None:
    doc = {
        "@context": {
            "p": {"@id": str(NS.p), "@type": str(datatype), "@container": "@list"}
        },
        "@id": str(NS.s),
        "p": [value],
    }
    g = _parse(doc)

    (head,) = g.objects(NS.s, NS.p)
    (parsed,) = Collection(g, head)

    assert isinstance(parsed, Literal)
    assert parsed == _from_ntriples(expected)
    assert type(parsed.value) is python_type


def test_a_number_of_10_to_the_21_or_more_is_written_as_a_double_under_any_datatype() -> (
    None
):
    """Step 10 applies whatever the datatype, so the integer literal is ill-typed, as in pyld."""
    doc = {
        "@context": {"p": {"@id": str(NS.p), "@type": str(XSD.integer)}},
        "@id": str(NS.s),
        "p": 10**21,
    }

    parsed = _object(_parse(doc))

    assert parsed.datatype == XSD.integer
    assert parsed.ill_typed
    assert float(parsed) == 1e21
