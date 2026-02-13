from io import BytesIO, StringIO

import pytest

from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.results.tsvresults import TSVResultParser
from rdflib.query import ResultRow
from rdflib.term import Literal, URIRef


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


def test_parse_tsv_from_bytes_skips_blank_lines() -> None:
    source = BytesIO(b"?x\n\n<urn:x1>\n")

    parser = TSVResultParser()
    result = parser.parse(source)
    assert result.vars is not None
    var_x = result.vars[0]

    assert len(result.bindings) == 1
    assert result.bindings[0][var_x] == URIRef("urn:x1")


def test_convert_term_rejects_unknown_compvalue_name() -> None:
    parser = TSVResultParser()

    with pytest.raises(Exception, match="I dont know how to handle this"):
        parser.convertTerm(CompValue("unknown", value="x"))


def test_convert_term_rejects_unexpected_type() -> None:
    parser = TSVResultParser()

    with pytest.raises(ValueError, match="Unexpected type"):
        parser.convertTerm("not-a-term")
