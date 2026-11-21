from __future__ import annotations

import itertools
import logging

import pyparsing
import pytest

import rdflib
from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.plugins.sparql.algebra import translateAlgebra
from rdflib.plugins.sparql.processor import prepareQuery
from rdflib.term import Node, URIRef
from test.utils.outcome import OutcomeChecker, OutcomePrimitive

RESERVED_PCHARS = [
    "%20",
    "%21",
    "%23",
    "%24",
    "%25",
    "%26",
    "%27",
    "%28",
    "%29",
    "%2A",
    "%2B",
    "%2C",
    "%2F",
    "%3A",
    "%3B",
    "%3D",
    "%3F",
    "%40",
    "%5B",
    "%5D",
]

# Characters that can follow a backslash in a local name, see
# https://www.w3.org/TR/sparql11-query/#rPN_LOCAL_ESC
PN_LOCAL_ESC_CHARS = "_~.-!$&'()*+,;=/?#@%"


@pytest.mark.parametrize(
    "reserved_char_percent_encoded",
    RESERVED_PCHARS,
)
def test_sparql_parse_reserved_char_percent_encoded(reserved_char_percent_encoded):
    data = f"""@prefix : <https://www.example.co/reserved/language#> .

<https://www.example.co/reserved/root> :_id "01G39WKRH76BGY5D3SKDHJP2SX" ;
    :transcript{reserved_char_percent_encoded}data [ :_id "01G39WKRH7JYRX78X7FG4RCNYF" ;
            :_key "transcript{reserved_char_percent_encoded}data" ;
            :value "value" ;
            :value_id "01G39WKRH7PVK1DXQHWT08DZA8" ] ."""

    q = f"""PREFIX : <https://www.example.co/reserved/language#>
    SELECT  ?o
    WHERE {{ ?s :transcript{reserved_char_percent_encoded}data/:value ?o . }}"""

    g = rdflib.Graph()
    g.parse(data=data, format="ttl")
    res = g.query(q)

    assert list(res)[0][0] == rdflib.term.Literal("value")

    assert reserved_char_percent_encoded in str(
        rdflib.plugins.sparql.parser.parseQuery(q)
    )


PNAME_PREFIX = Namespace("https://example.com/test_pnames/")


@pytest.fixture(scope="module")
def blank_graph() -> Graph:
    return Graph()


@pytest.mark.parametrize(
    ["pname_ns", "pname", "expected_result"],
    list(
        itertools.chain(
            [
                ("eg", "invalid/PN_PREFIX", pyparsing.ParseException),
                ("", "eg:a", Exception),
                ("", ":invalid PN_LOCAL", pyparsing.ParseException),
                ("", ":invalid/PN_LOCAL", pyparsing.ParseException),
                ("", ":a:b:c", PNAME_PREFIX["a:b:c"]),
                ("", ":", URIRef(f"{PNAME_PREFIX}")),
                ("", ":a", PNAME_PREFIX.a),
                ("eg", " eg:obj ", PNAME_PREFIX.obj),
                ("", "  :obj  ", PNAME_PREFIX.obj),
                ("eg", " \t eg:obj \t ", PNAME_PREFIX.obj),
                ("", " \n :obj \n ", PNAME_PREFIX.obj),
                ("eg", "eg:", URIRef(f"{PNAME_PREFIX}")),
                ("eg", "eg:a", PNAME_PREFIX.a),
                ("", ":transcript%20data", PNAME_PREFIX["transcript%20data"]),
            ],
            (
                ("", f":aaa{pchar}zzz", PNAME_PREFIX[f"aaa{pchar}zzz"])
                for pchar in RESERVED_PCHARS
            ),
            (
                ("", f":aaa\\{char}zzz", PNAME_PREFIX[f"aaa{char}zzz"])
                for char in PN_LOCAL_ESC_CHARS
            ),
            [
                ("", ":\\#start", PNAME_PREFIX["#start"]),
                ("", ":end\\.", PNAME_PREFIX["end."]),
                ("", ":\\-", PNAME_PREFIX["-"]),
                ("", ":a%20\\#b", PNAME_PREFIX["a%20#b"]),
                ("", ":a\\%20b", PNAME_PREFIX["a%20b"]),
                ("", ':a\\"b', pyparsing.ParseException),
                ("", ':\\"', pyparsing.ParseException),
            ],
        )
    ),
)
def test_pnames(
    pname_ns: str,
    pname: str,
    expected_result: OutcomePrimitive[Node],
    blank_graph: Graph,
) -> None:
    """
    The given pname produces the expected result.
    """
    checker = OutcomeChecker[Node].from_primitive(expected_result)

    with checker.context():
        query_string = f"""\
        PREFIX {pname_ns}: <{PNAME_PREFIX}>

        CONSTRUCT {{
            <example:_subject> <example:_predicate> {pname}.
        }} WHERE {{}}
        """
        query_result = blank_graph.query(query_string)
        assert query_result.type == "CONSTRUCT"
        assert isinstance(query_result.graph, Graph)
        triples = list(query_result.graph.triples((None, None, None)))
        assert len(triples) == 1
        triple = triples[0]
        result = triple[2]
        logging.debug("result = %s", result)
        checker.check(result)


def test_pname_escapes_in_update() -> None:
    """
    SPARQL Update drops the backslash of escaped characters in local names.
    """
    graph = Graph()
    graph.update(
        f"""\
        PREFIX eg: <{PNAME_PREFIX}>
        INSERT DATA {{ eg:\\#s eg:p\\/q eg:o\\. }}
        """
    )
    assert set(graph) == {(PNAME_PREFIX["#s"], PNAME_PREFIX["p/q"], PNAME_PREFIX["o."])}


def test_pname_escaped_quote_in_update() -> None:
    """
    SPARQL Update rejects an escaped double quote in a local name.
    """
    with pytest.raises(pyparsing.ParseException):
        Graph().update(
            f"""\
            PREFIX eg: <{PNAME_PREFIX}>
            INSERT DATA {{ eg:s eg:p eg:a\\"b }}
            """
        )


def test_pname_escape_matches_data() -> None:
    """
    A local name with an escaped character matches the unescaped IRI in the
    data.
    """
    graph = Graph()
    graph.add((PNAME_PREFIX["a#b"], PNAME_PREFIX.p, PNAME_PREFIX["c/d"]))
    result = graph.query(
        f"""\
        PREFIX eg: <{PNAME_PREFIX}>
        SELECT ?o WHERE {{ eg:a\\#b eg:p ?o }}
        """
    )
    assert list(result) == [(PNAME_PREFIX["c/d"],)]


def test_pname_escape_translate_algebra() -> None:
    """
    `translateAlgebra` writes a local name with an escaped character as the
    unescaped IRI.
    """
    query = prepareQuery(
        f"""\
        PREFIX eg: <{PNAME_PREFIX}>
        SELECT ?o WHERE {{ eg:a\\#b eg:p ?o }}
        """
    )
    assert f"<{PNAME_PREFIX}a#b>" in translateAlgebra(query)
