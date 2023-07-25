# -*- coding: utf-8 -*-
# https://github.com/RDFLib/rdflib-jsonld/blob/feature/json-ld-1.1/rdflib_jsonld/util.py
from __future__ import annotations

import pathlib
from typing import IO, TYPE_CHECKING, Any, Optional, TextIO, Tuple, Union

if TYPE_CHECKING:
    import json
else:
    try:
        import json

        assert json  # workaround for pyflakes issue #13
    except ImportError:
        import simplejson as json

from io import TextIOBase, TextIOWrapper
from posixpath import normpath, sep
from urllib.parse import urljoin, urlsplit, urlunsplit

from rdflib.parser import (
    BytesIOWrapper,
    InputSource,
    PythonInputSource,
    StringInputSource,
    URLInputSource,
    create_input_source,
)


def source_to_json(
    source: Optional[
        Union[IO[bytes], TextIO, InputSource, str, bytes, pathlib.PurePath]
    ]
) -> Optional[Any]:
    if isinstance(source, PythonInputSource):
        return source.data

    if isinstance(source, StringInputSource):
        return json.load(source.getCharacterStream())

    # TODO: conneg for JSON (fix support in rdflib's URLInputSource!)
    source = create_input_source(source, format="json-ld")
    stream = source.getByteStream()
    try:
        if isinstance(stream, BytesIOWrapper):
            stream = stream.wrapped
        # Use character stream as-is, or interpret byte stream as UTF-8
        if isinstance(stream, TextIOBase):
            use_stream = stream
        else:
            use_stream = TextIOWrapper(stream, encoding="utf-8")
        return json.load(use_stream)
    finally:
        stream.close()


VOCAB_DELIMS = ("#", "/", ":")


def split_iri(iri: str) -> Tuple[str, Optional[str]]:
    for delim in VOCAB_DELIMS:
        at = iri.rfind(delim)
        if at > -1:
            return iri[: at + 1], iri[at + 1 :]
    return iri, None


def norm_url(base: str, url: str) -> str:
    """
    >>> norm_url('http://example.org/', '/one')
    'http://example.org/one'
    >>> norm_url('http://example.org/', '/one#')
    'http://example.org/one#'
    >>> norm_url('http://example.org/one', 'two')
    'http://example.org/two'
    >>> norm_url('http://example.org/one/', 'two')
    'http://example.org/one/two'
    >>> norm_url('http://example.org/', 'http://example.net/one')
    'http://example.net/one'
    >>> norm_url('http://example.org/', 'http://example.org//one')
    'http://example.org//one'
    """
    if "://" in url:
        return url
    parts = urlsplit(urljoin(base, url))
    path = normpath(parts[2])
    if sep != "/":
        path = "/".join(path.split(sep))
    if parts[2].endswith("/") and not path.endswith("/"):
        path += "/"
    result = urlunsplit(parts[0:2] + (path,) + parts[3:])
    if url.endswith("#") and not result.endswith("#"):
        result += "#"
    return result


# type error: Missing return statement
def context_from_urlinputsource(source: URLInputSource) -> Optional[str]:  # type: ignore[return]
    """
    Please note that JSON-LD documents served with the application/ld+json media type
    MUST have all context information, including references to external contexts,
    within the body of the document. Contexts linked via a
    http://www.w3.org/ns/json-ld#context HTTP Link Header MUST be
    ignored for such documents.
    """
    if source.content_type != "application/ld+json":
        try:
            # source.links is the new way of getting Link headers from URLInputSource
            links = source.links
        except AttributeError:
            # type error: Return value expected
            return  # type: ignore[return-value]
        for link in links:
            if ' rel="http://www.w3.org/ns/json-ld#context"' in link:
                i, j = link.index("<"), link.index(">")
                if i > -1 and j > -1:
                    # type error: Value of type variable "AnyStr" of "urljoin" cannot be "Optional[str]"
                    return urljoin(source.url, link[i + 1 : j])  # type: ignore[type-var]


__all__ = [
    "json",
    "source_to_json",
    "split_iri",
    "norm_url",
    "context_from_urlinputsource",
]
