from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
    ForbiddenError,
    PreconditionFailedError,
    UnauthorisedError,
)
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import GraphDBClient


def test_replace_nodes_patches_payload_and_returns_none(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response, status_code=200)
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    client.cluster.replace_nodes(
        add_nodes=["http://node2:7200"],
        remove_nodes=["http://node1:7200"],
    )

    mock_httpx_patch.assert_called_once_with(
        "/rest/cluster/config/node",
        json={"removeNodes": ["http://node1:7200"], "addNodes": ["http://node2:7200"]},
    )
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        (400, BadRequestError),
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (412, PreconditionFailedError),
    ],
)
def test_replace_nodes_raises_expected_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type[Exception],
):
    mock_response = Mock(
        spec=httpx.Response, status_code=status_code, text="Error message"
    )
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(exception_class):
        client.cluster.replace_nodes(
            add_nodes=["http://node2:7200"],
            remove_nodes=["http://node1:7200"],
        )


@pytest.mark.parametrize("status_code", [404, 409, 500, 503])
def test_replace_nodes_reraises_unexpected_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(httpx.HTTPStatusError):
        client.cluster.replace_nodes(
            add_nodes=["http://node2:7200"],
            remove_nodes=["http://node1:7200"],
        )


@pytest.mark.parametrize(
    "add_nodes, remove_nodes, expected_message",
    [
        (
            "http://node2:7200",
            ["http://node1:7200"],
            "add_nodes must be a list\\[str\\]",
        ),
        ([1, 2, 3], ["http://node1:7200"], "add_nodes must be a list\\[str\\]"),
        (
            ["http://node2:7200"],
            "http://node1:7200",
            "remove_nodes must be a list\\[str\\]",
        ),
        (["http://node2:7200"], [1, 2, 3], "remove_nodes must be a list\\[str\\]"),
    ],
)
def test_replace_nodes_validates_nodes_types(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    add_nodes,
    remove_nodes,
    expected_message: str,
):
    mock_httpx_patch = Mock()
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(TypeError, match=expected_message):
        client.cluster.replace_nodes(add_nodes=add_nodes, remove_nodes=remove_nodes)

    mock_httpx_patch.assert_not_called()
