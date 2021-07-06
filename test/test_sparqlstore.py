from rdflib import Graph, URIRef, Literal
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread
from unittest.mock import patch
from rdflib.namespace import RDF, XSD, XMLNS, FOAF, RDFS
from rdflib.plugins.stores.sparqlstore import SPARQLConnector
from typing import ClassVar

from . import helper
from .testutils import (
    MockHTTPResponse,
    ServedSimpleHTTPMock,
)


class SPARQLStoreFakeDBPediaTestCase(unittest.TestCase):
    store_name = "SPARQLStore"
    path: ClassVar[str]
    httpmock: ClassVar[ServedSimpleHTTPMock]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.httpmock = ServedSimpleHTTPMock()
        cls.path = f"{cls.httpmock.url}/sparql"

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.httpmock.stop()

    def setUp(self):
        self.httpmock.reset()
        self.graph = Graph(store="SPARQLStore")
        self.graph.open(self.path, create=True)
        ns = list(self.graph.namespaces())
        assert len(ns) > 0, ns

    def tearDown(self):
        self.graph.close()

    def test_Query(self):
        query = "select distinct ?Concept where {[] a ?Concept} LIMIT 1"
        _query = SPARQLConnector.query
        self.httpmock.do_get_responses.append(
            MockHTTPResponse(
                200,
                "OK",
                b"""\
<sparql xmlns="http://www.w3.org/2005/sparql-results#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/2001/sw/DataAccess/rf1/result2.xsd">
 <head>
  <variable name="Concept"/>
 </head>
 <results distinct="false" ordered="true">
  <result>
   <binding name="Concept"><uri>http://www.w3.org/2000/01/rdf-schema#Datatype</uri></binding>
  </result>
 </results>
</sparql>""",
                {"Content-Type": ["application/sparql-results+xml; charset=UTF-8"]},
            )
        )
        with patch("rdflib.plugins.stores.sparqlstore.SPARQLConnector.query") as mock:
            SPARQLConnector.query.side_effect = lambda *args, **kwargs: _query(
                self.graph.store, *args, **kwargs
            )
            res = self.graph.query(query, initNs={})
            count = 0
            for i in res:
                count += 1
                assert type(i[0]) == URIRef, i[0].n3()
            assert count > 0
            mock.assert_called_once()
            args, kwargs = mock.call_args

            def unpacker(query, default_graph=None, named_graph=None):
                return query, default_graph, named_graph

            (mquery, _, _) = unpacker(*args, *kwargs)
            for _, uri in self.graph.namespaces():
                assert mquery.count(f"<{uri}>") == 1
        self.assertEqual(self.httpmock.do_get_mock.call_count, 1)
        req = self.httpmock.do_get_requests.pop(0)
        self.assertRegex(req.path, r"^/sparql")
        self.assertIn(query, req.path_query["query"][0])

    def test_initNs(self):
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        self.httpmock.do_get_responses.append(
            MockHTTPResponse(
                200,
                "OK",
                """\
<sparql xmlns="http://www.w3.org/2005/sparql-results#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/2001/sw/DataAccess/rf1/result2.xsd">
 <head>
  <variable name="label"/>
 </head>
 <results distinct="false" ordered="true">
  <result>
   <binding name="label"><literal xml:lang="en">189</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 Scottish Football League</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 United States collegiate men&#39;s ice hockey season</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 Western Conference men&#39;s basketball season</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 collegiate men&#39;s basketball independents season in the United States</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 domestic association football cups</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 domestic association football leagues</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 in American ice hockey by league</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 in American ice hockey by team</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 in Belgian football</literal></binding>
  </result>
 </results>
</sparql>""".encode(
                    "utf8"
                ),
                {"Content-Type": ["application/sparql-results+xml; charset=UTF-8"]},
            )
        )
        res = self.graph.query(
            query, initNs={"xyzzy": "http://www.w3.org/2004/02/skos/core#"}
        )
        for i in res:
            assert type(i[0]) == Literal, i[0].n3()

        self.assertEqual(self.httpmock.do_get_mock.call_count, 1)
        req = self.httpmock.do_get_requests.pop(0)
        self.assertRegex(req.path, r"^/sparql")
        self.assertIn(query, req.path_query["query"][0])

    def test_noinitNs(self):
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        self.httpmock.do_get_responses.append(
            MockHTTPResponse(
                400,
                "Bad Request",
                b"""\
Virtuoso 37000 Error SP030: SPARQL compiler, line 1: Undefined namespace prefix in prefix:localpart notation at 'xyzzy:Concept' before ';'

SPARQL query:
SELECT ?label WHERE { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10""",
                {"Content-Type": ["text/plain"]},
            )
        )
        with self.assertRaises(ValueError):
            self.graph.query(query)
        self.assertEqual(self.httpmock.do_get_mock.call_count, 1)
        req = self.httpmock.do_get_requests.pop(0)
        self.assertRegex(req.path, r"^/sparql")
        self.assertIn(query, req.path_query["query"][0])

    def test_query_with_added_prolog(self):
        prologue = """\
        PREFIX xyzzy: <http://www.w3.org/2004/02/skos/core#>
        """
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        self.httpmock.do_get_responses.append(
            MockHTTPResponse(
                200,
                "OK",
                """\
<sparql xmlns="http://www.w3.org/2005/sparql-results#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/2001/sw/DataAccess/rf1/result2.xsd">
 <head>
  <variable name="label"/>
 </head>
 <results distinct="false" ordered="true">
  <result>
   <binding name="label"><literal xml:lang="en">189</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 Scottish Football League</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 United States collegiate men&#39;s ice hockey season</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 Western Conference men&#39;s basketball season</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 collegiate men&#39;s basketball independents season in the United States</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 domestic association football cups</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 domestic association football leagues</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 in American ice hockey by league</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 in American ice hockey by team</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 in Belgian football</literal></binding>
  </result>
 </results>
</sparql>""".encode(
                    "utf8"
                ),
                {"Content-Type": ["application/sparql-results+xml; charset=UTF-8"]},
            )
        )
        res = helper.query_with_retry(self.graph, prologue + query)
        for i in res:
            assert type(i[0]) == Literal, i[0].n3()
        self.assertEqual(self.httpmock.do_get_mock.call_count, 1)
        req = self.httpmock.do_get_requests.pop(0)
        self.assertRegex(req.path, r"^/sparql")
        self.assertIn(query, req.path_query["query"][0])

    def test_query_with_added_rdf_prolog(self):
        prologue = """\
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX xyzzy: <http://www.w3.org/2004/02/skos/core#>
        """
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        self.httpmock.do_get_responses.append(
            MockHTTPResponse(
                200,
                "OK",
                """\
<sparql xmlns="http://www.w3.org/2005/sparql-results#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/2001/sw/DataAccess/rf1/result2.xsd">
 <head>
  <variable name="label"/>
 </head>
 <results distinct="false" ordered="true">
  <result>
   <binding name="label"><literal xml:lang="en">189</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 Scottish Football League</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 United States collegiate men&#39;s ice hockey season</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 Western Conference men&#39;s basketball season</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 collegiate men&#39;s basketball independents season in the United States</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 domestic association football cups</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 domestic association football leagues</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 in American ice hockey by league</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 in American ice hockey by team</literal></binding>
  </result>
  <result>
   <binding name="label"><literal xml:lang="en">1899–1900 in Belgian football</literal></binding>
  </result>
 </results>
</sparql>""".encode(
                    "utf8"
                ),
                {"Content-Type": ["application/sparql-results+xml; charset=UTF-8"]},
            )
        )
        res = helper.query_with_retry(self.graph, prologue + query)
        for i in res:
            assert type(i[0]) == Literal, i[0].n3()
        self.assertEqual(self.httpmock.do_get_mock.call_count, 1)
        req = self.httpmock.do_get_requests.pop(0)
        self.assertRegex(req.path, r"^/sparql")
        self.assertIn(query, req.path_query["query"][0])

    def test_counting_graph_and_store_queries(self):
        query = """
            SELECT ?s
            WHERE {
                ?s ?p ?o .
            }
            LIMIT 5
            """
        g = Graph("SPARQLStore")
        g.open(self.path)
        count = 0
        response = MockHTTPResponse(
            200,
            "OK",
            """\
        <sparql xmlns="http://www.w3.org/2005/sparql-results#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/2001/sw/DataAccess/rf1/result2.xsd">
        <head>
        <variable name="s"/>
        </head>
        <results distinct="false" ordered="true">
        <result>
        <binding name="s"><uri>http://www.openlinksw.com/virtrdf-data-formats#default-iid</uri></binding>
        </result>
        <result>
        <binding name="s"><uri>http://www.openlinksw.com/virtrdf-data-formats#default-iid-nullable</uri></binding>
        </result>
        <result>
        <binding name="s"><uri>http://www.openlinksw.com/virtrdf-data-formats#default-iid-blank</uri></binding>
        </result>
        <result>
        <binding name="s"><uri>http://www.openlinksw.com/virtrdf-data-formats#default-iid-blank-nullable</uri></binding>
        </result>
        <result>
        <binding name="s"><uri>http://www.openlinksw.com/virtrdf-data-formats#default-iid-nonblank</uri></binding>
        </result>
        </results>
        </sparql>""".encode(
                "utf8"
            ),
            {"Content-Type": ["application/sparql-results+xml; charset=UTF-8"]},
        )

        self.httpmock.do_get_responses.append(response)

        result = g.query(query)
        for _ in result:
            count += 1

        assert count == 5, 'Graph("SPARQLStore") didn\'t return 5 records'

        from rdflib.plugins.stores.sparqlstore import SPARQLStore

        st = SPARQLStore(query_endpoint=self.path)
        count = 0
        self.httpmock.do_get_responses.append(response)
        result = st.query(query)
        for _ in result:
            count += 1

        assert count == 5, "SPARQLStore() didn't return 5 records"

        self.assertEqual(self.httpmock.do_get_mock.call_count, 2)
        for _ in range(2):
            req = self.httpmock.do_get_requests.pop(0)
            self.assertRegex(req.path, r"^/sparql")
            self.assertIn(query, req.path_query["query"][0])


