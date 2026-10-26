import itertools
import os
from urllib.error import URLError

import pytest

from rdflib.compare import isomorphic
from rdflib.graph import Dataset, Graph
from rdflib.plugins.parsers.notation3 import BadSyntax, exponent_syntax, join
from rdflib.term import Literal, URIRef
from test import TEST_DIR

test_data = """
#  Definitions of terms describing the n3 model
#

@keywords a.

@prefix n3: <#>.
@prefix log: <log.n3#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <#> .

@forAll :s, :p, :x, :y, :z.

n3:Statement    a rdf:Class .
n3:StatementSet a rdf:Class .

n3:includes     a rdfs:Property .   # Cf rdf:li

n3:predicate    a rdf:Property; rdfs:domain n3:statement .
n3:subject      a rdf:Property; rdfs:domain n3:statement .
n3:object       a rdf:Property; rdfs:domain n3:statement .

n3:context      a rdf:Property; rdfs:domain n3:statement;
                rdfs:range n3:StatementSet .



########### Rules

{ :x :p :y . } log:means { [
                n3:subject :x;
                n3:predicate :p;
                n3:object :y ] a log:Truth}.

# Needs more thought ... ideally, we have the implicit AND rules of
# juxtaposition (introduction and elimination)

{
    {
        {  :x n3:includes :s. } log:implies { :y n3:includes :s. } .
    } forall :s1 .
} log:implies { :x log:implies :y } .

{
    {
        {  :x n3:includes :s. } log:implies { :y n3:includes :s. } .
    } forall :s1
} log:implies { :x log:implies :y } .

# I think n3:includes has to be axiomatic builtin. - unless you go to syntax description.
# syntax.n3?
"""


class TestN3Case:
    def test_base_cumulative(self):
        """
        Test that the n3 parser supports base declarations
        This is issue #22
        """

        input = """
@prefix : <http://example.com/> .
# default base
<foo> :name "Foo" .
# change it
@base <http://example.com/doc/> .
<bar> :name "Bar" .
# and change it more - they are cumulative
@base <doc2/> .
<bing> :name "Bing" .
# unless abosulute
@base <http://test.com/> .
<bong> :name "Bong" .

"""
        g = Graph()
        g.parse(data=input, format="n3")
        print(list(g))
        assert (None, None, Literal("Foo")) in g
        assert (URIRef("http://example.com/doc/bar"), None, None) in g
        assert (URIRef("http://example.com/doc/doc2/bing"), None, None) in g
        assert (URIRef("http://test.com/bong"), None, None) in g

    def test_base_explicit(self):
        """
        Test that the n3 parser supports resolving relative URIs
        and that base will override
        """

        input = """
@prefix : <http://example.com/> .
# default base
<foo> :name "Foo" .
# change it
@base <http://example.com/doc/> .
<bar> :name "Bar" .
"""
        g = Graph()
        g.parse(data=input, publicID="http://blah.com/", format="n3")
        print(list(g))
        assert (URIRef("http://blah.com/foo"), None, Literal("Foo")) in g
        assert (URIRef("http://example.com/doc/bar"), None, None) in g

    def test_base_serialize(self):
        g = Graph()
        g.add(
            (
                URIRef("http://example.com/people/Bob"),
                URIRef("urn:knows"),
                URIRef("http://example.com/people/Linda"),
            )
        )
        s = g.serialize(
            base="http://example.com/people/", format="n3", encoding="latin-1"
        )
        assert b"<Bob>" in s
        g2 = Dataset()
        g2.parse(data=s, format="n3")
        assert list(g) == list(g2.triples((None, None, None)))

    def test_issue23(self):
        input = """<http://example.com/article1> <http://example.com/title> "this word is in \\u201Cquotes\\u201D"."""

        g = Graph()
        g.parse(data=input, format="n3")

        # Note difference in case of hex code, cwm allows lower-case
        input = """<http://example.com/article1> <http://example.com/title> "this word is in \\u201cquotes\\u201d"."""

        g.parse(data=input, format="n3")

    def test_issue29(self):
        input = """@prefix foo-bar: <http://example.org/> .

foo-bar:Ex foo-bar:name "Test" . """

        g = Graph()
        g.parse(data=input, format="n3")

    def test_issue68(self):
        input = """@prefix : <http://some.url/pome#>.\n\n:Brecon a :Place;\n\t:hasLord\n\t\t:Bernard_of_Neufmarch\xc3\xa9 .\n """

        g = Graph()
        g.parse(data=input, format="n3")

    def test_issue156(self):
        """
        Make sure n3 parser does not choke on UTF-8 BOM
        """
        g = Graph()
        n3_path = os.path.relpath(os.path.join(TEST_DIR, "data/issue156.n3", os.curdir))
        g.parse(n3_path, format="n3")

    def test_issue999(self):
        """
        Make sure the n3 parser does recognize exponent and leading dot in ".171e-11"
        """
        data = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://qudt.org/vocab/unit/MilliM-PER-YR>
  a <http://qudt.org/schema/qudt/Unit> ;
  <http://qudt.org/schema/qudt/conversionMultiplier> .171e-11 ;
  <http://qudt.org/schema/qudt/conversionOffset> 0e+00 ;
  <http://qudt.org/schema/qudt/description> "0.001-fold of the SI base unit metre divided by the unit year" ;
  <http://qudt.org/schema/qudt/hasQuantityKind> <http://qudt.org/vocab/quantitykind/Velocity> ;
  <http://qudt.org/schema/qudt/iec61360Code> "0112/2///62720#UAA868" ;
  <http://qudt.org/schema/qudt/uneceCommonCode> "H66" ;
  rdfs:isDefinedBy <http://qudt.org/2.1/vocab/unit> ;
  rdfs:isDefinedBy <http://qudt.org/vocab/unit> ;
  rdfs:label "MilliM PER YR" ;
  <http://www.w3.org/2004/02/skos/core#prefLabel> "millimetre per year" ;
