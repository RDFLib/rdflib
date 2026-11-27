"""
Every RDF 1.1 literal has a datatype (RDF 1.1 Concepts and Abstract Syntax,
section 3.3): ``rdf:langString`` if and only if it has a language tag, and
otherwise the datatype it is given. A simple literal, written without a
datatype, is syntactic sugar for an ``xsd:string`` literal, so ``"a"`` and
``"a"^^xsd:string`` are the same literal.

RDFLib left the datatype of such literals ``None``, so ``"a"`` and
``"a"^^xsd:string`` were different terms: a graph held both, and code that
compares terms, such as a SPARQL triple pattern or a SHACL ``sh:in`` check, did
not match one against the other.
"""

from __future__ import annotations

import json
import pickle
from datetime import date

import pytest

from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef
from rdflib.plugins.sparql.processor import prepareQuery
from rdflib.query import ResultRow
from rdflib.store import NodePickler

EX = Namespace("http://example.org/")


def test_a_literal_without_a_datatype_is_an_xsd_string_literal() -> None:
    plain, typed = Literal("a"), Literal("a", datatype=XSD.string)

    assert plain.datatype == XSD.string
    assert plain == typed
    assert hash(plain) == hash(typed)
    assert {plain, typed} == {plain}
    assert plain.ill_typed is False


def test_a_language_tagged_literal_has_the_datatype_rdf_langstring() -> None:
    tagged = Literal("a", lang="en")

    assert tagged.datatype == RDF.langString
    assert tagged == Literal("a", lang="en", datatype=RDF.langString)
    assert tagged != Literal("a")
    assert tagged.ill_typed is False


def test_a_language_tag_with_another_datatype_is_refused() -> None:
    with pytest.raises(TypeError):
        Literal("a", lang="en", datatype=XSD.string)


@pytest.mark.parametrize(
    ("made", "expected"),
    [
        (Literal(Literal("a")), Literal("a")),
        (Literal(Literal("a", lang="en")), Literal("a", lang="en")),
        # A datatype given replaces the language tag, and a tag the datatype.
        (Literal(Literal("a", lang="en"), datatype=XSD.string), Literal("a")),
        (Literal(Literal(1), lang="en"), Literal("1", lang="en")),
        (Literal(Literal("a", lang="en"), lang="de"), Literal("a", lang="de")),
    ],
)
def test_a_copied_literal_has_the_datatype_its_language_tag_implies(
    made: Literal, expected: Literal
) -> None:
    assert made == expected
    assert (made.language, made.datatype) == (expected.language, expected.datatype)
    assert made.value == expected.value


def test_a_copied_literal_keeps_whether_it_is_ill_typed() -> None:
    assert Literal(Literal("a")).ill_typed is False
    assert Literal(Literal("a", lang="en")).ill_typed is False
    assert Literal(Literal("x", datatype=XSD.integer)).ill_typed is True


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (Literal("a", lang="en"), "b", Literal("ab", lang="en")),
        (Literal("a", lang="en"), Literal("b"), Literal("ab", lang="en")),
        (Literal("a", lang="en"), Literal("b", lang="en"), Literal("ab", lang="en")),
        (Literal("a"), Literal("b", lang="en"), Literal("ab")),
        (Literal("a", datatype=XSD.string), "b", Literal("ab")),
    ],
)
def test_adding_to_a_string_literal_keeps_its_language_tag(
    left: Literal, right: str | Literal, expected: Literal
) -> None:
    assert left + right == expected


def test_language_tagged_literals_sort_after_the_xsd_string_literals() -> None:
    """The order RDFLib 7 gave, where a language-tagged literal had no datatype."""
    tagged_en, tagged_de = Literal("a", lang="en"), Literal("a", lang="de")
    day, one, b = Literal(date(2020, 1, 1)), Literal(1), Literal("b")
    c, custom = (
        Literal("c", datatype=XSD.string),
        Literal("x", datatype=URIRef("urn:dt")),
    )

    ordered = sorted([one, tagged_en, day, b, c, tagged_de, custom])

    assert ordered == [day, one, b, c, tagged_de, tagged_en, custom]
    assert b < tagged_en
    assert not tagged_en < b


def test_a_graph_holds_a_simple_literal_and_its_xsd_string_form_once() -> None:
    g = Graph().parse(
        data=f'<{EX.s}> <{EX.p}> "a" , "a"^^<{XSD.string}> .', format="turtle"
    )

    assert len(g) == 1