class SPARQLStoreUpdateTestCase(unittest.TestCase):
    def setUp(self):
        port = self.setup_mocked_endpoint()
        self.graph = Graph(store="SPARQLUpdateStore", identifier=URIRef("urn:ex"))
        self.graph.open(
            (
                "http://localhost:{port}/query".format(port=port),
                "http://localhost:{port}/update".format(port=port),
            ),
            create=False,
        )
        ns = list(self.graph.namespaces())
        assert len(ns) > 0, ns

    def setup_mocked_endpoint(self):
        # Configure mock server.
        s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        s.bind(("localhost", 0))
        address, port = s.getsockname()
        s.close()
        mock_server = HTTPServer(("localhost", port), SPARQL11ProtocolStoreMock)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        mock_server_thread = Thread(target=mock_server.serve_forever)
        mock_server_thread.setDaemon(True)
        mock_server_thread.start()
        print(
            "Started mocked sparql endpoint on http://localhost:{port}/".format(
                port=port
            )
        )
        return port

    def tearDown(self):
        self.graph.close()

    def test_Query(self):
        query = "insert data {<urn:s> <urn:p> <urn:o>}"
        res = self.graph.update(query)
        print(res)


class SPARQL11ProtocolStoreMock(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        If the body should be analysed as well, just use:
        ```
        body = self.rfile.read(int(self.headers['Content-Length'])).decode()
        print(body)
        ```
        """
        contenttype = self.headers.get("Content-Type")
        if self.path == "/query" or self.path == "/query?":
            if self.headers.get("Content-Type") == "application/sparql-query":
                pass
            elif (
                self.headers.get("Content-Type") == "application/x-www-form-urlencoded"
            ):
                pass
            else:
                self.send_response(406, "Not Acceptable")
                self.end_headers()
        elif self.path == "/update" or self.path == "/update?":
            if self.headers.get("Content-Type") == "application/sparql-update":
                pass
            elif (
                self.headers.get("Content-Type") == "application/x-www-form-urlencoded"
            ):
                pass
            else:
                self.send_response(406, "Not Acceptable")
                self.end_headers()
        else:
            print("self.path")
            print(self.path)
            self.send_response(404, "Not Found")
            self.end_headers()
        self.send_response(200, "OK")
        self.end_headers()
        return

    def do_GET(self):
        # Process an HTTP GET request and return a response with an HTTP 200 status.
        self.send_response(200, "OK")
        self.end_headers()
        return


class SPARQLMockTests(unittest.TestCase):
    def test_query(self):
        triples = {
            (RDFS.Resource, RDF.type, RDFS.Class),
            (RDFS.Resource, RDFS.isDefinedBy, URIRef(RDFS)),
            (RDFS.Resource, RDFS.label, Literal("Resource")),
            (RDFS.Resource, RDFS.comment, Literal("The class resource, everything.")),
        }
        rows = "\n".join([f'"{s}","{p}","{o}"' for s, p, o in triples])
        response_body = f"s,p,o\n{rows}".encode()
        response = MockHTTPResponse(
            200, "OK", response_body, {"Content-Type": ["text/csv; charset=utf-8"]}
        )

        graph = Graph(store="SPARQLStore", identifier="http://example.com")
        graph.bind("xsd", XSD)
        graph.bind("xml", XMLNS)
        graph.bind("foaf", FOAF)
        graph.bind("rdf", RDF)

        assert len(list(graph.namespaces())) >= 4

        with ServedSimpleHTTPMock() as httpmock:
            httpmock.do_get_responses.append(response)
            url = f"{httpmock.url}/query"
            graph.open(url)
            query_result = graph.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")

        rows = set(query_result)
        assert len(rows) == len(triples)
        for triple in triples:
            assert triple in rows

        httpmock.do_get_mock.assert_called_once()
        assert len(httpmock.do_get_requests) == 1
        request = httpmock.do_get_requests.pop()
        assert len(request.path_query["query"]) == 1
        query = request.path_query["query"][0]

        for _, uri in graph.namespaces():
            assert query.count(f"<{uri}>") == 1


if __name__ == "__main__":
    unittest.main()
