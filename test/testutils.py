from __future__ import print_function

import os
import sys
from types import TracebackType
import isodate
import datetime
import random

from contextlib import AbstractContextManager, contextmanager
from typing import (
    Callable,
    Iterable,
    List,
    Optional,
    TYPE_CHECKING,
    Type,
    Iterator,
    Set,
    Tuple,
    Dict,
    Any,
    TypeVar,
    Union,
    cast,
    NamedTuple,
)
from urllib.parse import ParseResult, unquote, urlparse, parse_qs
from traceback import print_exc
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import email.message
import unittest

from rdflib import BNode, Graph, ConjunctiveGraph
from rdflib.term import Identifier, Literal, Node, URIRef
from unittest.mock import MagicMock, Mock
from urllib.error import HTTPError
from urllib.request import urlopen
from pathlib import PurePath, PureWindowsPath
from nturl2path import url2pathname as nt_url2pathname
import rdflib.compare

if TYPE_CHECKING:
    import typing_extensions as te


def get_random_ip(parts: List[str] = None) -> str:
    if parts is None:
        parts = ["127"]
    for _ in range(4 - len(parts)):
        parts.append(f"{random.randint(0, 255)}")
    return ".".join(parts)


@contextmanager
def ctx_http_server(
    handler: Type[BaseHTTPRequestHandler], host: str = "127.0.0.1"
) -> Iterator[HTTPServer]:
    server = HTTPServer((host, 0), handler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    yield server
    server.shutdown()
    server.socket.close()
    server_thread.join()


IdentifierTriple = Tuple[Identifier, Identifier, Identifier]
IdentifierTripleSet = Set[IdentifierTriple]
IdentifierQuad = Tuple[Identifier, Identifier, Identifier, Identifier]
IdentifierQuadSet = Set[IdentifierQuad]


class GraphHelper:
    """
    Provides methods which are useful for working with graphs.
    """

    @classmethod
    def identifier(self, node: Node) -> Identifier:
        """
        Return the identifier of the provided node.
        """
        if isinstance(node, Graph):
            return node.identifier
        else:
            return cast(Identifier, node)

    @classmethod
    def identifiers(cls, nodes: Tuple[Node, ...]) -> Tuple[Identifier, ...]:
        """
        Return the identifiers of the provided nodes.
        """
        result = []
        for node in nodes:
            result.append(cls.identifier(node))
        return tuple(result)

    @classmethod
    def triple_set(
        cls, graph: Graph, exclude_blanks: bool = False
    ) -> IdentifierTripleSet:
        result = set()
        for sn, pn, on in graph.triples((None, None, None)):
            s, p, o = cls.identifiers((sn, pn, on))
            if exclude_blanks and (
                isinstance(s, BNode) or isinstance(p, BNode) or isinstance(o, BNode)
            ):
                continue
            result.add((s, p, o))
        return result

    @classmethod
    def triple_sets(
        cls, graphs: Iterable[Graph], exclude_blanks: bool = False
    ) -> List[IdentifierTripleSet]:
        """
        Extracts the set of all triples from the supplied Graph.
        """
        result: List[IdentifierTripleSet] = []
        for graph in graphs:
            result.append(cls.triple_set(graph, exclude_blanks))
        return result

    @classmethod
    def quad_set(
        cls, graph: ConjunctiveGraph, exclude_blanks: bool = False
    ) -> IdentifierQuadSet:
        """
        Extracts the set of all quads from the supplied ConjunctiveGraph.
        """
        result = set()
        for sn, pn, on, gn in graph.quads((None, None, None, None)):
            s, p, o, g = cls.identifiers((sn, pn, on, gn))
            if exclude_blanks and (
                isinstance(s, BNode)
                or isinstance(p, BNode)
                or isinstance(o, BNode)
                or isinstance(g, BNode)
            ):
                continue
            result.add((s, p, o, g))
        return result

    @classmethod
    def triple_or_quad_set(
        cls, graph: Graph, exclude_blanks: bool = False
    ) -> Union[IdentifierQuadSet, IdentifierTripleSet]:
        """
        Extracts quad or triple sets depending on whether or not the graph is
        ConjunctiveGraph or a normal Graph.
        """
        if isinstance(graph, ConjunctiveGraph):
            return cls.quad_set(graph, exclude_blanks)
        return cls.triple_set(graph, exclude_blanks)

    @classmethod
    def assert_triple_sets_equals(
        cls, lhs: Graph, rhs: Graph, exclude_blanks: bool = False
    ) -> None:
        """
        Asserts that the triple sets in the two graphs are equal.
        """
        lhs_set = cls.triple_set(lhs, exclude_blanks)
        rhs_set = cls.triple_set(rhs, exclude_blanks)
        assert lhs_set == rhs_set

    @classmethod
    def assert_quad_sets_equals(
        cls, lhs: ConjunctiveGraph, rhs: ConjunctiveGraph, exclude_blanks: bool = False
    ) -> None:
        """
        Asserts that the quads sets in the two graphs are equal.
        """
        lhs_set = cls.quad_set(lhs, exclude_blanks)
        rhs_set = cls.quad_set(rhs, exclude_blanks)
        assert lhs_set == rhs_set

    @classmethod
    def assert_sets_equals(
        cls, lhs: Graph, rhs: Graph, exclude_blanks: bool = False
    ) -> None:
        """
        Asserts that that ther quad or triple sets from the two graphs are equal.
        """
        lhs_set = cls.triple_or_quad_set(lhs, exclude_blanks)
        rhs_set = cls.triple_or_quad_set(rhs, exclude_blanks)
        assert lhs_set == rhs_set

    @classmethod
    def format_set(
        cls, item_set: Union[IdentifierQuadSet, IdentifierTripleSet], prefix: str = "  "
    ) -> str:
        items = []
        for item in item_set:
            items.append(f"{prefix}{item}")
        return "\n".join(items)

    @classmethod
    def format_graph_set(cls, graph: Graph, prefix: str = "  ") -> str:
        return cls.format_set(cls.triple_or_quad_set(graph), prefix)

    @classmethod
    def assert_isomorphic(cls, lhs: Graph, rhs: Graph) -> None:
        """
        This asserts that the two graphs are isomorphic, providing a nicely
        formatted error message if they are not.
        """

        def format_report() -> str:
            in_both, in_lhs, in_rhs = rdflib.compare.graph_diff(lhs, rhs)
            return (
                "in both:\n"
                f"{cls.format_graph_set(in_both)}"
                "\nonly in first:\n"
                f"{cls.format_graph_set(in_lhs)}"
                "\nonly in second:\n"
                f"{cls.format_graph_set(in_rhs)}"
            )

        assert rdflib.compare.isomorphic(lhs, rhs), format_report()

    @classmethod
    def strip_literal_datatypes(cls, graph: Graph, datatypes: Set[URIRef]) -> None:
        """
        Strips datatypes in the provided set from literals in the graph.
        """
        for object in graph.objects():
            if not isinstance(object, Literal):
                continue
            if object.datatype is None:
                continue
            if object.datatype in datatypes:
                object._datatype = None


GenericT = TypeVar("GenericT", bound=Any)


def make_spypair(method: GenericT) -> Tuple[GenericT, Mock]:
    m = MagicMock()

    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        m(*args, **kwargs)
        return method(self, *args, **kwargs)

    setattr(wrapper, "mock", m)
    return cast(GenericT, wrapper), m


HeadersT = Dict[str, List[str]]
PathQueryT = Dict[str, List[str]]


class MockHTTPRequests(NamedTuple):
    method: str
    path: str
    parsed_path: ParseResult
    path_query: PathQueryT
    headers: email.message.Message


class MockHTTPResponse(NamedTuple):
    status_code: int
    reason_phrase: str
    body: bytes
    headers: HeadersT


class SimpleHTTPMock:
    """
    SimpleHTTPMock allows testing of code that relies on an HTTP server.

    NOTE: Currently only the GET and POST methods is supported.

    Objects of this class has a list of responses for each method (GET, POST, etc...)
    and returns these responses for these methods in sequence.

    All request received are appended to a method specific list.

    Example usage:
    >>> httpmock = SimpleHTTPMock()
    >>> with ctx_http_server(httpmock.Handler) as server:
    ...    url = "http://{}:{}".format(*server.server_address)
    ...    # add a response the server should give:
    ...    httpmock.do_get_responses.append(
    ...        MockHTTPResponse(404, "Not Found", b"gone away", {})
    ...    )
    ...
    ...    # send a request to get the first response
    ...    http_error: Optional[HTTPError] = None
    ...    try:
    ...        urlopen(f"{url}/bad/path")
    ...    except HTTPError as caught:
    ...        http_error = caught
    ...
    ...    assert http_error is not None
    ...    assert http_error.code == 404
    ...
    ...    # get and validate request that the mock received
    ...    req = httpmock.do_get_requests.pop(0)
    ...    assert req.path == "/bad/path"
    """

    # TODO: add additional methods (PUT, PATCH, ...) similar to GET and POST
    def __init__(self):
        self.do_get_requests: List[MockHTTPRequests] = []
        self.do_get_responses: List[MockHTTPResponse] = []

        self.do_post_requests: List[MockHTTPRequests] = []
        self.do_post_responses: List[MockHTTPResponse] = []

        _http_mock = self

        class Handler(SimpleHTTPRequestHandler):
            http_mock = _http_mock

            def _do_GET(self):
                parsed_path = urlparse(self.path)
                path_query = parse_qs(parsed_path.query)
                request = MockHTTPRequests(
                    "GET", self.path, parsed_path, path_query, self.headers
                )
                self.http_mock.do_get_requests.append(request)

                response = self.http_mock.do_get_responses.pop(0)
                self.send_response(response.status_code, response.reason_phrase)
                for header, values in response.headers.items():
                    for value in values:
                        self.send_header(header, value)
                self.end_headers()

                self.wfile.write(response.body)
                self.wfile.flush()
                return

            (do_GET, do_GET_mock) = make_spypair(_do_GET)

            def _do_POST(self):
                parsed_path = urlparse(self.path)
                path_query = parse_qs(parsed_path.query)
                request = MockHTTPRequests(
                    "POST", self.path, parsed_path, path_query, self.headers
                )
                self.http_mock.do_post_requests.append(request)

                response = self.http_mock.do_post_responses.pop(0)
                self.send_response(response.status_code, response.reason_phrase)
                for header, values in response.headers.items():
                    for value in values:
                        self.send_header(header, value)
                self.end_headers()

                self.wfile.write(response.body)
                self.wfile.flush()
                return

            (do_POST, do_POST_mock) = make_spypair(_do_POST)

            def log_message(self, format: str, *args: Any) -> None:
                pass

        self.Handler = Handler
        self.do_get_mock = Handler.do_GET_mock
        self.do_post_mock = Handler.do_POST_mock

    def reset(self):
        self.do_get_requests.clear()
        self.do_get_responses.clear()
        self.do_get_mock.reset_mock()
        self.do_post_requests.clear()
        self.do_post_responses.clear()
        self.do_post_mock.reset_mock()

    @property
    def call_count(self):
        return self.do_post_mock.call_count + self.do_get_mock.call_count


class SimpleHTTPMockTests(unittest.TestCase):
    def test_example(self) -> None:
        httpmock = SimpleHTTPMock()
        with ctx_http_server(httpmock.Handler) as server:
            url = "http://{}:{}".format(*server.server_address)
            # add two responses the server should give:
            httpmock.do_get_responses.append(
                MockHTTPResponse(404, "Not Found", b"gone away", {})
            )
            httpmock.do_get_responses.append(
                MockHTTPResponse(200, "OK", b"here it is", {})
            )

            # send a request to get the first response
            with self.assertRaises(HTTPError) as raised:
                urlopen(f"{url}/bad/path")
            assert raised.exception.code == 404

            # get and validate request that the mock received
            req = httpmock.do_get_requests.pop(0)
            self.assertEqual(req.path, "/bad/path")

            # send a request to get the second response
            resp = urlopen(f"{url}/")
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), b"here it is")

            httpmock.do_get_responses.append(
                MockHTTPResponse(404, "Not Found", b"gone away", {})
            )
            httpmock.do_get_responses.append(
                MockHTTPResponse(200, "OK", b"here it is", {})
            )


