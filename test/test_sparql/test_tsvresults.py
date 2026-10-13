"""Tests for SPARQL TSV result format parsing and serialization.

Parser tests exercise the pyparsing-based TSVResultParser.
Serializer tests exercise the TSVResultSerializer, covering term encoding,
structure, escaping, and round-trip correctness against W3C test data.
"""

from io import BytesIO, StringIO
from pathlib import Path

import pytest

from rdflib.namespace import XSD
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.results.tsvresults import (
    TSVResultParser,
    TSVResultSerializer,
    _serialize_term,
    _tsv_quote_encode,
)
from rdflib.query import Result, ResultRow
from rdflib.term import BNode, Literal, URIRef, Variable

# ---------------------------------------------------------------------------
# Path to W3C CSV/TSV result test data
# ---------------------------------------------------------------------------
W3C_DATA_DIR = (
    Path(__file__).parent.parent
    / "data"
    / "suites"
    / "w3c"
    / "sparql11"
    / "csv-tsv-res"
)


# ===========================================================================
# Parser tests
# ===========================================================================


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


# ===========================================================================
# Serializer tests: _tsv_quote_encode helper
# ===========================================================================


@pytest.mark.parametrize(
    ("input_str", "expected"),
    [
        pytest.param("hello", '"hello"', id="plain_string"),
        pytest.param("", '""', id="empty_string"),
        pytest.param("a\\b", '"a\\\\b"', id="backslash"),
        pytest.param('say "hi"', '"say \\"hi\\""', id="double_quote"),
        pytest.param("col1\tcol2", '"col1\\tcol2"', id="tab"),
        pytest.param("line1\nline2", '"line1\\nline2"', id="newline"),
        pytest.param("before\rafter", '"before\\rafter"', id="carriage_return"),
        pytest.param('\\\t\n\r"', '"\\\\\\t\\n\\r\\""', id="combined_escapes"),
    ],
)
def test_tsv_quote_encode(input_str: str, expected: str) -> None:
    """Verify TSV string quoting produces correct escape sequences."""
    assert _tsv_quote_encode(input_str) == expected


# ===========================================================================
# Serializer tests: _serialize_term
# ===========================================================================


@pytest.mark.parametrize(
    ("term", "expected"),
    [
        # URIs
        pytest.param(
            URIRef("http://example.org/x"),
            "<http://example.org/x>",
            id="uri",
        ),
        pytest.param(
            URIRef("http://example.org/ns#Thing"),
            "<http://example.org/ns#Thing>",
            id="uri_with_fragment",
        ),
        # Blank nodes
        pytest.param(BNode("b0"), "_:b0", id="bnode"),
        # Unbound (None)
        pytest.param(None, "", id="unbound"),
        # Plain string literals
        pytest.param(Literal("Hello"), '"Hello"', id="plain_string"),
        pytest.param(
            Literal('She said "hi"'),
            '"She said \\"hi\\""',
            id="string_with_double_quote",
        ),
        pytest.param(Literal("col1\tcol2"), '"col1\\tcol2"', id="string_with_tab"),
        pytest.param(
            Literal("line1\nline2"), '"line1\\nline2"', id="string_with_newline"
        ),
        pytest.param(Literal("before\rafter"), '"before\\rafter"', id="string_with_cr"),
        pytest.param(
            Literal("path\\to\\file"),
            '"path\\\\to\\\\file"',
            id="string_with_backslash",
        ),
        # Language-tagged literals
        pytest.param(Literal("chat", lang="fr"), '"chat"@fr', id="lang_tagged"),
        pytest.param(
            Literal("colour", lang="en-GB"),
            '"colour"@en-GB',
            id="lang_tagged_with_region",
        ),
        # Typed literals (non-abbreviated)
        pytest.param(
            Literal("2023-01-01", datatype=XSD.date),
            '"2023-01-01"^^<http://www.w3.org/2001/XMLSchema#date>',
            id="typed_xsd_date",
        ),
        pytest.param(
            Literal("foo", datatype=XSD.string),
            '"foo"^^<http://www.w3.org/2001/XMLSchema#string>',
            id="typed_xsd_string",
        ),
        pytest.param(
            Literal("value", datatype=URIRef("http://example.org/myType")),
            '"value"^^<http://example.org/myType>',
            id="typed_custom_datatype",
        ),
        pytest.param(
            Literal("a7", datatype=XSD.hexBinary),
            '"a7"^^<http://www.w3.org/2001/XMLSchema#hexBinary>',
            id="typed_hex_binary",
        ),
        # Abbreviated numeric literals
        pytest.param(Literal(42), "42", id="integer"),
        pytest.param(Literal(-7), "-7", id="negative_integer"),
        pytest.param(Literal(0), "0", id="zero_integer"),
        pytest.param(Literal("5.5", datatype=XSD.decimal), "5.5", id="decimal"),
        pytest.param(
            Literal("3", datatype=XSD.decimal), "3.0", id="decimal_integer_form"
        ),
        # Abbreviated boolean literals
        pytest.param(Literal(True), "true", id="boolean_true"),
        pytest.param(Literal(False), "false", id="boolean_false"),
        # Non-abbreviated integer subtype
        pytest.param(
            Literal("-3", datatype=XSD.negativeInteger),
            '"-3"^^<http://www.w3.org/2001/XMLSchema#negativeInteger>',
            id="negative_integer_subtype",
        ),
    ],
)
def test_serialize_term(term, expected: str) -> None:
    """Verify individual RDF term serialization to TSV format."""
    assert _serialize_term(term) == expected


