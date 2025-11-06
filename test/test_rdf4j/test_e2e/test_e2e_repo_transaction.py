from pathlib import Path

import pytest

from rdflib.contrib.rdf4j.client import Repository, Transaction
from rdflib.contrib.rdf4j.exceptions import TransactionClosedError
from rdflib.term import Variable, Literal


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
