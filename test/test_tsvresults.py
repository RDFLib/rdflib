import unittest
from six import StringIO
from rdflib.plugins.sparql.results.tsvresults import TSVResultParser


class TestTSVResults(unittest.TestCase):

    def test_empty_tsvresults_bindings(self):
        # check that optional bindings are ordered properly
        source = """?s\t?p\t?o
        \t<urn:p>\t<urn:o>
        <urn:s>\t\t<urn:o>
        <urn:s>\t<urn:p>\t"""

        parser = TSVResultParser()
        source = StringIO(source)
        result = parser.parse(source)

        for idx, row in enumerate(result):
            self.assertTrue(row[idx] is None)
