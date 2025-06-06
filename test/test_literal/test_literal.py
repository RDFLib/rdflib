from __future__ import annotations

import builtins
import datetime
import logging
from collections.abc import Generator
from decimal import Decimal
from typing import Any, Callable, Union

from rdflib.xsd_datetime import Duration
from test.utils import affix_tuples
from test.utils.literal import LiteralChecker, literal_idfn
from test.utils.namespace import EGDC
from test.utils.outcome import OutcomeChecker, OutcomePrimitive, OutcomePrimitives

# NOTE: The config below enables strict mode for mypy.
# mypy: no_ignore_errors
# mypy: warn_unused_configs, disallow_any_generics
# mypy: disallow_subclassing_any, disallow_untyped_calls
# mypy: disallow_untyped_defs, disallow_incomplete_defs
# mypy: check_untyped_defs, disallow_untyped_decorators
# mypy: no_implicit_optional, warn_redundant_casts, warn_unused_ignores
# mypy: warn_return_any, no_implicit_reexport, strict_equality


try:
    import html5rdf as _  # noqa: F401

    _HAVE_HTML5RDF = True
except ImportError:
    _HAVE_HTML5RDF = False

import pytest

import rdflib  # needed for eval(repr(...)) below
from rdflib import XSD
from rdflib.namespace import RDF
from rdflib.term import (
    _XSD_BOOLEAN,
    _XSD_DATE,
    _XSD_DATETIME,
    _XSD_DECIMAL,
    _XSD_DOUBLE,
    _XSD_DURATION,
    _XSD_FLOAT,
    _XSD_INTEGER,
    _XSD_STRING,
    _XSD_TIME,
    Literal,
    URIRef,
    _reset_bindings,
    bind,
)


# Untyped decorator makes function untyped
@pytest.fixture()  # type: ignore[misc, unused-ignore]
def clear_bindings() -> Generator[None, None, None]:
    try:
        yield
    finally:
        _reset_bindings()


def test_repr_apostrophe() -> None:
    a = rdflib.Literal("'")
    b = eval(repr(a))
    assert a == b


def test_repr_quote() -> None:
    a = rdflib.Literal('"')
    b = eval(repr(a))
    assert a == b


def test_backslash() -> None:
    d = r"""
<rdf:RDF
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:foo="http://example.org/foo#">
<rdf:Description>
    <foo:bar>a\b</foo:bar>
</rdf:Description>
</rdf:RDF>
"""
    g = rdflib.Graph()
    g.parse(data=d, format="xml")
    a = rdflib.Literal("a\\b")
    b = list(g.objects())[0]
    assert a == b


def test_literal_from_bool() -> None:
    _l = rdflib.Literal(True)
    assert _l.datatype == rdflib.XSD["boolean"]


# Untyped decorator makes function untyped
@pytest.mark.parametrize(  # type: ignore[misc, unused-ignore]
    "lang, exception_type",
    [
        ({}, TypeError),
        ([], TypeError),
        (1, TypeError),
        (b"en", TypeError),
        ("999", ValueError),
        ("-", ValueError),
    ],
)
def test_cant_pass_invalid_lang(
    lang: Any,
    exception_type: type[Exception],
) -> None:
    """
    Construction of Literal fails if the language tag is invalid.
    """
    with pytest.raises(exception_type):
        Literal("foo", lang=lang)


# Untyped decorator makes function untyped
@pytest.mark.parametrize(  # type: ignore[misc, unused-ignore]
    "lexical, datatype, is_ill_typed",
    [
        ("true", XSD.boolean, False),
        ("1", XSD.boolean, False),
        (b"false", XSD.boolean, False),
        (b"0", XSD.boolean, False),
        ("yes", XSD.boolean, True),
        ("200", XSD.byte, True),
        (b"-128", XSD.byte, False),
        ("127", XSD.byte, False),
        ("255", XSD.unsignedByte, False),
        ("-100", XSD.unsignedByte, True),
        (b"200", XSD.unsignedByte, False),
        (b"64300", XSD.short, True),
        ("-6000", XSD.short, False),
        ("1000000", XSD.nonNegativeInteger, False),
        ("-100", XSD.nonNegativeInteger, True),
        ("a", XSD.double, True),
        ("0", XSD.double, False),
        ("0.1", XSD.double, False),
        ("0.1", XSD.decimal, False),
        ("0.g", XSD.decimal, True),
        ("b", XSD.integer, True),
        ("2147483647", XSD.int, False),
        ("2147483648", XSD.int, True),
        ("2147483648", XSD.integer, False),
        ("valid ASCII", XSD.string, False),
        pytest.param("هذا رجل ثلج⛄", XSD.string, False, id="snowman-ar"),
        ("More ASCII", None, None),
        ("Not a valid time", XSD.time, True),
        ("Not a valid date", XSD.date, True),
        ("7264666c6962", XSD.hexBinary, False),
        # RDF.langString is not a recognized datatype IRI as we assign no literal value to it, though this should likely change.
        ("English string", RDF.langString, None),
        # The datatypes IRIs below should never be recognized.
        ("[p]", EGDC.unrecognized, None),
    ],
)
def test_ill_typed_literals(
    lexical: Union[bytes, str],
    datatype: URIRef | None,
    is_ill_typed: bool | None,
) -> None:
    """
    ill_typed has the correct value.
    """
    lit = Literal(lexical, datatype=datatype)
    assert lit.ill_typed is is_ill_typed
    if is_ill_typed is False:
        # If the literal is not ill typed it should have a value associated with it.
        assert lit.value is not None


