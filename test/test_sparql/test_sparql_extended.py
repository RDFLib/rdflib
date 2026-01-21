from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence

import pytest

from rdflib import Graph, Literal
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import prettify_parsetree
from rdflib.term import Identifier, Variable


@pytest.mark.parametrize(
    ["query_string", "expected_bindings"],
    [
        pytest.param(
            """
            SELECT ?label ?deprecated WHERE {
                ?s rdfs:label "Class"
                OPTIONAL {
                    ?s
                    rdfs:comment
                    ?label
                }
                OPTIONAL {
                    ?s
                    owl:deprecated
                    ?deprecated
                }
            }
            """,
            [{Variable("label"): Literal("The class of classes.")}],
            id="select-optional",
        ),
    ],
)
def test_queries(
    query_string: str,
    expected_bindings: Sequence[Mapping[Variable, Identifier]],
    rdfs_graph: Graph,
) -> None:
    """
    Results of queries against the rdfs.ttl return the expected values.
    """
    query_tree = parseQuery(query_string)

    logging.debug("query_tree = %s", prettify_parsetree(query_tree))
    query = translateQuery(query_tree)
    # query._original_args = (query_string, {}, None)
    result = rdfs_graph.query(query)

    # Pretty print the result
    result_ser = result.serialize(format="txt")
    assert result_ser is not None
    pretty_string = result_ser.decode("utf-8")
    logging.debug("result:\n%s", pretty_string)
    assert expected_bindings == result.bindings
