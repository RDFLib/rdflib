import sys
import isodate
import datetime
import random

from contextlib import contextmanager
from typing import (
    List,
    Type,
    Iterator,
    Set,
    Tuple,
    Dict,
    Any,
    TypeVar,
    cast,
    NamedTuple,
)
from urllib.parse import ParseResult, urlparse, parse_qs
from traceback import print_exc
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import email.message
from nose import SkipTest
from .earl import add_test, report

from rdflib import BNode, Graph, ConjunctiveGraph
from rdflib.term import Node
from unittest.mock import MagicMock, Mock


# TODO: make an introspective version (like this one) of
# rdflib.graphutils.isomorphic and use instead.
def crapCompare(g1, g2):
    """A really crappy way to 'check' if two graphs are equal. It ignores blank
    nodes completely and ignores subgraphs."""
    if len(g1) != len(g2):
        raise Exception("Graphs dont have same length")
    for t in g1:
        s = _no_blank(t[0])
        o = _no_blank(t[2])
        if not (s, t[1], o) in g2:
            e = "(%s, %s, %s) is not in both graphs!" % (s, t[1], o)
            raise Exception(e)


def _no_blank(node):
    if isinstance(node, BNode):
        return None
    if isinstance(node, Graph):
        return None  # node._Graph__identifier = _SQUASHED_NODE
    return node


def check_serialize_parse(fpath, infmt, testfmt, verbose=False):
    g = ConjunctiveGraph()
    _parse_or_report(verbose, g, fpath, format=infmt)
    if verbose:
        for t in g:
            print(t)
        print("========================================")
        print("Parsed OK!")
    s = g.serialize(format=testfmt)
    if verbose:
        print(s)
    g2 = ConjunctiveGraph()
    _parse_or_report(verbose, g2, data=s, format=testfmt)
    if verbose:
        print(g2.serialize())
    crapCompare(g, g2)


def _parse_or_report(verbose, graph, *args, **kwargs):
    try:
        graph.parse(*args, **kwargs)
    except:
        if verbose:
            print("========================================")
            print("Error in parsing serialization:")
            print(args, kwargs)
        raise


def nose_tst_earl_report(generator, earl_report_name=None):
    from optparse import OptionParser

    p = OptionParser()
    (options, args) = p.parse_args()

    skip = 0
    tests = 0
    success = 0

    for t in generator(args):
        tests += 1
        print("Running ", t[1].uri)
        try:
            t[0](t[1])
            add_test(t[1].uri, "passed")
            success += 1
        except SkipTest as e:
            add_test(t[1].uri, "untested", e.message)
            print("skipping %s - %s" % (t[1].uri, e.message))
            skip += 1

        except KeyboardInterrupt:
            raise
        except AssertionError:
            add_test(t[1].uri, "failed")
        except:
            add_test(t[1].uri, "failed", "error")
            print_exc()
            sys.stderr.write("%s\n" % t[1].uri)

    print(
        "Ran %d tests, %d skipped, %d failed. " % (tests, skip, tests - skip - success)
    )
    if earl_report_name:
        now = isodate.datetime_isoformat(datetime.datetime.utcnow())
        earl_report = "test_reports/%s-%s.ttl" % (
            earl_report_name,
            now.replace(":", ""),
        )

        report.serialize(earl_report, format="n3")
        report.serialize("test_reports/%s-latest.ttl" % earl_report_name, format="n3")
        print("Wrote EARL-report to '%s'" % earl_report)


def get_random_ip(parts: List[str] = None) -> str:
    if parts is None:
        parts = ["127"]
    for _ in range(4 - len(parts)):
        parts.append(f"{random.randint(0, 255)}")
    return ".".join(parts)


@contextmanager
def ctx_http_server(handler: Type[BaseHTTPRequestHandler]) -> Iterator[HTTPServer]:
    host = get_random_ip()
    server = HTTPServer((host, 0), handler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    yield server
    server.shutdown()
    server.socket.close()
    server_thread.join()


class GraphHelper:
    @classmethod
    def triple_set(cls, graph: Graph) -> Set[Tuple[Node, Node, Node]]:
        return set(graph.triples((None, None, None)))

    @classmethod
    def equals(cls, lhs: Graph, rhs: Graph) -> bool:
        return cls.triple_set(lhs) == cls.triple_set(rhs)


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
    # TODO: add additional methods (POST, PUT, ...) similar to get
    def __init__(self):
        self.do_get_requests: List[MockHTTPRequests] = []
        self.do_get_responses: List[MockHTTPResponse] = []

        _http_mock = self

        class Handler(SimpleHTTPRequestHandler):
            http_mock = _http_mock

            def _do_GET(self):
                parsed_path = urlparse(self.path)
                path_query = parse_qs(parsed_path.query)
                request = MockHTTPRequests(
                    self.path, parsed_path, path_query, self.headers
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

        self.Handler = Handler
        self.do_get_mock = Handler.do_GET_mock

    def reset(self):
        self.do_get_requests.clear()
        self.do_get_responses.clear()
        self.do_get_mock.reset_mock()
