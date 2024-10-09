from __future__ import annotations

import logging
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ContextManager,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    cast,
)
from unittest.mock import MagicMock, Mock
from urllib.parse import parse_qs, urlparse

from test.utils.http import (
    MethodName,
    MockHTTPRequest,
    MockHTTPResponse,
    apply_headers_to,
    get_random_ip,
)

__all__: List[str] = ["make_spypair", "BaseHTTPServerMock", "ServedBaseHTTPServerMock"]

if TYPE_CHECKING:
    import typing_extensions as te


GenericT = TypeVar("GenericT", bound=Any)


def make_spypair(method: GenericT) -> Tuple[GenericT, Mock]:
    m = MagicMock()

    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        m(*args, **kwargs)
        return method(self, *args, **kwargs)

    setattr(wrapper, "mock", m)
    return cast(GenericT, wrapper), m


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
            logging.debug("headers %s", request.headers)
            requests[method_name].append(request)

            try:
                response = responses[method_name].pop(0)
            except IndexError as error:
                raise ValueError(f"No response for {method_name} request") from error
            handler.send_response(response.status_code, response.reason_phrase)
            apply_headers_to(response.headers, handler)
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
        if isinstance(host, (bytes, bytearray)):
            host = host.decode("utf-8")
        return f"{host}:{port}"

    @property
    def url(self) -> str:
        return f"http://{self.address_string}"

    def __enter__(self) -> ServedBaseHTTPServerMock:
        return self

    def __exit__(
        self,
        __exc_type: Optional[Type[BaseException]],
        __exc_value: Optional[BaseException],
        __traceback: Optional[TracebackType],
    ) -> te.Literal[False]:
        self.stop()
        return False
