from __future__ import annotations

import logging
from pathlib import Path

import pytest

from rdflib import Graph, Namespace

EX = Namespace("http://example.org/")
HERE = Path(__file__).parent
PATH_DATA = HERE / "test_unbound_values-data.ttl"


@pytest.fixture(scope="module")
def rdfs_graph() -> Graph:
    """An RDFS graph for testing SPARQL queries with unbound values."""
    g = Graph()
    g.parse(PATH_DATA, format="turtle")
    return g


@pytest.mark.parametrize(
    ["query_file", "expected_rows"],
    [
        pytest.param(
            HERE / "test_unbound_values-working.rq",
            3,
            id="working",
        ),
        pytest.param(
            HERE / "test_unbound_values-failing.rq",
            3,
            id="failing",
        ),
    ],
)
def test_queries(
    query_file: Path,
    expected_rows: int,
    rdfs_graph: Graph,
) -> None:
    """Test that SPARQL queries return expected number of rows."""
    query_string = query_file.read_text()
    result = rdfs_graph.query(query_string)

    result_ser = result.serialize(format="txt")
    assert result_ser is not None
    pretty_string = result_ser.decode("utf-8")
    logging.debug("result:\n%s", pretty_string)
    assert expected_rows == len(result)
