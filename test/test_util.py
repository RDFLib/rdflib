# -*- coding: utf-8 -*-

import logging
import time
from contextlib import ExitStack
from pathlib import Path
from test.data import TEST_DATA_DIR
from test.utils.graph import cached_graph
from test.utils.namespace import RDFT
from typing import Any, Collection, List, Optional, Set, Tuple, Type, Union

import pytest

from rdflib import XSD, util
from rdflib.graph import ConjunctiveGraph, Graph, QuotedGraph
from rdflib.namespace import RDF, RDFS
from rdflib.term import BNode, IdentifiedNode, Literal, Node, URIRef
from rdflib.util import _coalesce, _iri2uri, find_roots, get_tree

n3source = """\
@prefix : <http://www.w3.org/2000/10/swap/Primer#>.
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix dc:  <http://purl.org/dc/elements/1.1/> .
@prefix foo: <http://www.w3.org/2000/10/swap/Primer#>.
@prefix swap: <http://www.w3.org/2000/10/swap/>.

<> dc:title
  "Primer - Getting into the Semantic Web and RDF using N3".

<#pat> <#knows> <#jo> .
<#pat> <#age> 24 .
<#al> is <#child> of <#pat> .

<#pat> <#child>  <#al>, <#chaz>, <#mo> ;
       <#age>    24 ;
       <#eyecolor> "blue" .

:Person a rdfs:Class.

:Pat a :Person.

:Woman a rdfs:Class; rdfs:subClassOf :Person .

:sister a rdf:Property.

:sister rdfs:domain :Person;
        rdfs:range :Woman.

:Woman = foo:FemaleAdult .
:Title a rdf:Property; = dc:title .

"""  # --- End of primer code


class TestUtilMisc:
    def setup_method(self):
        self.x = Literal(
            "2008-12-01T18:02:00Z",
            datatype=URIRef("http://www.w3.org/2001/XMLSchema#dateTime"),
        )

    def test_util_list2set(self):
        base = [Literal("foo"), self.x]
        r = util.list2set(base + base)
        assert r == base

    def test_util_uniq(self):
        base = ["michel", "hates", "pizza"]
        r = util.uniq(base + base)
        assert sorted(r) == sorted(base)
        base = ["michel", "hates", "pizza"]
        r = util.uniq(base + base, strip=True)
        assert sorted(r) == sorted(base)


class TestUtilDateTime:
    def setup_method(self):
        self.x = Literal(
            "2008-12-01T18:02:00Z",
            datatype=URIRef("http://www.w3.org/2001/XMLSchema#dateTime"),
        )

    def test_util_date_time_tisnoneandnotz(self):
        t = None
        res = util.date_time(t, local_time_zone=False)
        assert res[4:5] == "-"

    def test_util_date_time_tisnonebuttz(self):
        t = None
        res = util.date_time(t, local_time_zone=True)
        assert res[4:5] == "-"

    def test_util_date_time_tistime(self):
        t = time.time()
        res = util.date_time(t, local_time_zone=False)
        assert res[4:5] == "-"

    def test_util_date_time_tistimewithtz(self):
        t = time.time()
        res = util.date_time(t, local_time_zone=True)
        assert res[4:5] == "-"

    def test_util_parse_date_time(self):
        t = time.time()
        res = util.parse_date_time("1970-01-01")
        assert res is not t

    def test_util_parse_date_timewithtz(self):
        t = time.time()
        res = util.parse_date_time("1970-01-01")
        assert res is not t

    def test_util_date_timewithtoutz(self):
        t = time.time()

        def ablocaltime(t):
            from time import gmtime

            res = gmtime(t)
            return res

        util.localtime = ablocaltime
        res = util.date_time(t, local_time_zone=True)
        assert res is not t


