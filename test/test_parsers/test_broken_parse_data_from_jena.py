import os
from test.data import TEST_DATA_DIR

import pytest

import rdflib

# Recovered from
# https://github.com/RDFLib/rdflib/tree/6b4607018ebf589da74aea4c25408999f1acf2e2

broken_parse_data = os.path.join(TEST_DATA_DIR, "broken_parse_test")


@pytest.fixture
def xfail_broken_parse_data(request):
    fname = request.getfixturevalue("testfile")

    expected_failures = [
        "n3-writer-test-02.n3",
        "n3-writer-test-25.n3",
        "rdf-test-01.n3",
        "rdf-test-08.n3",
        "rdf-test-10.n3",
        "rdf-test-24.n3",
    ]

    if fname in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fname}")
        )


@pytest.mark.parametrize("testfile", os.listdir(broken_parse_data))
@pytest.mark.usefixtures("xfail_broken_parse_data")
def test_n3_serializer_roundtrip(testfile) -> None:

    g1 = rdflib.ConjunctiveGraph()

    g1.parse(os.path.join(broken_parse_data, testfile), format="n3")
