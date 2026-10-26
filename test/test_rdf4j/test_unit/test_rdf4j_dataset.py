from __future__ import annotations

from collections.abc import Callable

import pytest

from rdflib import Dataset
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.plugins.stores.rdf4j import RDF4JStore


@pytest.mark.parametrize("measure", [len, bool], ids=["length", "truth"])
def test_dataset_size_with_blank_node_graph(measure: Callable[[Dataset], int]) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/protocol":
            return httpx.Response(200, text="12")
        if request.url.path == "/repositories/test-repo":
            return httpx.Response(200)
        if request.url.path == "/repositories/test-repo/contexts":
            return httpx.Response(
                200,
                json={
                    "results": {
                        "bindings": [
                            {"contextID": {"type": "bnode", "value": "blank"}},
                            {"contextID": {"type": "uri", "value": "urn:named"}},
                        ]
                    }
                },
            )
        assert request.url.path == "/repositories/test-repo/size"
        sizes = {None: 6, "_:blank": 2, "<urn:named>": 3, "null": 1}
        return httpx.Response(200, text=str(sizes[request.url.params.get("context")]))

    store = RDF4JStore(
        "http://rdf4j.invalid/",
        "test-repo",
        transport=httpx.MockTransport(respond),
    )
    try:
        dataset = Dataset(store)
        assert measure(dataset) == (6 if measure is len else True)
    finally:
        store.close()
