from __future__ import annotations

import io
import json
import pathlib
import typing as t
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


class _CloudRestoreKwargs(t.TypedDict, total=False):
    repositories: list[str]
    restore_system_data: bool
    remove_stale_repositories: bool


def test_cloud_restore_sends_bucket_uri(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    params_part = (
        None,
        json.dumps({"bucketUri": "s3:///bucket/backup-name"}),
        "application/json",
    )
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.recovery.cloud_restore("s3:///bucket/backup-name")

    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/cloud-restore",
        headers={"Accept": "application/json"},
        files=[("params", params_part)],
    )


@pytest.mark.parametrize(
    "kwargs, expected_payload",
    [
        (
            {"repositories": ["repo1", "repo2"]},
            {"repositories": ["repo1", "repo2"], "bucketUri": "gs://bucket/backup"},
        ),
        (
            {"repositories": []},
            {"repositories": [], "bucketUri": "gs://bucket/backup"},
        ),
        (
            {"restore_system_data": True},
            {"restoreSystemData": True, "bucketUri": "gs://bucket/backup"},
        ),
        (
            {"remove_stale_repositories": True},
            {"removeStaleRepositories": True, "bucketUri": "gs://bucket/backup"},
        ),
        (
            {
                "repositories": ["repo1"],
                "restore_system_data": True,
                "remove_stale_repositories": False,
            },
            {
                "repositories": ["repo1"],
                "restoreSystemData": True,
                "removeStaleRepositories": False,
                "bucketUri": "gs://bucket/backup",
            },
        ),
    ],
)
def test_cloud_restore_sends_params_combinations_as_json(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    kwargs: _CloudRestoreKwargs,
    expected_payload: dict[str, object],
):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.recovery.cloud_restore("gs://bucket/backup", **kwargs)

    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/cloud-restore",
        headers={"Accept": "application/json"},
        files=[("params", (None, json.dumps(expected_payload), "application/json"))],
    )


def test_cloud_restore_uploads_authentication_file_bytes(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    params_part = (
        None,
        json.dumps({"bucketUri": "gs://bucket/backup"}),
        "application/json",
    )
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.recovery.cloud_restore(
        "gs://bucket/backup",
        authentication_file=b'{"type":"service_account"}',
    )

    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/cloud-restore",
        headers={"Accept": "application/json"},
        files=[
            ("params", params_part),
            (
                "authenticationFile",
                (
                    "authentication-file",
                    b'{"type":"service_account"}',
                    "application/octet-stream",
                ),
            ),
        ],
    )


def test_cloud_restore_uploads_authentication_file_like(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    params_part = (
        None,
        json.dumps({"bucketUri": "gs://bucket/backup"}),
        "application/json",
    )
    auth_file = io.BytesIO(b"creds")
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.recovery.cloud_restore(
        "gs://bucket/backup",
        authentication_file=auth_file,
    )

    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/cloud-restore",
        headers={"Accept": "application/json"},
        files=[
            ("params", params_part),
            (
                "authenticationFile",
                ("authentication-file", auth_file, "application/octet-stream"),
            ),
        ],
    )


def test_cloud_restore_uploads_authentication_file_path(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
):
    params_part = (
        None,
        json.dumps({"bucketUri": "gs://bucket/backup"}),
        "application/json",
    )
    auth_path = tmp_path / "google-credentials.json"
    auth_path.write_bytes(b"creds")

    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.recovery.cloud_restore(
        "gs://bucket/backup",
        authentication_file=auth_path,
    )

    mock_httpx_post.assert_called_once_with(
        "/rest/recovery/cloud-restore",
        headers={"Accept": "application/json"},
        files=[
            ("params", params_part),
            (
                "authenticationFile",
                ("google-credentials.json", ANY, "application/octet-stream"),
            ),
        ],
    )

    file_obj = mock_httpx_post.call_args.kwargs["files"][1][1][1]
    assert hasattr(file_obj, "read")
    assert file_obj.closed is True


@pytest.mark.parametrize(
    "invalid_bucket_uri",
    [
        "",
        None,
        123,
    ],
)
def test_cloud_restore_validates_bucket_uri(
    client: GraphDBClient,
    invalid_bucket_uri,
):
    with pytest.raises(ValueError, match="bucket_uri must be a non-empty string"):
        client.recovery.cloud_restore(invalid_bucket_uri)


@pytest.mark.parametrize(
    "invalid_repos",
    [
        "not a list",
        123,
        {"key": "value"},
        ("tuple",),
    ],
)
def test_cloud_restore_raises_value_error_for_invalid_repositories(
    client: GraphDBClient,
    invalid_repos,
):
    with pytest.raises(ValueError, match="repositories must be a list or None"):
        client.recovery.cloud_restore("gs://bucket/backup", repositories=invalid_repos)


def test_cloud_restore_raises_value_error_for_non_string_repository_ids(
    client: GraphDBClient,
):
    with pytest.raises(ValueError, match="repositories must be a list of strings"):
        client.recovery.cloud_restore(
            "gs://bucket/backup", repositories=["repo1", 123]  # type: ignore[list-item]
        )


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
def test_cloud_restore_raises_value_error_for_invalid_restore_system_data(
    client: GraphDBClient,
    invalid_system_data,
):
    with pytest.raises(ValueError, match="restore_system_data must be a bool or None"):
        client.recovery.cloud_restore(
            "gs://bucket/backup",
            restore_system_data=invalid_system_data,
        )


@pytest.mark.parametrize(
    "invalid_remove_stale",
    [
        "true",
        1,
        0,
        "false",
        [],
    ],
)
def test_cloud_restore_raises_value_error_for_invalid_remove_stale_repositories(
    client: GraphDBClient,
    invalid_remove_stale,
):
    with pytest.raises(
        ValueError, match="remove_stale_repositories must be a bool or None"
    ):
        client.recovery.cloud_restore(
            "gs://bucket/backup",
            remove_stale_repositories=invalid_remove_stale,
        )


def test_cloud_restore_validates_authentication_file_type(client: GraphDBClient):
    with pytest.raises(ValueError, match="authentication_file must be"):
        client.recovery.cloud_restore(
            "gs://bucket/backup",
            authentication_file=object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "status_code, exception_class, match_message",
    [
        (400, BadRequestError, "Bad request"),
        (401, UnauthorisedError, "Request is unauthorised"),
        (403, ForbiddenError, "Request is forbidden"),
    ],
)
def test_cloud_restore_raises_exceptions_for_error_status_codes(
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
        client.recovery.cloud_restore("gs://bucket/backup")


@pytest.mark.parametrize("status_code", [404, 500, 502, 503])
def test_cloud_restore_reraises_other_http_errors(
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
        client.recovery.cloud_restore("gs://bucket/backup")
