from pathlib import Path

import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.client import Repository
from rdflib.term import URIRef, Variable

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)


def test_e2e_repo_query(repo: Repository):
    path = str(Path(__file__).parent.parent / "data/quads-1.nq")
    repo.overwrite(path)
    assert repo.size() == 2

    query = "select ?s ?p ?o where { ?s ?p ?o }"
    results = repo.query(query)
    assert len(results) == 2
    s_var = Variable("s")
    p_var = Variable("p")
    o_var = Variable("o")
    subjects = [URIRef("http://example.org/s"), URIRef("http://example.org/s2")]
    predicates = [URIRef("http://example.org/p"), URIRef("http://example.org/p2")]
    objects = [URIRef("http://example.org/o"), URIRef("http://example.org/o2")]
    for row in results.bindings:
        assert row.get(s_var) in subjects
        assert row.get(p_var) in predicates
        assert row.get(o_var) in objects

    query = "ask where { ?s ?p ?o }"
    results = repo.query(query)
    assert results.askAnswer is True

    query = "ask where { <urn:s> <urn:p> <urn:o> }"
    results = repo.query(query)
    assert results.askAnswer is False

    query = "construct { ?s ?p ?o } where { graph <urn:graph:a> { ?s ?p ?o } }"
    results = repo.query(query)
    assert len(results.graph) == 1
    assert (
        URIRef("http://example.org/s"),
        URIRef("http://example.org/p"),
        URIRef("http://example.org/o"),
    ) in results.graph

    query = "describe <http://example.org/s2>"
    results = repo.query(query)
    assert len(results.graph) == 1
    assert (
        URIRef("http://example.org/s2"),
        URIRef("http://example.org/p2"),
        URIRef("http://example.org/o2"),
    ) in results.graph

    # Provide a keyword argument "limit" to the query method
    # We have 2 statements in the repository, and this should return only one
    query = "select ?s ?p ?o where { ?s ?p ?o }"
    results = repo.query(query, limit=1)
    assert len(results) == 1
