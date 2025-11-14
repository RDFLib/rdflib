from __future__ import annotations

from pathlib import Path

import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.exceptions import TransactionClosedError
from rdflib.term import Literal, URIRef, Variable

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.rdf4j.client import Repository, Transaction


@pytest.mark.testcontainer
def test_e2e_repo_transaction(repo: Repository):
    path = str(Path(__file__).parent.parent / "data/quads-1.nq")
    repo.overwrite(path)
    assert repo.size() == 2

    with repo.transaction() as txn:
        txn.ping()
        assert txn.size() == 2
        assert txn.size("urn:graph:a") == 1

    # Open a transaction without a context manager
    txn = Transaction(repo)
    txn.open()
    assert txn.size() == 2
    txn.rollback()
    assert txn.url is None

    # Raises an error as the transaction is closed.
    with pytest.raises(TransactionClosedError):
        txn.ping()

    path = str(Path(__file__).parent.parent / "data/quads-2.nq")
    with repo.transaction() as txn:
        query = "select (count(*) as ?count) where {?s ?p ?o}"
        result = txn.query(query)
        # Before upload, the number of statements is 2.
        assert result.bindings[0][Variable("count")] == Literal(2)
        # Add data.
        txn.upload(path)
        assert txn.size() == 3
        result = txn.query(query)
        # Now it's 3.
        assert result.bindings[0][Variable("count")] == Literal(3)
        # Repo is still 2 as we've not yet committed.
        assert repo.size() == 2

    # Transaction committed, size is now 3.
    assert repo.size() == 3


@pytest.mark.testcontainer
def test_e2e_repo_transaction_delete(repo: Repository):
    path = str(Path(__file__).parent.parent / "data/quads-1.nq")
    repo.overwrite(path)
    data = "<http://example.org/s> <http://example.org/p-another> <http://example.org/o-another> <urn:graph:a2> ."
    repo.upload(data)
    assert repo.size() == 3
    assert repo.size("urn:graph:a2") == 1

    with repo.transaction() as txn:
        txn.delete(data)
        assert txn.size() == 2
        assert txn.size("urn:graph:a2") == 0


@pytest.mark.testcontainer
def test_e2e_repo_transaction_update(repo: Repository):
    path = str(Path(__file__).parent.parent / "data/quads-1.nq")
    repo.overwrite(path)
    assert repo.size() == 2

    query = "INSERT DATA { GRAPH <urn:graph:a2> { <http://example.org/s> <http://example.org/p-another> <http://example.org/o-another> } }"
    with repo.transaction() as txn:
        txn.update(query)
        assert txn.size() == 3
        assert txn.size("urn:graph:a2") == 1


@pytest.mark.testcontainer
def test_e2e_repo_transaction_get(repo: Repository):
    path = str(Path(__file__).parent.parent / "data/quads-1.nq")
    repo.overwrite(path)
    assert repo.size() == 2

    with repo.transaction() as txn:
        ds = txn.get()
        assert len(ds) == 2

    repo.upload(str(Path(__file__).parent.parent / "data/quads-2.nq"))
    repo.upload(str(Path(__file__).parent.parent / "data/quads-3.nq"))
    assert repo.size() == 4

    with repo.transaction() as txn:
        ds = txn.get()
        assert len(ds) == 4

        ds = txn.get(graph_name="urn:graph:a")
        assert len(ds) == 1

        ds = txn.get(pred=URIRef("http://example.org/p"))
        assert len(ds) == 2