def test_the_implied_datatype_is_not_shown_by_repr_or_n3() -> None:
    assert repr(Literal("a", datatype=XSD.string)) == "rdflib.term.Literal('a')"
    assert repr(Literal("a", lang="en")) == "rdflib.term.Literal('a', lang='en')"
    assert Literal("a", datatype=XSD.string).n3() == '"a"'
    assert Literal("a", lang="en").n3() == '"a"@en'


# A simple and a language-tagged literal as RDFLib 7 pickled them, with
# protocol 2, whose bytes do not depend on the Python version, and the
# arguments its __reduce__ gave them.
RDFLIB7_PICKLES = [
    pytest.param(
        Literal("a"),
        b"\x80\x02crdflib.term\nLiteral\nq\x00X\x01\x00\x00\x00aq\x01NN\x87q\x02Rq\x03.",
        ("a", None, None),
        id="simple",
    ),
    pytest.param(
        Literal("a", lang="en"),
        b"\x80\x02crdflib.term\nLiteral\nq\x00X\x01\x00\x00\x00aq\x01X\x02\x00\x00"
        b"\x00enq\x02N\x87q\x03Rq\x04.",
        ("a", "en", None),
        id="language-tagged",
    ),
]


@pytest.mark.parametrize(("literal", "pickled", "reduced"), RDFLIB7_PICKLES)
def test_a_literal_with_an_implied_datatype_pickles_as_in_rdflib_7(
    literal: Literal, pickled: bytes, reduced: tuple[str, str | None, None]
) -> None:
    assert pickle.loads(pickled) == literal
    assert pickle.loads(pickled).datatype == literal.datatype
    assert pickle.dumps(literal, protocol=2) == pickled
    # The store's NodePickler, whose output the BerkeleyDB store uses as the
    # key, pickles these arguments with Python's default protocol.
    assert literal.__reduce__() == (Literal, reduced)
    assert NodePickler().dumps(literal) == pickle.dumps(literal)
    assert NodePickler().dumps(Literal("a", datatype=XSD.string)) == (
        NodePickler().dumps(Literal("a"))
    )


@pytest.mark.parametrize("literal", [Literal("a"), Literal("a", lang="en")])
def test_the_state_of_a_literal_restores_its_implied_datatype(
    literal: Literal,
) -> None:
    restored = Literal.__new__(Literal, str(literal))
    restored.__setstate__(literal.__getstate__())

    assert (restored.language, restored.datatype) == (
        literal.language,
        literal.datatype,
    )


def _graph() -> Graph:
    g = Graph(bind_namespaces="none")
    g.bind("ex", EX)
    g.add((EX.s, EX.p, Literal("a", datatype=XSD.string)))
    g.add((EX.s, EX.q, Literal("b", lang="en")))
    return g


@pytest.mark.parametrize(
    ("fmt", "simple", "tagged"),
    [
        ("nt", f'<{EX.s}> <{EX.p}> "a" .', f'<{EX.s}> <{EX.q}> "b"@en .'),
        ("turtle", 'ex:p "a"', 'ex:q "b"@en'),
        ("origturtle", 'ex:p "a"', 'ex:q "b"@en'),
        ("n3", 'ex:p "a"', 'ex:q "b"@en'),
        ("xml", "<ex:p>a</ex:p>", '<ex:q xml:lang="en">b</ex:q>'),
        ("pretty-xml", "<ex:p>a</ex:p>", '<ex:q xml:lang="en">b</ex:q>'),
        ("trix", "<plainLiteral>a</plainLiteral>", 'xml:lang="en">b</plainLiteral>'),
    ],
)
def test_an_xsd_string_literal_is_written_as_a_simple_literal(
    fmt: str, simple: str, tagged: str
) -> None:
    out = _graph().serialize(format=fmt)

    assert simple in out
    assert tagged in out
    assert "XMLSchema#string" not in out
    assert "langString" not in out
    assert "xsd:" not in out


def test_json_ld_writes_an_xsd_string_literal_without_a_type() -> None:
    doc = json.loads(_graph().serialize(format="json-ld"))
    (node,) = doc if isinstance(doc, list) else doc["@graph"]

    assert node[str(EX.p)] == [{"@value": "a"}]
    assert node[str(EX.q)] == [{"@value": "b", "@language": "en"}]


