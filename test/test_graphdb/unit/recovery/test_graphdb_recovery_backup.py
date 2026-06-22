"""Unit tests for RecoveryManagement.backup method."""

from __future__ import annotations

import pathlib
from unittest.mock import MagicMock, Mock

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


def test_backup_returns_bytes_when_dest_is_none(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup returns bytes when dest is None."""
    backup_content = b"tar archive content here"
    mock_response = Mock(spec=httpx.Response, content=backup_content)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    result = client.recovery.backup()

    assert isinstance(result, bytes)
    assert result == backup_content
    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/backup",
        json={},
    )


def test_backup_with_repositories_param(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup passes repositories parameter correctly."""
    backup_content = b"tar archive content"
    mock_response = Mock(spec=httpx.Response, content=backup_content)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    result = client.recovery.backup(repositories=["repo1", "repo2"])

    assert result == backup_content
    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/backup",
        json={"repositories": ["repo1", "repo2"]},
    )


def test_backup_with_system_data_param(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup passes backup_system_data parameter correctly."""
    backup_content = b"tar archive content"
    mock_response = Mock(spec=httpx.Response, content=backup_content)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    result = client.recovery.backup(backup_system_data=True)

    assert result == backup_content
    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/backup",
        json={"backupSystemData": True},
    )


def test_backup_with_all_params(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup passes all parameters correctly."""
    backup_content = b"tar archive content"
    mock_response = Mock(spec=httpx.Response, content=backup_content)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    result = client.recovery.backup(
        repositories=["repo1"],
        backup_system_data=False,
    )

    assert result == backup_content
    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/backup",
        json={"repositories": ["repo1"], "backupSystemData": False},
    )


def test_backup_streams_to_disk_when_dest_provided(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    """Test that backup streams response to disk when dest is provided."""
    backup_content = b"tar archive content for streaming"
    dest_file = tmp_path / "backup.tar"

    # Create a mock context manager for stream
    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [backup_content]
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)

    mock_stream = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "stream", mock_stream)

    result = client.recovery.backup(dest=dest_file)

    assert result == dest_file
    assert dest_file.read_bytes() == backup_content
    mock_stream.assert_called_once_with(
        "POST",
        "/rest/recovery/backup",
        json={},
    )


def test_backup_streams_to_directory_uses_content_disposition_filename(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    """Test that backup uses filename from Content-Disposition when dest is a directory."""
    backup_content = b"tar archive content for streaming"

    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [backup_content]
    mock_response.headers = {"Content-Disposition": "attachment; filename=backup.tar"}
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)

    mock_stream = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "stream", mock_stream)

    result = client.recovery.backup(dest=tmp_path)

    expected_path = tmp_path / "backup.tar"
    assert result == expected_path
    assert expected_path.read_bytes() == backup_content


def test_backup_streams_to_directory_sanitizes_content_disposition_filename(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    """Test that backup prevents path traversal via Content-Disposition filename."""
    backup_content = b"content"

    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [backup_content]
    mock_response.headers = {
        "Content-Disposition": "attachment; filename=../../evil.tar"
    }
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)

    mock_stream = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "stream", mock_stream)

    result = client.recovery.backup(dest=tmp_path)

    expected_path = tmp_path / "evil.tar"
    assert result == expected_path
    assert expected_path.read_bytes() == backup_content


def test_backup_streams_to_directory_prefers_filename_star(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    """Test that backup prefers filename*= over filename= when present."""
    backup_content = b"content"

    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [backup_content]
    mock_response.headers = {
        "Content-Disposition": "attachment; filename=plain.tar; filename*=UTF-8''preferred.tar"
    }
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)

    mock_stream = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "stream", mock_stream)

    result = client.recovery.backup(dest=tmp_path)

    expected_path = tmp_path / "preferred.tar"
    assert result == expected_path
    assert expected_path.read_bytes() == backup_content


def test_backup_streams_to_directory_falls_back_to_default_filename_when_missing_header(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    """Test that backup uses a default name when Content-Disposition is missing."""
    backup_content = b"content"

    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [backup_content]
    mock_response.headers = {}
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)

    mock_stream = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "stream", mock_stream)

    result = client.recovery.backup(dest=tmp_path)

    expected_path = tmp_path / "graphdb-backup.tar"
    assert result == expected_path
    assert expected_path.read_bytes() == backup_content


def test_backup_streams_to_disk_with_string_path(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    """Test that backup accepts string path for dest."""
    backup_content = b"tar archive content"
    dest_file = tmp_path / "backup.tar"

    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [backup_content]
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)

    mock_stream = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "stream", mock_stream)

    result = client.recovery.backup(dest=str(dest_file))

    assert isinstance(result, pathlib.Path)
    assert result == dest_file
    assert dest_file.read_bytes() == backup_content


