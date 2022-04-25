# NOTE: The config below enables strict mode for mypy.
# mypy: no_ignore_errors
# mypy: warn_unused_configs, disallow_any_generics
# mypy: disallow_subclassing_any, disallow_untyped_calls
# mypy: disallow_untyped_defs, disallow_incomplete_defs
# mypy: check_untyped_defs, disallow_untyped_decorators
# mypy: no_implicit_optional, warn_redundant_casts, warn_unused_ignores
# mypy: warn_return_any, no_implicit_reexport, strict_equality

import datetime
import unittest
from decimal import Decimal
from typing import Any, Optional, Sequence, Tuple, Type, Union

import pytest

import rdflib  # needed for eval(repr(...)) below
from rdflib import XSD
from rdflib.namespace import RDF, Namespace
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
    bind,
)

EGNS = Namespace("http://example.com/")


class TestLiteral:
    def test_repr_apostrophe(self) -> None:
        a = rdflib.Literal("'")
        b = eval(repr(a))
        assert a == b

    def test_repr_quote(self) -> None:
        a = rdflib.Literal('"')
        b = eval(repr(a))
        assert a == b

    def test_backslash(self) -> None:
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

    def test_literal_from_bool(self) -> None:
        _l = rdflib.Literal(True)
        assert _l.datatype == rdflib.XSD["boolean"]