@pytest.mark.parametrize(
    ("context", "expected"),
    [
        # Compaction picks a term typed xsd:string only for a value with that
        # @type, which RDF to Object Conversion never gives; pyld 3.3.0 writes
        # the same.
        (
            {"name": {"@id": str(EX.p), "@type": str(XSD.string)}},
            {str(EX.p): "a"},
        ),
        # A value object without @language keeps a default language off it.
        (
            {"@language": "en", "name": {"@id": str(EX.p)}},
            {"name": {"@value": "a"}},
        ),
    ],
)
def test_json_ld_writes_an_xsd_string_literal_as_json_ld_compaction_does(
    context: dict[str, object], expected: dict[str, object]
) -> None:
    g = Graph()
    g.add((EX.s, EX.p, Literal("a", datatype=XSD.string)))

    out = json.loads(g.serialize(format="json-ld", context=context))
    out.pop("@context")

    assert out == {"@id": str(EX.s), **expected}
    assert set(
        Graph().parse(data=json.dumps(out | {"@context": context}), format="json-ld")
    ) == set(g)


def test_sparql_results_write_an_xsd_string_literal_without_a_datatype() -> None:
    result = _graph().query(f"SELECT ?o WHERE {{ <{EX.s}> <{EX.p}> ?o }}")

    as_json = json.loads(result.serialize(format="json") or b"")
    as_xml = (result.serialize(format="xml") or b"").decode("utf-8")
    as_tsv = (result.serialize(format="tsv") or b"").decode("utf-8")

    assert as_json["results"]["bindings"] == [{"o": {"type": "literal", "value": "a"}}]
    assert "<literal>a</literal>" in as_xml
    assert as_tsv.splitlines() == ["?o", '"a"']


@pytest.mark.parametrize(
    "pattern",
    [
        '?s <urn:p> "a"',
        '?s <urn:p> ?o FILTER(sameTerm(?o, "a"))',
        '?s <urn:p> ?o FILTER(?o IN ("a"))',
        '?s <urn:p> ?o FILTER(?o = "a")',
        '?s <urn:p> ?o FILTER(!(?o NOT IN ("a")))',
    ],
)
def test_sparql_matches_a_simple_literal_against_an_xsd_string_one(
    pattern: str,
) -> None:
    g = Graph()
    g.add((URIRef("urn:s"), URIRef("urn:p"), Literal("a", datatype=XSD.string)))

    assert len(g.query(f"SELECT ?s WHERE {{ {pattern} }}")) == 1


def test_sparql_groups_a_simple_literal_with_its_xsd_string_form() -> None:
    g = Graph()
    g.add((URIRef("urn:s1"), URIRef("urn:p"), Literal("a")))
    g.add((URIRef("urn:s2"), URIRef("urn:p"), Literal("a", datatype=XSD.string)))

    rows = list(
        g.query("SELECT ?o (COUNT(?s) AS ?n) WHERE { ?s <urn:p> ?o } GROUP BY ?o")
    )

    assert [tuple(row) for row in rows] == [(Literal("a"), Literal(2))]  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ('DATATYPE("a")', XSD.string),
        ('DATATYPE("a"@en)', RDF.langString),
        (f'STRLANG("a"^^<{XSD.string}>, "en")', Literal("a", lang="en")),
        (f'<{XSD.string}>("a"@en)', Literal("a")),
        ('CONCAT("a"@en, "b"@de)', Literal("ab")),
        ('CONCAT("a"@en, "b"@en)', Literal("ab", lang="en")),
        ('UCASE("a"@en)', Literal("A", lang="en")),
        ('STRLEN("ab"@en)', Literal(2)),
        # A literal of the datatype rdf:langString needs a language tag.
        (f'UCASE("a"^^<{RDF.langString}>)', None),
        (f'STRLANG("a"^^<{RDF.langString}>, "en")', None),
    ],
)
def test_sparql_functions_treat_a_simple_literal_as_xsd_string(
    expression: str, expected: URIRef | Literal | None
) -> None:
    # ?x keeps the row when the expression is an error and leaves ?v unbound.
    query = prepareQuery(
        f"SELECT ?x ?v WHERE {{ BIND(1 AS ?x) BIND({expression} AS ?v) }}"
    )

    (row,) = Graph().query(query)

    assert isinstance(row, ResultRow)
    assert row.v == expected
