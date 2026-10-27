import subprocess
import sys
from collections.abc import Iterator
from io import BytesIO, StringIO

import pytest
from pyparsing import ParserElement

from rdflib.namespace import XSD
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.results.tsvresults import TSVResultParser
from rdflib.query import ResultRow
from rdflib.term import Literal, URIRef, Variable


def test_empty_tsvresults_bindings() -> None:
    # check that optional bindings are ordered properly
    source = """?s\t?p\t?o
    \t<urn:p>\t<urn:o>
    <urn:s>\t\t<urn:o>
    <urn:s>\t<urn:p>\t"""

    parser = TSVResultParser()
    source_io = StringIO(source)
    result = parser.parse(source_io)

    for idx, row in enumerate(result):
        assert isinstance(row, ResultRow)
        assert row[idx] is None


def test_dbpedia_style_optional_unbound_var() -> None:
    source = (
        "?person\t?deathDate\n"
        '<http://dbpedia.org/resource/Albert_Einstein>\t"1955-04-18"^^<http://www.w3.org/2001/XMLSchema#date>\n'
        "<http://dbpedia.org/resource/Barack_Obama>\t\n"
    )

    parser = TSVResultParser()
    result = parser.parse(StringIO(source))
    assert result.vars is not None
    person, death_date = result.vars

    assert len(result.bindings) == 2
    assert result.bindings[0][person] == URIRef(
        "http://dbpedia.org/resource/Albert_Einstein"
    )
    assert result.bindings[0][death_date] == Literal(
        "1955-04-18", datatype=URIRef("http://www.w3.org/2001/XMLSchema#date")
    )
    assert result.bindings[1][person] == URIRef(
        "http://dbpedia.org/resource/Barack_Obama"
    )
    assert death_date not in result.bindings[1]


def test_dbpedia_style_all_projected_vars_unbound_row_is_preserved() -> None:
    source = "?x\t?y\n\t\n"

    parser = TSVResultParser()
    result = parser.parse(StringIO(source))

    # Parser should preserve fully-unbound solution rows as empty mappings.
    assert len(result.bindings) == 1
    assert result.bindings[0] == {}


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        ("\t\t<urn:c>", {"c": URIRef("urn:c")}),
        ("<urn:a>\t \t<urn:c>", {"a": URIRef("urn:a"), "c": URIRef("urn:c")}),
        (" <urn:a> \t\t <urn:c> ", {"a": URIRef("urn:a"), "c": URIRef("urn:c")}),
        (" \t<urn:b>\t ", {"b": URIRef("urn:b")}),
    ],
)
def test_tabs_separate_columns_and_spaces_around_values_are_skipped(
    row: str, expected: dict[str, URIRef]
) -> None:
    result = TSVResultParser().parse(StringIO(f"?a\t?b\t?c\n{row}\n"))

    bindings = {Variable(var): value for var, value in expected.items()}
    assert result.bindings == [bindings]


def test_parse_tsv_from_bytes_skips_blank_lines() -> None:
    source = BytesIO(b"?x\n\n<urn:x1>\n")

    parser = TSVResultParser()
    result = parser.parse(source)
    assert result.vars is not None
    var_x = result.vars[0]

    assert len(result.bindings) == 1
    assert result.bindings[0][var_x] == URIRef("urn:x1")


@pytest.mark.parametrize(
    "cell",
    [
        pytest.param("-2.5", id="short"),
        pytest.param("-1.234567890123456789012345678901234567890", id="40-digits"),
    ],
)
def test_negative_decimal(cell: str) -> None:
    parser = TSVResultParser()
    result = parser.parse(StringIO(f"?a\n{cell}\n"))
    assert result.vars is not None
    var_a = result.vars[0]

    assert result.bindings == [{var_a: Literal(cell, datatype=XSD.decimal)}]


def test_crlf_line_endings() -> None:
    source = "?a\t?b\r\n<urn:a>\t\r\n\r\n\t<urn:b>\r\n"

    result = TSVResultParser().parse(StringIO(source))

    assert result.bindings == [
        {Variable("a"): URIRef("urn:a")},
        {Variable("b"): URIRef("urn:b")},
    ]


@pytest.fixture
def default_whitespace_without_cr() -> Iterator[None]:
    # Other code in the process can change pyparsing's default whitespace, as
    # `tsvresults` used to.
    default = ParserElement.DEFAULT_WHITE_CHARS
    ParserElement.set_default_whitespace_chars(" \n")
    try:
        yield
    finally:
        ParserElement.set_default_whitespace_chars(default)


def test_crlf_line_endings_do_not_depend_on_default_whitespace(
    default_whitespace_without_cr: None,
) -> None:
    result = TSVResultParser().parse(StringIO("?a\n<urn:a>\r\n"))

    assert result.bindings == [{Variable("a"): URIRef("urn:a")}]


def test_convert_term_rejects_unknown_compvalue_name() -> None:
    parser = TSVResultParser()

    with pytest.raises(Exception, match="I dont know how to handle this"):
        parser.convertTerm(CompValue("unknown", value="x"))


def test_convert_term_rejects_unexpected_type() -> None:
    parser = TSVResultParser()

    with pytest.raises(ValueError, match="Unexpected type"):
        parser.convertTerm("not-a-term")


def test_parsing_tsv_results_keeps_tabs_as_whitespace_for_other_grammars() -> None:
    # The TSV grammar is built when its plugin is first loaded, so check in a fresh
    # interpreter that loading it doesn't change how other pyparsing grammars that
    # are built afterwards treat tabs.
    script = """
from io import StringIO

from pyparsing import Word, alphas

from rdflib.query import Result

Result.parse(StringIO("?x\\n<urn:x>\\n"), format="tsv")
print(Word(alphas)[1, ...].parse_with_tabs().parse_string("a\\tb").as_list())
"""
    completed = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=30
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "['a', 'b']"
