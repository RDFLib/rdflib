from __future__ import annotations

import itertools
import logging

import pyparsing
import pytest

import rdflib
from rdflib import Graph
from rdflib.namespace import Namespace
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
