"""
Runs the RDFLib SPARQL test suite.
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

REMOTE_BASE_IRI = (
    "http://raw.github.com/RDFLib/rdflib/main/test/data/suites/rdflib/sparql/"
)
LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/rdflib/sparql/"
MAPPER = URIMapper.from_mappings(
    (REMOTE_BASE_IRI, ensure_suffix(LOCAL_BASE_DIR.as_uri(), "/")),
)

MARK_DICT: MarksDictType = {
    f"{REMOTE_BASE_IRI}manifest.ttl#test-codepoint-escape-02": pytest.mark.xfail(
        reason="known codepoint escape issue"
    ),
    f"{REMOTE_BASE_IRI}manifest.ttl#test-codepoint-escape-03": pytest.mark.xfail(
        reason="known codepoint escape issue"
    ),
    f"{REMOTE_BASE_IRI}manifest.ttl#test-codepoint-escape-04": pytest.mark.xfail(
        reason="known codepoint escape issue"
    ),
    f"{REMOTE_BASE_IRI}manifest.ttl#test-codepoint-escape-bad": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
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
        LOCAL_BASE_DIR / "manifest.ttl",
        mark_dict=MARK_DICT,
        markers=(
            lambda entry: pytest.mark.skip(reason="tester not implemented")
            if entry.type in SKIP_TYPES
            else None,
        ),
        report_prefix="rdflib_sparql",
    ),
)
def test_entry_rdflib(monkeypatch: MonkeyPatch, manifest_entry: SPARQLEntry) -> None:
    check_entry(monkeypatch, manifest_entry)
