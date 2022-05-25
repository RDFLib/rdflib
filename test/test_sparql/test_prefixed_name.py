import itertools
import logging
from contextlib import ExitStack
from typing import Type, Union

import pyparsing
import pytest
from pyparsing import Optional

import rdflib
from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.term import URIRef

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
            ("eg", "invalid/PN_PREFIX", pyparsing.exceptions.ParseException),
            ("", "eg:a", Exception),
            ("", ":invalid PN_LOCAL", pyparsing.exceptions.ParseException),
            ("", ":invalid/PN_LOCAL", pyparsing.exceptions.ParseException),
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
    expected_result: Union[URIRef, Type[Exception]],
    blank_graph: Graph,
) -> None:
    """
    The given pname produces the expected result.
    """
    catcher: Optional[pytest.ExceptionInfo[Exception]] = None

    with ExitStack() as xstack:
        if isinstance(expected_result, type) and issubclass(expected_result, Exception):
            catcher = xstack.enter_context(pytest.raises(expected_result))
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

    if catcher is not None:
        assert isinstance(catcher, pytest.ExceptionInfo)
        assert catcher.value is not None
    else:
        assert isinstance(expected_result, URIRef)
        assert expected_result == result
