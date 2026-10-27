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

from __future__ import annotations

from rdflib import Graph
from rdflib.plugins.sparql.processor import prepareQuery
from rdflib.plugins.sparql.sparql import Query
from rdflib.query import ResultRow
from test.data import TEST_DATA_DIR
from test.utils.graph import cached_graph

query_string_expanded = r"""
SELECT ?nIndividual
WHERE {
  ?nIndividual a <http://example.org/ontology/core/MyClassB> .
}"""

# SPARQL 1.1 allows the forward slash in the local component of a name when
# it is escaped with a backslash, which is then dropped from the IRI.
# https://www.w3.org/TR/sparql11-query/#rPN_LOCAL_ESC
query_string_prefixed = r"""
PREFIX ex: <http://example.org/ontology/>
SELECT ?nIndividual
WHERE {
  ?nIndividual a ex:core\/MyClassB .
}"""


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
    query_object = prepareQuery(query_string, initNs=nsdict)
    assert isinstance(query_object, Query)


def test_query_prepares_expanded() -> None:
    _test_query_prepares(query_string_expanded)


def test_query_prepares_prefixed() -> None:
    _test_query_prepares(query_string_prefixed)


def _test_escapes_and_query(graph: Graph, query_string: str) -> None:
    """
    Confirm search-results behavior of SPARQL engine when a concept
    would be prefixed at a point that leaves a forward-slash character
    in the suffix.

    The prefixed and expanded queries give the same results.
    """
    expected: set[str] = {
        "http://example.org/kb/individual-b",
    }
    computed: set[str] = set()

    query_object = prepareQuery(query_string)
    for result in graph.query(query_object):
        assert isinstance(result, ResultRow)
        computed.add(str(result[0]))

    assert expected == computed


def test_escapes_and_query_turtle_expanded() -> None:
    graph = cached_graph((TEST_DATA_DIR / "variants/forward_slash.ttl",))
    _test_escapes_and_query(graph, query_string_expanded)


def test_escapes_and_query_turtle_prefixed() -> None:
    graph = cached_graph((TEST_DATA_DIR / "variants/forward_slash.ttl",))
    _test_escapes_and_query(graph, query_string_prefixed)


def test_escapes_and_query_jsonld_expanded() -> None:
    graph = cached_graph((TEST_DATA_DIR / "variants/forward_slash.jsonld",))
    _test_escapes_and_query(graph, query_string_expanded)


def test_escapes_and_query_jsonld_prefixed() -> None:
    graph = cached_graph((TEST_DATA_DIR / "variants/forward_slash.jsonld",))
    _test_escapes_and_query(graph, query_string_prefixed)