class TestNewPT:
    # NOTE: TestNewPT is written for pytest so that pytest features like
    # parametrize can be used.
    # New tests should be added here instead of in TestNew.
    @pytest.mark.parametrize(
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
        self,
        lang: Any,
        exception_type: Type[Exception],
    ) -> None:
        """
        Construction of Literal fails if the language tag is invalid.
        """
        with pytest.raises(exception_type):
            Literal("foo", lang=lang)

    @pytest.mark.parametrize(
        "lexical, datatype, is_ill_formed",
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
            ("[p]", EGNS.unrecognized, None),
        ],
    )
    def test_ill_formed_literals(
        self,
        lexical: Union[bytes, str],
        datatype: Optional[URIRef],
        is_ill_formed: Optional[bool],
    ) -> None:
        """
        ill_formed has the correct value.
        """
        lit = Literal(lexical, datatype=datatype)
        assert lit.ill_formed is is_ill_formed
        if is_ill_formed is False:
            # If the literal is not ill formed it should have a value associated with it.
            assert lit.value is not None

    def test_datetime_sub(self) -> None:
        a = Literal('2006-01-01T20:50:00', datatype=_XSD_DATETIME)
        b = Literal('2006-02-01T20:50:00', datatype=_XSD_DATETIME)
        result = b - a
        expected = Literal('P31D', datatype=_XSD_DURATION)
        assert result == expected

    def test_datetime_sub2(self) -> None:
        a = Literal('2006-01-02T20:50:00', datatype=_XSD_DATETIME)
        b = Literal('2006-05-01T20:50:00', datatype=_XSD_DATETIME)
        result = b - a
        expected = Literal('P119D', datatype=_XSD_DURATION)
        assert result == expected

    def test_datetime_sub3(self) -> None:
        a = Literal('2006-07-01T20:52:00', datatype=_XSD_DATETIME)
        b = Literal('2006-11-01T12:50:00', datatype=_XSD_DATETIME)
        result = a - b
        expected = Literal('-P122DT15H58M', datatype=_XSD_DURATION)
        assert result == expected

    def test_date_sub4(self) -> None:
        a = Literal('2006-07-01T20:52:00', datatype=_XSD_DATE)
        b = Literal('2006-11-01T12:50:00', datatype=_XSD_DATE)
        result = b - a
        expected = Literal('P123D', datatype=_XSD_DURATION)
        assert result == expected

    def test_date_sub5(self) -> None:
        a = Literal('2006-08-01', datatype=_XSD_DATE)
        b = Literal('2006-11-01', datatype=_XSD_DATE)
        result = b - a
        expected = Literal('P92D', datatype=_XSD_DURATION)
        assert result == expected

    def test_integer_sub(self) -> None:
        """extends the issue OF #629 - Handling substraction
        operations in Literals"""
        a = Literal('5', datatype=XSD.integer)
        b = Literal('10', datatype=XSD.integer)
        result = b - a
        expected = Literal('5', datatype=XSD.integer)
        assert result == expected

    def test_datatype_enforcement_error_messages(self) -> None:
        a = Literal('5')
        b = Literal('10', datatype=_XSD_INTEGER)

        with pytest.raises(TypeError) as e:
            result = a - b
        assert e.match(
            "Minuend Literal must have Numeric, Date, Datetime or Time datatype."
        )

        with pytest.raises(TypeError) as e:
            result = b - a
        assert e.match(
            "Subtrahend Literal must have Numeric, Date, Datetime or Time datatype."
        )

    def test_datatype_enforcement_int_float(self) -> None:
        a = Literal('5', datatype=_XSD_INTEGER)
        b = Literal('10', datatype=_XSD_FLOAT)

        result = a - b
        assert result == Literal("-5", datatype=_XSD_DECIMAL)

        result = b - a
        assert result == Literal("5", datatype=_XSD_DECIMAL)

    def test_datatype_enforcement_float_decimal(self) -> None:
        a = Literal('5', datatype=_XSD_FLOAT)
        b = Literal('10', datatype=_XSD_DECIMAL)

        result = a - b
        assert result == Literal("-5", datatype=_XSD_DECIMAL)

        result = b - a
        assert result == Literal("5", datatype=_XSD_DECIMAL)

    def test_datatype_enforcement_float_double(self) -> None:
        a = Literal('5', datatype=_XSD_FLOAT)
        b = Literal('10', datatype=_XSD_DOUBLE)

        result = a - b
        assert result == Literal("-5", datatype=_XSD_DECIMAL)

        result = b - a
        assert result == Literal("5", datatype=_XSD_DECIMAL)

    @pytest.mark.parametrize(
        "desc, a, b, op, emsg",
        [
            (
                "Attempt to subtract strings",
                Literal("20:00:00", datatype=_XSD_STRING),
                Literal("23:30:00", datatype=_XSD_STRING),
                "bminusa",
                r"unsupported operand type\(s\) for -: 'str' and 'str",
            ),
            (
                "Attempt to add string to time",
                Literal("20:00:00", datatype=_XSD_TIME),
                Literal("23:30:00", datatype=_XSD_STRING),
                "aplusb",
                "Cannot add a Literal of datatype http://www.w3.org/2001/XMLSchema#string to a Literal of datatype http://www.w3.org/2001/XMLSchema#time",
            ),
            (
                "Attempt to subtract string from time",
                Literal("20:00:00", datatype=_XSD_TIME),
                Literal("23:30:00", datatype=_XSD_STRING),
                "bminusa",
                "Cannot subtract a Literal of datatype http://www.w3.org/2001/XMLSchema#time from a Literal of datatype http://www.w3.org/2001/XMLSchema#string",
            ),
            (
                "Attempt to add integer to time",
                Literal("20:52:00", datatype=_XSD_TIME),
                Literal("12", datatype=_XSD_INTEGER),
                "aplusb",
                "Cannot add a Literal of datatype http://www.w3.org/2001/XMLSchema#integer to a Literal of datatype http://www.w3.org/2001/XMLSchema#time",
            ),
            (
                "Attempt to add time to integer",
                Literal("20:52:00", datatype=_XSD_TIME),
                Literal("12", datatype=_XSD_INTEGER),
                "bplusa",
                "Cannot add a Literal of datatype http://www.w3.org/2001/XMLSchema#time to a Literal of datatype http://www.w3.org/2001/XMLSchema#integer",
            ),
            (
                "Attempt to subtract integer from time",
                Literal("20:52:00", datatype=_XSD_TIME),
                Literal("12", datatype=_XSD_INTEGER),
                "aminusb",
                "Cannot subtract a Literal of datatype http://www.w3.org/2001/XMLSchema#integer from a Literal of datatype http://www.w3.org/2001/XMLSchema#time",
            ),
            (
                "Attempt to subtract time from integer",
                Literal("20:52:00", datatype=_XSD_TIME),
                Literal("12", datatype=_XSD_INTEGER),
                "bminusa",
                "Cannot subtract a Literal of datatype http://www.w3.org/2001/XMLSchema#time from a Literal of datatype http://www.w3.org/2001/XMLSchema#integer",
            ),
            (
                "Attempt to add duration to integer",
                Literal("12", datatype=_XSD_INTEGER),
                Literal("P122DT15H58M", datatype=_XSD_DURATION),
                "aplusb",
                "Cannot add a Literal of datatype http://www.w3.org/2001/XMLSchema#duration to a Literal of datatype http://www.w3.org/2001/XMLSchema#integer",
            ),
            (
                "Attempt to add integer to duration",
                Literal("12", datatype=_XSD_INTEGER),
                Literal("P122DT15H58M", datatype=_XSD_DURATION),
                "bplusa",
                "Cannot add a Literal of datatype http://www.w3.org/2001/XMLSchema#integer to a Literal of datatype http://www.w3.org/2001/XMLSchema#duration",
            ),
            (
                "Attempt to subtract duration from integer",
                Literal("12", datatype=_XSD_INTEGER),
                Literal("P122DT15H58M", datatype=_XSD_DURATION),
                "aminusb",
                "Cannot subtract a Literal of datatype http://www.w3.org/2001/XMLSchema#duration from a Literal of datatype http://www.w3.org/2001/XMLSchema#integer",
            ),
            (
                "Attempt to subtract integer from duration",
                Literal("12", datatype=_XSD_INTEGER),
                Literal("P122DT15H58M", datatype=_XSD_DURATION),
                "bminusa",
                "Cannot subtract a Literal of datatype http://www.w3.org/2001/XMLSchema#integer from a Literal of datatype http://www.w3.org/2001/XMLSchema#duration",
            ),
        ],
    )
    def test_datetime_errors(
        self, desc: str, a: Literal, b: Literal, op: str, emsg: str
    ) -> None:
        with pytest.raises(TypeError) as e:
            if op == "aplusb":
                result = a + b
            elif op == "bplusa":
                result = b + a
            elif op == "aminusb":
                result = a - b
            elif op == "bminusa":
                result = b - a
        assert e.match(emsg)

    @pytest.mark.parametrize(
        "a, b, op, expected",
        [
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
        ],
    )
    def test_datetime(self, a: Literal, b: Literal, op: str, expected: Literal) -> None:
        if op == "aplusb":
            assert a + b == expected
        elif op == "aminusb":
            assert a - b == expected
        elif op == "bminusa":
            assert b - a == expected

    @pytest.mark.parametrize(
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
        self,
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


class TestNew(unittest.TestCase):
    # NOTE: Please use TestNewPT for new tests instead of this which is written
    # for unittest.
    def testCantPassLangAndDatatype(self) -> None:
        self.assertRaises(
            TypeError, Literal, "foo", lang="en", datatype=URIRef("http://example.com/")
        )

    def testCantPassInvalidLang(self) -> None:
        self.assertRaises(ValueError, Literal, "foo", lang="999")

    def testFromOtherLiteral(self) -> None:
        l = Literal(1)
        l2 = Literal(l)
        self.assertTrue(isinstance(l.value, int))
        self.assertTrue(isinstance(l2.value, int))

        # change datatype
        l = Literal("1")
        l2 = Literal(l, datatype=rdflib.XSD.integer)
        self.assertTrue(isinstance(l2.value, int))

    def testDatatypeGetsAutoURIRefConversion(self) -> None:
        # drewp disapproves of this behavior, but it should be
        # represented in the tests
        x = Literal("foo", datatype="http://example.com/")
        self.assertTrue(isinstance(x.datatype, URIRef))

        x = Literal("foo", datatype=Literal("pennies"))
        self.assertEqual(x.datatype, URIRef("pennies"))


class TestRepr(unittest.TestCase):
    def testOmitsMissingDatatypeAndLang(self) -> None:
        self.assertEqual(repr(Literal("foo")), "rdflib.term.Literal('foo')")

    def testOmitsMissingDatatype(self) -> None:
        self.assertEqual(
            repr(Literal("foo", lang="en")),
            "rdflib.term.Literal('foo', lang='en')",
        )

    def testOmitsMissingLang(self) -> None:
        self.assertEqual(
            repr(Literal("foo", datatype=URIRef("http://example.com/"))),
            "rdflib.term.Literal('foo', datatype=rdflib.term.URIRef('http://example.com/'))",
        )

    def test_subclass_name_appears_in_repr(self) -> None:
        class MyLiteral(Literal):
            pass

        x = MyLiteral("foo")
        assert repr(x) == "MyLiteral('foo')"


class TestDoubleOutput(unittest.TestCase):
    def testNoDanglingPoint(self) -> None:
        """confirms the fix for https://github.com/RDFLib/rdflib/issues/237"""
        vv = Literal("0.88", datatype=_XSD_DOUBLE)
        out = vv._literal_n3(use_plain=True)
        assert out in ["8.8e-01", "0.88"], out


class TestParseBoolean(unittest.TestCase):
    """confirms the fix for https://github.com/RDFLib/rdflib/issues/913"""

    def test_true_boolean(self) -> None:
        test_value = Literal("tRue", datatype=_XSD_BOOLEAN)
        assert test_value.value
        test_value = Literal("1", datatype=_XSD_BOOLEAN)
        assert test_value.value

    def test_false_boolean(self) -> None:
        test_value = Literal("falsE", datatype=_XSD_BOOLEAN)
        assert test_value.value is False
        test_value = Literal("0", datatype=_XSD_BOOLEAN)
        assert test_value.value is False

    def test_non_false_boolean(self) -> None:
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


class TestBindings(unittest.TestCase):
    def testBinding(self) -> None:
        class a:
            def __init__(self, v: str) -> None:
                self.v = v[3:-3]

            def __str__(self) -> str:
                return "<<<%s>>>" % self.v

        dtA = rdflib.URIRef("urn:dt:a")
        bind(dtA, a)

        va = a("<<<2>>>")
        la = Literal(va, normalize=True)
        assert la.value == va
        assert la.datatype == dtA

        la2 = Literal("<<<2>>>", datatype=dtA)
        assert isinstance(la2.value, a)
        assert la2.value.v == va.v

        class b:
            def __init__(self, v: str) -> None:
                self.v = v[3:-3]

            def __str__(self) -> str:
                return "B%s" % self.v

        dtB = rdflib.URIRef("urn:dt:b")
        bind(dtB, b, None, lambda x: "<<<%s>>>" % x)

        vb = b("<<<3>>>")
        lb = Literal(vb, normalize=True)
        assert lb.value == vb
        assert lb.datatype == dtB

    def testSpecificBinding(self) -> None:
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


class TestXsdLiterals(unittest.TestCase):
    def test_make_literals(self) -> None:
        """
        Tests literal construction.
        """
        inputs = [
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
            # these literals get converted to python types
            ("1921-05-01", XSD.date, datetime.date),
            ("1921-05-01T00:00:00", XSD.dateTime, datetime.datetime),
            ("1921-05", XSD.gYearMonth, datetime.date),
            ("0001-01", XSD.gYearMonth, datetime.date),
            ("0001-12", XSD.gYearMonth, datetime.date),
            ("2002-01", XSD.gYearMonth, datetime.date),
            ("9999-01", XSD.gYearMonth, datetime.date),
            ("9999-12", XSD.gYearMonth, datetime.date),
            ("1921", XSD.gYear, datetime.date),
            ("2000", XSD.gYear, datetime.date),
            ("0001", XSD.gYear, datetime.date),
            ("9999", XSD.gYear, datetime.date),
            ("1982", XSD.gYear, datetime.date),
            ("2002", XSD.gYear, datetime.date),
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
        self.check_make_literals(inputs)

    @unittest.expectedFailure
    def test_make_literals_ki(self) -> None:
        """
        Known issues with literal construction.
        """
        inputs = [
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
        self.check_make_literals(inputs)

    def check_make_literals(
        self, inputs: Sequence[Tuple[str, URIRef, Optional[type]]]
    ) -> None:
        for literal_pair in inputs:
            (lexical, _type, value_cls) = literal_pair
            with self.subTest(f"testing {literal_pair}"):
                literal = Literal(lexical, datatype=_type)
                if value_cls is not None:
                    self.assertIsInstance(literal.value, value_cls)
                else:
                    self.assertIsNone(literal.value)
                self.assertEqual(lexical, f"{literal}")


if __name__ == "__main__":
    unittest.main()
