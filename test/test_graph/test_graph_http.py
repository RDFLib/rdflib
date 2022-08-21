import re
from http.server import BaseHTTPRequestHandler
from test.data import TEST_DATA_DIR
from test.utils import GraphHelper
from test.utils.graph import cached_graph
from test.utils.httpservermock import (
    MethodName,
    MockHTTPResponse,
    ServedBaseHTTPServerMock,
    ctx_http_server,
)
from urllib.error import HTTPError

import pytest

from rdflib import Graph, Namespace

"""
Test that correct content negotiation headers are passed
by graph.parse
"""


xmltestdoc = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns="http://example.org/"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:about="http://example.org/a">
    <b rdf:resource="http://example.org/c"/>
  </rdf:Description>
</rdf:RDF>
"""

n3testdoc = """@prefix : <http://example.org/> .

:a :b :c .
"""

nttestdoc = "<http://example.org/a> <http://example.org/b> <http://example.org/c> .\n"

ttltestdoc = """@prefix : <http://example.org/> .

            :a :b :c .
            """

jsonldtestdoc = """
                [
                  {
                    "@id": "http://example.org/a",
                    "http://example.org/b": [
                      {
                        "@id": "http://example.org/c"
                      }
                    ]
                  }
                ]
                """

EG = Namespace("http://example.org/")


class ContentNegotiationHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802

        self.send_response(200, "OK")
        # fun fun fun parsing accept header.

        acs = self.headers["Accept"].split(",")
        acq = [x.split(";") for x in acs if ";" in x]
        acn = [(x, "q=1") for x in acs if ";" not in x]
        acs = [(x[0].strip(), float(x[1].strip()[2:])) for x in acq + acn]
        ac = sorted(acs, key=lambda x: x[1])
        ct = ac[-1]

        if "application/rdf+xml" in ct:
            rct = "application/rdf+xml"
            content = xmltestdoc
        elif "text/n3" in ct:
            rct = "text/n3"
            content = n3testdoc
        elif "application/trig" in ct:
            rct = "application/trig"
            content = ttltestdoc
        elif "text/plain" in ct or "application/n-triples" in ct:
            rct = "text/plain"
            content = nttestdoc
        elif "application/ld+json" in ct:
            rct = "application/ld+json"
            content = jsonldtestdoc
        else:  # "text/turtle" in ct:
            rct = "text/turtle"
            content = ttltestdoc

        self.send_header("Content-type", rct)
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def log_message(self, *args):
        pass


class TestGraphHTTP:
    def test_content_negotiation(self) -> None:
        expected = Graph()
        expected.add((EG.a, EG.b, EG.c))
        expected_triples = GraphHelper.triple_set(expected)

        with ctx_http_server(ContentNegotiationHandler) as server:
            (host, port) = server.server_address
            url = f"http://{host}:{port}/foo"
            for format in ("xml", "n3", "nt"):
                graph = Graph()
                graph.parse(url, format=format)
                assert expected_triples == GraphHelper.triple_set(graph)

    def test_content_negotiation_no_format(self) -> None:
        expected = Graph()
        expected.add((EG.a, EG.b, EG.c))
        expected_triples = GraphHelper.triple_set(expected)

        with ctx_http_server(ContentNegotiationHandler) as server:
            (host, port) = server.server_address
            url = f"http://{host}:{port}/foo"
            graph = Graph()
            graph.parse(url)
            assert expected_triples == GraphHelper.triple_set(graph)

    def test_source(self) -> None:
        expected = Graph()
        expected.add((EG["a"], EG["b"], EG["c"]))
        expected_triples = GraphHelper.triple_set(expected)

        with ServedBaseHTTPServerMock() as httpmock:
            url = httpmock.url

            httpmock.responses[MethodName.GET].append(
                MockHTTPResponse(
                    200,
                    "OK",
                    f"<{EG['a']}> <{EG['b']}> <{EG['c']}>.".encode(),
                    {"Content-Type": ["text/turtle"]},
                )
            )
            graph = Graph()
            graph.parse(source=url)
            assert expected_triples == GraphHelper.triple_set(graph)

    def test_3xx(self) -> None:
        expected = Graph()
        expected.add((EG["a"], EG["b"], EG["c"]))
        expected_triples = GraphHelper.triple_set(expected)

        with ServedBaseHTTPServerMock() as httpmock:
            url = httpmock.url

            for idx in range(3):
                httpmock.responses[MethodName.GET].append(
                    MockHTTPResponse(
                        302,
                        "FOUND",
                        "".encode(),
                        {"Location": [f"{url}/loc/302/{idx}"]},
                    )
                )
            for idx in range(3):
                httpmock.responses[MethodName.GET].append(
                    MockHTTPResponse(
                        303,
                        "See Other",
                        "".encode(),
                        {"Location": [f"{url}/loc/303/{idx}"]},
                    )
                )
            for idx in range(3):
                httpmock.responses[MethodName.GET].append(
                    MockHTTPResponse(
                        308,
                        "Permanent Redirect",
                        "".encode(),
                        {"Location": [f"{url}/loc/308/{idx}"]},
                    )
                )

            httpmock.responses[MethodName.GET].append(
                MockHTTPResponse(
                    200,
                    "OK",
                    f"<{EG['a']}> <{EG['b']}> <{EG['c']}>.".encode(),
                    {"Content-Type": ["text/turtle"]},
                )
            )

            graph = Graph()
            graph.parse(location=url, format="turtle")
            assert expected_triples == GraphHelper.triple_set(graph)

            httpmock.mocks[MethodName.GET].assert_called()
            assert len(httpmock.requests[MethodName.GET]) == 10
            for request in httpmock.requests[MethodName.GET]:
                assert re.match(r"text/turtle", request.headers.get("Accept"))

            request_paths = [
                request.path for request in httpmock.requests[MethodName.GET]
            ]
            assert request_paths == [
                "/",
                "/loc/302/0",
                "/loc/302/1",
                "/loc/302/2",
                "/loc/303/0",
                "/loc/303/1",
                "/loc/303/2",
                "/loc/308/0",
                "/loc/308/1",
                "/loc/308/2",
            ]

    def test_5xx(self):
        with ServedBaseHTTPServerMock() as httpmock:
            url = httpmock.url
            httpmock.responses[MethodName.GET].append(
                MockHTTPResponse(500, "Internal Server Error", "".encode(), {})
            )

            graph = Graph()

            with pytest.raises(HTTPError) as raised:
                graph.parse(location=url, format="turtle")

            assert raised.value.code == 500


def test_iri_source(function_httpmock: ServedBaseHTTPServerMock) -> None:
    diverse_triples_path = TEST_DATA_DIR / "variants/diverse_triples.ttl"

    function_httpmock.responses[MethodName.GET].append(
        MockHTTPResponse(
            200,
            "OK",
            diverse_triples_path.read_bytes(),
            {"Content-Type": ["text/turtle"]},
        )
    )
    g = Graph()
    g.parse(f"{function_httpmock.url}/resource/Almería")
    assert function_httpmock.call_count == 1
    GraphHelper.assert_triple_sets_equals(cached_graph((diverse_triples_path,)), g)

    req = function_httpmock.requests[MethodName.GET].pop(0)
    assert req.path == "/resource/Almer%C3%ADa"
