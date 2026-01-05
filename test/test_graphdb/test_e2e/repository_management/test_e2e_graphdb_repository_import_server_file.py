from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.models import ImportSettings, ParserSettings


@pytest.mark.testcontainer
def test_get_server_import_files_returns_list(client: GraphDBClient):
    """Test that get_server_import_files returns a list."""
    repo = client.repositories.get("test-repo")
    result = repo.get_server_import_files()

    assert isinstance(result, list)
    # Verify we get the 3 mounted test files (quads-1.nq, quads-2.nq, quads-3.nq)
    assert len(result) == 3


@pytest.mark.testcontainer
def test_get_server_import_files_returns_import_settings_instances(
    client: GraphDBClient,
):
    """Test that get_server_import_files returns ImportSettings instances when files exist."""
    repo = client.repositories.get("test-repo")
    result = repo.get_server_import_files()

    # Should return 3 ImportSettings instances for the mounted test files
    assert isinstance(result, list)
    assert len(result) == 3
    for item in result:
        assert isinstance(item, ImportSettings)


@pytest.mark.testcontainer
def test_get_server_import_files_import_settings_have_required_fields(
    client: GraphDBClient,
):
    """Test that ImportSettings instances have all required fields."""
    repo = client.repositories.get("test-repo")
    result = repo.get_server_import_files()

    assert len(result) == 3
    for item in result:
        # Check required fields exist and have correct types
        assert isinstance(item.name, str)
        assert item.status in {
            "PENDING",
            "IMPORTING",
            "DONE",
            "ERROR",
            "NONE",
            "INTERRUPTING",
        }
        assert isinstance(item.size, str)
        assert isinstance(item.lastModified, int)
        assert isinstance(item.imported, int)
        assert isinstance(item.addedStatements, int)
        assert isinstance(item.removedStatements, int)
        assert isinstance(item.numReplacedGraphs, int)
        # Verify parserSettings is correctly converted to ParserSettings instance
        assert isinstance(item.parserSettings, ParserSettings)


@pytest.mark.testcontainer
def test_get_server_import_files_returns_expected_file_names(
    client: GraphDBClient,
):
    """Test that get_server_import_files returns the expected mounted file names."""
    repo = client.repositories.get("test-repo")
    result = repo.get_server_import_files()

    # Extract file names from the results
    file_names = {item.name for item in result}
    expected_files = {"quads-1.nq", "quads-2.nq", "quads-3.nq"}

    assert file_names == expected_files