# Untyped decorator makes function untyped
@pytest.mark.parametrize(  # type: ignore[misc, unused-ignore]
    "a, b, op, expected_result",
    [
        pytest.param(
            Literal("20:00:00", datatype=_XSD_STRING),
            Literal("23:30:00", datatype=_XSD_STRING),
            "bminusa",
            TypeError(r"unsupported operand type\(s\) for -: 'str' and 'str'"),
            id="Attempt to subtract strings",
        ),
        pytest.param(
            Literal("20:00:00", datatype=_XSD_TIME),
            Literal("23:30:00", datatype=_XSD_STRING),
            "aplusb",
            TypeError(
                "Cannot add a Literal of datatype http://www.w3.org/2001/XMLSchema#string to a Literal of datatype http://www.w3.org/2001/XMLSchema#time"
            ),
            id="Attempt to add string to time",
        ),
        pytest.param(
            Literal("20:00:00", datatype=_XSD_TIME),
            Literal("23:30:00", datatype=_XSD_STRING),
            "bminusa",
            TypeError(
                "Cannot subtract a Literal of datatype http://www.w3.org/2001/XMLSchema#time from a Literal of datatype http://www.w3.org/2001/XMLSchema#string"
            ),
            id="Attempt to subtract string from time",
        ),
        pytest.param(
            Literal("20:52:00", datatype=_XSD_TIME),
            Literal("12", datatype=_XSD_INTEGER),
            "aplusb",
            TypeError(
                "Cannot add a Literal of datatype http://www.w3.org/2001/XMLSchema#integer to a Literal of datatype http://www.w3.org/2001/XMLSchema#time"
            ),
            id="Attempt to add integer to time",
        ),
        pytest.param(
            Literal("20:52:00", datatype=_XSD_TIME),
            Literal("12", datatype=_XSD_INTEGER),
            "bplusa",
            TypeError(
                "Cannot add a Literal of datatype http://www.w3.org/2001/XMLSchema#time to a Literal of datatype http://www.w3.org/2001/XMLSchema#integer"
            ),
            id="Attempt to add time to integer",
        ),
        pytest.param(
            Literal("20:52:00", datatype=_XSD_TIME),
            Literal("12", datatype=_XSD_INTEGER),
            "aminusb",
            TypeError(
                "Cannot subtract a Literal of datatype http://www.w3.org/2001/XMLSchema#integer from a Literal of datatype http://www.w3.org/2001/XMLSchema#time"
            ),
            id="Attempt to subtract integer from time",
        ),
        pytest.param(
            Literal("20:52:00", datatype=_XSD_TIME),
            Literal("12", datatype=_XSD_INTEGER),
            "bminusa",
            TypeError(
                "Cannot subtract a Literal of datatype http://www.w3.org/2001/XMLSchema#time from a Literal of datatype http://www.w3.org/2001/XMLSchema#integer"
            ),
            id="Attempt to subtract time from integer",
        ),
        pytest.param(
            Literal("12", datatype=_XSD_INTEGER),
            Literal("P122DT15H58M", datatype=_XSD_DURATION),
            "aplusb",
            TypeError(
                "Cannot add a Literal of datatype http://www.w3.org/2001/XMLSchema#duration to a Literal of datatype http://www.w3.org/2001/XMLSchema#integer"
            ),
            id="Attempt to add duration to integer",
        ),
        pytest.param(
            Literal("12", datatype=_XSD_INTEGER),
            Literal("P122DT15H58M", datatype=_XSD_DURATION),
            "bplusa",
            TypeError(
                "Cannot add a Literal of datatype http://www.w3.org/2001/XMLSchema#integer to a Literal of datatype http://www.w3.org/2001/XMLSchema#duration"
            ),
            id="Attempt to add integer to duration",
        ),
        pytest.param(
            Literal("12", datatype=_XSD_INTEGER),
            Literal("P122DT15H58M", datatype=_XSD_DURATION),
            "aminusb",
            TypeError(
                "Cannot subtract a Literal of datatype http://www.w3.org/2001/XMLSchema#duration from a Literal of datatype http://www.w3.org/2001/XMLSchema#integer"
            ),
            id="Attempt to subtract duration from integer",
        ),
        pytest.param(
            Literal("12", datatype=_XSD_INTEGER),
            Literal("P122DT15H58M", datatype=_XSD_DURATION),
            "bminusa",
            TypeError(
                "Cannot subtract a Literal of datatype http://www.w3.org/2001/XMLSchema#integer from a Literal of datatype http://www.w3.org/2001/XMLSchema#duration"
            ),
            id="Attempt to subtract integer from duration",
        ),
        (
            Literal("2006-01-01T20:50:00", datatype=_XSD_DATETIME),
            Literal("2006-02-01T20:50:00", datatype=_XSD_DATETIME),
            "bminusa",
            Literal("P31D", datatype=_XSD_DURATION),
        ),
        (
            Literal("2006-01-02T20:50:00", datatype=_XSD_DATETIME),
            Literal("2006-05-01T20:50:00", datatype=_XSD_DATETIME),
            "bminusa",
            Literal("P119D", datatype=_XSD_DURATION),
        ),
        (
            Literal("2006-07-01T20:52:00", datatype=_XSD_DATETIME),
            Literal("2006-11-01T12:50:00", datatype=_XSD_DATETIME),
            "aminusb",
            Literal("-P122DT15H58M", datatype=_XSD_DURATION),
        ),
        (
            Literal("2006-07-01T20:52:00", datatype=_XSD_DATETIME),
            Literal("2006-11-01T12:50:00", datatype=_XSD_DATETIME),
            "bminusa",
            Literal("P122DT15H58M", datatype=_XSD_DURATION),
        ),
        (
            Literal("2006-07-01T20:52:00", datatype=_XSD_DATE),
            Literal("2006-11-01T12:50:00", datatype=_XSD_DATE),
            "bminusa",
            Literal("P123D", datatype=_XSD_DURATION),
        ),
        (
            Literal("2006-08-01", datatype=_XSD_DATE),
            Literal("2006-11-01", datatype=_XSD_DATE),
            "bminusa",
            Literal("P92D", datatype=_XSD_DURATION),
        ),
        (
            Literal("20:52:00", datatype=_XSD_TIME),
            Literal("12:50:00", datatype=_XSD_TIME),
            "bminusa",
            Literal("-PT8H2M", datatype=_XSD_DURATION),
        ),
        (
            Literal("20:00:00", datatype=_XSD_TIME),
            Literal("23:30:00", datatype=_XSD_TIME),
            "bminusa",
            Literal("PT3H30M", datatype=_XSD_DURATION),
        ),
        (
            Literal("2006-01-01T20:50:00", datatype=_XSD_DATETIME),
            Literal("P31D", datatype=_XSD_DURATION),
            "aplusb",
            Literal("2006-02-01T20:50:00", datatype=_XSD_DATETIME),
        ),
        (
            Literal("2006-01-02T20:50:00", datatype=_XSD_DATETIME),
            Literal("P119D", datatype=_XSD_DURATION),
            "aplusb",
            Literal("2006-05-01T20:50:00", datatype=_XSD_DATETIME),
        ),
        (
            Literal("2006-07-01T20:52:00", datatype=_XSD_DATETIME),
            Literal("P122DT15H58M", datatype=_XSD_DURATION),
            "aplusb",
            Literal("2006-11-01T12:50:00", datatype=_XSD_DATETIME),
        ),
        (
            Literal("2006-07-01T20:52:00", datatype=_XSD_DATE),
            Literal("P123D", datatype=_XSD_DURATION),
            "aplusb",
            Literal("2006-11-01T12:50:00", datatype=_XSD_DATE),
        ),
        (
            Literal("2006-08-01", datatype=_XSD_DATE),
            Literal("P92D", datatype=_XSD_DURATION),
            "aplusb",
            Literal("2006-11-01", datatype=_XSD_DATE),
        ),
        (
            Literal("20:52:00", datatype=_XSD_TIME),
            Literal("-PT8H2M", datatype=_XSD_DURATION),
            "aplusb",
            Literal("12:50:00", datatype=_XSD_TIME),
        ),
        (
            Literal("20:00:00", datatype=_XSD_TIME),
            Literal("PT3H30M", datatype=_XSD_DURATION),
            "aplusb",
            Literal("23:30:00", datatype=_XSD_TIME),
        ),
        (
            Literal("3", datatype=_XSD_INTEGER),
            Literal("5", datatype=_XSD_INTEGER),
            "aplusb",
            Literal("8", datatype=_XSD_INTEGER),
        ),
        (
            Literal("3", datatype=_XSD_INTEGER),
            Literal("5", datatype=_XSD_INTEGER),
            "bminusa",
            Literal("2", datatype=_XSD_INTEGER),
        ),
        (
            Literal("5.3", datatype=_XSD_FLOAT),
            Literal("8.5", datatype=_XSD_FLOAT),
            "bminusa",
            Literal("3.2", datatype=_XSD_FLOAT),
        ),
        (
            Literal("5.3", datatype=_XSD_DECIMAL),
            Literal("8.5", datatype=_XSD_DECIMAL),
            "bminusa",
            Literal("3.2", datatype=_XSD_DECIMAL),
        ),
        (
            Literal("5.3", datatype=_XSD_DOUBLE),
            Literal("8.5", datatype=_XSD_DOUBLE),
            "aminusb",
            Literal("-3.2", datatype=_XSD_DOUBLE),
        ),
        (
            Literal("8.5", datatype=_XSD_DOUBLE),
            Literal("5.3", datatype=_XSD_DOUBLE),
            "aminusb",
            Literal("3.2", datatype=_XSD_DOUBLE),
        ),
        (
            Literal(Duration(hours=1)),
            Literal(Duration(hours=1)),
            "aplusb",
            Literal(Duration(hours=2)),
        ),
        (
            Literal(datetime.timedelta(days=1)),
            Literal(datetime.timedelta(days=1)),
            "aplusb",
            Literal(datetime.timedelta(days=2)),
        ),
        (
            Literal(datetime.time.fromisoformat("04:23:01.000384")),
            Literal(Duration(hours=1)),
            "aplusb",
            Literal("05:23:01.000384", datatype=XSD.time),
        ),
        (
            Literal(datetime.date.fromisoformat("2011-11-04")),
            Literal(Duration(days=1)),
            "aplusb",
            Literal("2011-11-05", datatype=XSD.date),
        ),
        (
            Literal(datetime.datetime.fromisoformat("2011-11-04 00:05:23.283+00:00")),
            Literal(Duration(days=1)),
            "aplusb",
            Literal("2011-11-05T00:05:23.283000+00:00", datatype=XSD.dateTime),
        ),
        (
            Literal(datetime.time.fromisoformat("04:23:01.000384")),
            Literal(datetime.timedelta(hours=1)),
            "aplusb",
            Literal("05:23:01.000384", datatype=XSD.time),
        ),
        (
            Literal(datetime.date.fromisoformat("2011-11-04")),
            Literal(datetime.timedelta(days=1)),
            "aplusb",
            Literal("2011-11-05", datatype=XSD.date),
        ),
        (
            Literal(datetime.datetime.fromisoformat("2011-11-04 00:05:23.283+00:00")),
            Literal(datetime.timedelta(days=1)),
            "aplusb",
            Literal("2011-11-05T00:05:23.283000+00:00", datatype=XSD.dateTime),
        ),
        (
            Literal(datetime.time.fromisoformat("04:23:01.000384")),
            Literal(Duration(hours=1)),
            "aminusb",
            Literal("03:23:01.000384", datatype=XSD.time),
        ),
        (
            Literal(datetime.date.fromisoformat("2011-11-04")),
            Literal(Duration(days=1)),
            "aminusb",
            Literal("2011-11-03", datatype=XSD.date),
        ),
        (
            Literal(datetime.datetime.fromisoformat("2011-11-04 00:05:23.283+00:00")),
            Literal(Duration(days=1)),
            "aminusb",
            Literal("2011-11-03T00:05:23.283000+00:00", datatype=XSD.dateTime),
        ),
        (
            Literal(datetime.time.fromisoformat("04:23:01.000384")),
            Literal(datetime.timedelta(hours=1)),
            "aminusb",
            Literal("03:23:01.000384", datatype=XSD.time),
        ),
        (
            Literal(datetime.date.fromisoformat("2011-11-04")),
            Literal(datetime.timedelta(days=1)),
            "aminusb",
            Literal("2011-11-03", datatype=XSD.date),
        ),
        (
            Literal(datetime.datetime.fromisoformat("2011-11-04 00:05:23.283+00:00")),
            Literal(datetime.timedelta(days=1)),
            "aminusb",
            Literal("2011-11-03T00:05:23.283000+00:00", datatype=XSD.dateTime),
        ),
        (
            Literal("5", datatype=XSD.integer),
            Literal("10", datatype=XSD.integer),
            "bminusa",
            Literal("5", datatype=XSD.integer),
        ),
        (
            Literal("5"),
            Literal("10", datatype=_XSD_INTEGER),
            "aminusb",
            TypeError(
                "Minuend Literal must have Numeric, Date, Datetime or Time datatype."
            ),
        ),
        (
            Literal("5"),
            Literal("10", datatype=_XSD_INTEGER),
            "bminusa",
            TypeError(
                "Subtrahend Literal must have Numeric, Date, Datetime or Time datatype."
            ),
        ),
        *affix_tuples(
            (
                Literal("5", datatype=_XSD_INTEGER),
                Literal("10", datatype=_XSD_FLOAT),
            ),
            [
                ("aminusb", Literal("-5", datatype=_XSD_DECIMAL)),
                ("aplusb", Literal("15", datatype=_XSD_DECIMAL)),
                ("bminusa", Literal("5", datatype=_XSD_DECIMAL)),
                ("bplusa", Literal("15", datatype=_XSD_DECIMAL)),
            ],
            None,
        ),
        *affix_tuples(
            (
                Literal("5", datatype=_XSD_FLOAT),
                Literal("10", datatype=_XSD_DECIMAL),
            ),
            [
                ("aminusb", Literal("-5", datatype=_XSD_DECIMAL)),
                ("aplusb", Literal("15", datatype=_XSD_DECIMAL)),
                ("bminusa", Literal("5", datatype=_XSD_DECIMAL)),
                ("bplusa", Literal("15", datatype=_XSD_DECIMAL)),
            ],
            None,
        ),
        *affix_tuples(
            (
                Literal("5", datatype=_XSD_FLOAT),
                Literal("10", datatype=_XSD_DOUBLE),
            ),
            [
                ("aminusb", Literal("-5", datatype=_XSD_DECIMAL)),
                ("aplusb", Literal("15", datatype=_XSD_DECIMAL)),
                ("bminusa", Literal("5", datatype=_XSD_DECIMAL)),
                ("bplusa", Literal("15", datatype=_XSD_DECIMAL)),
            ],
            None,
        ),
        *affix_tuples(
            (
                Literal(Decimal("1.2121214312312")),
                Literal(1),
            ),
            [
                ("aminusb", Literal(Decimal("0.2121214312312"))),
                ("aplusb", Literal(Decimal("2.2121214312312"))),
                ("bminusa", Literal(Decimal("-0.2121214312312"))),
                ("bplusa", Literal(Decimal("2.2121214312312"))),
            ],
            None,
        ),
        *affix_tuples(
            (
                Literal("P31D", datatype=_XSD_DURATION),
                Literal("P5D", datatype=_XSD_DURATION),
            ),
            [
                ("aplusb", Literal("P36D", datatype=_XSD_DURATION)),
                ("aminusb", Literal("P26D", datatype=_XSD_DURATION)),
            ],
            None,
        ),
        *affix_tuples(
            (
                Literal("P119D", datatype=_XSD_DURATION),
                Literal("2006-01-02T20:50:00", datatype=_XSD_DATETIME),
            ),
            [
                ("aplusb", TypeError(r".*datatype.*")),
                ("aminusb", TypeError(r".*datatype.*")),
            ],
            None,
        ),
        *affix_tuples(
            (
                Literal(Duration(days=4)),
                Literal(datetime.timedelta(days=1)),
            ),
            [
                (
                    "aplusb",
                    TypeError(
                        r"Cannot add a Literal of datatype.*to a Literal of datatype.*"
                    ),
                ),
                (
                    "aminusb",
                    TypeError(
                        r"Cannot subtract a Literal of datatype.*from a Literal of datatype.*"
                    ),
                ),
            ],
            None,
        ),
        *affix_tuples(
            (
                Literal(Duration(days=4)),
                Literal(Duration(days=1)),
            ),
            [
                ("aplusb", Literal(Duration(days=5))),
                ("aminusb", Literal(Duration(days=3))),
            ],
            None,
        ),
        *affix_tuples(
            (
                Literal(datetime.timedelta(hours=4)),
                Literal(datetime.timedelta(hours=1)),
            ),
            [
                ("aplusb", Literal(datetime.timedelta(hours=5))),
                ("aminusb", Literal(datetime.timedelta(hours=3))),
            ],
            None,
        ),
    ],
)
def test_literal_addsub(
    a: Literal,
    b: Literal,
    op: str,
    expected_result: OutcomePrimitive[Literal],
) -> None:
    checker = OutcomeChecker[Literal].from_primitive(expected_result)
    with checker.context():
        if op == "aplusb":
            result = a + b

        elif op == "aminusb":
            result = a - b
        elif op == "bminusa":
            result = b - a
        elif op == "bplusa":
            result = b + a
        else:
            raise ValueError(f"invalid operation {op}")
        logging.debug("result = %r", result)
        checker.check(result)


