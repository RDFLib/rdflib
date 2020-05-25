from rdflib import Graph, URIRef, Literal, BNode
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import isomorphic

import unittest
from nose.tools import eq_


class TestConstructInitBindings(unittest.TestCase):
    def test_construct_init_bindings(self):
        """
        This is issue https://github.com/RDFLib/rdflib/issues/1001
        """

        g1 = Graph()

        q_str = """
        PREFIX : <urn:ns1:>
        CONSTRUCT {
          ?uri :prop1 ?val1;
               :prop2 ?c .
        }
        WHERE {
          bind(uri(concat("urn:ns1:", ?a)) as ?uri)
          bind(?b as ?val1)
        }
        """
        q_prepared = prepareQuery(q_str)

        expected = [
            (URIRef("urn:ns1:A"), URIRef("urn:ns1:prop1"), Literal("B")),
            (URIRef("urn:ns1:A"), URIRef("urn:ns1:prop2"), Literal("C")),
        ]
        results = g1.query(
            q_prepared,
            initBindings={"a": Literal("A"), "b": Literal("B"), "c": Literal("C")},
        )

        eq_(sorted(results, key=lambda x: str(x[1])), expected)
