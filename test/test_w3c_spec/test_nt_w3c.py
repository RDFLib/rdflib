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

from rdflib.graph import Graph

logger = logging.getLogger(__name__)

REMOTE_BASE_IRI = "http://www.w3.org/2013/N-TriplesTests/"
LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/w3c/ntriples/"
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
        logger.debug(
            "action = %s\n%s", action_path, action_path.read_text(encoding=ENCODING)
        )
    catcher: Optional[pytest.ExceptionInfo[Exception]] = None
    graph = Graph()
    with ExitStack() as xstack:
        if entry.type == RDFT.TestNTriplesNegativeSyntax:
            catcher = xstack.enter_context(pytest.raises(Exception))
        graph.parse(action_path, publicID=entry.action, format="ntriples")
    if catcher is not None:
        assert catcher.value is not None

    if entry.type == RDFT.TestNTriplesPositiveSyntax:
        graph_data = graph.serialize(format="ntriples")
        result_graph = Graph()
        result_graph.parse(data=graph_data, publicID=entry.action, format="ntriples")
        GraphHelper.assert_isomorphic(graph, result_graph)
        GraphHelper.assert_sets_equals(
            graph, result_graph, bnode_handling=BNodeHandling.COLLAPSE
        )


MARK_DICT = {
    f"{REMOTE_BASE_IRI}#nt-syntax-bad-uri-02": pytest.mark.xfail(
        reason="accepts an invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#nt-syntax-bad-uri-03": pytest.mark.xfail(
        reason="accepts an invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#nt-syntax-bad-uri-04": pytest.mark.xfail(
        reason="accepts an invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#nt-syntax-bad-uri-05": pytest.mark.xfail(
        reason="accepts an invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#nt-syntax-bad-esc-01": pytest.mark.xfail(
        reason="accepts badly escaped literal"
    ),
    f"{REMOTE_BASE_IRI}#nt-syntax-bad-esc-02": pytest.mark.xfail(
        reason="accepts badly escaped literal"
    ),
    f"{REMOTE_BASE_IRI}#nt-syntax-bad-esc-03": pytest.mark.xfail(
        reason="accepts badly escaped literal"
    ),
    f"{REMOTE_BASE_IRI}#nt-syntax-bad-esc-04": pytest.mark.xfail(
        reason="accepts badly escaped literal"
    ),
    f"{REMOTE_BASE_IRI}#minimal_whitespace": pytest.mark.xfail(
        reason="Not parsing valid N-Triples syntax."
    ),
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