# Untyped decorator makes function untyped
@pytest.mark.parametrize(  # type: ignore[misc, unused-ignore]
    "a_value, b_value, result_value, datatype",
    [
        [3, 5, 2, XSD.integer],
        [5.3, 8.5, 3.2, XSD.decimal],
        [5.3, 8.5, 3.2, XSD.double],
        [5.3, 8.5, 3.2, XSD.float],
        # [XSD.byte")],
        [3, 5, 2, XSD.int],
        [5.3, 8.5, 3.2, XSD.long],
        [-3, -5, -2, XSD.negativeInteger],
        [3, 5, 2, XSD.nonNegativeInteger],
        [-5.3, -8.5, -3.2, XSD.nonPositiveInteger],
        [3, 5, 2, XSD.positiveInteger],
        [3, 5, 2, XSD.short],
        [0, 0, 0, XSD.unsignedByte],
        [3, 5, 2, XSD.unsignedInt],
        [5.3, 8.5, 3.2, XSD.unsignedLong],
        [5.3, 8.5, 3.2, XSD.unsignedShort],
    ],
)
def test_numeric_literals(
    a_value: Union[int, float],
    b_value: Union[int, float],
    result_value: Union[int, float],
    datatype: URIRef,
) -> None:
    a = Literal(a_value, datatype=datatype)
    b = Literal(b_value, datatype=datatype)

    result = b - a
    expected = Literal(result_value, datatype=datatype)
    assert result == expected, repr(result)


