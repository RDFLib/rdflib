"""End-to-end tests for RecoveryManagement.backup method.

These tests verify the GraphDB POST /rest/recovery/backup endpoint
returns a tar archive file containing repository and system data.

Key findings from API testing:
- Content-Type: application/x-tar;charset=UTF-8
- Content-Disposition: attachment; filename=backup-YYYY-MM-DD-HH-MM-SS.tar
- The response body is a tar archive containing:
  - snapshot-metadata.js - Backup metadata
  - settings.js - GraphDB settings
  - users.js - User accounts (when backupSystemData=True)
  - {repository-id}-repository-metadata.js - Repository metadata
  - repositories/{repository-id}/1.chunk - Repository data chunks
"""

from __future__ import annotations

import io
import tarfile

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient


@pytest.mark.testcontainer
def test_backup_returns_bytes(client: GraphDBClient):
    """Test that backup returns bytes when dest is None."""
    result = client.recovery.backup()

    assert isinstance(result, bytes)
    assert len(result) > 0


@pytest.mark.testcontainer
def test_backup_returns_valid_tar_archive(client: GraphDBClient):
    """Test that backup returns a valid tar archive."""
    result = client.recovery.backup()

    # Verify result is a valid tar archive
    with tarfile.open(fileobj=io.BytesIO(result), mode="r:*") as tar:
        members = tar.getnames()
        assert len(members) > 0, "Tar archive should contain files"


@pytest.mark.testcontainer
def test_backup_with_repositories_returns_repo_data(client: GraphDBClient):
    """Test that backup with specific repository includes that repo's data."""
    result = client.recovery.backup(repositories=["test-repo"])

    assert isinstance(result, bytes)

    with tarfile.open(fileobj=io.BytesIO(result), mode="r:*") as tar:
        members = tar.getnames()
        # Check that test-repo data is included
        repo_files = [m for m in members if "test-repo" in m]
        assert len(repo_files) > 0, "Archive should contain test-repo data"


@pytest.mark.testcontainer
def test_backup_with_system_data_includes_users(client: GraphDBClient):
    """Test that backup with system data flag includes user data."""
    result = client.recovery.backup(backup_system_data=True)

    assert isinstance(result, bytes)

    with tarfile.open(fileobj=io.BytesIO(result), mode="r:*") as tar:
        members = tar.getnames()
        assert any(m.endswith("users.js") for m in members)


@pytest.mark.testcontainer
def test_backup_without_system_data_excludes_users(client: GraphDBClient):
    """Test that backup_system_data=False excludes user data."""
    result = client.recovery.backup(backup_system_data=False)

    assert isinstance(result, bytes)

    with tarfile.open(fileobj=io.BytesIO(result), mode="r:*") as tar:
        members = tar.getnames()
        assert not any(m.endswith("users.js") for m in members)


@pytest.mark.testcontainer
def test_backup_with_all_options_returns_complete_archive(client: GraphDBClient):
    """Test that backup with all options returns complete archive."""
    result = client.recovery.backup(
        repositories=["test-repo"],
        backup_system_data=True,
    )

    assert isinstance(result, bytes)

    with tarfile.open(fileobj=io.BytesIO(result), mode="r:*") as tar:
        members = tar.getnames()

        # Verify expected contents
        assert any("snapshot-metadata" in m for m in members)
        assert any("test-repo" in m for m in members)


@pytest.mark.testcontainer
def test_backup_streams_to_disk(client: GraphDBClient, tmp_path):
    """Test that backup streams to disk when dest is provided."""
    dest_file = tmp_path / "backup.tar"

    result = client.recovery.backup(dest=dest_file)

    assert result == dest_file
    assert dest_file.exists()
    assert dest_file.stat().st_size > 0


@pytest.mark.testcontainer
def test_backup_streams_valid_tar_to_disk(client: GraphDBClient, tmp_path):
    """Test that backup streams a valid tar archive to disk."""
    dest_file = tmp_path / "backup.tar"

    result = client.recovery.backup(dest=dest_file)

    # Verify the file is a valid tar archive
    with tarfile.open(result, mode="r:*") as tar:
        members = tar.getnames()
        assert len(members) > 0, "Tar archive should contain files"