class TestUtilTermConvert:
    def setup_method(self):
        self.x = Literal(
            "2008-12-01T18:02:00Z",
            datatype=URIRef("http://www.w3.org/2001/XMLSchema#dateTime"),
        )

    def test_util_to_term_sisNone(self):
        s = None
        assert util.to_term(s) == s
        assert util.to_term(s, default="") == ""

    def test_util_to_term_sisstr(self):
        s = '"http://example.com"'
        res = util.to_term(s)
        assert isinstance(res, Literal)
        assert str(res) == s[1:-1]

    def test_util_to_term_sisurl(self):
        s = "<http://example.com>"
        res = util.to_term(s)
        assert isinstance(res, URIRef)
        assert str(res) == s[1:-1]

    def test_util_to_term_sisbnode(self):
        s = "_http%23%4F%4Fexample%33com"
        res = util.to_term(s)
        assert isinstance(res, BNode)

    def test_util_to_term_sisunknown(self):
        s = "http://example.com"
        with pytest.raises(Exception):
            util.to_term(s)

    def test_util_to_term_sisnotstr(self):
        s = self.x
        with pytest.raises(Exception):
            util.to_term(s)

    def test_util_from_n3_sisnonenodefault(self):
        s = None
        default = None
        res = util.from_n3(s, default=default, backend=None)
        assert res == default

    def test_util_from_n3_sisnonewithdefault(self):
        s = None
        default = "TestofDefault"
        res = util.from_n3(s, default=default, backend=None)
        assert res == default

    def test_util_from_n3_expectdefaultbnode(self):
        s = "michel"
        res = util.from_n3(s, default=None, backend=None)
        assert isinstance(res, BNode)

    def test_util_from_n3_expectbnode(self):
        s = "_:michel"
        res = util.from_n3(s, default=None, backend=None)
        assert isinstance(res, BNode)

    def test_util_from_n3_expectliteral(self):
        s = '"michel"'
        res = util.from_n3(s, default=None, backend=None)
        assert isinstance(res, Literal)

    def test_util_from_n3_expecturiref(self):
        s = "<http://example.org/schema>"
        res = util.from_n3(s, default=None, backend=None)
        assert isinstance(res, URIRef)

    def test_util_from_n3_expectliteralandlang(self):
        s = '"michel"@fr'
        res = util.from_n3(s, default=None, backend=None)
        assert isinstance(res, Literal)

    def test_util_from_n3_expectliteralandlangdtype(self):
        s = '"michel"@fr^^xsd:fr'
        res = util.from_n3(s, default=None, backend=None)
        assert isinstance(res, Literal)
        assert res == Literal("michel", datatype=XSD["fr"])

    def test_util_from_n3_expectliteralanddtype(self):
        s = '"true"^^xsd:boolean'
        res = util.from_n3(s, default=None, backend=None)
        assert res.eq(Literal("true", datatype=XSD["boolean"]))

    def test_util_from_n3_expectliteralwithdatatypefromint(self):
        s = "42"
        res = util.from_n3(s)
        assert res == Literal(42)

    def test_util_from_n3_expectliteralwithdatatypefrombool(self):
        s = "true"
        res = util.from_n3(s)
        assert res == Literal(True)
        s = "false"
        res = util.from_n3(s)
        assert res == Literal(False)

    def test_util_from_n3_expectliteralmultiline(self):
        s = '"""multi\nline\nstring"""@en'
        res = util.from_n3(s, default=None, backend=None)
        assert res == Literal("multi\nline\nstring", lang="en")

    def test_util_from_n3_expectliteralwithescapedquote(self):
        s = '"\\""'
        res = util.from_n3(s, default=None, backend=None)
        assert res == Literal('"')

    def test_util_from_n3_expectliteralwithtrailingbackslash(self):
        s = '"trailing\\\\"^^<http://www.w3.org/2001/XMLSchema#string>'
        res = util.from_n3(s)
        assert res == Literal("trailing\\", datatype=XSD["string"])
        assert res.n3() == s

    def test_util_from_n3_expectpartialidempotencewithn3(self):
        for n3 in (
            "<http://ex.com/foo>",
            '"foo"@de',
            "<http://ex.com/漢字>",
            "<http://ex.com/a#あ>",
            # '"\\""', # exception as '\\"' --> '"' by orig parser as well
            '"""multi\n"line"\nstring"""@en',
        ):
            assert util.from_n3(n3).n3() == n3, "from_n3(%(n3e)r).n3() != %(n3e)r" % {
                "n3e": n3
            }

    def test_util_from_n3_expectsameasn3parser(self):
        def parse_n3(term_n3):
            """Disclaimer: Quick and dirty hack using the n3 parser."""
            prepstr = (
                "@prefix  xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
                "<urn:no_use> <urn:no_use> %s.\n" % term_n3
            )
            g = ConjunctiveGraph()
            g.parse(data=prepstr, format="n3")
            return [t for t in g.triples((None, None, None))][0][2]

        for n3 in (  # "michel", # won't parse in original parser
            # "_:michel", # BNodes won't be the same
            '"michel"',
            "<http://example.org/schema>",
            '"michel"@fr',
            # '"michel"@fr^^xsd:fr', # FIXME: invalid n3, orig parser will prefer datatype
            # '"true"^^xsd:boolean', # FIXME: orig parser will expand xsd prefix
            "42",
            "true",
            "false",
            '"""multi\nline\nstring"""@en',
            "<http://ex.com/foo>",
            '"foo"@de',
            '"\\""@en',
            '"""multi\n"line"\nstring"""@en',
        ):
            res, exp = util.from_n3(n3), parse_n3(n3)
            assert (
                res == exp
            ), "from_n3(%(n3e)r): %(res)r != parser.notation3: %(exp)r" % {
                "res": res,
                "exp": exp,
                "n3e": n3,
            }

    def test_util_from_n3_expectquotedgraph(self):
        s = "{<http://example.com/schema>}"
        res = util.from_n3(s, default=None, backend="Memory")
        assert isinstance(res, QuotedGraph)

    def test_util_from_n3_expectgraph(self):
        s = "[<http://example.com/schema>]"
        res = util.from_n3(s, default=None, backend="Memory")
        assert isinstance(res, Graph)

    @pytest.mark.parametrize(
        ["escaped", "raw"],
        [
            ("\\t", "\t"),
            ("\\b", "\b"),
            ("\\n", "\n"),
            ("\\r", "\r"),
            ("\\f", "\f"),
            ('\\"', '"'),
            ("\\'", "'"),
            ("\\\\", "\\"),
            ("\\u00F6", "ö"),
            ("\\U000000F6", "ö"),
        ],
    )
    def test_util_from_n3_escapes(self, escaped: str, raw: str) -> None:
        literal_str = str(util.from_n3(f'"{escaped}"'))
        assert literal_str == f"{raw}"

    @pytest.mark.parametrize(
        "string",
        [
            ("jörn"),
            ("j\\xf6rn"),
            ("\\I"),
        ],
    )
    def test_util_from_n3_not_escapes(self, string: str) -> None:
        literal_str = str(util.from_n3(f'"{string}"'))
        assert literal_str == f"{string}"

    @pytest.mark.xfail
    @pytest.mark.parametrize(
        "string",
        [
            (f"j\\366rn"),
            (f"\\"),
            (f"\\0"),
        ],
    )
    def test_util_from_n3_not_escapes_xf(self, string: str) -> None:
        literal_str = str(util.from_n3(f'"{string}"'))
        assert literal_str == f"{string}"


