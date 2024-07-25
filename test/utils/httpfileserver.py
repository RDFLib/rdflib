from __future__ import annotations

import enum
import logging
import posixpath
from dataclasses import dataclass, field
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Type
from urllib.parse import parse_qs, urljoin, urlparse
from uuid import uuid4

from test.utils.http import HeadersT, MethodName, MockHTTPRequest, apply_headers_to

__all__: List[str] = [
    "LocationType",
    "ProtoResource",
    "Resource",
    "ProtoRedirectResource",
    "ProtoFileResource",
    "RedirectResource",
    "FileResource",
    "HTTPFileInfo",
    "HTTPFileServer",
]


class LocationType(enum.Enum):
    RELATIVE_PATH = enum.auto()
    ABSOLUTE_PATH = enum.auto()
    URL = enum.auto()


@dataclass(
    frozen=True,
)
class ProtoResource:
    headers: HeadersT


@dataclass(frozen=True)
class Resource(ProtoResource):
    url_path: str
    url: str


@dataclass(frozen=True)
class ProtoRedirectResource(ProtoResource):
    status: int
    location_type: LocationType


@dataclass(frozen=True)
class ProtoFileResource(ProtoResource):
    file_path: Path


@dataclass(frozen=True)
class RedirectResource(Resource, ProtoRedirectResource):
    location: str


@dataclass(frozen=True)
class FileResource(Resource, ProtoFileResource):
    pass


@dataclass(frozen=True)
class HTTPFileInfo:
    """
    Information about a file served by the HTTPFileServerRequestHandler.

    :param request_url: The URL that should be requested to get the file.
    :param effective_url: The URL that the file will be served from after
        redirects.
    :param redirects: A sequence of redirects that will be given to the client
        if it uses the ``request_url``. This sequence will terminate in the
        ``effective_url``.
    """

    # request_url: str
    # effective_url: str
    file: FileResource
    redirects: Sequence[RedirectResource] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return self.file.file_path

    @property
    def request_url(self) -> str:
        """
        The URL that should be requested to get the file.
        """
        if self.redirects:
            return self.redirects[0].url
        else:
            return self.file.url

    @property
    def effective_url(self) -> str:
        """
        The URL that the file will be served from after
        redirects.
        """
        return self.file.url


class HTTPFileServer(HTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        bind_and_activate: bool = True,
    ) -> None:
        self._resources: Dict[str, Resource] = {}
        self.Handler = self.make_handler()
        super().__init__(server_address, self.Handler, bind_and_activate)

    @property
    def url(self) -> str:
        (host, port) = self.server_address
        if isinstance(host, (bytes, bytearray)):
            host = host.decode("utf-8")
        return f"http://{host}:{port}"

    @lru_cache(maxsize=1024)
    def add_file_with_caching(
        self,
        proto_file: ProtoFileResource,
        proto_redirects: Optional[Sequence[ProtoRedirectResource]] = None,
        suffix: str = "",
    ) -> HTTPFileInfo:
        return self.add_file(proto_file, proto_redirects, suffix)

    def add_file(
        self,
        proto_file: ProtoFileResource,
        proto_redirects: Optional[Sequence[ProtoRedirectResource]] = None,
        suffix: str = "",
    ) -> HTTPFileInfo:
        url_path = f"/file/{uuid4().hex}{suffix}"
        url = urljoin(self.url, url_path)
        file_resource = FileResource(
            url_path=url_path,
            url=url,
            file_path=proto_file.file_path,
            headers=proto_file.headers,
        )
        self._resources[url_path] = file_resource

        if proto_redirects is None:
            proto_redirects = []

        redirects: List[RedirectResource] = []
        for proto_redirect in reversed(proto_redirects):
            redirect_url_path = f"/redirect/{uuid4().hex}{suffix}"
            if proto_redirect.location_type == LocationType.URL:
                location = url
            elif proto_redirect.location_type == LocationType.ABSOLUTE_PATH:
                location = url_path
            elif proto_redirect.location_type == LocationType.RELATIVE_PATH:
                location = posixpath.relpath(url_path, redirect_url_path)
            else:
                raise ValueError(
                    f"unsupported location_type={proto_redirect.location_type}"
                )
            url_path = redirect_url_path
            url = urljoin(self.url, url_path)
            redirect_resource = RedirectResource(
                url_path=url_path,
                url=url,
                status=proto_redirect.status,
                location_type=proto_redirect.location_type,
                location=location,
                headers=proto_redirect.headers,
            )
            self._resources[url_path] = redirect_resource

        file_info = HTTPFileInfo(file_resource, redirects)
        return file_info

    def make_handler(self) -> Type[BaseHTTPRequestHandler]:
        class Handler(BaseHTTPRequestHandler):
            server: HTTPFileServer

            def do_GET(self) -> None:  # noqa: N802
                parsed_path = urlparse(self.path)
                path_query = parse_qs(parsed_path.query)
                body = None
                content_length = self.headers.get("Content-Length")
                if content_length is not None:
                    body = self.rfile.read(int(content_length))
                method_name = MethodName.GET
                request = MockHTTPRequest(
                    method_name,
                    self.path,
                    parsed_path,
                    path_query,
                    self.headers,
                    body,
                )
                logging.debug("handling %s request: %s", method_name, request)
                logging.debug("headers %s", request.headers)

                resource_path = parsed_path.path
                if resource_path not in self.server._resources:
                    self.send_error(404, "File not found")
                    return

                resource = self.server._resources[resource_path]
                if isinstance(resource, FileResource):
                    self.send_response(200)
                elif isinstance(resource, RedirectResource):
                    self.send_response(resource.status)
                    self.send_header("Location", resource.location)
                apply_headers_to(resource.headers, self)

                self.end_headers()

                if isinstance(resource, FileResource):
                    with resource.file_path.open("rb") as f:
                        self.wfile.write(f.read())
                        self.wfile.flush()
                return

        Handler.server = self

        return Handler
