from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import ResponseFormatError
from rdflib.contrib.graphdb.models import RepositorySizeInfo
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import (
        GraphDBClient,
    )


def test_size_with_location_parameter(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that the location parameter is correctly passed to the GraphDB API."""
    mock_response = Mock(
        spec=httpx.Response, json=lambda: {"inferred": 0, "total": 0, "explicit": 0}
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    client.graphdb_repositories.size("test-repo", location="http://example.com/location")
    mock_httpx_get.assert_called_once_with(
        "/rest/repositories/test-repo/size",
        params={"location": "http://example.com/location"},
    )


@pytest.mark.parametrize(
    "response_value, expected_parsed_value",
    [
        [{"inferred": 0, "total": 0, "explicit": 0}, RepositorySizeInfo(0, 0, 0)],
        [
            {"inferred": 1, "total": 123, "explicit": 122},
            RepositorySizeInfo(1, 123, 122),
        ],
        [{"inferred": 1, "total": 123, "explicit": "122"}, ResponseFormatError],
        [{"inferred": 1, "explicit": 122}, ResponseFormatError],
    ],
)
def test_size_values(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    response_value: str,
    expected_parsed_value: RepositorySizeInfo | type[ResponseFormatError],
):
    """Test that the return value of the response is correctly parsed."""
    mock_response = Mock(spec=httpx.Response, json=lambda: response_value)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    if isinstance(expected_parsed_value, RepositorySizeInfo):
        size = client.graphdb_repositories.size("test-repo")
        assert size == expected_parsed_value
    else:
        with pytest.raises(expected_parsed_value):
            client.graphdb_repositories.size("test-repo")

    mock_httpx_get.assert_called_once_with(
        "/rest/repositories/test-repo/size",
        params={},
    )
