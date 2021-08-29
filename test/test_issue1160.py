import unittest
from unittest import mock

import rdflib

from rdflib import ConjunctiveGraph
from rdflib.parser import URLInputSource

QUERY = """
SELECT DISTINCT ?g
FROM NAMED <http://ns.example.com/named#>
WHERE {
  GRAPH ?g {
    ?s ?p ?o .
  }
}
"""


class NamedGraphWithFragmentTest(unittest.TestCase):
    def test_named_graph_with_fragment(self):
        """Test that fragment part of the URL is not erased."""
        graph = ConjunctiveGraph()

        with mock.patch("rdflib.parser.URLInputSource") as load_mock:
            # We have to expect an exception here.
            self.assertRaises(Exception, graph.query, QUERY)

        load_mock.assert_called_with(
            rdflib.URIRef("http://ns.example.com/named#"),
            "nt",
        )
