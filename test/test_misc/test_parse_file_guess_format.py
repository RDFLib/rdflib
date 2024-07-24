# NOTE: The config below enables strict mode for mypy.
# mypy: no_ignore_errors
# mypy: warn_unused_configs, disallow_any_generics
# mypy: disallow_subclassing_any, disallow_untyped_calls
# mypy: disallow_untyped_defs, disallow_incomplete_defs
# mypy: check_untyped_defs, disallow_untyped_decorators
# mypy: no_implicit_optional, warn_redundant_casts, warn_unused_ignores
# mypy: warn_return_any, no_implicit_reexport, strict_equality

import logging
import os
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

import pytest

from rdflib import Graph
from rdflib.exceptions import ParserError
from rdflib.util import guess_format
from test.data import TEST_DATA_DIR


class TestFileParserGuessFormat:
    def test_guess_format(self) -> None:
        assert guess_format("example.trix") == "trix"
        assert guess_format("local-file.jsonld") == "json-ld"
        assert guess_format("local-file.json-ld") == "json-ld"
        assert guess_format("/some/place/on/disk/example.json") == "json-ld"
        assert guess_format("../../relative/place/on/disk/example.json") == "json-ld"
        assert guess_format("example.rdf") == "xml"
        assert guess_format("example.nt") == "nt"
        assert guess_format("example.nq") == "nquads"
        assert guess_format("example.nquads") == "nquads"
        assert guess_format("example.n3") == "n3"
        assert guess_format("example.docx", None) is None
        assert guess_format("example", None) is None
        assert guess_format("example.mkv", None) is None

    def test_jsonld(self) -> None:
        g = Graph()
        assert isinstance(g.parse("test/jsonld/1.1/manifest.jsonld"), Graph)
        assert isinstance(g.parse("test/jsonld/file_ending_test_01.json"), Graph)
        assert isinstance(g.parse("test/jsonld/file_ending_test_01.json-ld"), Graph)
        assert isinstance(g.parse("test/jsonld/file_ending_test_01.jsonld"), Graph)

    def test_ttl(self) -> None:
        g = Graph()
        assert isinstance(
            g.parse(
                os.path.join(
                    TEST_DATA_DIR, "suites", "w3c", "turtle", "IRI_subject.ttl"
                )
            ),
            Graph,
        )

    def test_n3(self) -> None:
        g = Graph()
        assert isinstance(
            g.parse(os.path.join(TEST_DATA_DIR, "example-lots_of_graphs.n3")), Graph
        )

    def test_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        g = Graph()
        graph_logger = logging.getLogger("rdflib")  # noqa: F841

        with TemporaryDirectory() as tmpdirname:
            newpath = Path(tmpdirname).joinpath("no_file_ext")
            copyfile(
                os.path.join(
                    TEST_DATA_DIR,
                    "suites",
                    "w3c",
                    "rdf-xml",
                    "datatypes",
                    "test001.rdf",
                ),
                str(newpath),
            )
            with pytest.raises(
                ParserError, match=r"Could not guess RDF format"
            ), caplog.at_level("WARNING"):
                g.parse(str(newpath))

            assert any(
                rec.levelno == logging.WARNING
                and (
                    "does not look like a valid URI, trying to serialize this will break."
                    in rec.message
                )
                for rec in caplog.records
            )
