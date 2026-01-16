"""Unit tests for RecoveryManagement.restore method."""

from __future__ import annotations

import io
import json
import pathlib
from unittest.mock import ANY, Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
    ForbiddenError,
    UnauthorisedError,
)
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import GraphDBClient


def test_restore_uploads_bytes_backup(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    backup_content = b"tar archive content here"
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.recovery.restore(backup_content)

    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/restore",
        files=[
            ("params", (None, "{}", "application/json")),
            ("file", ("graphdb-backup.tar", backup_content, "application/x-tar")),
        ],
    )


def test_restore_uploads_file_like_backup(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    backup_file = io.BytesIO(b"tar archive content here")
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.recovery.restore(backup_file)

    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/restore",
        files=[
            ("params", (None, "{}", "application/json")),
            ("file", ("graphdb-backup.tar", backup_file, "application/x-tar")),
        ],
    )


def test_restore_uploads_path_backup(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    backup_path = tmp_path / "backup.tar"
    backup_path.write_bytes(b"tar bytes")

    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.recovery.restore(backup_path)

    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/restore",
        files=[
            ("params", (None, "{}", "application/json")),
            ("file", ("backup.tar", ANY, "application/x-tar")),
        ],
    )

    # Ensure file handle opened by restore() is closed after the request is built.
    file_obj = mock_httpx_post.call_args.kwargs["files"][1][1][1]
    assert hasattr(file_obj, "read")
    assert file_obj.closed is True


@pytest.mark.parametrize(
    "kwargs, expected_payload",
    [
        ({"repositories": ["repo1"]}, {"repositories": ["repo1"]}),
        ({"repositories": []}, {"repositories": []}),
        ({"restore_system_data": True}, {"restoreSystemData": True}),
        (
            {"remove_stale_repositories": True},
            {"removeStaleRepositories": True},
        ),
        (
            {
                "repositories": ["repo1"],
                "restore_system_data": True,
                "remove_stale_repositories": True,
            },
            {
                "repositories": ["repo1"],
                "restoreSystemData": True,
                "removeStaleRepositories": True,
            },
        ),
    ],
)
def test_restore_sends_params_combinations_as_json(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    kwargs: dict[str, object],
    expected_payload: dict[str, object],
):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.recovery.restore(b"tar", **kwargs)

    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/restore",
        files=[
            ("params", (None, json.dumps(expected_payload), "application/json")),
            ("file", ("graphdb-backup.tar", b"tar", "application/x-tar")),
        ],
    )


@pytest.mark.parametrize(
    "status_code, exception_class, match_message",
    [
        (400, BadRequestError, "Bad request"),
        (401, UnauthorisedError, "Request is unauthorised"),
        (403, ForbiddenError, "Request is forbidden"),
    ],
)
def test_restore_raises_exceptions_for_error_status_codes(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type,
    match_message: str,
):
    mock_response = Mock(
        spec=httpx.Response,
        status_code=status_code,
        text="Server error message",
    )
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(exception_class, match=match_message):
        client.recovery.restore(b"tar")


@pytest.mark.parametrize("status_code", [404, 500, 502, 503])
def test_restore_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    mock_response = Mock(
        spec=httpx.Response,
        status_code=status_code,
        text="Error",
    )
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(httpx.HTTPStatusError):
        client.recovery.restore(b"tar")


def test_restore_validates_params_type(
    client: GraphDBClient,
):
    with pytest.raises(ValueError, match="repositories must be a list or None"):
        client.recovery.restore(b"tar", repositories="nope")  # type: ignore[arg-type]


def test_restore_validates_repositories_list_items(
    client: GraphDBClient,
):
    with pytest.raises(ValueError, match="repositories must be a list of strings"):
        client.recovery.restore(b"tar", repositories=["repo1", 123])  # type: ignore[list-item]


def test_restore_validates_restore_system_data_type(
    client: GraphDBClient,
):
    with pytest.raises(ValueError, match="restore_system_data must be a bool or None"):
        client.recovery.restore(b"tar", restore_system_data="nope")  # type: ignore[arg-type]


def test_restore_validates_remove_stale_repositories_type(
    client: GraphDBClient,
):
    with pytest.raises(
        ValueError, match="remove_stale_repositories must be a bool or None"
    ):
        client.recovery.restore(  # type: ignore[arg-type]
            b"tar", remove_stale_repositories="nope"
        )


def test_restore_validates_backup_type(
    client: GraphDBClient,
):
    with pytest.raises(ValueError, match="backup must be"):
        client.recovery.restore(object())  # type: ignore[arg-type]
