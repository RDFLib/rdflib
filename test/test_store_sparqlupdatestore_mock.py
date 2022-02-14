from rdflib.graph import ConjunctiveGraph
from typing import ClassVar
from rdflib import Namespace
from .testutils import MockHTTPResponse, ServedSimpleHTTPMock
import unittest

EG = Namespace("http://example.org/")


class TestSPARQLConnector(unittest.TestCase):
    query_path: ClassVar[str]
    query_endpoint: ClassVar[str]
    update_path: ClassVar[str]
    update_endpoint: ClassVar[str]
    httpmock: ClassVar[ServedSimpleHTTPMock]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.httpmock = ServedSimpleHTTPMock()
        cls.query_path = "/db/sparql"
        cls.query_endpoint = f"{cls.httpmock.url}{cls.query_path}"
        cls.update_path = "/db/update"
        cls.update_endpoint = f"{cls.httpmock.url}{cls.update_path}"

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.httpmock.stop()

    def setUp(self):
        self.httpmock.reset()

    def tearDown(self):
        pass

    def test_graph_update(self):
        graph = ConjunctiveGraph("SPARQLUpdateStore")
        graph.open((self.query_endpoint, self.update_endpoint))
        update_statement = f"INSERT DATA {{ {EG['subj']} {EG['pred']} {EG['obj']}. }}"

        self.httpmock.do_post_responses.append(
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
        self.assertEqual(self.httpmock.call_count, 1)
        req = self.httpmock.do_post_requests.pop(0)
        self.assertEqual(req.parsed_path.path, self.update_path)
        self.assertIn("application/sparql-update", req.headers.get("content-type"))