@pytest.mark.parametrize(
    ("term", "substring"),
    [
        pytest.param(
            Literal("1.5", datatype=XSD.double),
            "e",
            id="double_scientific_notation",
        ),
        pytest.param(
            Literal("1.0E6", datatype=XSD.double),
            "e",
            id="double_large_scientific_notation",
        ),
    ],
)
def test_serialize_term_double_notation(term, substring: str) -> None:
    """Verify xsd:double uses scientific notation (exact form varies)."""
    result = _serialize_term(term)
    assert substring in result.lower()


@pytest.mark.parametrize(
    "term",
    [
        pytest.param(Literal(float("inf"), datatype=XSD.double), id="double_inf"),
        pytest.param(Literal(float("nan"), datatype=XSD.double), id="double_nan"),
    ],
)
def test_serialize_term_non_abbreviated_specials(term) -> None:
    """Verify inf/NaN fall back to quoted form with datatype annotation."""
    result = _serialize_term(term)
    assert result.startswith('"')
    assert "^^<" in result
    assert "double" in result


# ===========================================================================
# Serializer tests: full serialization structure
# ===========================================================================


class TestTSVResultSerializer:
    """Tests for the complete TSVResultSerializer output."""

    def _make_result(self, vars, bindings):
        """Helper to build a Result object with given vars and bindings."""
        r = Result("SELECT")
        r.vars = [Variable(v) for v in vars]
        r.bindings = []
        for binding in bindings:
            row = {}
            for var_name, term in binding.items():
                row[Variable(var_name)] = term
            r.bindings.append(row)
        return r

    def _serialize(self, result: Result) -> str:
        """Serialize a Result to a TSV string."""
        buf = BytesIO()
        serializer = TSVResultSerializer(result)
        serializer.serialize(buf)
        return buf.getvalue().decode("utf-8")

    def test_header_row(self) -> None:
        result = self._make_result(["s", "p", "o"], [])
        output = self._serialize(result)
        # Header should be first line, variables prefixed with '?'
        lines = output.split("\n")
        assert lines[0] == "?s\t?p\t?o"

    def test_single_variable(self) -> None:
        result = self._make_result(
            ["x"],
            [{"x": URIRef("http://example.org/a")}],
        )
        output = self._serialize(result)
        lines = output.strip("\n").split("\n")
        assert lines[0] == "?x"
        assert lines[1] == "<http://example.org/a>"

    def test_multiple_rows(self) -> None:
        result = self._make_result(
            ["x", "y"],
            [
                {"x": URIRef("http://ex.org/1"), "y": Literal("hello")},
                {"x": URIRef("http://ex.org/2"), "y": Literal("world")},
            ],
        )
        output = self._serialize(result)
        lines = output.strip("\n").split("\n")
        assert len(lines) == 3  # header + 2 data rows
        assert lines[1] == '<http://ex.org/1>\t"hello"'
        assert lines[2] == '<http://ex.org/2>\t"world"'

    def test_unbound_variable_middle(self) -> None:
        # Unbound variable in the middle produces an empty field
        result = self._make_result(
            ["s", "p", "o"],
            [{"s": URIRef("urn:s"), "o": URIRef("urn:o")}],  # p is unbound
        )
        output = self._serialize(result)
        lines = output.strip("\n").split("\n")
        assert lines[1] == "<urn:s>\t\t<urn:o>"

    def test_unbound_variable_end(self) -> None:
        # Unbound variable at end of row
        result = self._make_result(
            ["s", "p", "o"],
            [{"s": URIRef("urn:s"), "p": URIRef("urn:p")}],  # o is unbound
        )
        output = self._serialize(result)
        lines = output.strip("\n").split("\n")
        assert lines[1] == "<urn:s>\t<urn:p>\t"

    def test_fully_unbound_row(self) -> None:
        # All variables unbound -> row is just tabs
        result = self._make_result(["a", "b", "c"], [{}])
        output = self._serialize(result)
        lines = output.strip("\n").split("\n")
        assert lines[1] == "\t\t"

    def test_empty_result_set(self) -> None:
        # No bindings -> just the header row
        result = self._make_result(["x", "y"], [])
        output = self._serialize(result)
        lines = output.strip("\n").split("\n")
        assert len(lines) == 1
        assert lines[0] == "?x\t?y"

    def test_line_endings_are_lf(self) -> None:
        # TSV spec requires LF, not CRLF
        result = self._make_result(["x"], [{"x": URIRef("urn:a")}])
        output = self._serialize(result)
        assert "\r\n" not in output
        assert "\r" not in output
        assert output.endswith("\n")

    def test_encoding_utf8_default(self) -> None:
        # Verify that non-ASCII characters are encoded correctly
        result = self._make_result(
            ["x"],
            [{"x": Literal("\u00e9l\u00e8ve")}],  # "élève"
        )
        buf = BytesIO()
        serializer = TSVResultSerializer(result)
        serializer.serialize(buf, encoding="utf-8")
        raw = buf.getvalue()
        # Should contain the UTF-8 encoded form, not escaped
        assert "\u00e9l\u00e8ve".encode() in raw

    def test_non_select_raises(self) -> None:
        # ASK results should be rejected
        r = Result("ASK")
        r.askAnswer = True
        with pytest.raises(Exception, match="SELECT"):
            TSVResultSerializer(r)

    def test_serialize_to_text_stream(self) -> None:
        # Verify serialization works with a text stream (StringIO-like)
        result = self._make_result(["x"], [{"x": URIRef("urn:test")}])
        buf = StringIO()
        serializer = TSVResultSerializer(result)
        serializer.serialize(buf)
        output = buf.getvalue()
        assert output == "?x\n<urn:test>\n"

    def test_mixed_term_types(self) -> None:
        # Row with IRI, literal, bnode, integer
        result = self._make_result(
            ["a", "b", "c", "d"],
            [
                {
                    "a": URIRef("http://example.org/x"),
                    "b": Literal("text"),
                    "c": BNode("node1"),
                    "d": Literal(99),
                }
            ],
        )
        output = self._serialize(result)
        lines = output.strip("\n").split("\n")
        assert lines[1] == '<http://example.org/x>\t"text"\t_:node1\t99'


