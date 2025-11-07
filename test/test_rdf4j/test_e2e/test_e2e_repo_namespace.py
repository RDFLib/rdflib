import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.client import NamespaceListingResult, Repository

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)


@pytest.mark.testcontainer
def test_e2e_repo_namespace_crud(repo: Repository):
    assert repo.namespaces.list() == []

    # Delete a non-existent prefix
    repo.namespaces.remove("non-existent")

    # Retrieve a non-existent prefix
    assert repo.namespaces.get("non-existent") is None

    # Set a new prefix
    repo.namespaces.set("test", "http://example.org/test/")
    assert set(repo.namespaces.list()) == {
        NamespaceListingResult(prefix="test", namespace="http://example.org/test/")
    }
    assert repo.namespaces.get("test") == "http://example.org/test/"

    # Set another
    repo.namespaces.set("test2", "http://example.org/test2/")
    assert set(repo.namespaces.list()) == {
        NamespaceListingResult(prefix="test", namespace="http://example.org/test/"),
        NamespaceListingResult(prefix="test2", namespace="http://example.org/test2/"),
    }
    assert repo.namespaces.get("test2") == "http://example.org/test2/"

    # Update an existing prefix (overwrite)
    repo.namespaces.set("test", "http://example.org/test-updated/")
    assert set(repo.namespaces.list()) == {
        NamespaceListingResult(
            prefix="test", namespace="http://example.org/test-updated/"
        ),
        NamespaceListingResult(prefix="test2", namespace="http://example.org/test2/"),
    }
    assert repo.namespaces.get("test") == "http://example.org/test-updated/"

    # Delete test prefix
    repo.namespaces.remove("test")
    assert set(repo.namespaces.list()) == {
        NamespaceListingResult(prefix="test2", namespace="http://example.org/test2/")
    }
    assert repo.namespaces.get("test") is None
    assert repo.namespaces.get("test2") == "http://example.org/test2/"

    # Clear
    repo.namespaces.clear()
    assert repo.namespaces.list() == []
    assert repo.namespaces.get("test") is None
    assert repo.namespaces.get("test2") is None
