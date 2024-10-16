import logging
from decimal import Decimal

import pytest

from rdflib.graph import Graph
from rdflib.namespace import XSD, Namespace
from rdflib.plugins.sparql.operators import _lang_range_check
from rdflib.term import BNode, Identifier, Literal, URIRef

EG = Namespace("https://example.com/")


@pytest.mark.parametrize(
    ["expression", "expected_result"],
    [
        (r"isIRI('eg:IRI')", Literal(False)),
        (r"isIRI(eg:IRI)", Literal(True)),
        (r"isURI('eg:IRI')", Literal(False)),
        (r"isURI(eg:IRI)", Literal(True)),
        (r"isBLANK(eg:IRI)", Literal(False)),
        (r"isBLANK(BNODE())", Literal(True)),
        (r"isLITERAL(eg:IRI)", Literal(False)),
        (r"isLITERAL('eg:IRI')", Literal(True)),
        (r"isNumeric(eg:IRI)", Literal(False)),
        (r"isNumeric(1)", Literal(True)),
        (r"STR(eg:IRI)", Literal("https://example.com/IRI")),
        (r"STR(1)", Literal("1")),
        (r'LANG("Robert"@en)', Literal("en")),
        (r'LANG("Robert")', Literal("")),
        (r'DATATYPE("Robert")', XSD.string),
        (r'DATATYPE("42"^^xsd:integer)', XSD.integer),
        (r'IRI("http://example/")', URIRef("http://example/")),
        (r'BNODE("example")', BNode),
        (r'STRDT("123", xsd:integer)', Literal("123", datatype=XSD.integer)),
        (r'STRLANG("cats and dogs", "en")', Literal("cats and dogs", lang="en")),
        (r"UUID()", URIRef),
        (r"STRUUID()", Literal),
        (r'STRLEN("chat")', Literal(4)),
        (r'SUBSTR("foobar", 4)', Literal("bar")),
        (r'UCASE("foo")', Literal("FOO")),
        (r'LCASE("BAR")', Literal("bar")),
        (r'strStarts("foobar", "foo")', Literal(True)),
        (r'strStarts("foobar", "bar")', Literal(False)),
        (r'strEnds("foobar", "bar")', Literal(True)),
        (r'strEnds("foobar", "foo")', Literal(False)),
        (r'contains("foobar", "bar")', Literal(True)),
        (r'contains("foobar", "barfoo")', Literal(False)),
        (r'strbefore("abc","b")', Literal("a")),
        (r'strbefore("abc","xyz")', Literal("")),
        (r'strafter("abc","b")', Literal("c")),
        (r'strafter("abc","xyz")', Literal("")),
        (r"ENCODE_FOR_URI('this/is/a/test')", Literal("this%2Fis%2Fa%2Ftest")),
        (r"ENCODE_FOR_URI('this is a test')", Literal("this%20is%20a%20test")),
        (
            r"ENCODE_FOR_URI('AAA~~0123456789~~---~~___~~...~~ZZZ')",
            Literal("AAA~~0123456789~~---~~___~~...~~ZZZ"),
        ),
        (r'CONCAT("foo", "bar")', Literal("foobar")),
        (r'langMatches(lang("That Seventies Show"@en), "en")', Literal(True)),
        (
            r'langMatches(lang("Cette Série des Années Soixante-dix"@fr), "en")',
            Literal(False),
        ),
        (
            r'langMatches(lang("Cette Série des Années Septante"@fr-BE), "en")',
            Literal(False),
        ),
        (r'langMatches(lang("Il Buono, il Bruto, il Cattivo"), "en")', Literal(False)),
        (r'langMatches(lang("That Seventies Show"@en), "FR")', Literal(False)),
        (
            r'langMatches(lang("Cette Série des Années Soixante-dix"@fr), "FR")',
            Literal(True),
        ),
        (
            r'langMatches(lang("Cette Série des Années Septante"@fr-BE), "FR")',
            Literal(True),
        ),
        (r'langMatches(lang("Il Buono, il Bruto, il Cattivo"), "FR")', Literal(False)),
        (r'langMatches(lang("That Seventies Show"@en), "*")', Literal(True)),
        (
            r'langMatches(lang("Cette Série des Années Soixante-dix"@fr), "*")',
            Literal(True),
        ),
        (
            r'langMatches(lang("Cette Série des Années Septante"@fr-BE), "*")',
            Literal(True),
        ),
        (r'langMatches(lang("Il Buono, il Bruto, il Cattivo"), "*")', Literal(False)),
        (r'langMatches(lang("abc"@en-gb), "en-GB")', Literal(True)),
        (r'regex("Alice", "^ali", "i")', Literal(True)),
        (r'regex("Bob", "^ali", "i")', Literal(False)),
        (r'replace("abcd", "b", "Z")', Literal("aZcd")),
        (r"abs(-1.5)", Literal("1.5", datatype=XSD.decimal)),
        (r"round(2.4999)", Literal("2", datatype=XSD.decimal)),
        (r"round(2.5)", Literal("3", datatype=XSD.decimal)),
        (r"round(-2.5)", Literal("-2", datatype=XSD.decimal)),
        (r"round(0.1)", Literal("0", datatype=XSD.decimal)),
        (r"round(-0.1)", Literal("0", datatype=XSD.decimal)),
        (r"RAND()", Literal),
        (r"now()", Literal),
        (r'month("2011-01-10T14:45:13.815-05:00"^^xsd:dateTime)', Literal(1)),
        (r'day("2011-01-10T14:45:13.815-05:00"^^xsd:dateTime)', Literal(10)),
        (r'hours("2011-01-10T14:45:13.815-05:00"^^xsd:dateTime)', Literal(14)),
        (r'minutes("2011-01-10T14:45:13.815-05:00"^^xsd:dateTime)', Literal(45)),
        (
            r'seconds("2011-01-10T14:45:13.815-05:00"^^xsd:dateTime)',
            Literal(Decimal("13.815")),
        ),
        (
            r'timezone("2011-01-10T14:45:13.815-05:00"^^xsd:dateTime)',
            Literal("-PT5H", datatype=XSD.dayTimeDuration),
        ),
        (
            r'timezone("2011-01-10T14:45:13.815Z"^^xsd:dateTime)',
            Literal("PT0S", datatype=XSD.dayTimeDuration),
        ),
        (
            r'tz("2011-01-10T14:45:13.815-05:00"^^xsd:dateTime)	',
            Literal("-05:00"),
        ),
        (
            r'tz("2011-01-10T14:45:13.815Z"^^xsd:dateTime)	',
            Literal("Z"),
        ),
        (
            r'tz("2011-01-10T14:45:13.815"^^xsd:dateTime)	',
            Literal(""),
        ),
        (r'MD5("abc")', Literal("900150983cd24fb0d6963f7d28e17f72")),
        (r'SHA1("abc")', Literal("a9993e364706816aba3e25717850c26c9cd0d89d")),
        (
            r'SHA256("abc")',
            Literal("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
        ),
        (
            r'SHA384("abc")',
            Literal(
                "cb00753f45a35e8bb5a03d699ac65007272c32ab0eded1631a8b605a43ff5bed8086072ba1e7cc2358baeca134c825a7"
            ),
        ),
        (
            r'SHA512("abc")',
            Literal(
                "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f"
            ),
        ),
    ],
)
def test_function(expression: str, expected_result: Identifier) -> None:
    graph = Graph()
    query_string = """
    PREFIX eg: <https://example.com/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    CONSTRUCT { eg:subject eg:predicate ?o }
    WHERE {
        BIND(???EXPRESSION_PLACEHOLDER??? AS ?o)
    }
    """.replace(
        "???EXPRESSION_PLACEHOLDER???", expression
    )
    result = graph.query(query_string)
    assert result.type == "CONSTRUCT"
    assert isinstance(result.graph, Graph)
    logging.debug("result = %s", list(result.graph.triples((None, None, None))))
    actual_result = result.graph.value(EG.subject, EG.predicate, any=False)
    if isinstance(expected_result, type):
        assert isinstance(actual_result, expected_result)
    else:
        assert actual_result == expected_result


@pytest.mark.parametrize(
    ["literal", "range", "expected_result"],
    [
        (Literal("en"), Literal("en"), True),
        (Literal("en"), Literal("EN"), True),
        (Literal("EN"), Literal("en"), True),
        (Literal("EN"), Literal("EN"), True),
        (Literal("en"), Literal("en-US"), False),
        (Literal("en-US"), Literal("en-US"), True),
        (Literal("en-gb"), Literal("en-GB"), True),
    ],
)
def test_lang_range_check(
    literal: Literal, range: Literal, expected_result: bool
) -> None:
    actual_result = _lang_range_check(range, literal)
    assert expected_result == actual_result
