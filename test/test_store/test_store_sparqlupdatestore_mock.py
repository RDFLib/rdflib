from test.utils.httpservermock import (
    MethodName,
    MockHTTPResponse,
    ServedBaseHTTPServerMock,
)
from typing import ClassVar

from rdflib import Namespace
from rdflib.graph import ConjunctiveGraph

EG = Namespace("http://example.org/")


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
        graph = ConjunctiveGraph("SPARQLUpdateStore")
        graph.open((self.query_endpoint, self.update_endpoint))
        update_statement = f"INSERT DATA {{ {EG['subj']} {EG['pred']} {EG['obj']}. }}"

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
        graph = ConjunctiveGraph("SPARQLUpdateStore")
        graph.open((self.query_endpoint, self.update_endpoint))
        update_statement = f"INSERT DATA {{ {EG['subj']} {EG['pred']} {EG['obj']}. }}"

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
