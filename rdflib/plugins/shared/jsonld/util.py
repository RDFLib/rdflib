# https://github.com/RDFLib/rdflib-jsonld/blob/feature/json-ld-1.1/rdflib_jsonld/util.py
from __future__ import annotations

import pathlib
from typing import IO, TYPE_CHECKING, Any, List, Optional, TextIO, Tuple, Union

if TYPE_CHECKING:
    import json
else:
    try:
        import json

        assert json  # workaround for pyflakes issue #13
    except ImportError:
        import simplejson as json

from html.parser import HTMLParser
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
    ],
    fragment_id: Optional[str] = None,
    extract_all_scripts: Optional[bool] = False,
) -> Tuple[Any, Any]:
    """Extract JSON from a source document.

    The source document can be JSON or HTML with embedded JSON script elements (type attribute = "application/ld+json").
    To process as HTML ``source.content_type`` must be set to "text/html" or "application/xhtml+xml".

    :param source: the input source document (JSON or HTML)

    :param fragment_id: if source is an HTML document then extract only the script element with matching id attribute, defaults to None

    :param extract_all_scripts: if source is an HTML document then extract all script elements (unless fragment_id is provided), defaults to False (extract only the first script element)

    :return: Tuple with the extracted JSON document and value of the HTML base element
    """

    if isinstance(source, PythonInputSource):
        return (source.data, None)

    if isinstance(source, StringInputSource):
        return (json.load(source.getCharacterStream()), None)

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

        if source.content_type in ("text/html", "application/xhtml+xml"):
            parser = HTMLJSONParser(
                fragment_id=fragment_id, extract_all_scripts=extract_all_scripts
            )
            parser.feed(use_stream.read())
            return (parser.get_json(), parser.get_base())
        else:
            return (json.load(use_stream), None)
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


class HTMLJSONParser(HTMLParser):
    def __init__(
        self,
        fragment_id: Optional[str] = None,
        extract_all_scripts: Optional[bool] = False,
    ):
        super().__init__()
        self.fragment_id = fragment_id
        self.json: List[Any] = []
        self.contains_json = False
        self.fragment_id_does_not_match = False
        self.base = None
        self.extract_all_scripts = extract_all_scripts
        self.script_count = 0

    def handle_starttag(self, tag, attrs):
        self.contains_json = False
        self.fragment_id_does_not_match = False

        # Only set self. contains_json to True if the
        # type is 'application/ld+json'
        if tag == "script":
            for attr, value in attrs:
                if attr == "type" and value == "application/ld+json":
                    self.contains_json = True
                elif attr == "id" and self.fragment_id and value != self.fragment_id:
                    self.fragment_id_does_not_match = True

        elif tag == "base":
            for attr, value in attrs:
                if attr == "href":
                    self.base = value

    def handle_data(self, data):
        # Only do something when we know the context is a
        # script element containing application/ld+json

        if self.contains_json is True and self.fragment_id_does_not_match is False:

            if not self.extract_all_scripts and self.script_count > 0:
                return

            if data.strip() == "":
                # skip empty data elements
                return

            # Try to parse the json
            parsed = json.loads(data)

            # Add to the result document
            if isinstance(parsed, list):
                self.json.extend(parsed)
            else:
                self.json.append(parsed)

            self.script_count += 1

    def get_json(self):
        return self.json

    def get_base(self):
        return self.base
