"""End-to-end tests for RecoveryManagement.restore method.

These tests verify the GraphDB POST /rest/recovery/restore endpoint accepts a
backup tar produced by RecoveryManagement.backup and restores repository data.
"""

from __future__ import annotations

import pathlib
import time

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.rdf4j.exceptions import RepositoryNotFoundError

    from rdflib.contrib.graphdb import GraphDBClient


def _wait_for(
    check,
    *,
    timeout_s: float = 30.0,
    interval_s: float = 0.5,
    description: str = "condition",
):
    start = time.monotonic()
    last_exc: Exception | None = None
    while time.monotonic() - start < timeout_s:
        try:
            if check():
                return
        except Exception as exc:  # noqa: BLE001 - used to make e2e polling robust
            last_exc = exc
        time.sleep(interval_s)
    if last_exc is not None:
        raise AssertionError(f"Timed out waiting for {description}: {last_exc}") from last_exc
    raise AssertionError(f"Timed out waiting for {description}")


@pytest.mark.testcontainer
def test_restore_bytes_roundtrips_repository_data(client: GraphDBClient):
    repo_id = "test-repo"
    repo = client.repositories.get(repo_id)

    ask_query = 'ASK { <http://example/s> <http://example/p> "o" }'
    repo.update('INSERT DATA { <http://example/s> <http://example/p> "o" . }')
    assert repo.size() >= 1
    assert repo.query(ask_query).askAnswer is True

    backup_bytes = client.recovery.backup(repositories=[repo_id])

    repo.update("CLEAR ALL")
    _wait_for(lambda: repo.size() == 0, description="repository to be cleared")
    assert repo.query(ask_query).askAnswer is False

    client.recovery.restore(backup_bytes, repositories=[repo_id])

    def _restored() -> bool:
        restored_repo = client.repositories.get(repo_id)
        return restored_repo.size() >= 1 and restored_repo.query(ask_query).askAnswer is True

    _wait_for(_restored, description="repository data to be restored")


@pytest.mark.testcontainer
def test_restore_path_roundtrips_repository_data(
    client: GraphDBClient,
    tmp_path: pathlib.Path,
):
    repo_id = "test-repo"
    repo = client.repositories.get(repo_id)

    ask_query = 'ASK { <http://example/s2> <http://example/p2> "o2" }'
    repo.update('INSERT DATA { <http://example/s2> <http://example/p2> "o2" . }')
    assert repo.query(ask_query).askAnswer is True

    backup_bytes = client.recovery.backup(repositories=[repo_id])
    backup_path = tmp_path / "backup.tar"
    backup_path.write_bytes(backup_bytes)

    repo.update("CLEAR ALL")
    _wait_for(lambda: repo.size() == 0, description="repository to be cleared")
    assert repo.query(ask_query).askAnswer is False

    client.recovery.restore(backup_path, repositories=[repo_id])

    def _restored() -> bool:
        restored_repo = client.repositories.get(repo_id)
        return restored_repo.query(ask_query).askAnswer is True

    _wait_for(_restored, description="repository data to be restored")


@pytest.mark.testcontainer
def test_restore_remove_stale_repositories_removes_unrestored_repo(
    client: GraphDBClient,
):
    repo_id = "test-repo"
    extra_repo_id = "test-repo-stale"
    config_path = (
        pathlib.Path(__file__).parent.parent
        / "repo-configs"
        / "test-graphdb-repo-config.ttl"
    )
    ttl_config = config_path.read_text().replace(repo_id, extra_repo_id)

    try:
        client.repositories.create(extra_repo_id, ttl_config)
        assert extra_repo_id in {r.id for r in client.repos.list()}

        backup_bytes = client.recovery.backup(repositories=[repo_id])
        client.recovery.restore(
            backup_bytes,
            repositories=[repo_id],
            remove_stale_repositories=True,
        )

        _wait_for(
            lambda: extra_repo_id not in {r.id for r in client.repos.list()},
            description="stale repository to be removed",
        )

        with pytest.raises(RepositoryNotFoundError):
            client.repos.get(extra_repo_id)
    finally:
        try:
            client.repositories.delete(extra_repo_id)
        except (RepositoryNotFoundError, RuntimeError):
            pass

