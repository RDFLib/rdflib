#!/usr/bin/env python3

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

"""
This test-set demonstrates usage of identifier prefixing and the
forward-slash character in Turtle, JSON-LD, and SPARQL.  The motivating
use case originated with attempts to interact with IANA Media Types as
prefixed concepts, e.g. "application/json" somehow being
"mime:application/json".
"""

from test.data import TEST_DATA_DIR
from test.utils.graph import cached_graph
from typing import Set

import pytest

from rdflib import Graph
from rdflib.plugins.sparql.processor import prepareQuery
from rdflib.plugins.sparql.sparql import Query
from rdflib.query import ResultRow

query_string_expanded = r"""
SELECT ?nIndividual
WHERE {
  ?nIndividual a <http://example.org/ontology/core/MyClassB> .
}"""

# NOTE: This is expected to fail.  The SPARQL grammar production rules
# for prefixed IRIs, especially at production rule PN_LOCAL, have no way
# to reach the forward-slash or backslash characters.
# https://www.w3.org/TR/rdf-sparql-query/#grammar
query_string_prefixed = r"""
PREFIX ex: <http://example.org/ontology/>
SELECT ?nIndividual
WHERE {
  # NOTE: Syntax is incorrect - forward slash cannot be included in
  # local component of name.
  ?nIndividual a ex:core\/MyClassB .
}"""

PN_LOCAL_BACKSLASH_XFAIL_REASON = """
    Contrary to the ratified SPARQL 1.1 grammar, the RDFlib SPARQL propcessor
    accepts backslashes as part of PN_LOCAL which it treats as escape
    characters.

    There should be a way to instruct the SPARQL parser to operate in strict
    mode, and in strict mode backslashes should not be permitted in PN_LOCAL.

    See https://github.com/RDFLib/rdflib/issues/1871
"""


def _test_query_prepares(query_string: str) -> None:
    """
    Confirm parse behavior of SPARQL engine when a concept would be
    prefixed at a point that leaves a forward-slash character in the
    suffix.
    """
    nsdict = {
        "ex": "http://example.org/ontology/",
        "kb": "http://example.org/kb/",
        "owl": "http://www.w3.org/2002/07/owl#",
    }
    # TODO: A 'strict' flag for prepareQuery is under consideration to
    # adjust parse behavior around backslash characters.
    query_object = prepareQuery(query_string, initNs=nsdict)
    assert isinstance(query_object, Query)


def test_query_prepares_expanded() -> None:
    _test_query_prepares(query_string_expanded)


@pytest.mark.xfail(reason=PN_LOCAL_BACKSLASH_XFAIL_REASON)
def test_query_prepares_prefixed() -> None:
    with pytest.raises(ValueError):
        _test_query_prepares(query_string_prefixed)


def _test_escapes_and_query(
    graph: Graph, query_string: str, expected_query_compiled: bool
) -> None:
    """
    Confirm search-results behavior of SPARQL engine when a concept
    would be prefixed at a point that leaves a forward-slash character
    in the suffix.

    Note that _test_query_prepares also exercises the expected parse
    failure.  This parameterized test is more for demonstrating that
    searching can work without prefixes.
    """
    expected: Set[str] = {
        "http://example.org/kb/individual-b",
    }
    computed: Set[str] = set()

    query_compiled: bool = False
    try:
        query_object = prepareQuery(query_string)
        query_compiled = True
    except Exception:
        pass
    assert expected_query_compiled == query_compiled

    for result in graph.query(query_object):
        assert isinstance(result, ResultRow)
        computed.add(str(result[0]))

    assert expected == computed


def test_escapes_and_query_turtle_expanded() -> None:
    graph = cached_graph((TEST_DATA_DIR / "variants/forward_slash.ttl",))
    _test_escapes_and_query(graph, query_string_expanded, True)


@pytest.mark.xfail(reason=PN_LOCAL_BACKSLASH_XFAIL_REASON, raises=AssertionError)
def test_escapes_and_query_turtle_prefixed() -> None:
    graph = cached_graph((TEST_DATA_DIR / "variants/forward_slash.ttl",))
    _test_escapes_and_query(graph, query_string_prefixed, False)


def test_escapes_and_query_jsonld_expanded() -> None:
    graph = cached_graph((TEST_DATA_DIR / "variants/forward_slash.jsonld",))
    _test_escapes_and_query(graph, query_string_expanded, True)


@pytest.mark.xfail(reason=PN_LOCAL_BACKSLASH_XFAIL_REASON, raises=AssertionError)
def test_escapes_and_query_jsonld_prefixed() -> None:
    graph = cached_graph((TEST_DATA_DIR / "variants/forward_slash.jsonld",))
    _test_escapes_and_query(graph, query_string_prefixed, False)
