"""
Infinite and NaN doubles and floats have the lexical forms `INF`, `-INF` and
`NaN`.

These are the canonical forms of the special values of `xsd:double` and
`xsd:float` (XML Schema 1.1 Part 2, appendix E.1). A literal took its lexical
form from Python's `str()` instead, `inf` and `nan`, which are not in the
lexical space of these types at all. Only Turtle and N3 output corrected that
(#658). N-Triples, N-Quads, RDF/XML and SPARQL wrote the Python spelling, and
reading a valid `"INF"^^xsd:double` turned it into `"inf"`.
"""

from __future__ import annotations

import math

import pytest

from rdflib import XSD, Dataset, Graph, Literal, URIRef, Variable

S = URIRef("http://example.org/s")
P = URIRef("http://example.org/p")


@pytest.mark.parametrize(
    ("literal", "lexical"),
    [
        pytest.param(Literal(math.inf), "INF", id="float-inf"),
        pytest.param(Literal(-math.inf), "-INF", id="float-minus-inf"),
        pytest.param(Literal(math.nan), "NaN", id="float-nan"),
        pytest.param(Literal(-math.nan), "NaN", id="float-minus-nan"),
        pytest.param(Literal(math.inf, datatype=XSD.float), "INF", id="inf-as-float"),
        pytest.param(Literal("INF", datatype=XSD.double), "INF", id="typed-INF"),
        pytest.param(Literal("+INF", datatype=XSD.double), "INF", id="typed-plus-INF"),
        pytest.param(
            Literal("-INF", datatype=XSD.double), "-INF", id="typed-minus-INF"
        ),
        pytest.param(Literal("NaN", datatype=XSD.double), "NaN", id="typed-NaN"),
        pytest.param(Literal("INF", datatype=XSD.float), "INF", id="typed-float-INF"),
        pytest.param(
            Literal("inf", datatype=XSD.double, normalize=False).normalize(),
            "INF",
            id="normalized",
        ),
    ],
)
def test_a_special_value_has_its_xsd_lexical_form(
    literal: Literal, lexical: str
) -> None:
    assert str(literal) == lexical
    assert literal == Literal(lexical, datatype=literal.datatype)


@pytest.mark.parametrize(
    "format", ["nt", "nquads", "xml", "pretty-xml", "trix", "hext", "patch"]
)
def test_special_values_are_written_in_their_xsd_lexical_forms(format: str) -> None:
    g = Dataset() if format in ("nquads", "patch") else Graph()
    for value in (math.inf, -math.inf, math.nan):
        g.add((S, P, Literal(value)))

    data = g.serialize(format=format)

    for lexical in ("INF", "-INF", "NaN"):
        assert f'"{lexical}"' in data or f">{lexical}<" in data
    for python_form in ("inf", "-inf", "nan"):
        assert f'"{python_form}"' not in data and f">{python_form}<" not in data


def test_special_values_round_trip_through_n_triples_unchanged() -> None:
    data = "".join(
        f'<{S}> <{P}> "{lexical}"^^<{datatype}> .\n'
        for lexical in ("INF", "-INF", "NaN")
        for datatype in (XSD.double, XSD.float)
    )

    g = Graph().parse(data=data, format="nt")

    assert sorted(g.serialize(format="nt").splitlines()) == sorted(data.splitlines())


def test_a_sparql_pattern_with_a_special_value_matches_parsed_data() -> None:
    g = Graph().parse(
        data=f'<{S}> <{P}> "INF"^^<{XSD.double}>, "NaN"^^<{XSD.double}> .',
        format="turtle",
    )
    query = 'SELECT ?s { ?s ?p "INF"^^xsd:double , "NaN"^^xsd:double }'

    assert g.query(query, initNs={"xsd": XSD}).bindings == [{Variable("s"): S}]


def test_sparql_str_of_a_special_value_is_its_xsd_lexical_form() -> None:
    query = (
        'SELECT (STR(xsd:double("INF")) AS ?inf) (STR(xsd:double("NaN")) AS ?nan) {}'
    )

    (binding,) = Graph().query(query, initNs={"xsd": XSD}).bindings

    assert {str(name): str(value) for name, value in binding.items()} == {
        "inf": "INF",
        "nan": "NaN",
    }


@pytest.mark.parametrize(
    ("literal", "lexical"),
    [
        pytest.param(Literal(1.5), "1.5", id="fraction"),
        pytest.param(Literal(1e-07), "1e-07", id="small"),
        pytest.param(Literal(-0.0), "-0.0", id="negative-zero"),
        pytest.param(Literal(1e300), "1e+300", id="large"),
        pytest.param(
            Literal("inf", datatype=XSD.double, normalize=False),
            "inf",
            id="not-normalized",
        ),
        pytest.param(Literal("inf"), "inf", id="plain-string"),
    ],
)
def test_other_lexical_forms_are_unchanged(literal: Literal, lexical: str) -> None:
    """Guard: finite values, unnormalized literals and strings keep their form."""
    assert str(literal) == lexical


@pytest.mark.parametrize(
    ("lexical", "written"),
    [
        pytest.param("infinity", "INF", id="infinity"),
        pytest.param("INFINITY", "INF", id="uppercase-infinity"),
        pytest.param("-Infinity", "-INF", id="minus-infinity"),
        pytest.param("NAN", "NaN", id="uppercase-nan"),
        pytest.param("inf", "INF", id="inf"),
        pytest.param("+INF", "+INF", id="plus-INF-kept"),
        pytest.param("1e400", "1e400", id="overflowing-numeral-kept"),
        pytest.param(" 1e400", " 1e400", id="padded-overflowing-numeral-kept"),
    ],
)
def test_n3_writes_an_unnormalized_special_value_in_an_xsd_form(
    lexical: str, written: str
) -> None:
    """Python's spellings are replaced; numerals and valid XSD forms are kept."""
    literal = Literal(lexical, datatype=XSD.double, normalize=False)

    assert literal.n3() == f'"{written}"^^<{XSD.double}>'


def test_n3_keeps_an_overflowing_decimal_numeral() -> None:
    """Guard: a decimal too large for a float is not rewritten as INF."""
    lexical = " 1" + "0" * 400
    literal = Literal(lexical, datatype=XSD.decimal, normalize=False)

    assert literal.n3() == f'"{lexical}"^^<{XSD.decimal}>'


@pytest.mark.parametrize("datatype", [XSD.double, XSD.float])
def test_turtle_writes_an_unnormalized_python_spelling_in_an_xsd_form(
    datatype: URIRef,
) -> None:
    g = Graph()
    for value in ("infinity", "-Infinity", "NAN"):
        g.add((S, P, Literal(value, datatype=datatype, normalize=False)))

    data = g.serialize(format="turtle")

    for lexical in ("INF", "-INF", "NaN"):
        assert f'"{lexical}"^^' in data
    for python_form in ("infinity", "Infinity", "NAN"):
        assert python_form not in data