def test_cant_pass_lang_and_datatype() -> None:
    with pytest.raises(TypeError):
        Literal("foo", lang="en", datatype=URIRef("http://example.com/"))


def test_cant_pass_invalid_lang_int() -> None:
    with pytest.raises(ValueError):
        Literal("foo", lang="999")


def test_from_other_literal() -> None:
    l = Literal(1)  # noqa: E741
    l2 = Literal(l)
    assert isinstance(l.value, int)
    assert isinstance(l2.value, int)

    # change datatype
    l = Literal("1")  # noqa: E741
    l2 = Literal(l, datatype=rdflib.XSD.integer)
    assert isinstance(l2.value, int)


def test_datatype_gets_auto_uri_ref_conversion() -> None:
    # drewp disapproves of this behavior, but it should be
    # represented in the tests
    x = Literal("foo", datatype="http://example.com/")
    assert isinstance(x.datatype, URIRef)

    x = Literal("foo", datatype=Literal("pennies"))
    assert x.datatype == URIRef("pennies")


def test_omits_missing_datatype_and_lang() -> None:
    assert repr(Literal("foo")) == "rdflib.term.Literal('foo')"


def test_omits_missing_datatype() -> None:
    assert repr(Literal("foo", lang="en")) == "rdflib.term.Literal('foo', lang='en')"


