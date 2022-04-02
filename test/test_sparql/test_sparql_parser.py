from rdflib import Graph, Literal
from rdflib.term import Node
from rdflib.namespace import Namespace
from rdflib.plugins.sparql.processor import processUpdate
import unittest
import sys
import math
from typing import Set, Tuple


def triple_set(graph: Graph) -> Set[Tuple[Node, Node, Node]]:
    return set(graph.triples((None, None, None)))


class SPARQLParserTests(unittest.TestCase):
    def test_insert_recursionlimit(self) -> None:
        # These values are experimentally determined
        # to cause the RecursionError reported in
        # https://github.com/RDFLib/rdflib/issues/1336
        resource_count = math.ceil(sys.getrecursionlimit() / (33 - 3))
        self.do_insert(resource_count)

    def test_insert_large(self) -> None:
        self.do_insert(200)

    def do_insert(self, resource_count: int) -> None:
        EGV = Namespace("http://example.org/vocab#")
        EGI = Namespace("http://example.org/instance#")
        prop0, prop1, prop2 = EGV["prop0"], EGV["prop1"], EGV["prop2"]
        g0 = Graph()
        for index in range(resource_count):
            resource = EGI[f"resource{index}"]
            g0.add((resource, prop0, Literal(index)))
            g0.add((resource, prop1, Literal("example resource")))
            g0.add((resource, prop2, Literal(f"resource #{index}")))

        g0ntriples = g0.serialize(format="ntriples")
        g1 = Graph()

        self.assertNotEqual(triple_set(g0), triple_set(g1))

        processUpdate(g1, f"INSERT DATA {{ {g0ntriples!s} }}")

        self.assertEqual(triple_set(g0), triple_set(g1))


if __name__ == "__main__":

    unittest.main()
