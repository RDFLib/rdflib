import os
import pathlib
from unittest import mock

import pytest

from rdflib.graph import Graph
from rdflib.namespace import RDF, RDFS
from rdflib.parser import _create_input_source_from_location
from rdflib.term import Literal, URIRef


class TestParser:
    backend = "default"
    path = "store"

    def setup_method(self):
        self.graph = Graph(store=self.backend)
        self.graph.open(self.path)

    def teardown_method(self):
        self.graph.close()

    def testNoPathWithHash(self):  # noqa: N802
        g = self.graph
        g.parse(
            data="""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
>

<rdfs:Class rdf:about="http://example.org#">
  <rdfs:label>testing</rdfs:label>
</rdfs:Class>

</rdf:RDF>
""",
            format="xml",
            publicID="http://example.org",
        )

        subject = URIRef("http://example.org#")
        label = g.value(subject, RDFS.label)
        assert label == Literal("testing")
        type = g.value(subject, RDF.type)
        assert type == RDFS.Class


class TestGitHubIssues:
    def test_issue_1228_a(self):
        data = """
        PREFIX sdo: <https://schema.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        <x:> sdo:startDate "1982"^^xsd:gYear .
        """

        g = Graph().parse(data=data, format="ttl")
        assert "1982-01-01" not in data
        assert "1982-01-01" not in g.serialize(format="ttl")

    def test_issue_1228_b(self):
        data = """\
<?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:sdo="https://schema.org/"
    >
    <rdf:Description rdf:about="x:">
        <sdo:startDate
            rdf:datatype="http://www.w3.org/2001/XMLSchema#gYear">1982</sdo:startDate>
    </rdf:Description>
</rdf:RDF>"""

        g = Graph().parse(data=data, format="xml")
        assert "1982-01-01" not in data
        assert "1982-01-01" not in g.serialize(format="xml")

    def test_issue_806(self):
        data = (
            "<http://dbpedia.org/resource/Australian_Labor_Party> "
            "<http://dbpedia.org/ontology/formationYear> "
            '"1891"^^<http://www.w3.org/2001/XMLSchema#gYear> .'
        )
        g = Graph()
        g.parse(data=data, format="nt")
        for _, _, o in g:
            assert "1891-01-01" not in o.n3()


class TestWindowsUNCPaths:
    """Regression tests for https://github.com/RDFLib/rdflib/issues/3424."""

    @pytest.mark.skipif(os.name != "nt", reason="UNC paths are Windows-only")
    def test_unc_path_with_backslashes_not_resolved_against_cwd(self):
        location = "\\\\host\\share\\x.ttl"
        with mock.patch("builtins.open", mock.mock_open(read_data=b"")) as m:
            absolute_location, _, _, _ = _create_input_source_from_location(
                file=None,
                format=None,
                input_source=None,
                location=location,
            )
        assert str(absolute_location).startswith("file://")
        assert "host" in str(absolute_location)
        assert not str(absolute_location).startswith(pathlib.Path.cwd().as_uri())
        m.assert_called_once_with(location, "rb")

    def test_forward_slash_unc_path_keeps_network_path_reference_behaviour(self):
        # ``//host/share/...`` is treated as a network-path reference rather than a UNC path because the two are indistinguishable.
        location = "//host/share/x.ttl"
        with mock.patch("rdflib.parser.URLInputSource") as mock_url_source:
            absolute_location, _, _, _ = _create_input_source_from_location(
                file=None,
                format=None,
                input_source=None,
                location=location,
            )
        assert str(absolute_location) == "file://host/share/x.ttl"
        mock_url_source.assert_called_once_with(absolute_location, None)

    def test_relative_filename_still_resolved_against_cwd(self):
        location = "rdflib_issue_3424_nonexistent.ttl"
        with mock.patch("builtins.open", mock.mock_open()):
            absolute_location, _, _, _ = _create_input_source_from_location(
                file=None,
                format=None,
                input_source=None,
                location=location,
            )
        base = pathlib.Path.cwd().as_uri()
        assert str(absolute_location) == str(URIRef(location, base=base))

    def test_existing_local_absolute_path_unchanged(self):
        location = str(pathlib.Path(__file__).absolute())
        with mock.patch("builtins.open", mock.mock_open()):
            absolute_location, _, _, _ = _create_input_source_from_location(
                file=None,
                format=None,
                input_source=None,
                location=location,
            )
        assert str(absolute_location) == pathlib.Path(location).absolute().as_uri()