def test_omits_missing_lang() -> None:
    assert (
        repr(Literal("foo", datatype=URIRef("http://example.com/")))
        == "rdflib.term.Literal('foo', datatype=rdflib.term.URIRef('http://example.com/'))"
    )


def test_subclass_name_appears_in_repr() -> None:
    class MyLiteral(Literal):
        pass

    x = MyLiteral("foo")
    assert repr(x) == "MyLiteral('foo')"


def test_no_dangling_point() -> None:
    """confirms the fix for https://github.com/RDFLib/rdflib/issues/237"""
    vv = Literal("0.88", datatype=_XSD_DOUBLE)
    out = vv._literal_n3(use_plain=True)
    assert out in ["8.8e-01", "0.88"], out


def test_true_boolean() -> None:
    test_value = Literal("tRue", datatype=_XSD_BOOLEAN)
    assert test_value.value
    test_value = Literal("1", datatype=_XSD_BOOLEAN)
    assert test_value.value


def test_false_boolean() -> None:
    test_value = Literal("falsE", datatype=_XSD_BOOLEAN)
    assert test_value.value is False
    test_value = Literal("0", datatype=_XSD_BOOLEAN)
    assert test_value.value is False


def test_non_false_boolean() -> None:
    with pytest.warns(
        UserWarning,
        match=r"Parsing weird boolean, 'abcd' does not map to True or False",
    ):
        test_value = Literal("abcd", datatype=_XSD_BOOLEAN)
    assert test_value.value is False

    with pytest.warns(
        UserWarning,
        match=r"Parsing weird boolean, '10' does not map to True or False",
    ):
        test_value = Literal("10", datatype=_XSD_BOOLEAN)
    assert test_value.value is False


