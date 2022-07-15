"""
Parser plugin interface.

This module defines the parser plugin interface and contains other
related parser support code.

The module is mainly useful for those wanting to write a parser that
can plugin to rdflib. If you are wanting to invoke a parser you likely
want to do so through the Graph class parse method.

"""

import codecs
import os
import pathlib
import sys
from io import BufferedIOBase, BytesIO, RawIOBase, StringIO, TextIOBase, TextIOWrapper
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    BinaryIO,
    List,
    Optional,
    TextIO,
    Tuple,
    Union,
)
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import Request, url2pathname, urlopen
from xml.sax import xmlreader

import rdflib.util
from rdflib import __version__
from rdflib.namespace import Namespace
from rdflib.term import URIRef

if TYPE_CHECKING:
    from http.client import HTTPMessage, HTTPResponse

    from rdflib import Graph

__all__ = [
    "Parser",
    "InputSource",
    "StringInputSource",
    "URLInputSource",
    "FileInputSource",
    "PythonInputSource",
]


class Parser(object):
    __slots__ = ()

    def __init__(self):
        pass

    def parse(self, source: "InputSource", sink: "Graph"):
        pass


class BytesIOWrapper(BufferedIOBase):
    __slots__ = ("wrapped", "encoded", "encoding")

    def __init__(self, wrapped: str, encoding="utf-8"):
        super(BytesIOWrapper, self).__init__()
        self.wrapped = wrapped
        self.encoding = encoding
        self.encoded = None

    def read(self, *args, **kwargs):
        if self.encoded is None:
            b, blen = codecs.getencoder(self.encoding)(self.wrapped)
            self.encoded = BytesIO(b)
        return self.encoded.read(*args, **kwargs)

    def read1(self, *args, **kwargs):
        if self.encoded is None:
            b = codecs.getencoder(self.encoding)(self.wrapped)
            self.encoded = BytesIO(b)
        return self.encoded.read1(*args, **kwargs)

    def readinto(self, *args, **kwargs):
        raise NotImplementedError()

    def readinto1(self, *args, **kwargs):
        raise NotImplementedError()

    def write(self, *args, **kwargs):
        raise NotImplementedError()


class InputSource(xmlreader.InputSource, object):
    """
    TODO:
    """

    def __init__(self, system_id: Optional[str] = None):
        xmlreader.InputSource.__init__(self, system_id=system_id)
        self.content_type: Optional[str] = None
        self.auto_close = False  # see Graph.parse(), true if opened by us

    def close(self):
        c = self.getCharacterStream()
        if c and hasattr(c, "close"):
            try:
                c.close()
            except Exception:
                pass
        f = self.getByteStream()
        if f and hasattr(f, "close"):
            try:
                f.close()
            except Exception:
                pass


class PythonInputSource(InputSource):
    """
    Constructs an RDFLib Parser InputSource from a Python data structure,
    for example, loaded from JSON with json.load or json.loads:

    >>> import json
    >>> as_string = \"\"\"{
    ...   "@context" : {"ex" : "http://example.com/ns#"},
    ...   "@graph": [{"@type": "ex:item", "@id": "#example"}]
    ... }\"\"\"
    >>> as_python = json.loads(as_string)
    >>> source = create_input_source(data=as_python)
    >>> isinstance(source, PythonInputSource)
    True
    """

    def __init__(self, data, system_id=None):
        self.content_type = None
        self.auto_close = False  # see Graph.parse(), true if opened by us
        self.public_id = None
        self.system_id = system_id
        self.data = data

    def getPublicId(self):  # noqa: N802
        return self.public_id

    def setPublicId(self, public_id):  # noqa: N802
        self.public_id = public_id

    def getSystemId(self):  # noqa: N802
        return self.system_id

    def setSystemId(self, system_id):  # noqa: N802
        self.system_id = system_id

    def close(self):
        self.data = None


class StringInputSource(InputSource):
    """
    Constructs an RDFLib Parser InputSource from a Python String or Bytes
    """

    def __init__(
        self,
        value: Union[str, bytes],
        encoding: str = "utf-8",
        system_id: Optional[str] = None,
    ):
        super(StringInputSource, self).__init__(system_id)
        stream: Union[BinaryIO, TextIO]
        if isinstance(value, str):
            stream = StringIO(value)
            self.setCharacterStream(stream)
            self.setEncoding(encoding)
            b_stream = BytesIOWrapper(value, encoding)
            self.setByteStream(b_stream)
        else:
            stream = BytesIO(value)
            self.setByteStream(stream)
            c_stream = TextIOWrapper(stream, encoding)
            self.setCharacterStream(c_stream)
            self.setEncoding(c_stream.encoding)


