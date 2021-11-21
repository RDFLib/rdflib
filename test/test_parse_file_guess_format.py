import unittest
import logging
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from rdflib.exceptions import ParserError

from rdflib import Graph


class FileParserGuessFormatTest(unittest.TestCase):
    def test_jsonld(self):
        g = Graph()
        self.assertIsInstance(g.parse("test/jsonld/1.1/manifest.jsonld"), Graph)

    def test_ttl(self):
        g = Graph()
        self.assertIsInstance(g.parse("test/w3c/turtle/IRI_subject.ttl"), Graph)

    def test_n3(self):
        g = Graph()
        self.assertIsInstance(g.parse("test/n3/example-lots_of_graphs.n3"), Graph)

    def test_warning(self):
        g = Graph()
        graph_logger = logging.getLogger("rdflib")

        with TemporaryDirectory() as tmpdirname:
            newpath = Path(tmpdirname).joinpath("no_file_ext")
            copyfile("test/rdf/Manifest.rdf", str(newpath))
            with self.assertLogs(graph_logger, "WARNING"):
                with self.assertRaises(ParserError):
                    g.parse(str(newpath))


if __name__ == "__main__":
    unittest.main()
