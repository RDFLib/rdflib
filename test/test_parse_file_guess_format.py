import unittest
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from xml.sax import SAXParseException

from rdflib import Graph, logger as graph_logger


class FileParserGuessFormatTest(unittest.TestCase):
    def test_ttl(self):
        g = Graph()
        self.assertIsInstance(g.parse("test/w3c/turtle/IRI_subject.ttl"), Graph)

    def test_n3(self):
        g = Graph()
        self.assertIsInstance(g.parse("test/n3/example-lots_of_graphs.n3"), Graph)

    def test_warning(self):
        g = Graph()
        with TemporaryDirectory() as tmpdirname:
            newpath = Path(tmpdirname).joinpath("no_file_ext")
            copyfile("test/w3c/turtle/IRI_subject.ttl", newpath)
            with self.assertLogs(graph_logger, "WARNING") as log_cm:
                with self.assertRaises(SAXParseException):
                    g.parse(str(newpath))
            self.assertTrue(any("Could not guess format" in msg for msg in log_cm.output))


if __name__ == '__main__':
    unittest.main()