headers = {
    "User-agent": "rdflib-%s (https://rdflib.github.io/; eikeon@eikeon.com)"
    % __version__
}


class URLInputSource(InputSource):
    """
    Constructs an RDFLib Parser InputSource from a URL to read it from the Web.
    """

    links: List[str]

    @classmethod
    def getallmatchingheaders(cls, message: "HTTPMessage", name):
        # This is reimplemented here, because the method
        # getallmatchingheaders from HTTPMessage is broken since Python 3.0
        name = name.lower()
        return [val for key, val in message.items() if key.lower() == name]

    @classmethod
    def get_links(cls, response: "HTTPResponse"):
        linkslines = cls.getallmatchingheaders(response.headers, "Link")
        retarray = []
        for linksline in linkslines:
            links = [linkstr.strip() for linkstr in linksline.split(",")]
            for link in links:
                retarray.append(link)
        return retarray

    def get_alternates(self, type_: Optional[str] = None) -> List[str]:
        typestr: Optional[str] = f'type="{type_}"' if type_ else None
        relstr = 'rel="alternate"'
        alts = []
        for link in self.links:
            parts = [p.strip() for p in link.split(";")]
            if relstr not in parts:
                continue
            if typestr:
                if typestr in parts:
                    alts.append(parts[0].strip("<>"))
            else:
                alts.append(parts[0].strip("<>"))
        return alts

    def __init__(self, system_id: Optional[str] = None, format: Optional[str] = None):
        super(URLInputSource, self).__init__(system_id)
        self.url = system_id

        # copy headers to change
        myheaders = dict(headers)
        if format == "xml":
            myheaders["Accept"] = "application/rdf+xml, */*;q=0.1"
        elif format == "n3":
            myheaders["Accept"] = "text/n3, */*;q=0.1"
        elif format in ["turtle", "ttl"]:
            myheaders["Accept"] = "text/turtle, application/x-turtle, */*;q=0.1"
        elif format == "nt":
            myheaders["Accept"] = "text/plain, */*;q=0.1"
        elif format == "trig":
            myheaders["Accept"] = "application/trig, */*;q=0.1"
        elif format == "trix":
            myheaders["Accept"] = "application/trix, */*;q=0.1"
        elif format == "json-ld":
            myheaders[
                "Accept"
            ] = "application/ld+json, application/json;q=0.9, */*;q=0.1"
        else:
            # if format not given, create an Accept header from all registered
            # parser Media Types
            from rdflib.parser import Parser
            from rdflib.plugin import plugins

            acc = []
            for p in plugins(kind=Parser):  # only get parsers
                if "/" in p.name:  # all Media Types known have a / in them
                    acc.append(p.name)

            myheaders["Accept"] = ", ".join(acc)

        req = Request(system_id, None, myheaders)  # type: ignore[arg-type]

        def _urlopen(req: Request) -> Any:
            try:
                return urlopen(req)
            except HTTPError as ex:
                # 308 (Permanent Redirect) is not supported by current python version(s)
                # See https://bugs.python.org/issue40321
                # This custom error handling should be removed once all
                # supported versions of python support 308.
                if ex.code == 308:
                    req.full_url = ex.headers.get("Location")
                    return _urlopen(req)
                else:
                    raise

        response: HTTPResponse = _urlopen(req)
        self.url = response.geturl()  # in case redirections took place
        self.links = self.get_links(response)
        if format in ("json-ld", "application/ld+json"):
            alts = self.get_alternates(type_="application/ld+json")
            for link in alts:
                full_link = urljoin(self.url, link)
                if full_link != self.url and full_link != system_id:
                    response = _urlopen(Request(full_link))
                    self.url = response.geturl()  # in case redirections took place
                    break

        self.setPublicId(self.url)
        content_types = self.getallmatchingheaders(response.headers, "content-type")
        self.content_type = content_types[0] if content_types else None
        if self.content_type is not None:
            self.content_type = self.content_type.split(";", 1)[0]
        self.setByteStream(response)
        # TODO: self.setEncoding(encoding)
        self.response_info = response.info()  # a mimetools.Message instance

    def __repr__(self):
        return self.url