.
        """
        g = Graph()
        g.parse(data=data, format="n3")
        g.parse(data=data, format="turtle")

    def test_dot_in_prefix(self):
        g = Graph()
        g.parse(
            data="@prefix a.1: <http://example.org/> .\n a.1:cake <urn:x> <urn:y> . \n",
            format="n3",
        )

    def test_model(self):
        g = Dataset()
        g.parse(data=test_data, format="n3")
        i = 0
        for s, p, o, c in g:
            if isinstance(s, Graph):
                i += 1
        assert i == 3
        assert len(list(g.graphs())) == 13

        g.close()

    def test_quoted_serialization(self):
        g = Dataset()
        g.parse(data=test_data, format="n3")
        g.serialize(format="n3")

    def test_parse(self):
        g = Dataset()
        try:
            g.parse(
                "http://groups.csail.mit.edu/dig/2005/09/rein/examples/troop42-policy.n3",
                format="n3",
            )
        except URLError:
            pytest.skip("No network to retrieve the information, skipping test")

    def test_single_quoted_literals(self):
        test_data = [
            """@prefix : <#> . :s :p 'o' .""",
            """@prefix : <#> . :s :p '''o''' .""",
        ]

        for data in test_data:
            # N3 doesn't accept single quotes around string literals
            g = Dataset()
            with pytest.raises(BadSyntax):
                g.parse(data=data, format="n3")

            g = Dataset()
            g.parse(data=data, format="turtle")
            assert len(g) == 1
            for _, _, o, c in g:
                assert o == Literal("o")

    def test_local_name_must_not_begin_with_dash(self):
        # this is issue https://github.com/RDFLib/rdflib/issues/3403
        # PN_LOCAL may contain "-" but must not start with it.
        for format in ("n3", "turtle"):
            g = Graph()
            with pytest.raises(BadSyntax):
                g.parse(
                    data="@prefix : <http://example.org/> .\n:s :p :-o .",
                    format=format,
                )

            g = Graph()
            g.parse(
                data="@prefix : <http://example.org/> .\n:s :p :o-1 .",
                format=format,
            )
            assert len(g) == 1

    def test_missing_datatype_iri_raises_badsyntax(self):
        # A literal with a "^^" datatype marker but no datatype IRI must raise
        # BadSyntax, not IndexError from reading the (empty) datatype result.
        for fmt in ("n3", "turtle", "trig"):
            g = Dataset()
            with pytest.raises(BadSyntax):
                g.parse(data='<a> <b> "x"^^ .', format=fmt)

    def test_empty_prefix(self):
        # this is issue https://github.com/RDFLib/rdflib/issues/312
        g1 = Graph()
        g1.parse(data=":a :b :c .", format="n3")

        g2 = Graph()
        g2.parse(data="@prefix : <#> . :a :b :c .", format="n3")

        assert set(g1) == set(g2), (
            "Document with declared empty prefix must match default #"
        )

    @pytest.mark.parametrize(
        "do_normalize_literal, expected_result",
        [(True, {"1.0", "10000000000.0"}), (False, {"1e10", "1e0"})],
    )
    def test_float_no_norm(self, do_normalize_literal, expected_result):
        import rdflib

        original_normalize_literal = rdflib.NORMALIZE_LITERALS
        try:
            rdflib.NORMALIZE_LITERALS = do_normalize_literal
            g1 = Graph()
            g1.parse(data=":a :b 1e10, 1e0 .", format="n3")
            values = set(str(o) for o in g1.objects())
            assert values == expected_result
        finally:
            rdflib.NORMALIZE_LITERALS = original_normalize_literal