# ===========================================================================
# Serializer tests: round-trip (serialize -> parse)
# ===========================================================================


class TestTSVRoundTrip:
    """Verify that serializing and then parsing produces equivalent bindings."""

    def _round_trip(self, result: Result) -> Result:
        """Serialize then parse a Result, returning the parsed copy."""
        buf = BytesIO()
        serializer = TSVResultSerializer(result)
        serializer.serialize(buf)
        buf.seek(0)
        parser = TSVResultParser()
        return parser.parse(buf)

    def _make_result(self, vars, bindings):
        r = Result("SELECT")
        r.vars = [Variable(v) for v in vars]
        r.bindings = []
        for binding in bindings:
            row = {}
            for var_name, term in binding.items():
                row[Variable(var_name)] = term
            r.bindings.append(row)
        return r

    def test_round_trip_uris(self) -> None:
        original = self._make_result(
            ["x"],
            [
                {"x": URIRef("http://example.org/a")},
                {"x": URIRef("http://example.org/b")},
            ],
        )
        parsed = self._round_trip(original)
        assert parsed.vars == original.vars
        assert len(parsed.bindings) == 2
        x = Variable("x")
        assert parsed.bindings[0][x] == URIRef("http://example.org/a")
        assert parsed.bindings[1][x] == URIRef("http://example.org/b")

    def test_round_trip_literals(self) -> None:
        original = self._make_result(
            ["val"],
            [
                {"val": Literal("plain")},
                {"val": Literal("tagged", lang="en")},
                {"val": Literal("2023-01-01", datatype=XSD.date)},
                {"val": Literal(42)},
                {"val": Literal(True)},
            ],
        )
        parsed = self._round_trip(original)
        val = Variable("val")
        assert parsed.bindings[0][val] == Literal("plain")
        assert parsed.bindings[1][val] == Literal("tagged", lang="en")
        assert parsed.bindings[2][val] == Literal("2023-01-01", datatype=XSD.date)
        assert parsed.bindings[3][val] == Literal(42)
        assert parsed.bindings[4][val] == Literal(True)

    def test_round_trip_unbound_vars(self) -> None:
        original = self._make_result(
            ["a", "b"],
            [
                {"a": URIRef("urn:x")},  # b is unbound
                {"b": Literal("y")},  # a is unbound
                {},  # both unbound
            ],
        )
        parsed = self._round_trip(original)
        a, b = Variable("a"), Variable("b")
        assert parsed.bindings[0][a] == URIRef("urn:x")
        assert b not in parsed.bindings[0]
        assert a not in parsed.bindings[1]
        assert parsed.bindings[1][b] == Literal("y")
        assert parsed.bindings[2] == {}

    def test_round_trip_special_characters_in_literals(self) -> None:
        # Literals with characters that need escaping
        original = self._make_result(
            ["val"],
            [
                {"val": Literal("tab\there")},
                {"val": Literal("new\nline")},
                {"val": Literal("cr\rhere")},
                {"val": Literal('quote"here')},
                {"val": Literal("back\\slash")},
            ],
        )
        parsed = self._round_trip(original)
        val = Variable("val")
        assert parsed.bindings[0][val] == Literal("tab\there")
        assert parsed.bindings[1][val] == Literal("new\nline")
        assert parsed.bindings[2][val] == Literal("cr\rhere")
        assert parsed.bindings[3][val] == Literal('quote"here')
        assert parsed.bindings[4][val] == Literal("back\\slash")

    def test_round_trip_empty_result(self) -> None:
        original = self._make_result(["x", "y"], [])
        parsed = self._round_trip(original)
        assert parsed.vars == original.vars
        assert len(parsed.bindings) == 0


