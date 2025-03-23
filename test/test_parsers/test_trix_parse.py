import os

from rdflib.graph import Dataset
from test.data import TEST_DATA_DIR


class TestTrixParse:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def testAperture(self):  # noqa: N802
        g = Dataset()

        trix_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "suites", "trix/trix-aperture.trix"), os.curdir
        )
        g.parse(trix_path, format="trix")
        c = list(g.contexts())

        # print list(g.contexts())
        t = sum(map(len, g.contexts()))

        assert t == 24
        assert len(c) == 5

        # print "Parsed %d triples"%t

    def testSpec(self):  # noqa: N802
        g = Dataset()

        trix_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "suites", "trix/trix-nokia-example.trix"),
            os.curdir,
        )
        g.parse(trix_path, format="trix")

        # print "Parsed %d triples"%len(g)

    def testNG4j(self):  # noqa: N802
        g = Dataset()

        trix_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "suites", "trix/trix-ng4j-test-01.trix"),
            os.curdir,
        )
        g.parse(trix_path, format="trix")

        # print "Parsed %d triples"%len(g)
