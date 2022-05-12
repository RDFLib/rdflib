import email.message
import enum
import logging
import random
from collections import defaultdict
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ContextManager,
    Dict,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypeVar,
    cast,
)
from unittest.mock import MagicMock, Mock
from urllib.parse import ParseResult, parse_qs, urlparse

if TYPE_CHECKING:
    import typing_extensions as te


def get_random_ip(ip_prefix: Optional[List[str]] = None) -> str:
    if ip_prefix is None:
        parts = ["127"]
    for _ in range(4 - len(parts)):
        parts.append(f"{random.randint(0, 255)}")
    return ".".join(parts)


@contextmanager
def ctx_http_server(
    handler: Type[BaseHTTPRequestHandler], host: Optional[str] = "127.0.0.1"
) -> Iterator[HTTPServer]:
    host = get_random_ip() if host is None else host
    server = HTTPServer((host, 0), handler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    yield server
    server.shutdown()
    server.socket.close()
    server_thread.join()


GenericT = TypeVar("GenericT", bound=Any)


def make_spypair(method: GenericT) -> Tuple[GenericT, Mock]:
    m = MagicMock()

    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        m(*args, **kwargs)
        return method(self, *args, **kwargs)

    setattr(wrapper, "mock", m)  # noqa
    return cast(GenericT, wrapper), m


HeadersT = Dict[str, List[str]]
PathQueryT = Dict[str, List[str]]


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


class MockHTTPResponse(NamedTuple):
    status_code: int
    reason_phrase: str
    body: bytes
    headers: HeadersT


RequestDict = Dict[MethodName, List[MockHTTPRequest]]
ResponseDict = Dict[MethodName, List[MockHTTPResponse]]


class BaseHTTPServerMock:
    def __init__(self) -> None:
        self.requests: Dict[MethodName, List[MockHTTPRequest]] = defaultdict(
            lambda: list()
        )
        self.responses: Dict[MethodName, List[MockHTTPResponse]] = defaultdict(
            lambda: list()
        )
        self.mocks: Dict[MethodName, Mock] = {}

        class Handler(BaseHTTPRequestHandler):
            pass

        self.Handler = Handler

        for name in MethodName:
            name_str = name.name
            do_handler, mock = make_spypair(
                self.make_do_handler(name, self.requests, self.responses)
            )
            setattr(self.Handler, f"do_{name_str}", do_handler)
            self.mocks[name] = mock

    @classmethod
    def make_do_handler(
        cls, method_name: MethodName, requests: RequestDict, responses: ResponseDict
    ) -> Callable[[BaseHTTPRequestHandler], None]:
        def do_handler(handler: BaseHTTPRequestHandler) -> None:
            parsed_path = urlparse(handler.path)
            path_query = parse_qs(parsed_path.query)
            body = None
            content_length = handler.headers.get("Content-Length")
            if content_length is not None:
                body = handler.rfile.read(int(content_length))
            request = MockHTTPRequest(
                method_name,
                handler.path,
                parsed_path,
                path_query,
                handler.headers,
                body,
            )
            logging.debug("handling %s request: %s", method_name, request)
            requests[method_name].append(request)

            response = responses[method_name].pop(0)
            handler.send_response(response.status_code, response.reason_phrase)
            for header, values in response.headers.items():
                for value in values:
                    handler.send_header(header, value)
            handler.end_headers()

            handler.wfile.write(response.body)
            handler.wfile.flush()
            return

        return do_handler

    def reset(self) -> None:
        self.requests.clear()
        self.responses.clear()
        for name in MethodName:
            self.mocks[name].reset_mock()

    @property
    def call_count(self) -> int:
        return sum(self.mocks[name].call_count for name in MethodName)


class ServedBaseHTTPServerMock(
    BaseHTTPServerMock, ContextManager["ServedBaseHTTPServerMock"]
):
    def __init__(self, host: Optional[str] = "127.0.0.1") -> None:
        super().__init__()
        host = get_random_ip() if host is None else host
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

    def __enter__(self) -> "ServedBaseHTTPServerMock":
        return self

    def __exit__(
        self,
        __exc_type: Optional[Type[BaseException]],
        __exc_value: Optional[BaseException],
        __traceback: Optional[TracebackType],
    ) -> "te.Literal[False]":
        self.stop()
        return False
