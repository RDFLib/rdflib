"""This runs the nt tests for the W3C RDF Working Group's N-Triples
test suite."""
import logging
from contextlib import ExitStack
from test.data import TEST_DATA_DIR
from test.utils import BNodeHandling, GraphHelper, ensure_suffix
from test.utils.dawg_manifest import ManifestEntry, params_from_sources
from test.utils.iri import URIMapper
from test.utils.namespace import RDFT
from typing import Optional

import pytest

import rdflib

rdflib.plugin.register(
    "larknqstar",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larknquadsstar",
    "LarkNQuadsStarParser",
)

from rdflib.graph import Graph

logger = logging.getLogger(__name__)

REMOTE_BASE_IRI = "http://www.w3.org/2013/N-TriplesTests/"
LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/rdf-star/nt/syntax/"
ENCODING = "utf-8"
MAPPER = URIMapper.from_mappings(
    (REMOTE_BASE_IRI, ensure_suffix(LOCAL_BASE_DIR.as_uri(), "/"))
)
VALID_TYPES = {RDFT.TestNTriplesPositiveSyntax, RDFT.TestNTriplesNegativeSyntax}


def check_entry(entry: ManifestEntry) -> None:
    assert entry.action is not None
    assert entry.type in VALID_TYPES
    action_path = entry.uri_mapper.to_local_path(entry.action)
    if logger.isEnabledFor(logging.DEBUG):
        logger.info(
            "action = %s\n%s", action_path, action_path.read_text(encoding=ENCODING)
        )
    catcher: Optional[pytest.ExceptionInfo[Exception]] = None
    graph = Graph()
    with ExitStack() as xstack:
        if entry.type == RDFT.TestNTriplesNegativeSyntax:
            catcher = xstack.enter_context(pytest.raises(Exception))
        graph.parse(action_path, publicID=entry.action, format="larknqstar")
    if catcher is not None:
        assert catcher.value is not None

    if entry.type == RDFT.TestNTriplesPositiveSyntax:
        graph_data = graph.serialize(format="ntriples")
        result_graph = Graph()
        # result_graph.parse(data=graph_data, publicID=entry.action, format="larknt")
        result_graph.parse(data=graph_data, publicID=entry.action, format="nt")
        GraphHelper.assert_isomorphic(graph, result_graph)
        GraphHelper.assert_sets_equals(
            graph, result_graph, bnode_handling=BNodeHandling.COLLAPSE
        )


MARK_DICT = {
    # TODO: Assess the execution cost of using urlparse to reject
    # when scheme == "", otherwise, restore these xfails
    # f"{REMOTE_BASE_IRI}#nt-syntax-bad-uri-06": pytest.mark.xfail(
    #     reason="accepts an invalid IRI"
    # ),
    # f"{REMOTE_BASE_IRI}#nt-syntax-bad-uri-07": pytest.mark.xfail(
    #     reason="accepts an invalid IRI"
    # ),
    # f"{REMOTE_BASE_IRI}#nt-syntax-bad-uri-08": pytest.mark.xfail(
    #     reason="accepts an invalid IRI"
    # ),
    # f"{REMOTE_BASE_IRI}#nt-syntax-bad-uri-09": pytest.mark.xfail(
    #     reason="accepts an invalid IRI"
    # ),
}


@pytest.mark.parametrize(
    ["manifest_entry"],
    params_from_sources(
        MAPPER,
        ManifestEntry,
        LOCAL_BASE_DIR / "manifest.ttl",
        mark_dict=MARK_DICT,
        report_prefix="rdflib_w3c_ntriples",
    ),
)
def test_entry(manifest_entry: ManifestEntry) -> None:
    check_entry(manifest_entry)
