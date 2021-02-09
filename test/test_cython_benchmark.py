import sys
import os
import unittest

from rdflib import Graph, URIRef, Literal
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

import rdflib
print("rdflib.__file__=", rdflib.__file__)



NUM=100000

class DatasetTestCase(unittest.TestCase):
    def setUp(self):
        self.grph = Graph()
        for idx in range(NUM):
            the_subject = URIRef("http://example.org/Subject_%d" % (idx % 100))
            the_predicate = URIRef("http://example.org/Predicate_%d" % (idx % 10))
            the_object = Literal("Object_%d" % (idx % 37))
            self.grph.add((the_subject, the_predicate, the_object))

    def tearDown(self):
        pass

    def testCopyRemove(self):
        grph_copy = Graph()
        for one_triple in self.grph:
            grph_copy.add(one_triple)
        grph_copy.remove((URIRef("http://example.org/Subject_%d" % 0), None, None))
        grph_copy.remove((None, URIRef("http://example.org/Predicate_%d" % 0), None))

    def testSerialize(self):
        as_n3 = self.grph.serialize(format="n3")
        from_n3 = Graph()
        from_n3.parse(data=as_n3, format="n3")

        as_turtle = self.grph.serialize(format="turtle")
        from_turtle = Graph()
        from_turtle.parse(data=as_turtle, format="turtle")

        as_xml = self.grph.serialize(format="xml")
        from_xml = Graph()
        from_xml.parse(data=as_xml, format="xml")


if __name__ == "__main__":
    unittest.main()
