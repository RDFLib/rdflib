from __future__ import annotations

import collections
import email.message
import enum
import random
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import (
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from urllib.parse import ParseResult

from test.utils.wildcard import EQ_WILDCARD

__all__: List[str] = []

HeadersT = Union[Dict[str, List[str]], Iterable[Tuple[str, str]]]
PathQueryT = Dict[str, List[str]]


def header_items(headers: HeadersT) -> Iterable[Tuple[str, str]]:
    if isinstance(headers, collections.abc.Mapping):
        for header, value in headers.items():
            if isinstance(value, list):
                for item in value:
                    yield header, item
    else:
        yield from headers


def apply_headers_to(headers: HeadersT, handler: BaseHTTPRequestHandler) -> None:
    for header, value in header_items(headers):
        handler.send_header(header, value)
    # handler.end_headers()


class MethodName(str, enum.Enum):
    CONNECT = enum.auto()
    DELETE = enum.auto()
    GET = enum.auto()
    HEAD = enum.auto()
    OPTIONS = enum.auto()
    PATCH = enum.auto()
    POST = enum.auto()
    PUT = enum.auto()
    TRACE = enum.auto()


class MockHTTPRequest(NamedTuple):
    method: MethodName
    path: str
    parsed_path: ParseResult
    path_query: PathQueryT
    headers: email.message.Message
    body: Optional[bytes]


MOCK_HTTP_REQUEST_WILDCARD = MockHTTPRequest(
    EQ_WILDCARD, EQ_WILDCARD, EQ_WILDCARD, EQ_WILDCARD, EQ_WILDCARD, EQ_WILDCARD
)
"""
This object should be equal to any `MockHTTPRequest` object.
"""


class MockHTTPResponse(NamedTuple):
    status_code: int
    reason_phrase: str
    body: bytes
    headers: HeadersT


def get_random_ip(ip_prefix: Optional[List[str]] = None) -> str:
    if ip_prefix is None:
        parts = ["127"]
    for _ in range(4 - len(parts)):
        parts.append(f"{random.randint(0, 255)}")
    return ".".join(parts)


@contextmanager
def ctx_http_handler(
    handler: Type[BaseHTTPRequestHandler], host: Optional[str] = "127.0.0.1"
) -> Iterator[HTTPServer]:
    host = get_random_ip() if host is None else host
    server = HTTPServer((host, 0), handler)
    with ctx_http_server(server) as server:
        yield server


HTTPServerT = TypeVar("HTTPServerT", bound=HTTPServer)


@contextmanager
def ctx_http_server(server: HTTPServerT) -> Iterator[HTTPServerT]:
    server_thread = Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    yield server
    server.shutdown()
    server.socket.close()
    server_thread.join()


def headers_as_message(headers: HeadersT) -> email.message.Message:
    message = email.message.Message()
    for header, value in header_items(headers):
        # This will append the value to any existing values for the header
        # instead of replacing it.
        message[header] = value
    return message
