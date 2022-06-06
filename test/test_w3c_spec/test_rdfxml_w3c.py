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

REMOTE_BASE_IRI = "http://www.w3.org/2013/RDFXMLTests/"
LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/w3c/rdf-xml/"
ENCODING = "utf-8"
MAPPER = URIMapper.from_mappings(
    (REMOTE_BASE_IRI, ensure_suffix(LOCAL_BASE_DIR.as_uri(), "/"))
)
VALID_TYPES = {RDFT.TestXMLNegativeSyntax, RDFT.TestXMLEval}


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
        if entry.type == RDFT.TestXMLNegativeSyntax:
            catcher = xstack.enter_context(pytest.raises(Exception))
        graph.parse(action_path, publicID=entry.action, format="xml")

    if catcher is not None:
        assert catcher.value is not None

    if entry.type == RDFT.TestXMLEval:
        assert entry.result is not None
        result_source = entry.uri_mapper.to_local_path(entry.result)
        result_graph = Graph()
        result_graph.parse(result_source, publicID=entry.action, format="ntriples")
        GraphHelper.assert_isomorphic(graph, result_graph)
        GraphHelper.assert_sets_equals(
            graph, result_graph, bnode_handling=BNodeHandling.COLLAPSE
        )


@pytest.mark.parametrize(
    ["manifest_entry"],
    params_from_sources(
        MAPPER,
        ManifestEntry,
        LOCAL_BASE_DIR / "manifest.ttl",
        report_prefix="rdflib_w3c_rdfxml",
    ),
)
def test_entry(manifest_entry: ManifestEntry) -> None:
    check_entry(manifest_entry)


REMOTE_BASE_IRI = "http://www.w3.org/2013/RDFXMLTests/"
NON_NORMATIVE_LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/w3c/rdf-xml-non-normative/"
NON_NORMATIVE_MAPPER = URIMapper.from_mappings(
    (REMOTE_BASE_IRI, ensure_suffix(NON_NORMATIVE_LOCAL_BASE_DIR.as_uri(), "/"))
)


@pytest.mark.parametrize(
    ["manifest_entry"],
    params_from_sources(
        NON_NORMATIVE_MAPPER,
        ManifestEntry,
        NON_NORMATIVE_LOCAL_BASE_DIR / "manifest.ttl",
        report_prefix="rdflib_w3c_rdfxml_non_normative",
    ),
)
def test_non_normative_entry(manifest_entry: ManifestEntry) -> None:
    check_entry(manifest_entry)
