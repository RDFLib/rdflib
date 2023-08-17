import logging
import re
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from test.utils import helper
from test.utils.httpservermock import (
    MethodName,
    MockHTTPResponse,
    ServedBaseHTTPServerMock,
)
from threading import Thread
from typing import Callable, ClassVar, Type
from unittest.mock import patch

import pytest

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, XMLNS, XSD
from rdflib.plugins.stores.sparqlstore import SPARQLConnector


class TestSPARQLStoreGraph:
    """
    Tests for ``rdflib.Graph(store="SPARQLStore")``.

    .. note::
        This is a pytest based test class to be used for new tests instead of
        the older `unittest.TestCase` based classes.
    """

    @pytest.mark.parametrize(
        "call, exception_type",
        [
            (
                lambda graph: graph.update("insert data {<urn:s> <urn:p> <urn:o>}"),
                TypeError,
            ),
            # Additional methods that modify graphs should be added here.
        ],
    )
    def test_graph_modify_fails(
        self, call: Callable[[Graph], None], exception_type: Type[Exception]
    ) -> None:
        """
        Methods that modify the Graph fail.
        """
        graph = Graph(store="SPARQLStore")
        graph.open("http://something.invalid/", create=True)
        with pytest.raises(exception_type) as ctx:
            call(graph)
        pattern_str = r"read.*only"
        msg = f"{ctx.value}"
        assert (
            re.search(pattern_str, msg, re.IGNORECASE) is not None
        ), f"exception text {msg!r} does not match regex {pattern_str!r}"


class TestSPARQLStoreFakeDBPedia:
    store_name = "SPARQLStore"
    path: ClassVar[str]
    httpmock: ClassVar[ServedBaseHTTPServerMock]

    @classmethod
    def setup_class(cls) -> None:
        cls.httpmock = ServedBaseHTTPServerMock()
        cls.path = f"{cls.httpmock.url}/sparql"

    @classmethod
    def teardown_class(cls) -> None:
        cls.httpmock.stop()

    def setup_method(self):
        self.httpmock.reset()
        self.graph = Graph(store="SPARQLStore")
        self.graph.open(self.path, create=True)
        ns = list(self.graph.namespaces())
        assert len(ns) > 0, ns

    def teardown_method(self):
        self.graph.close()

    def test_Query(self):
        query = "select distinct ?Concept where {[] a ?Concept} LIMIT 1"
        _query = SPARQLConnector.query
        self.httpmock.responses[MethodName.GET].append(
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
        assert self.httpmock.mocks[MethodName.GET].call_count == 1
        req = self.httpmock.requests[MethodName.GET].pop(0)
        assert re.match(r"^/sparql", req.path)
        assert query in req.path_query["query"][0]

    def test_initNs(self):
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        self.httpmock.responses[MethodName.GET].append(
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

        assert self.httpmock.mocks[MethodName.GET].call_count == 1
        req = self.httpmock.requests[MethodName.GET].pop(0)
        assert re.match(r"^/sparql", req.path)
        assert query in req.path_query["query"][0]

    def test_noinitNs(self):
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        self.httpmock.responses[MethodName.GET].append(
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
        with pytest.raises(ValueError):
            self.graph.query(query)
        assert self.httpmock.mocks[MethodName.GET].call_count == 1
        req = self.httpmock.requests[MethodName.GET].pop(0)
        assert re.match(r"^/sparql", req.path)
        assert query in req.path_query["query"][0]

    def test_query_with_added_prolog(self):
        prologue = """\
        PREFIX xyzzy: <http://www.w3.org/2004/02/skos/core#>
        """
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        self.httpmock.responses[MethodName.GET].append(
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
        assert self.httpmock.mocks[MethodName.GET].call_count == 1
        req = self.httpmock.requests[MethodName.GET].pop(0)
        assert re.match(r"^/sparql", req.path)
        assert query in req.path_query["query"][0]

    def test_query_with_added_rdf_prolog(self):
        prologue = """\
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX xyzzy: <http://www.w3.org/2004/02/skos/core#>
        """
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        self.httpmock.responses[MethodName.GET].append(
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
        assert self.httpmock.mocks[MethodName.GET].call_count == 1
        req = self.httpmock.requests[MethodName.GET].pop(0)
        assert re.match(r"^/sparql", req.path)
        assert query in req.path_query["query"][0]

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

        self.httpmock.responses[MethodName.GET].append(response)

        result = g.query(query)
        for _ in result:
            count += 1

        assert count == 5, 'Graph("SPARQLStore") didn\'t return 5 records'

        from rdflib.plugins.stores.sparqlstore import SPARQLStore

        st = SPARQLStore(query_endpoint=self.path)
        count = 0
        self.httpmock.responses[MethodName.GET].append(response)
        result = st.query(query)
        for _ in result:
            count += 1

        assert count == 5, "SPARQLStore() didn't return 5 records"

        assert self.httpmock.mocks[MethodName.GET].call_count == 2
        for _ in range(2):
            req = self.httpmock.requests[MethodName.GET].pop(0)
            assert re.match(r"^/sparql", req.path)
            assert query in req.path_query["query"][0]


class TestSPARQLStoreUpdate:
    def setup_method(self):
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
        mock_server_thread.daemon = True
        mock_server_thread.start()
        print(
            "Started mocked sparql endpoint on http://localhost:{port}/".format(
                port=port
            )
        )
        return port

    def teardown_method(self):
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
        contenttype = [
            part.strip() for part in f"{self.headers.get('Content-Type')}".split(";")
        ]
        logging.debug("contenttype = %s", contenttype)
        if self.path == "/query" or self.path == "/query?":
            if "application/sparql-query" in contenttype:
                pass
            elif "application/x-www-form-urlencoded" in contenttype:
                pass
            else:
                self.send_response(406, "Not Acceptable")
                self.end_headers()
        elif self.path == "/update" or self.path == "/update?":
            if "application/sparql-update" in contenttype:
                pass
            elif "application/x-www-form-urlencoded" in contenttype:
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


class TestSPARQLMock:
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

        with ServedBaseHTTPServerMock() as httpmock:
            httpmock.responses[MethodName.GET].append(response)
            url = f"{httpmock.url}/query"
            graph.open(url)
            query_result = graph.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")

        rows = set(query_result)
        assert len(rows) == len(triples)
        for triple in triples:
            assert triple in rows

        httpmock.mocks[MethodName.GET].assert_called_once()
        assert len(httpmock.requests[MethodName.GET]) == 1
        request = httpmock.requests[MethodName.GET].pop()
        assert len(request.path_query["query"]) == 1
        query = request.path_query["query"][0]

        for _, uri in graph.namespaces():
            assert query.count(f"<{uri}>") == 1
