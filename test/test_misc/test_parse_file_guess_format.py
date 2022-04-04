# NOTE: The config below enables strict mode for mypy.
# mypy: no_ignore_errors
# mypy: warn_unused_configs, disallow_any_generics
# mypy: disallow_subclassing_any, disallow_untyped_calls
# mypy: disallow_untyped_defs, disallow_incomplete_defs
# mypy: check_untyped_defs, disallow_untyped_decorators
# mypy: no_implicit_optional, warn_redundant_casts, warn_unused_ignores
# mypy: warn_return_any, no_implicit_reexport, strict_equality

import unittest
import logging
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from rdflib.exceptions import ParserError

from rdflib import Graph
from rdflib.util import guess_format


class FileParserGuessFormatTest(unittest.TestCase):
    def test_guess_format(self) -> None:
        self.assertEqual(guess_format("example.trix"), "trix")
        self.assertEqual(guess_format("local-file.jsonld"), "json-ld")
        self.assertEqual(guess_format("local-file.json-ld"), "json-ld")
        self.assertEqual(guess_format("/some/place/on/disk/example.json"), "json-ld")
        self.assertEqual(guess_format("../../relative/place/on/disk/example.json"), "json-ld")
        self.assertEqual(guess_format("example.rdf"), "xml")
        self.assertEqual(guess_format("example.nt"), "nt")
        self.assertEqual(guess_format("example.nq"), "nquads")
        self.assertEqual(guess_format("example.nquads"), "nquads")
        self.assertEqual(guess_format("example.n3"), "n3")
        self.assertIsNone(guess_format("example.docx", None))
        self.assertIsNone(guess_format("example", None))
        self.assertIsNone(guess_format("example.mkv", None))

    def test_jsonld(self) -> None:
        g = Graph()
        self.assertIsInstance(g.parse("test/jsonld/1.1/manifest.jsonld"), Graph)
        self.assertIsInstance(g.parse("test/jsonld/file_ending_test_01.json"), Graph)
        self.assertIsInstance(g.parse("test/jsonld/file_ending_test_01.json-ld"), Graph)
        self.assertIsInstance(g.parse("test/jsonld/file_ending_test_01.jsonld"), Graph)

    def test_ttl(self) -> None:
        g = Graph()
        self.assertIsInstance(g.parse("test/w3c/turtle/IRI_subject.ttl"), Graph)

    def test_n3(self) -> None:
        g = Graph()
        self.assertIsInstance(g.parse("test/n3/example-lots_of_graphs.n3"), Graph)

    def test_warning(self) -> None:
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