# ===========================================================================
# W3C test data round-trip tests
# ===========================================================================


class TestW3CRoundTrip:
    """Round-trip tests using W3C SPARQL 1.1 TSV expected result files.

    For each .tsv file: parse it, serialize the result back to TSV, parse
    again, and verify the bindings are semantically equivalent.  Blank node
    labels are not compared by identity -- only their structural role matters.
    """

    def _bindings_equivalent(self, bindings_a, bindings_b) -> bool:
        """Check if two binding lists are equivalent modulo blank node labels.

        Builds a positional bnode mapping: bnodes encountered in the same
        structural positions map to sequential canonical IDs independently
        within each binding list.
        """
        if len(bindings_a) != len(bindings_b):
            return False

        bnode_map_a = {}  # bnode_label_a -> canonical id
        bnode_map_b = {}  # bnode_label_b -> canonical id
        next_id_a = [0]
        next_id_b = [0]

        def canonical_a(term):
            if isinstance(term, BNode):
                label = str(term)
                if label not in bnode_map_a:
                    bnode_map_a[label] = next_id_a[0]
                    next_id_a[0] += 1
                return ("BNODE", bnode_map_a[label])
            return term

        def canonical_b(term):
            if isinstance(term, BNode):
                label = str(term)
                if label not in bnode_map_b:
                    bnode_map_b[label] = next_id_b[0]
                    next_id_b[0] += 1
                return ("BNODE", bnode_map_b[label])
            return term

        for row_a, row_b in zip(bindings_a, bindings_b):
            if set(row_a.keys()) != set(row_b.keys()):
                return False
            for var in row_a:
                term_a = canonical_a(row_a[var])
                term_b = canonical_b(row_b[var])
                if term_a != term_b:
                    return False
        return True

    @pytest.mark.parametrize(
        "tsv_filename",
        ["csvtsv01.tsv", "csvtsv02.tsv", "csvtsv03.tsv"],
    )
    def test_w3c_tsv_round_trip(self, tsv_filename: str) -> None:
        """Parse W3C expected .tsv, serialize, re-parse, and compare."""
        tsv_path = W3C_DATA_DIR / tsv_filename
        assert tsv_path.exists(), f"W3C test file not found: {tsv_path}"

        # Step 1: Parse the original .tsv file
        parser = TSVResultParser()
        with open(tsv_path, "r", encoding="utf-8") as f:
            original_result = parser.parse(f)

        # Step 2: Serialize the parsed result back to TSV
        buf = BytesIO()
        serializer = TSVResultSerializer(original_result)
        serializer.serialize(buf)

        # Step 3: Parse the re-serialized TSV
        buf.seek(0)
        reparsed_result = parser.parse(buf)

        # Step 4: Compare bindings (modulo blank node labels)
        assert (
            original_result.vars == reparsed_result.vars
        ), f"Variable lists differ: {original_result.vars} vs {reparsed_result.vars}"
        assert self._bindings_equivalent(
            original_result.bindings, reparsed_result.bindings
        ), (
            f"Bindings differ after round-trip for {tsv_filename}.\n"
            f"Original: {original_result.bindings}\n"
            f"Reparsed: {reparsed_result.bindings}"
        )
