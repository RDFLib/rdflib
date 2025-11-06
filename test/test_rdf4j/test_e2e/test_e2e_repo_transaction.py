from pathlib import Path

import pytest

from rdflib.contrib.rdf4j.client import Repository
from rdflib.contrib.rdf4j.exceptions import TransactionClosedError


def test_e2e_repo_transaction(repo: Repository):
    path = str(Path(__file__).parent.parent / "data/quads-1.nq")
    repo.overwrite(path)
    assert repo.size() == 2

    with repo.transaction() as txn:
        txn.ping()
        assert txn.size() == 2
        assert txn.size("urn:graph:a") == 1

    with pytest.raises(TransactionClosedError):
        txn.ping()