def test_backup_streams_chunked_content(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    """Test that backup correctly writes chunked stream to disk."""
    chunk1 = b"chunk1"
    chunk2 = b"chunk2"
    chunk3 = b"chunk3"
    dest_file = tmp_path / "backup.tar"

    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [chunk1, chunk2, chunk3]
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)

    mock_stream = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "stream", mock_stream)

    result = client.recovery.backup(dest=dest_file)

    assert dest_file.read_bytes() == chunk1 + chunk2 + chunk3
    assert result == dest_file


def test_backup_streams_with_all_params(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    """Test that backup passes all parameters when streaming to disk."""
    dest_file = tmp_path / "backup.tar"

    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [b"content"]
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)

    mock_stream = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "stream", mock_stream)

    client.recovery.backup(
        repositories=["repo1", "repo2"],
        backup_system_data=True,
        dest=dest_file,
    )

    mock_stream.assert_called_once_with(
        "POST",
        "/rest/recovery/backup",
        json={"repositories": ["repo1", "repo2"], "backupSystemData": True},
    )


@pytest.mark.parametrize(
    "invalid_repos",
    [
        "not a list",
        123,
        {"key": "value"},
        ("tuple",),
    ],
)
def test_backup_raises_value_error_for_invalid_repositories(
    client: GraphDBClient,
    invalid_repos,
):
    """Test that backup raises ValueError when repositories is not a list or None."""
    with pytest.raises(ValueError, match="repositories must be a list or None"):
        client.recovery.backup(repositories=invalid_repos)


def test_backup_raises_value_error_for_non_string_repository_ids(client: GraphDBClient):
    """Test that backup raises ValueError when repositories contains non-strings."""
    with pytest.raises(ValueError, match="repositories must be a list of strings"):
        client.recovery.backup(repositories=["repo1", 123])  # type: ignore[list-item]


@pytest.mark.parametrize(
    "invalid_system_data",
    [
        "true",
        1,
        0,
        "false",
        [],
    ],
)
def test_backup_raises_value_error_for_invalid_backup_system_data(
    client: GraphDBClient,
    invalid_system_data,
):
    """Test that backup raises ValueError when backup_system_data is not a bool or None."""
    with pytest.raises(ValueError, match="backup_system_data must be a bool"):
        client.recovery.backup(backup_system_data=invalid_system_data)


@pytest.mark.parametrize(
    "status_code, exception_class, match_message",
    [
        (400, BadRequestError, "Bad request"),
        (401, UnauthorisedError, "Request is unauthorised"),
        (403, ForbiddenError, "Request is forbidden"),
    ],
)
def test_backup_bytes_raises_exceptions_for_error_status_codes(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type,
    match_message: str,
):
    """Test that backup raises appropriate exceptions for error responses in bytes mode."""
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
        client.recovery.backup()


@pytest.mark.parametrize(
    "status_code",
    [404, 500, 502, 503],
)
def test_backup_bytes_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that backup re-raises HTTPStatusError for unhandled status codes in bytes mode."""
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
        client.recovery.backup()


@pytest.mark.parametrize(
    "status_code, exception_class, match_message",
    [
        (400, BadRequestError, "Bad request"),
        (401, UnauthorisedError, "Request is unauthorised"),
        (403, ForbiddenError, "Request is forbidden"),
    ],
)
def test_backup_stream_raises_exceptions_for_error_status_codes(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
    status_code: int,
    exception_class: type,
    match_message: str,
):
    """Test that backup raises appropriate exceptions for error responses in stream mode."""
    dest_file = tmp_path / "backup.tar"

    mock_response = MagicMock(
        status_code=status_code,
        text="Server error message",
    )
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)

    mock_stream = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "stream", mock_stream)

    with pytest.raises(exception_class, match=match_message):
        client.recovery.backup(dest=dest_file)


@pytest.mark.parametrize(
    "status_code",
    [404, 500, 502, 503],
)
def test_backup_stream_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
    status_code: int,
):
    """Test that backup re-raises HTTPStatusError for unhandled status codes in stream mode."""
    dest_file = tmp_path / "backup.tar"

    mock_response = MagicMock(
        status_code=status_code,
        text="Error",
    )
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)

    mock_stream = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "stream", mock_stream)

    with pytest.raises(httpx.HTTPStatusError):
        client.recovery.backup(dest=dest_file)