class ServedSimpleHTTPMock(SimpleHTTPMock, AbstractContextManager):
    """
    ServedSimpleHTTPMock is a ServedSimpleHTTPMock with a HTTP server.

    Example usage:
    >>> with ServedSimpleHTTPMock() as httpmock:
    ...    # add a response the server should give:
    ...    httpmock.do_get_responses.append(
    ...        MockHTTPResponse(404, "Not Found", b"gone away", {})
    ...    )
    ...
    ...    # send a request to get the first response
    ...    http_error: Optional[HTTPError] = None
    ...    try:
    ...        urlopen(f"{httpmock.url}/bad/path")
    ...    except HTTPError as caught:
    ...        http_error = caught
    ...
    ...    assert http_error is not None
    ...    assert http_error.code == 404
    ...
    ...    # get and validate request that the mock received
    ...    req = httpmock.do_get_requests.pop(0)
    ...    assert req.path == "/bad/path"
    """

    def __init__(self, host: str = "127.0.0.1"):
        super().__init__()
        self.server = HTTPServer((host, 0), self.Handler)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.socket.close()
        self.server_thread.join()

    @property
    def address_string(self) -> str:
        (host, port) = self.server.server_address
        return f"{host}:{port}"

    @property
    def url(self) -> str:
        return f"http://{self.address_string}"

    def __enter__(self) -> "ServedSimpleHTTPMock":
        return self

    def __exit__(
        self,
        __exc_type: Optional[Type[BaseException]],
        __exc_value: Optional[BaseException],
        __traceback: Optional[TracebackType],
    ) -> "te.Literal[False]":
        self.stop()
        return False


