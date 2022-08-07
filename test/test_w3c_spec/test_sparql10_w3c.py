"""
Runs the SPARQL 1.0 test suite from.
"""
from test.data import TEST_DATA_DIR
from test.utils import ensure_suffix
from test.utils.dawg_manifest import MarksDictType, params_from_sources
from test.utils.iri import URIMapper
from test.utils.sparql_checker import (
    SKIP_TYPES,
    SPARQLEntry,
    check_entry,
    ctx_configure_rdflib,
)
from typing import Generator

import pytest
from pytest import MonkeyPatch

REMOTE_BASE_IRI = "http://www.w3.org/2001/sw/DataAccess/tests/data-r2/"
LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/w3c/dawg-data-r2/"
MAPPER = URIMapper.from_mappings(
    (REMOTE_BASE_IRI, ensure_suffix(LOCAL_BASE_DIR.as_uri(), "/")),
)
MARK_DICT: MarksDictType = {
    f"{REMOTE_BASE_IRI}basic/manifest#term-6": pytest.mark.xfail(
        reason="query misinterpreted."
    ),
    f"{REMOTE_BASE_IRI}basic/manifest#term-7": pytest.mark.xfail(reason="..."),
    f"{REMOTE_BASE_IRI}expr-builtin/manifest#dawg-datatype-2": pytest.mark.xfail(
        reason="additional row in output"
    ),
    f"{REMOTE_BASE_IRI}open-world/manifest#date-1": pytest.mark.xfail(
        reason="RDFLib has more rows than it should have."
    ),
    f"{REMOTE_BASE_IRI}open-world/manifest#date-2": pytest.mark.xfail(
        reason="RDFLib result has one too few rows."
    ),
    f"{REMOTE_BASE_IRI}optional-filter/manifest#dawg-optional-filter-005-simplified": pytest.mark.xfail(
        reason="one row is missing a column"
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql1/manifest#syntax-bnodes-03": pytest.mark.xfail(
        reason="Issue with bnodes in query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql1/manifest#syntax-forms-01": pytest.mark.xfail(),
    f"{REMOTE_BASE_IRI}syntax-sparql1/manifest#syntax-lists-01": pytest.mark.xfail(
        reason="Issue with list in query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql1/manifest#syntax-lit-08": pytest.mark.skip(
        reason="bad test, positive syntax has invalid syntax."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql2/manifest#syntax-form-describe01": pytest.mark.xfail(
        reason="Describe not supported."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql2/manifest#syntax-general-08": pytest.mark.xfail(
        reason="Not parsing with no spaces."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql2/manifest#syntax-lists-04": pytest.mark.xfail(
        reason="Not handling lists in query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql3/manifest#blabel-cross-graph-bad": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql3/manifest#blabel-cross-optional-bad": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql3/manifest#blabel-cross-union-bad": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql3/manifest#syn-bad-26": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql4/manifest#syn-bad-34": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql4/manifest#syn-bad-35": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql4/manifest#syn-bad-36": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql4/manifest#syn-bad-37": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql4/manifest#syn-bad-38": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql4/manifest#syn-bad-GRAPH-breaks-BGP": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql4/manifest#syn-bad-OPT-breaks-BGP": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql4/manifest#syn-bad-UNION-breaks-BGP": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}syntax-sparql4/syn-bad-37.rq": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
}


@pytest.fixture(scope="module", autouse=True)
def configure_rdflib() -> Generator[None, None, None]:
    with ctx_configure_rdflib():
        yield None


@pytest.mark.parametrize(
    ["manifest_entry"],
    params_from_sources(
        MAPPER,
        SPARQLEntry,
        LOCAL_BASE_DIR / "manifest-evaluation.ttl",
        LOCAL_BASE_DIR / "manifest-syntax.ttl",
        mark_dict=MARK_DICT,
        markers=(
            lambda entry: pytest.mark.skip(reason="tester not implemented")
            if entry.type in SKIP_TYPES
            else None,
        ),
        report_prefix="rdflib_w3c_sparql10",
    ),
)
def test_entry_sparql10(monkeypatch: MonkeyPatch, manifest_entry: SPARQLEntry) -> None:
    check_entry(monkeypatch, manifest_entry)
