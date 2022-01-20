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

# NOTE: The config below enables strict mode for mypy.
# mypy: no_ignore_errors
# mypy: warn_unused_configs, disallow_any_generics
# mypy: disallow_subclassing_any, disallow_untyped_calls
# mypy: disallow_untyped_defs, disallow_incomplete_defs
# mypy: check_untyped_defs, disallow_untyped_decorators
# mypy: no_implicit_optional, warn_redundant_casts, warn_unused_ignores
# mypy: warn_return_any, no_implicit_reexport, strict_equality

from typing import Set, Tuple, Union

# TODO Bug - rdflib.plugins.sparql.prepareQuery() will run fine if this
# test is run, but mypy can't tell the symbol is exposed.
import rdflib.plugins.sparql.processor


def test_rdflib_query_exercise() -> None:
    """
    The purpose of this test is to exercise a selection of rdflib features under "mypy --strict" review.
    """

    graph = rdflib.Graph()

    literal_one = rdflib.Literal("1", datatype=rdflib.XSD.integer)
    literal_two = rdflib.Literal(2)
    literal_true = rdflib.Literal(True)

    # Set up predicate nodes, using hash IRI pattern.
    predicate_p = rdflib.URIRef("http://example.org/predicates#p")
    predicate_q = rdflib.URIRef("http://example.org/predicates#q")
    predicate_r = rdflib.URIRef("http://example.org/predicates#r")

    # Set up knowledge base nodes, using URN namespace, slash IRI pattern, and/or blank node.
    kb_bnode = rdflib.BNode()
    kb_http_uriref = rdflib.URIRef("http://example.org/kb/x")
    kb_https_uriref = rdflib.URIRef("https://example.org/kb/y")
    kb_urn_uriref = rdflib.URIRef("urn:example:kb:z")

    graph.add((kb_urn_uriref, predicate_p, literal_one))
    graph.add((kb_http_uriref, predicate_p, literal_one))
    graph.add((kb_https_uriref, predicate_p, literal_one))
    graph.add((kb_https_uriref, predicate_p, literal_two))
    graph.add((kb_https_uriref, predicate_q, literal_two))
    graph.add((kb_bnode, predicate_p, literal_one))

    expected_nodes_using_predicate_q: Set[rdflib.IdentifiedNode] = {
        kb_https_uriref
    }
    computed_nodes_using_predicate_q: Set[rdflib.IdentifiedNode] = set()
    for triple in graph.triples((None, predicate_q, None)):
        computed_nodes_using_predicate_q.add(triple[0])
    assert expected_nodes_using_predicate_q == computed_nodes_using_predicate_q

    one_usage_query = """\
SELECT ?resource
WHERE {
  ?resource <http://example.org/predicates#p> 1 .
}
"""

    expected_one_usage: Set[rdflib.IdentifiedNode] = {
        kb_bnode,
        kb_http_uriref,
        kb_https_uriref,
        kb_urn_uriref,
    }
    computed_one_usage: Set[rdflib.IdentifiedNode] = set()
    for one_usage_result in graph.query(one_usage_query):
        computed_one_usage.add(one_usage_result[0])
    assert expected_one_usage == computed_one_usage

    # The purpose of this query is confirming the believed return
    # signature of graph.query() is determined at *each* call of
    # graph.query(), rather than the first.  I.e. there should not be a
    # type error when the first call returns a length-one result tuple,
    # and the second a length-two result tuple.
    two_usage_query = """\
SELECT ?resource ?predicate
WHERE {
  ?resource ?predicate "2"^^xsd:integer .
}
"""

    expected_two_usage: Set[
        Tuple[
            rdflib.IdentifiedNode,
            rdflib.IdentifiedNode,
        ]
    ] = {(kb_https_uriref, predicate_p), (kb_https_uriref, predicate_q)}
    computed_two_usage: Set[
        Tuple[
            rdflib.IdentifiedNode,
            rdflib.IdentifiedNode,
        ]
    ] = set()
    for two_usage_result in graph.query(two_usage_query):
        computed_two_usage.add(two_usage_result)
    assert expected_two_usage == computed_two_usage

    nsdict = {k: v for (k, v) in graph.namespace_manager.namespaces()}

    prepared_one_usage_query = rdflib.plugins.sparql.processor.prepareQuery(
        one_usage_query, initNs=nsdict
    )
    computed_one_usage_from_prepared_query: Set[rdflib.IdentifiedNode] = set()
    for prepared_one_usage_result in graph.query(prepared_one_usage_query):
        computed_one_usage_from_prepared_query.add(prepared_one_usage_result[0])
    assert expected_one_usage == computed_one_usage_from_prepared_query

    for node_using_one in sorted(computed_one_usage):
        graph.add((node_using_one, predicate_r, literal_true))

    python_one: int = literal_one.toPython()
    assert python_one == 1

    python_two: int = literal_two.toPython()
    assert python_two == 2

    python_true: bool = literal_true.toPython()
    assert python_true == True

    python_iri: str = kb_https_uriref.toPython()
    assert python_iri == "https://example.org/kb/y"