@pytest.mark.parametrize(
    ["params", "default", "expected_result"],
    [
        ([], ..., None),
        (["something"], ..., "something"),
        ([False, "something"], ..., False),
        (["", "something"], ..., ""),
        ([0, "something"], ..., 0),
        ([None, "something", 1], ..., "something"),
        (["something", None, 1], ..., "something"),
        (["something", None, 1], 5, "something"),
        ([], 5, 5),
        ([None], 5, 5),
        ([None, None], 5, 5),
        ([None, None], 5, 5),
    ],
)
def test__coalesce(params: Collection[Any], default: Any, expected_result: Any) -> None:
    if default == Ellipsis:
        result = _coalesce(*params)
    else:
        result = _coalesce(*params, default)
    assert expected_result == result


def test__coalesce_typing() -> None:
    """
    type checking for _coalesce behaves as expected.
    """
    str_value: str
    optional_str_value: Optional[str]

    optional_str_value = _coalesce(None, "a", None)
    assert optional_str_value == "a"

    str_value = _coalesce(None, "a", None)  # type: ignore[assignment]
    assert str_value == "a"

    str_value = _coalesce(None, "a", None, default="3")
    assert str_value == "a"


@pytest.mark.parametrize(
    ["graph_sources", "prop", "roots", "expected_result"],
    [
        (
            (TEST_DATA_DIR / "defined_namespaces/rdfs.ttl",),
            RDFS.subClassOf,
            None,
            {RDF.Property, RDFS.Resource},
        ),
        (
            (TEST_DATA_DIR / "defined_namespaces/rdftest.ttl",),
            RDFS.subClassOf,
            None,
            {RDFT.Approval, RDFT.Test},
        ),
        (
            (
                TEST_DATA_DIR / "defined_namespaces/rdftest.ttl",
                TEST_DATA_DIR / "defined_namespaces/rdfs.ttl",
            ),
            RDFS.subClassOf,
            None,
            {RDFT.Approval, RDFT.Test, RDF.Property, RDFS.Resource},
        ),
        (
            tuple(),
            RDFS.subClassOf,
            None,
            set(),
        ),
        (
            tuple(),
            RDFS.subClassOf,
            {RDFS.Resource},
            {RDFS.Resource},
        ),
    ],
)
def test_find_roots(
    graph_sources: Tuple[Path, ...],
    prop: URIRef,
    roots: Optional[Set[Node]],
    expected_result: Union[Set[URIRef], Type[Exception]],
) -> None:

    catcher: Optional[pytest.ExceptionInfo[Exception]] = None

    graph = cached_graph(graph_sources)

    with ExitStack() as xstack:
        if isinstance(expected_result, type) and issubclass(expected_result, Exception):
            catcher = xstack.enter_context(pytest.raises(expected_result))
        result = find_roots(graph, prop, roots)
    if catcher is not None:
        assert catcher is not None
        assert catcher.value is not None
    else:
        assert expected_result == result


