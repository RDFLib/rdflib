from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest

from rdflib.contrib.graphdb import GraphDBClient


def test_ttyg(client: GraphDBClient, monkeypatch: pytest.MonkeyPatch):
    mock_response = Mock(spec=httpx.Response, text="some-result")
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)
    result = client.ttyg.query("agent-id", "test-tool", "query")
    assert result == "some-result"
    headers = {
        "Content-Type": "text/plain",
        "Accept": "text/plain",
    }
    mock_httpx_post.assert_called_once_with(
        "/rest/ttyg/agents/agent-id/test-tool", headers=headers, content="query"
    )
