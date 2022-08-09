"""Runs the tests for the W3C RDF Working Group's TriG test suite.

"""
import logging
from contextlib import ExitStack
from test.data import TEST_DATA_DIR
from test.utils import BNodeHandling, GraphHelper, ensure_suffix
from test.utils.dawg_manifest import ManifestEntry, params_from_sources
from test.utils.iri import URIMapper
from test.utils.namespace import RDFT
from typing import Optional

import pytest

from rdflib.graph import Dataset

logger = logging.getLogger(__name__)

REMOTE_BASE_IRI = "http://www.w3.org/2013/TriGTests/"
LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/w3c/trig/"
ENCODING = "utf-8"
MAPPER = URIMapper.from_mappings(
    (REMOTE_BASE_IRI, ensure_suffix(LOCAL_BASE_DIR.as_uri(), "/"))
)
VALID_TYPES = {
    RDFT.TestTrigEval,
    RDFT.TestTrigPositiveSyntax,
    RDFT.TestTrigNegativeSyntax,
    RDFT.TestTrigNegativeEval,
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
    dataset = Dataset()
    with ExitStack() as xstack:
        if entry.type in (RDFT.TestTrigNegativeSyntax, RDFT.TestTrigNegativeEval):
            catcher = xstack.enter_context(pytest.raises(Exception))
        dataset.parse(action_path, publicID=entry.action, format="trig")

    if catcher is not None:
        assert catcher.value is not None

    if entry.type == RDFT.TestTrigEval:
        assert entry.result is not None
        result_source = entry.uri_mapper.to_local_path(entry.result)
        result_dataset = Dataset()
        result_dataset.parse(result_source, publicID=entry.action, format="nquads")
        GraphHelper.assert_cgraph_isomorphic(
            dataset, result_dataset, exclude_bnodes=True
        )
        GraphHelper.assert_sets_equals(
            dataset, result_dataset, bnode_handling=BNodeHandling.COLLAPSE
        )


MARK_DICT = {
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-base-04": pytest.mark.xfail(
        reason="accepts @base in the wrong place"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-base-05": pytest.mark.xfail(
        reason="accepts BASE in the wrong place"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-prefix-06": pytest.mark.xfail(
        reason="accepts @prefix in the wrong place"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-prefix-07": pytest.mark.xfail(
        reason="accepts PREFIX in the wrong place"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-LITERAL2_with_langtag_and_datatype": pytest.mark.xfail(
        reason="accepts literal with langtag and datatype"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-uri-01": pytest.mark.xfail(
        reason="accepts an invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-uri-02": pytest.mark.xfail(
        reason="accepts an invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-uri-03": pytest.mark.xfail(
        reason="accepts an invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-uri-04": pytest.mark.xfail(
        reason="accepts an invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-uri-05": pytest.mark.xfail(
        reason="accepts an invalid IRI"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-struct-04": pytest.mark.xfail(
        reason="allows literal as subject"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-struct-05": pytest.mark.xfail(
        reason="allows literal as predicate"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-struct-06": pytest.mark.xfail(
        reason="allows BNodes as predicate"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-struct-07": pytest.mark.xfail(
        reason="allows BNodes as predicate"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-kw-04": pytest.mark.xfail(
        reason="accepts 'true' as a subject"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-kw-05": pytest.mark.xfail(
        reason="accepts 'true' as a predicate"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-n3-extras-03": pytest.mark.xfail(
        reason="accepts N3 paths"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-n3-extras-04": pytest.mark.xfail(
        reason="accepts N3 paths"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-n3-extras-06": pytest.mark.xfail(
        reason="accepts N3 paths"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-struct-12": pytest.mark.xfail(
        reason="ingores bad triples"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-struct-14": pytest.mark.xfail(
        reason="accepts literal as subject"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-struct-15": pytest.mark.xfail(
        reason="accepts literal as predicate"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-struct-16": pytest.mark.xfail(
        reason="accepts BNode as predicate"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-struct-17": pytest.mark.xfail(
        reason="accepts BNode as predicate"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-esc-02": pytest.mark.xfail(
        reason="accepts badly escaped literals"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-esc-03": pytest.mark.xfail(
        reason="accepts badly escaped literals"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-esc-04": pytest.mark.xfail(
        reason="accepts badly escaped literals"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-string-06": pytest.mark.xfail(
        reason="accepts badly quoted literals"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-string-07": pytest.mark.xfail(
        reason="accepts badly quoted literals"
    ),
    f"{REMOTE_BASE_IRI}#trig-eval-bad-01": pytest.mark.xfail(reason="accepts bad IRI"),
    f"{REMOTE_BASE_IRI}#trig-eval-bad-02": pytest.mark.xfail(reason="accepts bad IRI"),
    f"{REMOTE_BASE_IRI}#trig-eval-bad-03": pytest.mark.xfail(reason="accepts bad IRI"),
    f"{REMOTE_BASE_IRI}#trig-eval-bad-04": pytest.mark.xfail(reason="accepts bad IRI"),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-ln-dash-start": pytest.mark.xfail(
        reason="accepts dash in start of local name"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-list-01": pytest.mark.xfail(
        reason="ignores badly formed quad"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-list-02": pytest.mark.xfail(
        reason="ignores badly formed quad"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-list-03": pytest.mark.xfail(
        reason="ignores badly formed quad"
    ),
    f"{REMOTE_BASE_IRI}#trig-syntax-bad-list-04": pytest.mark.xfail(
        reason="ignores badly formed quad"
    ),
    f"{REMOTE_BASE_IRI}#trig-graph-bad-01": pytest.mark.xfail(
        reason="accepts GRAPH with no name"
    ),
    f"{REMOTE_BASE_IRI}#trig-graph-bad-07": pytest.mark.xfail(
        reason="accepts nested GRAPH"
    ),
}


@pytest.mark.parametrize(
    ["manifest_entry"],
    params_from_sources(
        MAPPER,
        ManifestEntry,
        LOCAL_BASE_DIR / "manifest.ttl",
        mark_dict=MARK_DICT,
        report_prefix="rdflib_w3c_trig",
    ),
)
def test_entry(manifest_entry: ManifestEntry) -> None:
    check_entry(manifest_entry)