@pytest.mark.parametrize(
    ["graph_sources", "root", "prop", "dir", "expected_result"],
    [
        (
            (
                TEST_DATA_DIR / "defined_namespaces/rdftest.ttl",
                TEST_DATA_DIR / "defined_namespaces/rdfs.ttl",
            ),
            RDFT.TestTurtlePositiveSyntax,
            RDFS.subClassOf,
            "down",
            (RDFT.TestTurtlePositiveSyntax, []),
        ),
        (
            (
                TEST_DATA_DIR / "defined_namespaces/rdftest.ttl",
                TEST_DATA_DIR / "defined_namespaces/rdfs.ttl",
            ),
            RDFT.TestTurtlePositiveSyntax,
            RDFS.subClassOf,
            "up",
            (
                RDFT.TestTurtlePositiveSyntax,
                [
                    (RDFT.TestSyntax, [(RDFT.Test, [])]),
                ],
            ),
        ),
        (
            (
                TEST_DATA_DIR / "defined_namespaces/rdftest.ttl",
                TEST_DATA_DIR / "defined_namespaces/rdfs.ttl",
            ),
            RDFS.Resource,
            RDFS.subClassOf,
            "down",
            (
                RDFS.Resource,
                [
                    (RDFS.Class, [(RDFS.Datatype, [])]),
                    (RDFS.Container, []),
                    (RDFS.Literal, []),
                ],
            ),
        ),
        (
            (
                TEST_DATA_DIR / "defined_namespaces/rdftest.ttl",
                TEST_DATA_DIR / "defined_namespaces/rdfs.ttl",
            ),
            RDFS.Resource,
            RDFS.subClassOf,
            "up",
            (RDFS.Resource, []),
        ),
        (
            (
                TEST_DATA_DIR / "defined_namespaces/rdftest.ttl",
                TEST_DATA_DIR / "defined_namespaces/rdfs.ttl",
            ),
            RDFT.Test,
            RDFS.subClassOf,
            "down",
            (
                RDFT.Test,
                [
                    (
                        RDFT.TestEval,
                        [
                            (RDFT.TestTrigNegativeEval, []),
                            (RDFT.TestTurtleEval, []),
                            (RDFT.TestTurtleNegativeEval, []),
                            (RDFT.XMLEval, []),
                        ],
                    ),
                    (
                        RDFT.TestSyntax,
                        [
                            (RDFT.TestNQuadsNegativeSyntax, []),
                            (RDFT.TestNQuadsPositiveSyntax, []),
                            (RDFT.TestNTriplesNegativeSyntax, []),
                            (RDFT.TestNTriplesPositiveSyntax, []),
                            (RDFT.TestTriGNegativeSyntax, []),
                            (RDFT.TestTriGPositiveSyntax, []),
                            (RDFT.TestTurtleNegativeSyntax, []),
                            (RDFT.TestTurtlePositiveSyntax, []),
                        ],
                    ),
                ],
            ),
        ),
        (
            (
                TEST_DATA_DIR / "defined_namespaces/rdftest.ttl",
                TEST_DATA_DIR / "defined_namespaces/rdfs.ttl",
            ),
            RDFT.Test,
            RDFS.subClassOf,
            "up",
            (RDFT.Test, []),
        ),
    ],
)
def test_get_tree(
    graph_sources: Tuple[Path, ...],
    root: IdentifiedNode,
    prop: URIRef,
    dir: str,
    expected_result: Union[Tuple[IdentifiedNode, List[Any]], Type[Exception]],
) -> None:

    catcher: Optional[pytest.ExceptionInfo[Exception]] = None

    graph = cached_graph(graph_sources)

    with ExitStack() as xstack:
        if isinstance(expected_result, type) and issubclass(expected_result, Exception):
            catcher = xstack.enter_context(pytest.raises(expected_result))
        result = get_tree(graph, root, prop, dir=dir)
        logging.debug("result = %s", result)
    if catcher is not None:
        assert catcher is not None
        assert catcher.value is not None
    else:
        assert expected_result == result


