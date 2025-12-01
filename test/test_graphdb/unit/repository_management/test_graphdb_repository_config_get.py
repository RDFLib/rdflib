from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    GraphDBError,
    InternalServerError,
    RepositoryNotFoundError,
    ResponseFormatError,
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


@pytest.mark.parametrize(
    "content_type, expected_exception",
    [
        ("application/json", None),
        ("text/turtle", None),
        ("application/rdf+xml", ValueError),
        (None, None),
    ],
)
def test_repo_config_headers_and_parameters(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    content_type: str | None,
    expected_exception: type[GraphDBError] | None,
):
    mock_response = Mock(spec=httpx.Response, text="", json=lambda: {})
    mock_response.headers = {}
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    if expected_exception is None:
        client.repos.get(
            "test-repo",
            content_type=content_type,
            location="http://example.com/location",
        )

        if content_type is None:
            mock_httpx_get.assert_called_once_with(
                "/rest/repositories/test-repo",
                headers={"Accept": "application/json"},
                params={"location": "http://example.com/location"},
            )
        else:
            mock_httpx_get.assert_called_once_with(
                "/rest/repositories/test-repo",
                headers={"Accept": content_type},
                params={"location": "http://example.com/location"},
            )
    else:
        with pytest.raises(expected_exception):
            client.repos.get(
                "test-repo",
                content_type=content_type,
                location="http://example.com/location",
            )


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        [404, RepositoryNotFoundError],
        [500, InternalServerError],
    ],
)
def test_repo_config_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type[GraphDBError],
):
    mock_response = Mock(spec=httpx.Response, status_code=status_code)
    mock_httpx_get = Mock(return_value=mock_response)
    mock_response.raise_for_status.side_effect = exception_class("Mocked exception")
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    with pytest.raises(exception_class):
        client.repos.get("test-repo")


@pytest.mark.parametrize(
    "content_type, response_text, exception_class, exception_text",
    [
        [
            "application/json",
            "{}",
            ResponseFormatError,
            "Failed to parse GraphDB response.",
        ],
        [
            "text/turtle",
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
            ResponseFormatError,
            "Error parsing RDF:",
        ],
    ],
)
def test_repo_config_response_text_exceptions(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    content_type: str,
    response_text: str,
    exception_class: type[GraphDBError],
    exception_text: str,
):
    mock_response = Mock(spec=httpx.Response, text=response_text)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    with pytest.raises(exception_class, match=exception_text):
        client.repos.get("test-repo", content_type=content_type)
