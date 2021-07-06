from rdflib import Graph, Namespace

from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError
from .testutils import SimpleHTTPMock, MockHTTPResponse, ctx_http_server, GraphHelper
import unittest


"""
Test that correct content negoation headers are passed
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


class ContentNegotiationHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        self.send_response(200, "OK")
        # fun fun fun parsing accept header.

        acs = self.headers["Accept"].split(",")
        acq = [x.split(";") for x in acs if ";" in x]
        acn = [(x, "q=1") for x in acs if ";" not in x]
        acs = [(x[0], float(x[1].strip()[2:])) for x in acq + acn]
        ac = sorted(acs, key=lambda x: x[1])
        ct = ac[-1]

        if "application/rdf+xml" in ct:
            rct = "application/rdf+xml"
            content = xmltestdoc
        elif "text/n3" in ct:
            rct = "text/n3"
            content = n3testdoc
        elif "text/plain" in ct:
            rct = "text/plain"
            content = nttestdoc

        self.send_header("Content-type", rct)
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def log_message(self, *args):
        pass


class TestGraphHTTP(unittest.TestCase):
    def content_negotiation(self) -> None:
        EG = Namespace("http://example.org/")
        expected = Graph()
        expected.add((EG["a"], EG["b"], EG["c"]))
        expected_triples = GraphHelper.triple_set(expected)

        with ctx_http_server(ContentNegotiationHandler) as server:
            (host, port) = server.server_address
            url = f"http://{host}:{port}/foo"
            for format in ("xml", "n3", "nt"):
                graph = Graph()
                graph.parse(url, format=format)
                self.assertEqual(expected_triples, GraphHelper.triple_set(graph))

    def test_3xx(self) -> None:
        EG = Namespace("http://example.com/")
        expected = Graph()
        expected.add((EG["a"], EG["b"], EG["c"]))
        expected_triples = GraphHelper.triple_set(expected)

        httpmock = SimpleHTTPMock()
        with ctx_http_server(httpmock.Handler) as server:
            (host, port) = server.server_address
            url = f"http://{host}:{port}/"

            for idx in range(3):
                httpmock.do_get_responses.append(
                    MockHTTPResponse(
                        302, "FOUND", "".encode(), {"Location": [f"{url}loc/302/{idx}"]}
                    )
                )
            for idx in range(3):
                httpmock.do_get_responses.append(
                    MockHTTPResponse(
                        303,
                        "See Other",
                        "".encode(),
                        {"Location": [f"{url}loc/303/{idx}"]},
                    )
                )
            for idx in range(3):
                httpmock.do_get_responses.append(
                    MockHTTPResponse(
                        308,
                        "Permanent Redirect",
                        "".encode(),
                        {"Location": [f"{url}loc/308/{idx}"]},
                    )
                )

            httpmock.do_get_responses.append(
                MockHTTPResponse(
                    200,
                    "OK",
                    f"<{EG['a']}> <{EG['b']}> <{EG['c']}>.".encode(),
                    {"Content-Type": ["text/turtle"]},
                )
            )

            graph = Graph()
            graph.parse(location=url, format="turtle")
            self.assertEqual(expected_triples, GraphHelper.triple_set(graph))

            httpmock.do_get_mock.assert_called()
            assert len(httpmock.do_get_requests) == 10
            for request in httpmock.do_get_requests:
                self.assertRegex(request.headers.get("Accept"), "text/turtle")

            request_paths = [request.path for request in httpmock.do_get_requests]
            self.assertEqual(
                request_paths,
                [
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
                ],
            )

    def test_5xx(self):
        httpmock = SimpleHTTPMock()
        with ctx_http_server(httpmock.Handler) as server:
            (host, port) = server.server_address
            url = f"http://{host}:{port}/"
            response = MockHTTPResponse(500, "Internal Server Error", "".encode(), {})
            httpmock.do_get_responses.append(response)

            graph = Graph()

            with self.assertRaises(HTTPError) as raised:
                graph.parse(location=url, format="turtle")

            self.assertEqual(raised.exception.code, 500)


if __name__ == "__main__":
    unittest.main()
