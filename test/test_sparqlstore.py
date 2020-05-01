from rdflib import Graph, URIRef, Literal
from six.moves.urllib.request import urlopen
import os
import unittest
from nose import SkipTest
from requests import HTTPError
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread
import requests

try:
    assert len(urlopen("http://dbpedia.org/sparql").read()) > 0
except:
    raise SkipTest("No HTTP connection.")


class SPARQLStoreDBPediaTestCase(unittest.TestCase):
    store_name = 'SPARQLStore'
    path = "http://dbpedia.org/sparql"
    storetest = True
    create = False

    def setUp(self):
        self.graph = Graph(store="SPARQLStore")
        self.graph.open(self.path, create=self.create)
        ns = list(self.graph.namespaces())
        assert len(ns) > 0, ns

    def tearDown(self):
        self.graph.close()

    def test_Query(self):
        query = "select distinct ?Concept where {[] a ?Concept} LIMIT 1"
        res = self.graph.query(query, initNs={})
        for i in res:
            assert type(i[0]) == URIRef, i[0].n3()

    def test_initNs(self):
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        res = self.graph.query(
            query,
            initNs={"xyzzy": "http://www.w3.org/2004/02/skos/core#"})
        for i in res:
            assert type(i[0]) == Literal, i[0].n3()

    def test_noinitNs(self):
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        self.assertRaises(
            HTTPError,
            self.graph.query,
            query)

    def test_query_with_added_prolog(self):
        prologue = """\
        PREFIX xyzzy: <http://www.w3.org/2004/02/skos/core#>
        """
        query = """\
        SELECT ?label WHERE
            { ?s a xyzzy:Concept ; xyzzy:prefLabel ?label . } LIMIT 10
        """
        res = self.graph.query(prologue + query)
        for i in res:
            assert type(i[0]) == Literal, i[0].n3()


class SPARQLStoreUpdateTestCase(unittest.TestCase):
    def setUp(self):
        port = self.setup_mocked_endpoint()
        self.graph = Graph(store="SPARQLUpdateStore", identifier=URIRef("urn:ex"))
        self.graph.open(("http://localhost:{port}/query".format(port=port),
            "http://localhost:{port}/update".format(port=port)), create=False)
        ns = list(self.graph.namespaces())
        assert len(ns) > 0, ns

    def setup_mocked_endpoint(self):
        # Configure mock server.
        s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        s.bind(('localhost', 0))
        address, port = s.getsockname()
        s.close()
        mock_server = HTTPServer(('localhost', port), SPARQL11ProtocolStoreMock)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        mock_server_thread = Thread(target=mock_server.serve_forever)
        mock_server_thread.setDaemon(True)
        mock_server_thread.start()
        print("Started mocked sparql endpoint on http://localhost:{port}/".format(port=port))
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
        if self.path == "/query":
            if self.headers.get("Content-Type") == "application/sparql-query":
                pass
            elif self.headers.get("Content-Type") == "application/x-www-form-urlencoded":
                pass
            else:
                self.send_response(requests.codes.not_acceptable)
                self.end_headers()
        elif self.path == "/update":
            if self.headers.get("Content-Type") == "application/sparql-update":
                pass
            elif self.headers.get("Content-Type") == "application/x-www-form-urlencoded":
                pass
            else:
                self.send_response(requests.codes.not_acceptable)
                self.end_headers()
        else:
            self.send_response(requests.codes.not_found)
            self.end_headers()
        self.send_response(requests.codes.ok)
        self.end_headers()
        return

    def do_GET(self):
        # Process an HTTP GET request and return a response with an HTTP 200 status.
        self.send_response(requests.codes.ok)
        self.end_headers()
        return

if __name__ == '__main__':
    unittest.main()
