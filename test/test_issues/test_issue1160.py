from unittest import mock

import pytest

import rdflib
from rdflib import ConjunctiveGraph

QUERY = """
SELECT DISTINCT ?g
FROM NAMED <http://ns.example.com/named#>
WHERE {
  GRAPH ?g {
    ?s ?p ?o .
  }
}
"""


def test_named_graph_with_fragment():
    """Test that fragment part of the URL is not erased."""
    graph = ConjunctiveGraph()

    with mock.patch("rdflib.parser.URLInputSource") as load_mock:
        # We have to expect an exception here.
        with pytest.raises(Exception):
            graph.query(QUERY)

    load_mock.assert_called_with(
        rdflib.URIRef("http://ns.example.com/named#"),
        "nt",
    )
