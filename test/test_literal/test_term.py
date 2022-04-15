"""
some more specific Literal tests are in test_literal.py
"""

import base64
import random

from rdflib.graph import Graph, QuotedGraph
from rdflib.namespace import XSD
from rdflib.term import BNode, Literal, URIRef, _is_valid_unicode


def uformat(s):
    return s.replace("u'", "'")


class TestURIRefRepr:
    """
    see also test_literal.TestRepr
    """

    def test_subclass_name_appears_in_repr(self):
        class MyURIRef(URIRef):
            pass

        x = MyURIRef("http://example.com/")
        assert repr(x) == uformat("MyURIRef(u'http://example.com/')")

    def test_graceful_ordering(self):
        u = URIRef("cake")
        g = Graph()
        a = u > u
        a = u > BNode()
        a = u > QuotedGraph(g.store, u)
        a = u > g


class TestBNodeRepr:
    def test_subclass_name_appears_in_repr(self):
        class MyBNode(BNode):
            pass

        x = MyBNode()
        assert repr(x).startswith("MyBNode(")


class TestLiteral:
    def test_base64_values(self):
        b64msg = "cmRmbGliIGlzIGNvb2whIGFsc28gaGVyZSdzIHNvbWUgYmluYXJ5IAAR83UC"
        decoded_b64msg = base64.b64decode(b64msg)
        lit = Literal(b64msg, datatype=XSD.base64Binary)
        assert lit.value == decoded_b64msg
        assert str(lit) == b64msg

    def test_total_order(self):
        types = {
            XSD.dateTime: (
                "2001-01-01T00:00:00",
                "2001-01-01T00:00:00Z",
                "2001-01-01T00:00:00-00:00",
            ),
            XSD.date: ("2001-01-01", "2001-01-01Z", "2001-01-01-00:00"),
            XSD.time: ("00:00:00", "00:00:00Z", "00:00:00-00:00"),
            XSD.gYear: ("2001", "2001Z", "2001-00:00"),  # interval
            XSD.gYearMonth: ("2001-01", "2001-01Z", "2001-01-00:00"),
        }
        literals = [
            Literal(literal, datatype=t)
            for t, literals in types.items()
            for literal in literals
        ]
        try:
            sorted(literals)
            orderable = True
        except TypeError as e:
            for l_ in literals:
                print(repr(l_), repr(l_.value))
            print(e)
            orderable = False
        assert orderable is True

        # also make sure that within a datetime things are still ordered:
        l1 = [
            Literal(l_, datatype=XSD.dateTime)
            for l_ in [
                "2001-01-01T00:00:00",
                "2001-01-01T01:00:00",
                "2001-01-01T01:00:01",
                "2001-01-02T01:00:01",
                "2001-01-01T00:00:00Z",
                "2001-01-01T00:00:00-00:00",
                "2001-01-01T01:00:00Z",
                "2001-01-01T01:00:00-00:00",
                "2001-01-01T00:00:00-01:30",
                "2001-01-01T01:00:00-01:30",
                "2001-01-02T01:00:01Z",
                "2001-01-02T01:00:01-00:00",
                "2001-01-02T01:00:01-01:30",
            ]
        ]
        l2 = list(l1)
        random.shuffle(l2)
        assert l1 == sorted(l2)

    def test_literal_add(self):
        from decimal import Decimal

        # compares Python decimals
        def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
            a = float(a)
            b = float(b)
            return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

        cases = [
            (1, Literal(1), Literal(1), Literal(2)),
            (2, Literal(Decimal(1)), Literal(Decimal(1)), Literal(Decimal(2))),
            (3, Literal(float(1)), Literal(float(1)), Literal(float(2))),
            (4, Literal(1), Literal(1.1), Literal(2.1, datatype=XSD.decimal)),
            (5, Literal(1.1), Literal(1.1), Literal(2.2)),
            (
                6,
                Literal(Decimal(1)),
                Literal(Decimal(1.1)),
                Literal(Decimal(2.1), datatype=XSD.decimal),
            ),
            (7, Literal(Decimal(1.1)), Literal(Decimal(1.1)), Literal(Decimal(2.2))),
            (8, Literal(float(1)), Literal(float(1.1)), Literal(float(2.1))),
            (9, Literal(float(1.1)), Literal(float(1.1)), Literal(float(2.2))),
            (10, Literal(-1), Literal(-1), Literal(-2)),
            (12, Literal(Decimal(-1)), Literal(Decimal(-1)), Literal(Decimal(-2))),
            (13, Literal(float(-1)), Literal(float(-1)), Literal(float(-2))),
            (14, Literal(-1), Literal(-1.1), Literal(-2.1)),
            (15, Literal(-1.1), Literal(-1.1), Literal(-2.2)),
            (16, Literal(Decimal(-1)), Literal(Decimal(-1.1)), Literal(Decimal(-2.1))),
            (
                17,
                Literal(Decimal(-1.1)),
                Literal(Decimal(-1.1)),
                Literal(Decimal(-2.2)),
            ),
            (18, Literal(float(-1)), Literal(float(-1.1)), Literal(float(-2.1))),
            (19, Literal(float(-1.1)), Literal(float(-1.1)), Literal(float(-2.2))),
            (20, Literal(1), Literal(1.0), Literal(2.0)),
            (21, Literal(1.0), Literal(1.0), Literal(2.0)),
            (22, Literal(Decimal(1)), Literal(Decimal(1.0)), Literal(Decimal(2.0))),
            (23, Literal(Decimal(1.0)), Literal(Decimal(1.0)), Literal(Decimal(2.0))),
            (24, Literal(float(1)), Literal(float(1.0)), Literal(float(2.0))),
            (25, Literal(float(1.0)), Literal(float(1.0)), Literal(float(2.0))),
            (
                26,
                Literal(1, datatype=XSD.integer),
                Literal(1, datatype=XSD.integer),
                Literal(2, datatype=XSD.integer),
            ),
            (
                27,
                Literal(1, datatype=XSD.integer),
                Literal("1", datatype=XSD.integer),
                Literal("2", datatype=XSD.integer),
            ),
            (
                28,
                Literal("1", datatype=XSD.integer),
                Literal("1", datatype=XSD.integer),
                Literal("2", datatype=XSD.integer),
            ),
            (
                29,
                Literal("1"),
                Literal("1", datatype=XSD.integer),
                Literal("11", datatype=XSD.string),
            ),
            (
                30,
                Literal(1),
                Literal("1", datatype=XSD.integer),
                Literal("2", datatype=XSD.integer),
            ),
            (
                31,
                Literal(Decimal(1), datatype=XSD.decimal),
                Literal(Decimal(1), datatype=XSD.decimal),
                Literal(Decimal(2), datatype=XSD.decimal),
            ),
            (
                32,
                Literal(Decimal(1)),
                Literal(Decimal(1), datatype=XSD.decimal),
                Literal(Decimal(2), datatype=XSD.decimal),
            ),
            (
                33,
                Literal(float(1)),
                Literal(float(1), datatype=XSD.float),
                Literal(float(2), datatype=XSD.float),
            ),
            (
                34,
                Literal(float(1), datatype=XSD.float),
                Literal(float(1), datatype=XSD.float),
                Literal(float(2), datatype=XSD.float),
            ),
            (35, Literal(1), 1, Literal(2)),
            (36, Literal(1), 1.0, Literal(2, datatype=XSD.decimal)),
            (37, Literal(1.0), 1, Literal(2, datatype=XSD.decimal)),
            (38, Literal(1.0), 1.0, Literal(2.0)),
            (39, Literal(Decimal(1.0)), Decimal(1), Literal(Decimal(2.0))),
            (40, Literal(Decimal(1.0)), Decimal(1.0), Literal(Decimal(2.0))),
            (41, Literal(float(1.0)), float(1), Literal(float(2.0))),
            (42, Literal(float(1.0)), float(1.0), Literal(float(2.0))),
            (
                43,
                Literal(1, datatype=XSD.integer),
                "+1.1",
                Literal("1+1.1", datatype=XSD.string),
            ),
            (
                44,
                Literal(1, datatype=XSD.integer),
                Literal("+1.1", datatype=XSD.string),
                Literal("1+1.1", datatype=XSD.string),
            ),
            (
                45,
                Literal(Decimal(1.0), datatype=XSD.integer),
                Literal("1", datatype=XSD.string),
                Literal("11", datatype=XSD.string),
            ),
            (
                46,
                Literal(1.1, datatype=XSD.integer),
                Literal("1", datatype=XSD.string),
                Literal("1.11", datatype=XSD.string),
            ),
            (
                47,
                Literal(1, datatype=XSD.integer),
                None,
                Literal(1, datatype=XSD.integer),
            ),
            (
                48,
                Literal("1", datatype=XSD.string),
                None,
                Literal("1", datatype=XSD.string),
            ),
        ]

        for case in cases:
            # see if the addition exactly matches the expected output
            case_passed = (case[1] + case[2]) == (case[3])
            # see if the addition almost matches the expected output, for decimal precision errors
            if not case_passed:
                try:
                    case_passed = isclose((case[1] + case[2].value), case[3].value)
                except:
                    pass

            if not case_passed:
                print(case[1], case[2])
                print("expected: " + case[3] + ", " + case[3].datatype)
                print(
                    "actual: "
                    + (case[1] + case[2])
                    + ", "
                    + (case[1] + case[2]).datatype
                )

            assert case_passed, "Case " + str(case[0]) + " failed"


class TestValidityFunctions:
    def test_is_valid_unicode(self):
        testcase_list = (
            (None, True),
            (1, True),
            (["foo"], True),
            ({"foo": b"bar"}, True),
            ("foo", True),
            (b"foo\x00", True),
            (b"foo\xf3\x02", False),
        )
        for val, expected in testcase_list:
            assert _is_valid_unicode(val) == expected