def test_binding(clear_bindings: None) -> None:
    class a:  # noqa: N801
        def __init__(self, v: str) -> None:
            self.v = v[3:-3]

        def __str__(self) -> str:
            return "<<<%s>>>" % self.v

    dtA = rdflib.URIRef("urn:dt:a")  # noqa: N806
    bind(dtA, a)

    va = a("<<<2>>>")
    la = Literal(va, normalize=True)
    assert la.value == va
    assert la.datatype == dtA

    la2 = Literal("<<<2>>>", datatype=dtA)
    assert isinstance(la2.value, a)
    assert la2.value.v == va.v

    class b:  # noqa: N801
        def __init__(self, v: str) -> None:
            self.v = v[3:-3]

        def __str__(self) -> str:
            return "B%s" % self.v

    dtB = rdflib.URIRef("urn:dt:b")  # noqa: N806
    bind(dtB, b, None, lambda x: "<<<%s>>>" % x)

    vb = b("<<<3>>>")
    lb = Literal(vb, normalize=True)
    assert lb.value == vb
    assert lb.datatype == dtB


def test_specific_binding(clear_bindings: None) -> None:
    def lexify(s: str) -> str:
        return "--%s--" % s

    def unlexify(s: str) -> str:
        return s[2:-2]

    datatype = rdflib.URIRef("urn:dt:mystring")

    # Datatype-specific rule
    bind(datatype, str, unlexify, lexify, datatype_specific=True)

    s = "Hello"
    normal_l = Literal(s)
    assert str(normal_l) == s
    assert normal_l.toPython() == s
    assert normal_l.datatype is None

    specific_l = Literal("--%s--" % s, datatype=datatype)
    assert str(specific_l) == lexify(s)
    assert specific_l.toPython() == s
    assert specific_l.datatype == datatype


