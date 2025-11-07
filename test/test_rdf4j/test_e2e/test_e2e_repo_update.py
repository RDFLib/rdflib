from pathlib import Path

import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.client import Repository

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)


def test_e2e_repo_query(repo: Repository):
    path = str(Path(__file__).parent.parent / "data/quads-1.nq")
    repo.overwrite(path)
    assert repo.size() == 2

    query = """INSERT DATA { GRAPH <urn:graph:a3> { <http://example.org/s3> <http://example.org/p3> <http://example.org/o3> } }"""
    repo.update(query)
    assert repo.size() == 3
