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

from typing import List, Set, Tuple

import pytest

import rdflib
from rdflib import Graph
from rdflib.plugins.sparql.processor import prepareQuery
from rdflib.plugins.sparql.sparql import Query
from rdflib.term import Node

# Determine version to delay a test until a version > 6 is being
# prepared for release.  A 7-point-0-anything, alpha or beta designation
# should enable some further tests backwards-incompatible with version 6.
# Treat rdflib.__version__ like it can be compiled into a version_info
# tuple similar to sys.version_info.
# TODO: During the release of version 7, this set of version-detection
# code and its corresponding skipifs can be deleted.
_rdflib_version_info_strs: List[str] = rdflib.__version__.split(".")
_is_version_7_started = False
if _rdflib_version_info_strs[0].isdigit():
    if int(_rdflib_version_info_strs[0]) >= 7:
        _is_version_7_started = True

# Note that the data and query strings are Python raw strings, so
# backslashes won't be escape characters to Python.
# The "*_expanded" variables eschew prefixing.

# Spell a class name without prefixing.
turtle_data_expanded = r"""
@prefix kb: <http://example.org/kb/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<http://example.org/ontology/core/MyClassA> a owl:Class .

kb:individual-a a <http://example.org/ontology/core/MyClassA> .
"""

# Spell a class name with prefixing, but have the prefixing NOT include
# one of the forward-slashed path components.
# The forward slash must be escaped, according to Turtle grammar
# production rules grammar rules including and between PN_LOCAL and
# PN_LOCAL_ESC.
# https://www.w3.org/TR/turtle/#sec-grammar-grammar
turtle_data_prefixed = r"""
@prefix ex: <http://example.org/ontology/> .
@prefix kb: <http://example.org/kb/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

ex:core\/MyClassB a owl:Class .

kb:individual-b a ex:core\/MyClassB .
"""

# This data is an equivalant graph with turtle_data_expanded.
jsonld_data_expanded = r"""
{
    "@context": {
        "kb": "http://example.org/kb/",
        "owl": "http://www.w3.org/2002/07/owl#"
    },
    "@graph": {
        "@id": "kb:individual-a",
        "@type": {
            "@id": "http://example.org/ontology/core/MyClassA",
            "@type": "owl:Class"
        }
    }
}
"""

# This data is an equivalant graph with turtle_data_prefixed.
# The JSON-LD spec does not provide a grammar production rule set in
# EBNF.  However, the section on compact IRIs indicates that an IRI can
# be prefixed at any point that would not result in a suffix starting
# with "//".  Hence, an unpaired forward slash, as a legal character of
# an IRI, can appear in the suffix component of a compact IRI.
# https://json-ld.org/spec/latest/json-ld/#compact-iris
jsonld_data_prefixed = r"""
{
    "@context": {
        "ex": "http://example.org/ontology/",
        "kb": "http://example.org/kb/",
        "owl": "http://www.w3.org/2002/07/owl#"
    },
    "@graph": {
        "@id": "kb:individual-b",
        "@type": {
            "@id": "ex:core/MyClassB",
            "@type": "owl:Class"
        }
    }
}
"""

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


def _test_parse_matches(turtle_data: str, jsonld_data: str) -> None:
    """
    Confirm that the two concrete syntaxes parse to the same set of
    triples.
    """
    g_turtle = Graph()
    g_jsonld = Graph()

    g_turtle.parse(data=turtle_data_expanded, format="turtle")
    g_jsonld.parse(data=jsonld_data_expanded, format="json-ld")

    triples_turtle: Set[Tuple[Node, Node, Node]] = {
        x for x in g_turtle.triples((None, None, None))
    }
    triples_jsonld: Set[Tuple[Node, Node, Node]] = {
        x for x in g_jsonld.triples((None, None, None))
    }

    assert triples_turtle == triples_jsonld


def test_parse_matches_expanded() -> None:
    _test_parse_matches(turtle_data_expanded, jsonld_data_expanded)


def test_parse_matches_prefixed() -> None:
    _test_parse_matches(turtle_data_prefixed, jsonld_data_prefixed)


def _test_escapes_to_iri(graph: Graph) -> None:
    """
    Confirm all triple-subjects within the two data graphs are found.
    """
    expected: Set[str] = {
        "http://example.org/kb/individual-a",
        "http://example.org/kb/individual-b",
        "http://example.org/ontology/core/MyClassA",
        "http://example.org/ontology/core/MyClassB",
    }
    computed: Set[str] = set()

    for triple in graph.triples((None, None, None)):
        computed.add(str(triple[0]))

    assert expected == computed


def test_escapes_to_iri_turtle() -> None:
    graph = Graph()
    graph.parse(data=turtle_data_expanded, format="turtle")
    graph.parse(data=turtle_data_prefixed, format="turtle")
    _test_escapes_to_iri(graph)


def test_escapes_to_iri_jsonld() -> None:
    graph = Graph()
    graph.parse(data=jsonld_data_expanded, format="json-ld")
    graph.parse(data=jsonld_data_prefixed, format="json-ld")
    _test_escapes_to_iri(graph)


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


@pytest.mark.skipif(
    not _is_version_7_started,
    reason="query failure detection delayed until rdflib version 7",
)
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
        computed.add(str(result[0]))

    assert expected == computed


def test_escapes_and_query_turtle_expanded() -> None:
    graph = Graph()
    graph.parse(data=turtle_data_expanded, format="turtle")
    graph.parse(data=turtle_data_prefixed, format="turtle")
    _test_escapes_and_query(graph, query_string_expanded, True)


@pytest.mark.skipif(
    not _is_version_7_started,
    reason="query failure detection delayed until rdflib version 7",
)
def test_escapes_and_query_turtle_prefixed() -> None:
    graph = Graph()
    graph.parse(data=turtle_data_expanded, format="turtle")
    graph.parse(data=turtle_data_prefixed, format="turtle")
    _test_escapes_and_query(graph, query_string_prefixed, False)


def test_escapes_and_query_jsonld_expanded() -> None:
    graph = Graph()
    graph.parse(data=jsonld_data_expanded, format="json-ld")
    graph.parse(data=jsonld_data_prefixed, format="json-ld")
    _test_escapes_and_query(graph, query_string_expanded, True)


@pytest.mark.skipif(
    not _is_version_7_started,
    reason="query failure detection delayed until rdflib version 7",
)
def test_escapes_and_query_jsonld_prefixed() -> None:
    graph = Graph()
    graph.parse(data=jsonld_data_expanded, format="json-ld")
    graph.parse(data=jsonld_data_prefixed, format="json-ld")
    _test_escapes_and_query(graph, query_string_prefixed, False)