# Untyped decorator makes function untyped
@pytest.mark.parametrize(  # type: ignore[misc, unused-ignore]
    ["lexical", "literal_type", "value_cls"],
    [
        # these literals do not get converted to Python types
        ("ABCD", XSD.integer, None),
        ("ABCD", XSD.gYear, None),
        ("-10000", XSD.gYear, None),
        ("-1921-00", XSD.gYearMonth, None),
        ("1921-00", XSD.gMonthDay, None),
        ("1921-13", XSD.gMonthDay, None),
        ("-1921-00", XSD.gMonthDay, None),
        ("10", XSD.gDay, None),
        ("-1", XSD.gDay, None),
        ("0000", XSD.gYear, None),
        ("0000-00-00", XSD.date, None),
        ("NOT A VALID HEX STRING", XSD.hexBinary, None),
        ("NOT A VALID BASE64 STRING", XSD.base64Binary, None),
        # xsd:gYear and xsd:gYearMonth also do not get converted
        ("1921-05", XSD.gYearMonth, None),
        ("0001-01", XSD.gYearMonth, None),
        ("0001-12", XSD.gYearMonth, None),
        ("2002-01", XSD.gYearMonth, None),
        ("9999-01", XSD.gYearMonth, None),
        ("9999-12", XSD.gYearMonth, None),
        ("1921", XSD.gYear, None),
        ("2000", XSD.gYear, None),
        ("0001", XSD.gYear, None),
        ("9999", XSD.gYear, None),
        ("1982", XSD.gYear, None),
        ("2002", XSD.gYear, None),
        # these literals get converted to python types
        ("1921-05-01", XSD.date, datetime.date),
        ("1921-05-01T00:00:00", XSD.dateTime, datetime.datetime),
        ("1921-05-01T00:00:00+00:30", XSD.dateTime, datetime.datetime),
        ("1921-05-01T00:00:00-00:30", XSD.dateTime, datetime.datetime),
        ("true", XSD.boolean, bool),
        ("abcdef0123", XSD.hexBinary, bytes),
        ("", XSD.hexBinary, bytes),
        ("UkRGTGli", XSD.base64Binary, bytes),
        ("", XSD.base64Binary, bytes),
        ("0.0000000000000000000000000000001", XSD.decimal, Decimal),
        ("0.1", XSD.decimal, Decimal),
        ("1", XSD.integer, int),
    ]
    + [
        pytest.param(*params, marks=pytest.mark.xfail(raises=AssertionError))
        for params in [
            ("1921-01Z", XSD.gYearMonth, datetime.date),
            ("1921Z", XSD.gYear, datetime.date),
            ("1921-00", XSD.gYearMonth, datetime.date),
            ("1921-05-01Z", XSD.date, datetime.date),
            ("1921-05-01+00:30", XSD.date, datetime.date),
            ("1921-05-01+00:30", XSD.date, datetime.date),
            ("1921-05-01+00:00", XSD.date, datetime.date),
            ("1921-05-01+00:00", XSD.date, datetime.date),
            ("1921-05-01T00:00:00Z", XSD.dateTime, datetime.datetime),
            ("1e-31", XSD.decimal, None),  # This is not a valid decimal value
        ]
    ],
)
def test_literal_construction_value_class(
    lexical: str, literal_type: URIRef, value_cls: type | None
) -> None:
    literal = Literal(lexical, datatype=literal_type)
    if value_cls is not None:
        assert isinstance(literal.value, value_cls)
    else:
        assert literal.value is None
    assert lexical == f"{literal}"