class ServedSimpleHTTPMockTests(unittest.TestCase):
    def test_example(self) -> None:
        with ServedSimpleHTTPMock() as httpmock:
            # add two responses the server should give:
            httpmock.do_get_responses.append(
                MockHTTPResponse(404, "Not Found", b"gone away", {})
            )
            httpmock.do_get_responses.append(
                MockHTTPResponse(200, "OK", b"here it is", {})
            )

            # send a request to get the first response
            with self.assertRaises(HTTPError) as raised:
                urlopen(f"{httpmock.url}/bad/path")
            assert raised.exception.code == 404

            # get and validate request that the mock received
            req = httpmock.do_get_requests.pop(0)
            self.assertEqual(req.path, "/bad/path")

            # send a request to get the second response
            resp = urlopen(f"{httpmock.url}/")
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), b"here it is")

            httpmock.do_get_responses.append(
                MockHTTPResponse(404, "Not Found", b"gone away", {})
            )
            httpmock.do_get_responses.append(
                MockHTTPResponse(200, "OK", b"here it is", {})
            )


def eq_(lhs, rhs, msg=None):
    """
    This function mimicks the similar function from nosetest. Ideally nothing
    should use it but there is a lot of code that still does and it's fairly
    simple to just keep this small pollyfill here for now.
    """
    if msg:
        assert lhs == rhs, msg
    else:
        assert lhs == rhs


PurePathT = TypeVar("PurePathT", bound=PurePath)


def file_uri_to_path(
    file_uri: str,
    path_class: Type[PurePathT] = PurePath,  # type: ignore[assignment]
    url2pathname: Optional[Callable[[str], str]] = None,
) -> PurePathT:
    """
    This function returns a pathlib.PurePath object for the supplied file URI.

    :param str file_uri: The file URI ...
    :param class path_class: The type of path in the file_uri. By default it uses
        the system specific path pathlib.PurePath, to force a specific type of path
        pass pathlib.PureWindowsPath or pathlib.PurePosixPath
    :returns: the pathlib.PurePath object
    :rtype: pathlib.PurePath
    """
    is_windows_path = isinstance(path_class(), PureWindowsPath)
    file_uri_parsed = urlparse(file_uri)
    if url2pathname is None:
        if is_windows_path:
            url2pathname = nt_url2pathname
        else:
            url2pathname = unquote
    pathname = url2pathname(file_uri_parsed.path)
    result = path_class(pathname)
    return result
