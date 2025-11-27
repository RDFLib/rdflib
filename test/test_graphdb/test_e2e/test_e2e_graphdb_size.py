import pathlib

import pytest

from rdflib.contrib.graphdb import GraphDBClient


@pytest.mark.testcontainer
def test_graphdb_size(client: GraphDBClient):
    size = client.graphdb.size("test-repo")
    assert size.inferred == 0 and size.total == 0 and size.explicit == 0

    repo = client.repositories.get("test-repo")
    with open(pathlib.Path(__file__).parent.parent / "data/quads-1.nq", "rb") as file:
        repo.overwrite(file)
    size = client.graphdb.size("test-repo")
    assert size.inferred == 0 and size.total == 2 and size.explicit == 2