@pytest.mark.testcontainer
def test_backup_streams_with_string_path(client: GraphDBClient, tmp_path):
    """Test that backup accepts string path for dest."""
    dest_file = tmp_path / "backup.tar"

    result = client.recovery.backup(dest=str(dest_file))

    assert result == dest_file
    assert dest_file.exists()


@pytest.mark.testcontainer
def test_backup_streams_to_directory_with_auto_filename(
    client: GraphDBClient, tmp_path
):
    """Test that backup uses filename from Content-Disposition when dest is a directory."""
    result = client.recovery.backup(dest=tmp_path)

    # Verify a file was created in the directory
    assert result.parent == tmp_path
    assert result.exists()

    # Verify the filename matches the expected pattern from Content-Disposition
    # Format: backup-YYYY-MM-DD-HH-MM-SS.tar
    assert result.name.startswith("backup-")
    assert result.name.endswith(".tar")

    # Verify it's a valid tar archive
    with tarfile.open(result, mode="r:*") as tar:
        members = tar.getnames()
        assert len(members) > 0


@pytest.mark.testcontainer
def test_backup_streams_to_directory_with_string_path(client: GraphDBClient, tmp_path):
    """Test that backup works with string directory path."""
    result = client.recovery.backup(dest=str(tmp_path))

    assert result.parent == tmp_path
    assert result.exists()
    assert result.name.startswith("backup-")
    assert result.name.endswith(".tar")


@pytest.mark.testcontainer
def test_backup_streams_with_all_options(client: GraphDBClient, tmp_path):
    """Test that backup streams correctly with all options."""
    dest_file = tmp_path / "backup.tar"

    result = client.recovery.backup(
        repositories=["test-repo"],
        backup_system_data=True,
        dest=dest_file,
    )

    assert dest_file.exists()

    with tarfile.open(result, mode="r:*") as tar:
        members = tar.getnames()
        # Verify expected contents
        assert any("test-repo" in m for m in members)


@pytest.mark.testcontainer
def test_backup_directory_vs_file_path_both_work(client: GraphDBClient, tmp_path):
    """Test that both directory and file paths work correctly."""
    # Test 1: Directory path (auto filename)
    dir_result = client.recovery.backup(dest=tmp_path)
    assert dir_result.parent == tmp_path
    assert dir_result.name.startswith("backup-")

    # Test 2: File path (explicit filename)
    file_path = tmp_path / "my-custom-backup.tar"
    file_result = client.recovery.backup(dest=file_path)
    assert file_result == file_path
    assert file_result.name == "my-custom-backup.tar"


@pytest.mark.testcontainer
def test_backup_bytes_and_stream_produce_same_structure(
    client: GraphDBClient, tmp_path
):
    """Test that bytes and streaming modes produce archives with same structure."""
    repo_id = "test-repo"
    # Get backup as bytes
    bytes_result = client.recovery.backup(repositories=[repo_id])

    # Get backup streamed to disk
    dest_file = tmp_path / "backup.tar"
    stream_result = client.recovery.backup(repositories=[repo_id], dest=dest_file)

    # Compare structures (not exact bytes, as timestamps may differ)
    with tarfile.open(fileobj=io.BytesIO(bytes_result), mode="r:*") as tar_bytes:
        bytes_members = set(tar_bytes.getnames())

    with tarfile.open(stream_result, mode="r:*") as tar_stream:
        stream_members = set(tar_stream.getnames())

    def _assert_contains_expected_repo_structure(members: set[str]) -> None:
        assert any("snapshot-metadata" in m for m in members)
        assert any(
            m.startswith(f"repositories/{repo_id}/") for m in members
        ), f"Expected repositories/{repo_id}/ entries in archive"
        assert any(
            f"{repo_id}-repository-metadata" in m for m in members
        ), "Expected repository metadata in archive"

    _assert_contains_expected_repo_structure(bytes_members)
    _assert_contains_expected_repo_structure(stream_members)
