from __future__ import annotations

from unittest.mock import Mock

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


def test_truncate_log_success(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that truncate_log succeeds with a 200 response."""
    mock_response = Mock(spec=httpx.Response, status_code=200)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    # Should not raise any exception
    client.cluster.truncate_log()

    mock_httpx_post.assert_called_once_with("/rest/cluster/truncate-log")
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        (400, BadRequestError),
        (401, UnauthorisedError),
        (403, ForbiddenError),
    ],
)
def test_truncate_log_raises_expected_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type[Exception],
):
    """Test that truncate_log raises appropriate exceptions for documented error responses."""
    mock_response = Mock(
        spec=httpx.Response, status_code=status_code, text="Error message"
    )
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(exception_class):
        client.cluster.truncate_log()

    mock_httpx_post.assert_called_once_with("/rest/cluster/truncate-log")


@pytest.mark.parametrize(
    "status_code",
    [404, 409, 500, 503],
)
def test_truncate_log_reraises_unexpected_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that truncate_log re-raises HTTPStatusError for undocumented status codes."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(httpx.HTTPStatusError):
        client.cluster.truncate_log()

    mock_httpx_post.assert_called_once_with("/rest/cluster/truncate-log")
