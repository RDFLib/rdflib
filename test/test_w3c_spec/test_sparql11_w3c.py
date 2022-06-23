"""
Runs the SPARQL 1.1 test suite from.
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

REMOTE_BASE_IRI = "http://www.w3.org/2009/sparql/docs/tests/data-sparql11/"
LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/w3c/sparql11/"
MAPPER = URIMapper.from_mappings(
    (REMOTE_BASE_IRI, ensure_suffix(LOCAL_BASE_DIR.as_uri(), "/")),
)
MARK_DICT: MarksDictType = {
    f"{REMOTE_BASE_IRI}aggregates/manifest#agg-err-01": pytest.mark.xfail(
        reason="Error in AVG should return no binding but it does."
    ),
    f"{REMOTE_BASE_IRI}aggregates/manifest#agg08": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}aggregates/manifest#agg09": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}aggregates/manifest#agg10": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}aggregates/manifest#agg11": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}aggregates/manifest#agg12": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}delete/manifest#dawg-delete-using-02a": pytest.mark.xfail(
        reason="known issue"
    ),
    f"{REMOTE_BASE_IRI}delete/manifest#dawg-delete-using-06a": pytest.mark.xfail(
        reason="known issue"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#paper-sparqldl-Q1-rdfs": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#paper-sparqldl-Q1": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#paper-sparqldl-Q2": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#paper-sparqldl-Q3": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#paper-sparqldl-Q4": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#parent10": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#parent3": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#parent4": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#parent5": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#parent6": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#parent7": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#parent8": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#parent9": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdf01": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdfs01": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdfs02": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdfs03": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdfs04": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdfs05": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdfs06": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdfs07": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdfs09": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdfs10": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#rdfs11": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#simple1": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#simple2": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#simple3": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#simple4": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#simple5": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#simple6": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#simple7": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#simple8": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#sparqldl-02": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#sparqldl-03": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#sparqldl-10": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#sparqldl-11": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#sparqldl-12": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}entailment/manifest#sparqldl-13": pytest.mark.xfail(
        reason="entailment not implemented"
    ),
    f"{REMOTE_BASE_IRI}functions/manifest#strdt01": pytest.mark.xfail(
        reason="Reason for test failure is not clear."
    ),
    f"{REMOTE_BASE_IRI}functions/manifest#strdt03": pytest.mark.xfail(
        reason="Reason for test failure is not clear."
    ),
    f"{REMOTE_BASE_IRI}grouping/manifest#group06": pytest.mark.xfail(
        reason="Accepts invalid query."
    ),
    f"{REMOTE_BASE_IRI}grouping/manifest#group07": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}property-path/manifest#pp37": pytest.mark.xfail(
        reason="RDFLib produces one extra row"
    ),
    f"{REMOTE_BASE_IRI}service/manifest#service1": pytest.mark.skip(
        reason="need custom handling"
    ),
    f"{REMOTE_BASE_IRI}service/manifest#service2": pytest.mark.skip(
        reason="need custom handling"
    ),
    f"{REMOTE_BASE_IRI}service/manifest#service3": pytest.mark.skip(
        reason="need custom handling"
    ),
    f"{REMOTE_BASE_IRI}service/manifest#service4a": pytest.mark.skip(
        reason="need custom handling"
    ),
    f"{REMOTE_BASE_IRI}service/manifest#service5": pytest.mark.skip(
        reason="test not supported"
    ),
    f"{REMOTE_BASE_IRI}service/manifest#service6": pytest.mark.skip(
        reason="need custom handling"
    ),
    f"{REMOTE_BASE_IRI}service/manifest#service7": pytest.mark.skip(
        reason="test not supported"
    ),
    f"{REMOTE_BASE_IRI}syntax-query/manifest#test_43": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-query/manifest#test_44": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-query/manifest#test_45": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-query/manifest#test_60": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-query/manifest#test_61a": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-query/manifest#test_62a": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-query/manifest#test_65": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-update-1/manifest#test_43": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-update-1/manifest#test_44": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-update-1/manifest#test_50": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-update-1/manifest#test_51": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-update-1/manifest#test_52": pytest.mark.xfail(
        reason="Parses sucessfully instead of failing."
    ),
    f"{REMOTE_BASE_IRI}syntax-update-1/manifest#test_54": pytest.mark.xfail(
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
        LOCAL_BASE_DIR / "manifest-all.ttl",
        mark_dict=MARK_DICT,
        markers=(
            lambda entry: pytest.mark.skip(reason="tester not implemented")
            if entry.type in SKIP_TYPES
            else None,
        ),
        report_prefix="rdflib_w3c_sparql11",
    ),
)
def test_entry_sparql11(monkeypatch: MonkeyPatch, manifest_entry: SPARQLEntry) -> None:
    check_entry(monkeypatch, manifest_entry)
