# https://github.com/RDFLib/rdflib-jsonld/blob/feature/json-ld-1.1/rdflib_jsonld/util.py
from __future__ import annotations

import json
import pathlib
from io import StringIO, TextIOWrapper
from posixpath import normpath, sep
from typing import IO, TYPE_CHECKING, Any, Optional, TextIO, Tuple, Union
from urllib.parse import urljoin, urlsplit, urlunsplit

try:
    import orjson

    _HAS_ORJSON = True
except ImportError:
    orjson = None
    _HAS_ORJSON = False


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
        # We can get the original string from the StringInputSource
        # It's hidden in the BytesIOWrapper 'wrapped' attribute
        b_stream = source.getByteStream()
        original_string: Optional[str] = None
        if isinstance(b_stream, BytesIOWrapper):
            wrapped_inner = b_stream.wrapped
            if isinstance(wrapped_inner, str):
                original_string = wrapped_inner
            elif isinstance(wrapped_inner, StringIO):
                original_string = wrapped_inner.getvalue()

        if _HAS_ORJSON:
            if original_string is not None:
                return orjson.loads(original_string)
            elif isinstance(b_stream, BytesIOWrapper):
                # use the CharacterStream instead
                c_stream = source.getCharacterStream()
                return orjson.loads(c_stream.read())
            else:
                return orjson.loads(b_stream.read())
        else:
            if original_string is not None:
                return json.loads(original_string)
            return json.load(source.getCharacterStream())

    # TODO: conneg for JSON (fix support in rdflib's URLInputSource!)
    source = create_input_source(source, format="json-ld")
    try:
        b_stream = source.getByteStream()
    except (AttributeError, LookupError):
        b_stream = None
    try:
        c_stream = source.getCharacterStream()
    except (AttributeError, LookupError):
        c_stream = None
    if b_stream is None and c_stream is None:
        raise ValueError(
            f"Source does not have a character stream or a byte stream and cannot be used {type(source)}"
        )
    underlying_string: Optional[str] = None
    if b_stream is not None and isinstance(b_stream, BytesIOWrapper):
        # Try to find an underlying string to use?
        wrapped_inner = b_stream.wrapped
        if isinstance(wrapped_inner, str):
            underlying_string = wrapped_inner
        elif isinstance(wrapped_inner, StringIO):
            underlying_string = wrapped_inner.getvalue()
    try:
        if _HAS_ORJSON:
            if underlying_string is not None:
                return orjson.loads(underlying_string)
            elif (
                (b_stream is not None and isinstance(b_stream, BytesIOWrapper))
                or b_stream is None
            ) and c_stream is not None:
                # use the CharacterStream instead
                return orjson.loads(c_stream.read())
            else:
                if TYPE_CHECKING:
                    assert b_stream is not None
                # b_stream is not None
                return orjson.loads(b_stream.read())
        else:
            if underlying_string is not None:
                return json.loads(underlying_string)
            if c_stream is not None:
                use_stream = c_stream
            else:
                if TYPE_CHECKING:
                    assert b_stream is not None
                # b_stream is not None
                use_stream = TextIOWrapper(b_stream, encoding="utf-8")
            return json.load(use_stream)

    finally:
        if b_stream is not None:
            try:
                b_stream.close()
            except AttributeError:
                pass
        if c_stream is not None:
            try:
                c_stream.close()
            except AttributeError:
                pass


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