class TestRegularExpressions:
    def test_exponents(self):
        signs = ("", "+", "-")
        mantissas = (
            "1",
            "1.",
            ".1",
            "12",
            "12.",
            "1.2",
            ".12",
            "123",
            "123.",
            "12.3",
            "1.23",
            ".123",
        )
        es = "eE"
        exps = ("1", "12", "+1", "-1", "+12", "-12")
        for parts in itertools.product(signs, mantissas, es, exps):
            expstring = "".join(parts)
            assert exponent_syntax.match(expstring)

    def test_invalid_exponents(self):
        # Add test cases as needed
        invalid = (".e1",)
        for expstring in invalid:
            assert not exponent_syntax.match(expstring)


@pytest.mark.parametrize(
    "base, reference, expected",
    [
        ("http://example.org/doc#", "#a", "http://example.org/doc#a"),
        ("http://example.org/doc#x", "#a", "http://example.org/doc#a"),
        ("http://example.org/doc#", "#", "http://example.org/doc#"),
        ("http://example.org/doc#x", "", "http://example.org/doc"),
        ("http://example.org/a/b#x/y", "c", "http://example.org/a/c"),
        ("http://example.org/a/b/c#x/y", "../d", "http://example.org/a/d"),
    ],
)
def test_join_ignores_base_fragment(base: str, reference: str, expected: str) -> None:
    """RFC 3986, section 5.2.2, resolves a reference without the base's fragment."""
    assert join(base, reference) == expected


@pytest.mark.parametrize("format", ["turtle", "trig", "n3"])
def test_parse_resolves_against_base_with_fragment(format: str) -> None:
    """A fragment-only reference replaces the fragment of the base IRI."""
    data = '@base <http://example.org/doc#> . <#a> <http://example.org/p> "v" .'
    dataset = Dataset()
    dataset.parse(data=data, format=format)
    assert {s for s, _, _, _ in dataset.quads()} == {URIRef("http://example.org/doc#a")}


@pytest.mark.parametrize(
    "base, reference, expected",
    [
        ("http://a/b/c/d;p?q", "?y", "http://a/b/c/d;p?y"),
        ("http://a/b/c/d;p?q", "?", "http://a/b/c/d;p?"),
        ("http://a/b/c/d;p?q", "?y#s", "http://a/b/c/d;p?y#s"),
        ("http://a/b/c/d;p?q", "?y:z", "http://a/b/c/d;p?y:z"),
        ("http://a/b/c/d;p?q", "?y/../z", "http://a/b/c/d;p?y/../z"),
        ("http://a/b/c/d;p?q", "?y?z", "http://a/b/c/d;p?y?z"),
        ("http://a/b/c/d;p?q", "?#s", "http://a/b/c/d;p?#s"),
        ("http://a/b/c/d;p?q/x#s/t", "?y", "http://a/b/c/d;p?y"),
        ("http://a/b#f?g", "?y", "http://a/b?y"),
        ("http://a/b?q?r", "?y", "http://a/b?y"),
        ("http://a", "?y", "http://a?y"),
        ("http://a?old/path", "?y", "http://a?y"),
        ("http://a/b/", "?y", "http://a/b/?y"),
        ("http://a/caf\u00e9/%3F?q", "?x=%2F", "http://a/caf\u00e9/%3F?x=%2F"),
        ("local:/a/b?old", "?y", "local:/a/b?y"),
        ("urn:isbn:123?old#f", "?y#g", "urn:isbn:123?y#g"),
    ],
)
def test_join_query_only_reference(base: str, reference: str, expected: str) -> None:
    """RFC 3986, section 5.2.2, keeps the base path for a query-only reference."""
    assert join(base, reference) == expected