@pytest.mark.parametrize(
    ["iri", "expected_result"],
    [
        (
            "https://example.com/resource/Almería",
            {
                "https://example.com/resource/Almer%C3%ADa",
            },
        ),
        (
            "https://example.com/resource/Almeria",
            {
                "https://example.com/resource/Almeria",
            },
        ),
        (
            "https://åæø.example.com/",
            {
                "https://xn--5cac8c.example.com/",
            },
        ),
        (
            # Note: expected result is the same because the function only works
            # for http and https.
            "example:é",
            {
                "example:é",
            },
        ),
        (
            # Note: expected result is the same because the function only works
            # for http and https.
            "urn:example:é",
            {
                "urn:example:é",
            },
        ),
        (
            "http://example.com/?é=1",
            {
                "http://example.com/?%C3%A9=1",
                "http://example.com/?%C3%A9%3D1",
            },
        ),
        (
            "http://example.com/#é",
            {
                "http://example.com/#%C3%A9",
            },
        ),
        (
            "http://example.com/é#",
            {
                "http://example.com/%C3%A9#",
            },
        ),
    ],
)
def test_iri2uri(iri: str, expected_result: Union[Set[str], Type[Exception]]) -> None:
    """
    Tests that
    """
    catcher: Optional[pytest.ExceptionInfo[Exception]] = None

    with ExitStack() as xstack:
        if isinstance(expected_result, type) and issubclass(expected_result, Exception):
            catcher = xstack.enter_context(pytest.raises(expected_result))
        result = _iri2uri(iri)
        logging.debug("result = %s", result)
    if catcher is not None:
        assert catcher is not None
        assert catcher.value is not None
    else:
        assert isinstance(expected_result, set)
        assert result in expected_result
