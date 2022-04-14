#!/usr/bin/env python
import os
import unittest
from test import TEST_DIR

from rdflib.graph import Dataset


class TestTrixParse(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAperture(self):

        g = Dataset()

        trix_path = os.path.relpath(
            os.path.join(TEST_DIR, "trix/aperture.trix"), os.curdir
        )
        g.parse(trix_path, format="trix")
        c = list(g.graphs())

        # print list(g.contexts())
        t = sum(map(len, g.graphs()))

        self.assertEqual(t, 24)
        self.assertEqual(len(c), 4)

        # print "Parsed %d triples"%t

    def testSpec(self):

        g = Dataset()

        trix_path = os.path.relpath(
            os.path.join(TEST_DIR, "trix/nokia_example.trix"), os.curdir
        )
        g.parse(trix_path, format="trix")

        # print "Parsed %d triples"%len(g)

    def testNG4j(self):

        g = Dataset()

        trix_path = os.path.relpath(
            os.path.join(TEST_DIR, "trix/ng4jtest.trix"), os.curdir
        )
        g.parse(trix_path, format="trix")

        # print "Parsed %d triples"%len(g)


if __name__ == "__main__":
    unittest.main()