def test_exception_in_converter(
    caplog: pytest.LogCaptureFixture, clear_bindings: None
) -> None:
    def lexify(s: str) -> str:
        return "--%s--" % s

    def unlexify(s: str) -> str:
        raise Exception("TEST_EXCEPTION")

    datatype = rdflib.URIRef("urn:dt:mystring")

    # Datatype-specific rule
    bind(datatype, str, unlexify, lexify, datatype_specific=True)

    s = "Hello"

    Literal("--%s--" % s, datatype=datatype)

    assert (
        caplog.record_tuples[0][1] == logging.WARNING
        and caplog.record_tuples[0][2].startswith("Failed to convert")
        and caplog.records[0].exc_info
        and str(caplog.records[0].exc_info[1]) == "TEST_EXCEPTION"
    )


class _UnknownType:
    """
    A class that is not known to rdflib, used to test the how
    rdflib.term.Literal handles unknown python types.
    """

    def __repr__(self) -> str:
        return "_UnknownType()"

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, _UnknownType):
            return True
        return False


# Untyped decorator makes function untyped
@pytest.mark.parametrize(  # type: ignore[misc, unused-ignore]
    ["literal_maker", "outcome"],
    [
        (
            lambda: Literal("foo"),
            LiteralChecker("foo", None, None, None, "foo"),
        ),
        (
            lambda: Literal("foo", None, ""),
            LiteralChecker(None, None, URIRef(""), None, "foo"),
        ),
        (
            lambda: Literal("foo", None, XSD.string),
            LiteralChecker("foo", None, XSD.string, False, "foo"),
        ),
        (
            lambda: Literal("1", None, XSD.integer),
            LiteralChecker(1, None, XSD.integer, False, "1"),
        ),
        (
            lambda: Literal("1", "en", XSD.integer),
            TypeError,
        ),
        (
            lambda: Literal(Literal("1", None, XSD.integer)),
            Literal("1", None, XSD.integer),
        ),
        (
            lambda: Literal(Literal("1", None, "")),
            [LiteralChecker(None, None, URIRef(""), None, "1"), Literal("1", None, "")],
        ),
        (lambda: Literal(Literal("1")), Literal("1")),
        (
            lambda: Literal(Literal("blue sky", "en")),
            Literal("blue sky", "en"),
        ),
        (
            lambda: Literal("<body>", datatype=RDF.HTML),
            LiteralChecker(
                ..., None, RDF.HTML, True if _HAVE_HTML5RDF else None, "<body>"
            ),
        ),
        (
            lambda: Literal("<table></table>", datatype=RDF.HTML),
            LiteralChecker(
                ...,
                None,
                RDF.HTML,
                False if _HAVE_HTML5RDF else None,
                "<table></table>",
            ),
        ),
        (
            lambda: Literal(_UnknownType(), datatype=EGDC.UnknownType),
            LiteralChecker(
                _UnknownType(), None, EGDC.UnknownType, None, "_UnknownType()"
            ),
        ),
    ],
    ids=literal_idfn,
)
def test_literal_construction(
    literal_maker: Callable[[], Literal],
    outcome: OutcomePrimitives[Literal],
) -> None:
    checker = OutcomeChecker[Literal].from_primitives(outcome)
    with checker.context():
        actual_outcome = literal_maker()
        checker.check(actual_outcome)


# Untyped decorator makes function untyped
@pytest.mark.parametrize(  # type: ignore[misc, unused-ignore]
    ["literal_maker", "normalize_literals", "outcome"],
    [
        (
            lambda: Literal("001000", datatype=XSD.integer),
            ...,
            LiteralChecker(1000, None, XSD.integer, False, "1000"),
        ),
        (
            lambda: Literal("001000", datatype=XSD.integer),
            True,
            LiteralChecker(1000, None, XSD.integer, False, "1000"),
        ),
        (
            lambda: Literal("001000", datatype=XSD.integer),
            False,
            LiteralChecker(1000, None, XSD.integer, False, "001000"),
        ),
    ],
    ids=literal_idfn,
)
def test_global_normalize(
    literal_maker: Callable[[], Literal],
    normalize_literals: Union[builtins.ellipsis, bool],
    outcome: OutcomePrimitives[Literal],
) -> None:
    _normalize_literals = rdflib.NORMALIZE_LITERALS
    try:
        if normalize_literals is not ...:
            rdflib.NORMALIZE_LITERALS = normalize_literals
        checker = OutcomeChecker[Literal].from_primitives(outcome)
        with checker.context():
            actual_outcome = literal_maker()
            checker.check(actual_outcome)
    finally:
        rdflib.NORMALIZE_LITERALS = _normalize_literals
