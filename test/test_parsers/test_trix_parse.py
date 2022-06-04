#!/usr/bin/env python
import os
import unittest
from test.data import TEST_DATA_DIR

from rdflib.graph import ConjunctiveGraph


class TestTrixParse(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAperture(self):

        g = ConjunctiveGraph()

        trix_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "suites", "trix/trix-aperture.trix"), os.curdir
        )
        g.parse(trix_path, format="trix")
        c = list(g.contexts())

        # print list(g.contexts())
        t = sum(map(len, g.contexts()))

        self.assertEqual(t, 24)
        self.assertEqual(len(c), 4)

        # print "Parsed %d triples"%t

    def testSpec(self):

        g = ConjunctiveGraph()

        trix_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "suites", "trix/trix-nokia-example.trix"),
            os.curdir,
        )
        g.parse(trix_path, format="trix")

        # print "Parsed %d triples"%len(g)

    def testNG4j(self):

        g = ConjunctiveGraph()

        trix_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "suites", "trix/trix-ng4j-test-01.trix"),
            os.curdir,
        )
        g.parse(trix_path, format="trix")

        # print "Parsed %d triples"%len(g)


if __name__ == "__main__":
    unittest.main()
