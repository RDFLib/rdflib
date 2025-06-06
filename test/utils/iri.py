"""
Various utilities for working with IRIs and URIs.
"""

from __future__ import annotations

import email.utils
import http.client
import logging
import mimetypes
from dataclasses import dataclass
from nturl2path import url2pathname as nt_url2pathname
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from typing import Callable, TypeVar, Union
from urllib.parse import quote, unquote, urljoin, urlparse, urlsplit, urlunsplit
from urllib.request import BaseHandler, OpenerDirector, Request
from urllib.response import addinfourl

from test.utils import ensure_suffix

PurePathT = TypeVar("PurePathT", bound=PurePath)


def file_uri_to_path(
    file_uri: str,
    path_class: type[PurePathT] = PurePath,  # type: ignore[assignment]
    url2pathname: Callable[[str], str] | None = None,
) -> PurePathT:
    """
    This function returns a pathlib.PurePath object for the supplied file URI.

    Args:
        file_uri: The file URI ...
        path_class: The type of path in the file_uri. By default it uses
            the system specific path pathlib.PurePath, to force a specific type of path
            pass pathlib.PureWindowsPath or pathlib.PurePosixPath

    Returns:
        The pathlib.PurePath object
    """
    is_windows_path = isinstance(path_class(), PureWindowsPath)
    file_uri_parsed = urlparse(file_uri)
    if url2pathname is None:
        if is_windows_path:
            # def _url2pathname(uri_path: str) -> str:
            #     return nt_url2pathname(unquote(uri_path))
            # url2pathname = _url2pathname
            url2pathname = nt_url2pathname
        else:
            url2pathname = unquote
    pathname = url2pathname(file_uri_parsed.path)
    result = path_class(pathname)
    return result


def rebase_url(old_url: str, old_base: str, new_base: str) -> str:
    logging.debug(
        "old_url = %s, old_base = %s, new_base = %s", old_url, old_base, new_base
    )
    if not old_base.endswith("/"):
        raise ValueError(
            f"base URI should end with '/' but old_base {old_base!r} does not"
        )
    if not new_base.endswith("/"):
        raise ValueError(
            f"base URI should end with '/' but new_base {new_base!r} does not"
        )
    old_surl = urlsplit(old_url)
    old_base_surl = urlsplit(old_base)
    if (old_surl.scheme, old_surl.netloc) != (
        old_base_surl.scheme,
        old_base_surl.netloc,
    ):
        raise ValueError(
            f"{old_url} does not have the same scheme or netlog as {old_base}"
        )
    old_path = PurePosixPath(unquote(old_surl.path))
    old_base_path = PurePosixPath(unquote(old_base_surl.path))
    rpath = old_path.relative_to(old_base_path)
    logging.debug("rpath = %s", rpath)
    joined = urljoin(new_base, quote(f"{rpath}"))
    new_surl = urlsplit(joined)
    new_url = urlunsplit(
        (
            new_surl.scheme,
            new_surl.netloc,
            new_surl.path,
            old_surl.query,
            old_surl.fragment,
        )
    )
    if old_url.endswith("/"):
        new_url = ensure_suffix(new_url, "/")
    logging.debug("result = %s", new_url)
    return new_url


URIMappingTupleType = tuple[str, str]


@dataclass(frozen=True)
class URIMapping:
    remote: str
    local: str

    @classmethod
    def from_tuple(cls, value: URIMappingTupleType) -> URIMapping:
        return cls(value[0], value[1])


@dataclass
class URIMapper:
    mappings: set[URIMapping]

    def to_local_uri(self, remote: str) -> str:
        return self._map(remote, to_local=True)

    def to_local_path(self, remote: str) -> Path:
        local_uri = self.to_local_uri(remote)
        logging.debug("local_uri = %s", local_uri)
        return file_uri_to_path(local_uri, Path)

    def to_local(self, remote: str) -> tuple[str, Path]:
        local_uri = self.to_local_uri(remote)
        local_path = file_uri_to_path(local_uri, Path)
        return (local_uri, local_path)

    def to_remote(self, local: Union[str, PurePath]) -> str:
        return self._map(local, to_local=False)

    def _map(self, value: Union[str, PurePath], to_local: bool = True) -> str:
        error: ValueError | None = None
        mapping: URIMapping
        uri = value.as_uri() if isinstance(value, PurePath) else value
        for mapping in self.mappings:
            try:
                if to_local:
                    return rebase_url(uri, mapping.remote, mapping.local)
                else:
                    return rebase_url(uri, mapping.local, mapping.remote)
            except ValueError as e:
                error = e
                continue
        error_msg = f"could not map {value} to remote"
        if error is not None:
            raise LookupError(error_msg) from error
        else:
            raise LookupError(error_msg)

    @classmethod
    def from_mappings(
        cls, *values: Union[URIMapping, URIMappingTupleType]
    ) -> URIMapper:
        result = set()
        for value in values:
            if isinstance(value, tuple):
                value = URIMapping.from_tuple(value)
            result.add(value)
        return cls(result)

    def opener(self) -> OpenerDirector:
        opener = OpenerDirector()

        opener.add_handler(URIMapperHTTPHandler(self))

        return opener


class URIMapperHTTPHandler(BaseHandler):
    def __init__(self, mapper: URIMapper):
        self.mapper = mapper

    def http_open(self, req: Request) -> addinfourl:
        url = req.get_full_url()
        local_uri, local_path = self.mapper.to_local(url)
        stats = local_path.stat()
        size = stats.st_size
        modified = email.utils.formatdate(stats.st_mtime, usegmt=True)
        mtype = mimetypes.guess_type(f"{local_path}")[0]
        headers = email.message_from_string(
            "Content-type: %s\nContent-length: %d\nLast-modified: %s\n"
            % (mtype or "text/plain", size, modified)
        )
        return addinfourl(local_path.open("rb"), headers, url, http.client.OK)