@pytest.mark.parametrize("format", ["turtle", "trig", "n3"])
@pytest.mark.parametrize("reference", ["?y", "?", "?y:z", "?y/../z", "?y#s"])
def test_parse_query_only_reference(format: str, reference: str) -> None:
    """Resolve query-only references in every position of a triple."""
    data = (
        "@base <http://a/b/c/d;p?q/x#s/t> . "
        f"<{reference}> <{reference}> <{reference}> ."
    )
    dataset = Dataset()
    dataset.parse(data=data, format=format)
    expected = URIRef("http://a/b/c/d;p" + reference)
    assert set(dataset.triples((None, None, None))) == {(expected, expected, expected)}


@pytest.mark.parametrize(
    "reference, expected",
    [
        ("#s:t", "http://a/b/c/d;p?q#s:t"),
        ("g?y:z", "http://a/b/c/g?y:z"),
        ("g#s:t", "http://a/b/c/g#s:t"),
        ("./a:b", "http://a/b/c/a:b"),
    ],
)
def test_join_reference_with_colon_after_delimiter(
    reference: str, expected: str
) -> None:
    """A colon after "/", "?" or "#" does not make a reference absolute."""
    assert join("http://a/b/c/d;p?q", reference) == expected


@pytest.mark.parametrize("format", ["turtle", "trig", "n3"])
@pytest.mark.parametrize(
    "reference, expected",
    [
        ("#s:t", "http://a/b/c/d;p?q#s:t"),
        ("g?y:z", "http://a/b/c/g?y:z"),
    ],
)
def test_parse_reference_with_colon_after_delimiter(
    format: str, reference: str, expected: str
) -> None:
    """A colon after "/", "?" or "#" does not make a reference absolute."""
    data = f"@base <http://a/b/c/d;p?q> . <{reference}> <{reference}> <{reference}> ."
    dataset = Dataset()
    dataset.parse(data=data, format=format)
    iri = URIRef(expected)
    assert set(dataset.triples((None, None, None))) == {(iri, iri, iri)}


@pytest.mark.parametrize("format", ["turtle", "trig", "n3"])
def test_parse_query_only_base_and_prefix(format: str) -> None:
    """Base and prefix declarations use the same query-only resolution."""
    data = """
        @base <http://a/b/c/d;p?q/x> .
        @base <?y:z> .
        @prefix e: <?term=> .
        <#s> e:p e:o .
    """
    dataset = Dataset()
    dataset.parse(data=data, format=format)
    assert set(dataset.triples((None, None, None))) == {
        (
            URIRef("http://a/b/c/d;p?y:z#s"),
            URIRef("http://a/b/c/d;p?term=p"),
            URIRef("http://a/b/c/d;p?term=o"),
        )
    }


@pytest.mark.parametrize(
    "reference, expected",
    [
        ("", "http://a/b/c/d;p?q"),
        ("#s", "http://a/b/c/d;p?q#s"),
        ("https://other/path?q", "https://other/path?q"),
    ],
)
def test_join_non_query_reference(reference: str, expected: str) -> None:
    """Resolve references that are not query-only, even if they contain a query."""
    assert join("http://a/b/c/d;p?q#old", reference) == expected


def test_join_query_requires_absolute_base() -> None:
    with pytest.raises(AssertionError, match="is not absolute"):
        join("relative/path", "?y:z")


def test_join_rejects_relative_path_with_opaque_base() -> None:
    with pytest.raises(ValueError, match="no slash after colon"):
        join("urn:isbn:123", "g?y:z")


@pytest.mark.parametrize(
    "base, reference, expected",
    [
        ("http://a/b?q/x", "g", "http://a/g"),
        ("http://a?q/x", "/g", "http://a/g"),
        ("http://a?q", "g", "http://a/g"),
        ("http://a?q", "/g", "http://a/g"),
        ("http://a?q/x", "g", "http://a/g"),
        ("http://a/b/?q/x", "g", "http://a/b/g"),
        ("http://a/b/c?q/x/y", "../g", "http://a/g"),
        ("http://a/b?q/x", "g?y/z#s", "http://a/g?y/z#s"),
        ("http://a?first?second/path", "g", "http://a/g"),
        ("http://a?", "g", "http://a/g"),
        ("http://a/caf\u00e9/%3F?q/x", "g", "http://a/caf\u00e9/g"),
        ("local:/a/b?q/x", "g", "local:/a/g"),
        ("http://a/b?q/x#old", "", "http://a/b?q/x"),
        ("http://a/b?q/x#old", "#s", "http://a/b?q/x#s"),
        ("http://a/b?q/x", "?y/z", "http://a/b?y/z"),
        ("http://a?q/x", "//other/g?y/z", "http://other/g?y/z"),
    ],
)
def test_join_base_query(base: str, reference: str, expected: str) -> None:
    """RFC 3986 merges paths without treating the base's query as a path."""
    assert join(base, reference) == expected


