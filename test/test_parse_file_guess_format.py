import unittest

from rdflib import Graph


class FileParserGuessFormatTest(unittest.TestCase):
    def test_ttl(self):
        g = Graph()
        self.assertIsInstance(g.parse("test/w3c/turtle/IRI_subject.ttl"), Graph)

    def test_n3(self):
        g = Graph()
        self.assertIsInstance(g.parse("test/n3/example-lots_of_graphs.n3"), Graph)


if __name__ == '__main__':
    unittest.main()
