from typing import ClassVar

from rdflib.graph import Dataset
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from test.utils.http import MethodName, MockHTTPResponse
from test.utils.httpservermock import ServedBaseHTTPServerMock
from test.utils.namespace import EGDO


class TestSPARQLConnector:
    query_path: ClassVar[str]
    query_endpoint: ClassVar[str]
    update_path: ClassVar[str]
    update_endpoint: ClassVar[str]
    httpmock: ClassVar[ServedBaseHTTPServerMock]

    @classmethod
    def setup_class(cls) -> None:
        cls.httpmock = ServedBaseHTTPServerMock()
        cls.query_path = "/db/sparql"
        cls.query_endpoint = f"{cls.httpmock.url}{cls.query_path}"
        cls.update_path = "/db/update"
        cls.update_endpoint = f"{cls.httpmock.url}{cls.update_path}"

    @classmethod
    def teardown_class(cls) -> None:
        cls.httpmock.stop()

    def setup_method(self):
        self.httpmock.reset()

    def teardown_method(self):
        pass

    def test_graph_update(self):
        graph = Dataset("SPARQLUpdateStore")
        graph.open((self.query_endpoint, self.update_endpoint))
        update_statement = (
            f"INSERT DATA {{ {EGDO['subj']} {EGDO['pred']} {EGDO['obj']}. }}"
        )

        self.httpmock.responses[MethodName.POST].append(
            MockHTTPResponse(
                200,
                "OK",
                b"Update succeeded",
                {"Content-Type": ["text/plain; charset=UTF-8"]},
            )
        )

        # This test assumes that updates are performed using POST
        # at the moment this is the only supported way for SPARQLUpdateStore
        # to do updates.
        graph.update(update_statement)
        assert self.httpmock.call_count == 1
        req = self.httpmock.requests[MethodName.POST].pop(0)
        assert req.parsed_path.path == self.update_path
        assert "application/sparql-update" in req.headers.get("content-type")

    def test_update_encoding(self):
        graph = Dataset("SPARQLUpdateStore")
        graph.open((self.query_endpoint, self.update_endpoint))
        update_statement = (
            f"INSERT DATA {{ {EGDO['subj']} {EGDO['pred']} {EGDO['obj']}. }}"
        )

        self.httpmock.responses[MethodName.POST].append(
            MockHTTPResponse(
                200,
                "OK",
                b"Update succeeded",
                {"Content-Type": ["text/plain; charset=UTF-8"]},
            )
        )

        # This test assumes that updates are performed using POST
        # at the moment this is the only supported way for SPARQLUpdateStore
        # to do updates.
        graph.update(update_statement)
        assert self.httpmock.call_count == 1
        req = self.httpmock.requests[MethodName.POST].pop(0)
        assert req.parsed_path.path == self.update_path
        assert "charset=UTF-8" in req.headers.get("content-type")

    def test_content_type(self):
        store = SPARQLUpdateStore(
            self.query_endpoint, self.update_endpoint, auth=("admin", "admin")
        )
        update_statement = (
            f"INSERT DATA {{ {EGDO['subj']} {EGDO['pred']} {EGDO['obj']}. }}"
        )

        for _ in range(2):
            # run it twice so we can pick up issues with order both ways.
            self.httpmock.responses[MethodName.POST].append(
                MockHTTPResponse(
                    200,
                    "OK",
                    b"Update succeeded",
                    {"Content-Type": ["text/plain; charset=UTF-8"]},
                )
            )

            self.httpmock.responses[MethodName.GET].append(
                MockHTTPResponse(
                    200,
                    "OK",
                    b"""<?xml version="1.0"?>
    <sparql xmlns="http://www.w3.org/2005/sparql-results#"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.w3.org/2001/sw/DataAccess/rf1/result2.xsd">
    <boolean>true</boolean>
    </sparql>
    """,
                    {"Content-Type": ["application/sparql-results+xml"]},
                )
            )

            # First make update request and check if Content-Type header is set
            store.update(update_statement)
            req = self.httpmock.requests[MethodName.POST].pop(0)
            assert "application/sparql-update" in req.headers.get("Content-Type")

            # Now make GET request and check that Content-Type header is not "application/sparql-update"
            query_statement = "ASK { ?s ?p ?o }"
            store.query(query_statement)
            req = self.httpmock.requests[MethodName.GET].pop(0)
            assert "application/sparql-update" not in req.headers.get(
                "Content-Type", ""
            )
