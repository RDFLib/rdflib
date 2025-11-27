from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient


@pytest.fixture(scope="function")
def client(monkeypatch: pytest.MonkeyPatch, request):
    monkeypatch.setattr(GraphDBClient, "protocol", 12)
    with GraphDBClient("http://localhost/", auth=("admin", "admin")) as client:
        yield client
