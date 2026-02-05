from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    ForbiddenError,
    GraphDBError,
    RepositoryNotFoundError,
    UnauthorisedError,
)
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import (
        GraphDBClient,
    )


def test_restart_sync_with_location_parameter(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that the sync and location parameter is correctly passed to the GraphDB API."""
    mock_response = Mock(spec=httpx.Response, text="")
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)
    client.graphdb_repositories.restart("test-repo", sync=True, location="http://example.com/location")
    mock_httpx_post.assert_called_once_with(
        "/rest/repositories/test-repo/restart",
        params={"sync": "true", "location": "http://example.com/location"},
    )


@pytest.mark.parametrize(
    "response_code, exception_class",
    [
        (200, None),
        (202, None),
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (404, RepositoryNotFoundError),
    ],
)
def test_restart_exceptions(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    response_code: int,
    exception_class: type[GraphDBError] | None,
):
    mock_response = Mock(spec=httpx.Response, status_code=response_code)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)
    if exception_class is not None:
        mock_response.raise_for_status.side_effect = exception_class("Mocked exception")
        with pytest.raises(exception_class):
            client.graphdb_repositories.restart("test-repo")


def test_restart_response_text(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response, text="some-result")
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)
    result = client.graphdb_repositories.restart("test-repo")
    assert result == "some-result"
