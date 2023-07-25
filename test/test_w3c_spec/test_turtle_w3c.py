"""This runs the turtle tests for the W3C RDF Working Group's Turtle
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

REMOTE_BASE_IRI = "http://www.w3.org/2013/TurtleTests/"
LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/w3c/turtle/"
ENCODING = "utf-8"
MAPPER = URIMapper.from_mappings(
    (REMOTE_BASE_IRI, ensure_suffix(LOCAL_BASE_DIR.as_uri(), "/"))
)
VALID_TYPES = {
    RDFT.TestTurtlePositiveSyntax,
    RDFT.TestTurtleNegativeSyntax,
    RDFT.TestTurtleEval,
    RDFT.TestTurtleNegativeEval,
}

# NOTE: `rdft:TestTrigNegativeEval` entries does not have `mf:result` as suggested
# by <https://www.w3.org/TR/rdf11-testcases/#evaluation-tests>, instead they seem
# to be regular `rdft:TestTrigNegativeSyntax`. For example, see `trig-eval-bad-01`
# <https://www.w3.org/2013/TrigTests/manifest.ttl>


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
        if entry.type in (RDFT.TestTurtleNegativeSyntax, RDFT.TestTurtleNegativeEval):
            catcher = xstack.enter_context(pytest.raises(Exception))
        graph.parse(action_path, publicID=entry.action, format="turtle")

    if catcher is not None:
        assert catcher.value is not None

    if entry.type == RDFT.TestTurtleEval:
        assert entry.result is not None
        result_source = entry.uri_mapper.to_local_path(entry.result)
        result_graph = Graph()
        result_graph.parse(result_source, publicID=entry.action, format="ntriples")
        GraphHelper.assert_isomorphic(graph, result_graph)
        GraphHelper.assert_sets_equals(
            graph, result_graph, bnode_handling=BNodeHandling.COLLAPSE
        )


MARK_DICT = {
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-LITERAL2_with_langtag_and_datatype": pytest.mark.xfail(
        reason="accepts literal with both language and datatype"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-uri-01": pytest.mark.xfail(
        reason="accepts invalid IRIs"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-uri-02": pytest.mark.xfail(
        reason="accepts invalid IRIs"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-uri-03": pytest.mark.xfail(
        reason="accepts invalid IRIs"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-uri-04": pytest.mark.xfail(
        reason="accepts invalid IRIs"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-uri-05": pytest.mark.xfail(
        reason="accepts invalid IRIs"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-struct-04": pytest.mark.xfail(
        reason="accepts literal as subject"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-struct-05": pytest.mark.xfail(
        reason="accepts literal as predicate"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-struct-06": pytest.mark.xfail(
        reason="accepts blank node as predicate"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-struct-07": pytest.mark.xfail(
        reason="accepts blank node as predicate"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-kw-04": pytest.mark.xfail(
        reason="accepts 'true' as subject"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-kw-05": pytest.mark.xfail(
        reason="accepts 'true' as predicate"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-n3-extras-03": pytest.mark.xfail(
        reason="accepts N3 paths"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-n3-extras-04": pytest.mark.xfail(
        reason="accepts N3 paths"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-n3-extras-06": pytest.mark.xfail(
        reason="accepts N3 paths"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-struct-14": pytest.mark.xfail(
        reason="accepts Literal as subject"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-struct-15": pytest.mark.xfail(
        reason="accepts Literal as predicate"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-struct-16": pytest.mark.xfail(
        reason="accepts blank node as as predicate"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-struct-17": pytest.mark.xfail(
        reason="accepts blank node as as predicate"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-esc-02": pytest.mark.xfail(
        reason="accepts badly escaped literal"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-esc-03": pytest.mark.xfail(
        reason="accepts badly escaped literal"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-esc-04": pytest.mark.xfail(
        reason="accepts badly escaped literal"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-string-06": pytest.mark.xfail(
        reason="accepts badly quoted string"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-string-07": pytest.mark.xfail(
        reason="accepts badly quoted string"
    ),
    f"{REMOTE_BASE_IRI}#turtle-eval-bad-01": pytest.mark.xfail(
        reason="accepts invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#turtle-eval-bad-02": pytest.mark.xfail(
        reason="accepts invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#turtle-eval-bad-03": pytest.mark.xfail(
        reason="accepts invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#turtle-eval-bad-04": pytest.mark.xfail(
        reason="accepts invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-bad-ln-dash-start": pytest.mark.xfail(
        reason="accepts dash at the start of local name production"
    ),
}


@pytest.mark.parametrize(
    ["manifest_entry"],
    params_from_sources(
        MAPPER,
        ManifestEntry,
        LOCAL_BASE_DIR / "manifest.ttl",
        mark_dict=MARK_DICT,
        report_prefix="rdflib_w3c_turtle",
    ),
)
def test_entry(manifest_entry: ManifestEntry) -> None:
    check_entry(manifest_entry)
