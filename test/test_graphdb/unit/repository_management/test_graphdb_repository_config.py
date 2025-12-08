from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
    ForbiddenError,
    GraphDBError,
    InternalServerError,
    RepositoryNotFoundError,
    ResponseFormatError,
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
    from rdflib.contrib.graphdb.models import (
        RepositoryConfigBeanCreate,
    )


@pytest.mark.parametrize(
    "content_type, expected_exception",
    [
        ("application/json", ResponseFormatError),
        ("text/turtle", None),
        ("application/rdf+xml", ValueError),
        (None, ResponseFormatError),
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


def test_repo_config_edit_headers_and_parameters(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that the edit method correctly passes headers and json parameter."""
    mock_response = Mock(spec=httpx.Response, status_code=200)
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    config = RepositoryConfigBeanCreate(
        id="test-repo",
        title="Test Repository",
        type="graphdb:FreeSailRepository",
        sesameType="graphdb:FreeSailRepository",
        location="",
    )

    client.repos.edit("test-repo", config)

    mock_httpx_put.assert_called_once_with(
        "/rest/repositories/test-repo",
        headers={"Content-Type": "application/json"},
        json=config.to_dict(),
    )


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        [400, BadRequestError],
        [401, UnauthorisedError],
        [403, ForbiddenError],
        [500, InternalServerError],
    ],
)
def test_repo_config_edit_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type[GraphDBError],
):
    """Test that the edit method raises the correct exceptions for different status codes."""
    mock_response = Mock(
        spec=httpx.Response, status_code=status_code, text="Error message"
    )
    mock_httpx_put = Mock(return_value=mock_response)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Request failed", request=Mock(), response=mock_response
    )
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    config = RepositoryConfigBeanCreate(
        id="test-repo",
        title="Test Repository",
        type="graphdb:FreeSailRepository",
        sesameType="graphdb:FreeSailRepository",
        location="",
    )

    with pytest.raises(exception_class):
        client.repos.edit("test-repo", config)


@pytest.mark.parametrize(
    "location, expected_params",
    [
        (None, {}),
        ("http://example.com/location", {"location": "http://example.com/location"}),
    ],
)
def test_repo_config_delete_parameters(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    location: str | None,
    expected_params: dict,
):
    """Test that delete passes the correct params to the GraphDB API."""
    mock_response = Mock(spec=httpx.Response, status_code=204)
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    client.repos.delete("test-repo", location=location)

    mock_httpx_delete.assert_called_once_with(
        "/rest/repositories/test-repo",
        params=expected_params,
    )


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        [400, BadRequestError],
        [401, UnauthorisedError],
        [403, ForbiddenError],
        [500, InternalServerError],
    ],
)
def test_repo_config_delete_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type[GraphDBError],
):
    """Test that delete raises the correct exceptions for different status codes."""
    mock_response = Mock(
        spec=httpx.Response, status_code=status_code, text="Error message"
    )
    mock_httpx_delete = Mock(return_value=mock_response)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Request failed", request=Mock(), response=mock_response
    )
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(exception_class):
        client.repos.delete("test-repo")


@pytest.mark.parametrize(
    "location, expected_params",
    [
        (None, {}),
        ("http://example.com/location", {"location": "http://example.com/location"}),
    ],
)
def test_repo_list_parameters(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    location: str | None,
    expected_params: dict,
):
    """Test that list passes the correct params to the GraphDB API."""
    mock_response = Mock(
        spec=httpx.Response, status_code=200, json=Mock(return_value=[])
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    client.repos.list(location=location)

    mock_httpx_get.assert_called_once_with(
        "/rest/repositories",
        params=expected_params,
    )


def test_repo_list_parses_response(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that list parses repository data into GraphDBRepository objects."""
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        json=Mock(
            return_value=[
                {
                    "id": "repo1",
                    "title": "Repo 1",
                    "type": "graphdb:FreeSailRepository",
                    "sesameType": "graphdb:FreeSailRepository",
                    "location": "",
                }
            ]
        ),
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repos = client.repos.list()

    assert len(repos) == 1
    assert repos[0].id == "repo1"


def test_repo_list_parse_error_raises_response_format_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that list raises ResponseFormatError on JSON parse issues."""
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        json=Mock(side_effect=ValueError("bad json")),
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError):
        client.repos.list()


def test_repo_list_internal_server_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that list propagates HTTPStatusError for server errors."""
    mock_response = Mock(
        spec=httpx.Response,
        status_code=500,
        text="server error",
    )
    mock_httpx_get = Mock(return_value=mock_response)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Request failed", request=Mock(), response=mock_response
    )
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(httpx.HTTPStatusError):
        client.repos.list()
