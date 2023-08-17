"""This runs the nquads tests for the W3C RDF Working Group's N-Quads
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

from rdflib.graph import Dataset

logger = logging.getLogger(__name__)

REMOTE_BASE_IRI = "http://www.w3.org/2013/NQuadsTests/"
LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/w3c/nquads/"
ENCODING = "utf-8"
MAPPER = URIMapper.from_mappings(
    (REMOTE_BASE_IRI, ensure_suffix(LOCAL_BASE_DIR.as_uri(), "/"))
)
VALID_TYPES = {RDFT.TestNQuadsPositiveSyntax, RDFT.TestNQuadsNegativeSyntax}


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
        if entry.type == RDFT.TestNQuadsNegativeSyntax:
            catcher = xstack.enter_context(pytest.raises(Exception))
        dataset.parse(action_path, publicID=entry.action, format="nquads")
    if catcher is not None:
        assert catcher.value is not None

    if entry.type == RDFT.TestNQuadsPositiveSyntax:
        graph_data = dataset.serialize(format="nquads")
        result_dataset = Dataset()
        result_dataset.parse(data=graph_data, publicID=entry.action, format="nquads")
        GraphHelper.assert_cgraph_isomorphic(
            dataset, result_dataset, exclude_bnodes=True
        )
        GraphHelper.assert_sets_equals(
            dataset, result_dataset, bnode_handling=BNodeHandling.COLLAPSE
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
    f"{REMOTE_BASE_IRI}#nt-syntax-bad-esc-03": pytest.mark.skip(
        reason="accepts badly escaped literal"
    ),
}


@pytest.mark.parametrize(
    ["manifest_entry"],
    params_from_sources(
        MAPPER,
        ManifestEntry,
        LOCAL_BASE_DIR / "manifest.ttl",
        mark_dict=MARK_DICT,
        report_prefix="rdflib_w3c_nquads",
    ),
)
def test_entry(manifest_entry: ManifestEntry) -> None:
    check_entry(manifest_entry)