class FileInputSource(InputSource):
    def __init__(
        self, file: Union[BinaryIO, TextIO, TextIOBase, RawIOBase, BufferedIOBase]
    ):
        base = pathlib.Path.cwd().as_uri()
        system_id = URIRef(pathlib.Path(file.name).absolute().as_uri(), base=base)  # type: ignore[union-attr]
        super(FileInputSource, self).__init__(system_id)
        self.file = file
        if isinstance(file, TextIOBase):  # Python3 unicode fp
            self.setCharacterStream(file)
            self.setEncoding(file.encoding)
            try:
                b = file.buffer  # type: ignore[attr-defined]
                self.setByteStream(b)
            except (AttributeError, LookupError):
                self.setByteStream(file)
        else:
            self.setByteStream(file)
            # We cannot set characterStream here because
            # we do not know the Raw Bytes File encoding.

    def __repr__(self):
        return repr(self.file)


def create_input_source(
    source: Optional[
        Union[IO[bytes], TextIO, InputSource, str, bytes, pathlib.PurePath]
    ] = None,
    publicID: Optional[str] = None,  # noqa: N803
    location: Optional[str] = None,
    file: Optional[Union[BinaryIO, TextIO]] = None,
    data: Union[str, bytes, dict] = None,
    format: str = None,
) -> InputSource:
    """
    Return an appropriate InputSource instance for the given
    parameters.
    """

    # test that exactly one of source, location, file, and data is not None.
    non_empty_arguments = list(
        filter(
            lambda v: v is not None,
            [source, location, file, data],
        )
    )

    if len(non_empty_arguments) != 1:
        raise ValueError(
            "exactly one of source, location, file or data must be given",
        )

    input_source = None

    if source is not None:
        if isinstance(source, InputSource):
            input_source = source
        else:
            if isinstance(source, str):
                location = source
            elif isinstance(source, pathlib.PurePath):
                location = str(source)
            elif isinstance(source, bytes):
                data = source
            elif hasattr(source, "read") and not isinstance(source, Namespace):  # type: ignore[unreachable]
                f = source
                input_source = InputSource()
                if hasattr(source, "encoding"):
                    input_source.setCharacterStream(source)
                    input_source.setEncoding(source.encoding)  # type: ignore[union-attr]
                    try:
                        b = file.buffer  # type: ignore[union-attr]
                        input_source.setByteStream(b)
                    except (AttributeError, LookupError):
                        input_source.setByteStream(source)
                else:
                    input_source.setByteStream(f)
                if f is sys.stdin:
                    input_source.setSystemId("file:///dev/stdin")
                elif hasattr(f, "name"):
                    input_source.setSystemId(f.name)
            else:
                raise Exception(
                    "Unexpected type '%s' for source '%s'" % (type(source), source)
                )

    absolute_location = None  # Further to fix for issue 130

    auto_close = False  # make sure we close all file handles we open

    if location is not None:
        (
            absolute_location,
            auto_close,
            file,
            input_source,
        ) = _create_input_source_from_location(
            file=file,
            format=format,
            input_source=input_source,
            location=location,
        )

    if file is not None:
        input_source = FileInputSource(file)

    if data is not None:
        if isinstance(data, dict):
            input_source = PythonInputSource(data)
            auto_close = True
        elif isinstance(data, (str, bytes, bytearray)):
            input_source = StringInputSource(data)
            auto_close = True
        else:
            raise RuntimeError(f"parse data can only str, or bytes. not: {type(data)}")

    if input_source is None:
        raise Exception("could not create InputSource")
    else:
        input_source.auto_close |= auto_close
        if publicID is not None:  # Further to fix for issue 130
            input_source.setPublicId(publicID)
        # Further to fix for issue 130
        elif input_source.getPublicId() is None:
            input_source.setPublicId(absolute_location or "")
        return input_source


def _create_input_source_from_location(
    file: Optional[Union[BinaryIO, TextIO]],
    format: Optional[str],
    input_source: Optional[InputSource],
    location: str,
) -> Tuple[URIRef, bool, Optional[Union[BinaryIO, TextIO]], Optional[InputSource]]:
    # Fix for Windows problem https://github.com/RDFLib/rdflib/issues/145 and
    # https://github.com/RDFLib/rdflib/issues/1430
    # NOTE: using pathlib.Path.exists on a URL fails on windows as it is not a
    # valid path. However os.path.exists() returns false for a URL on windows
    # which is why it is being used instead.
    if os.path.exists(location):
        location = pathlib.Path(location).absolute().as_uri()

    base = pathlib.Path.cwd().as_uri()

    absolute_location = URIRef(rdflib.util._iri2uri(location), base=base)

    if absolute_location.startswith("file:///"):
        filename = url2pathname(absolute_location.replace("file:///", "/"))
        file = open(filename, "rb")
    else:
        input_source = URLInputSource(absolute_location, format)

    auto_close = True
    # publicID = publicID or absolute_location  # Further to fix
    # for issue 130

    return absolute_location, auto_close, file, input_source