@pytest.mark.parametrize("format", ["turtle", "trig", "n3"])
@pytest.mark.parametrize("base", ["http://a/b?q/x", "http://a?q/x"])
def test_parse_path_against_base_query(format: str, base: str) -> None:
    data = f"@base <{base}> . <g> </p> <o?y/z#s> ."
    dataset = Dataset()
    dataset.parse(data=data, format=format)
    assert set(dataset.triples((None, None, None))) == {
        (URIRef("http://a/g"), URIRef("http://a/p"), URIRef("http://a/o?y/z#s"))
    }


@pytest.mark.parametrize("format", ["turtle", "trig", "n3"])
def test_parse_base_and_prefix_against_base_query(format: str) -> None:
    data = """
        @base <http://a/b?q/x> .
        @base <c?y/z> .
        @prefix e: <vocab/> .
        <s> e:p e:o .
    """
    dataset = Dataset()
    dataset.parse(data=data, format=format)
    assert set(dataset.triples((None, None, None))) == {
        (URIRef("http://a/s"), URIRef("http://a/vocab/p"), URIRef("http://a/vocab/o"))
    }


@pytest.mark.parametrize(
    "base, reference, expected",
    [
        ("http://a/b/c/d;p?q", "g/../h", "http://a/b/c/h"),
        ("http://a/b/c/d;p?q", "/./g", "http://a/g"),
        ("http://a/b/c/d;p?q", "/../g", "http://a/g"),
        ("http://a/b/c/d;p?q", "./g/.", "http://a/b/c/g/"),
        ("http://a/b/c/d;p?q", "g/./h", "http://a/b/c/g/h"),
        ("http://a/b/c/d;p?q", "g;x=1/./y", "http://a/b/c/g;x=1/y"),
        ("http://a/b/c/d;p?q", "g;x=1/../y", "http://a/b/c/y"),
        ("http://a/b/c/d;p?q", "g/../../../../h", "http://a/h"),
        ("http://a/b/c/d;p?q", "g/..", "http://a/b/c/"),
        ("http://a/b?q/x", "g/../h?y/../z#s/./t", "http://a/h?y/../z#s/./t"),
        ("http://a/b", "g/..?", "http://a/?"),
        ("http://a/b", "g/..#", "http://a/#"),
        ("http://a/b", "//other/a/../g?y/./z", "http://other/g?y/./z"),
        ("http://a/b", "//other?y/../z", "http://other?y/../z"),
        ("local:/a/b", "g/../h", "local:/a/h"),
        ("http://a/b/../c/d", "g", "http://a/c/g"),
        ("http://a/b", "g//h/../i", "http://a/g//i"),
        ("http://a/b", "g//../h", "http://a/g/h"),
        ("http://a/b", "g/%2E/%2e%2e/h", "http://a/g/%2E/%2e%2e/h"),
        ("http://a/b", "caf\u00e9/../h", "http://a/h"),
        ("http://a/b", "g?y/../z", "http://a/g?y/../z"),
        ("http://a/b", "g#s/../t", "http://a/g#s/../t"),
    ],
)
def test_join_dot_segments(base: str, reference: str, expected: str) -> None:
    """Remove dot segments from the resolved path, not its query or fragment."""
    assert join(base, reference) == expected


@pytest.mark.parametrize("format", ["turtle", "trig", "n3"])
@pytest.mark.parametrize("case", ["01", "02", "07", "08"])
def test_parse_dot_segments_w3c(format: str, case: str) -> None:
    """Run proposed IRI-resolution cases skipped by the manifest loader."""
    path = os.path.join(
        TEST_DIR, "data", "suites", "w3c", "n3", "TurtleTests", f"IRI-resolution-{case}"
    )
    actual = Graph().parse(path + ".ttl", format=format)
    expected = Graph().parse(path + ".nt", format="nt")
    assert isomorphic(actual, expected)
