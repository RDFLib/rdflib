from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Callable,
    MutableMapping,
    MutableSequence,
    Optional,
    Pattern,
    Tuple,
    Union,
)
from urllib.error import URLError

# from urllib.request import OpenerDirector, URLopener

if TYPE_CHECKING:
    # # from http.client import HTTPMessage, HTTPResponse
    from urllib.request import Request
    from urllib.response import addinfourl

    from rdflib._type_checking import _URLOpenerType

    # # from rdflib import Graph
    # _URLOpenerType = Callable[[Request], addinfourl]


# class URIForbiddenError(ValueError):
#     """
#     Raised when an attempt is made to load a forbidden URI.
#     """

#     def __init__(self, uri: str, reason: str, *args: object) -> None:
#         super().__init__(
#             (f"loading of uri={uri!r} forbidden" f": {reason}"),
#             uri,
#             reason,
#             *args,
#         )


class URIForbiddenError(URLError):
    """
    Raised when an attempt is made to load a forbidden URI.
    """

    def __init__(
        self, reason: Union[str, BaseException], filename: Optional[str] = None
    ) -> None:
        """
        :param reason: The reason for the error.
        :param filename: The URI that caused the error.
        """
        super().__init__(
            f"loading of uri={filename!r} forbidden" f": {reason}", filename
        )

    # def __init__(self, reason: Unionstr) -> None:
    #     super().__init__(reason, uri)


# class URINotFound(ValueError):
#     """
#     Raised when the requested URI is not found.
#     """

#     def __init__(self, uri: str, reason: str, *args: object) -> None:
#         super().__init__(
#             (f"uri={uri!r} not found" f": {reason}"),
#             uri,
#             reason,
#             *args,
#         )


# class LoadedResource(abc.ABC):
#     ...


# class LoadedResource(abc.ABC):
#     """
#     A resource that has been loaded from a URI.
#     """

#     @property
#     @abc.abstractmethod
#     def requested_uri(self) -> str:
#         """
#         The URI that was requested.
#         """
#         ...

#     @property
#     @abc.abstractmethod
#     def base_uri(self) -> str:
#         """
#         The URI that was used to load the resource.
#         """
#         ...

#     @property
#     @abc.abstractmethod
#     def binary_io(self) -> BinaryIO:
#         """
#         A binary IO object that can be used to read the resource.
#         """
#         ...

#     @property
#     @abc.abstractmethod
#     def encoding(self) -> str:
#         """
#         The encoding of the resource.
#         """
#         ...


# class OptionalURILoader(abc.ABC):
#     """
#     Loads an input source for URIs
#     """

#     @abc.abstractmethod
#     def load_uri(
#         self,
#         uri: str,
#         mime_type: Optional[str] = None,
#     ) -> Optional[InputSource]:
#         """
#         Loads an input source for the given URI.
#         """
#         ...


# class URILoader(OptionalURILoader, abc.ABC):
#     """
#     Loads an input source for URIs
#     """

#     @abc.abstractmethod
#     def load_uri(self, uri: str, mime_type: Optional[str] = None) -> InputSource:
#         ...


# class URILoaderSequence(URILoader):
#     loaders: MutableSequence[OptionalURILoader] = field(default_factory=list)

#     def load_uri(self, uri: str, mime_type: Optional[str] = None) -> InputSource:
#         for loader in self.loaders:
#             input_source = loader.load_uri(uri, mime_type)
#             if input_source is not None:
#                 return input_source
#         raise URINotFound(uri, mime_type, "no URI loader returned a result")


# @dataclass(frozen=True)
# class ResourceReference:
#     uri: str
#     mime_type: str

#     @property


def _copy_request(req: Request, *, url: Optional[str]) -> Request:
    """
    Copy a request object and replace the supplied kwargs.

    :param req: The request to copy.
    :param url: The URL to use in the copy.
    :return: The copy of the request.
    """
    return Request(
        url if url is not None else req.full_url,
        req.data,
        req.headers,
        req.origin_req_host,
        req.unverifiable,
        req.method,
    )


class URIFilterResult(abc.ABC):
    """
    The result of :py:meth:`OptionalURIFitler.check_uri` and
    :py:meth:`URIFitler.check_uri`.

    This should not be used directly, one of the subclasses should be used
    instead.
    """

    pass


class URIFilterAllowed(URIFilterResult):
    """
    Indicates that the URI is allowed.

    If this is returned no further filters will be checked. This is useful for
    allowlisting URIs.
    """

    pass


@dataclass
class URIFilterForbidden(URIFilterResult):
    """
    Indicates that the URI is forbidden.

    If this is returned no further filters will be checked. This is useful for
    denylisting URIs.

    :param reason: The reason for the URI being forbidden.
    """

    reason: str


class OptionalURIFitler(abc.ABC):
    """
    Determines if an URI is allowed or forbidden.
    """

    @abc.abstractmethod
    def check_uri(self, uri: str) -> Optional[URIFilterResult]:
        """
        Determines if an URI is allowed or forbidden.

        :param uri: The URI to check.
        :return: :py:class:`URIFilterAllowed` if the URI is allowed,
            :py:class:`URIFilterForbidden` if the URI is forbidden, or
            :py:obj:`None` if the filter makes no pronouncement on the supplied
            URI.
        """
        ...


class URIFitler(abc.ABC):
    """
    Determines if an URI is allowed or forbidden.
    """

    @abc.abstractmethod
    def check_uri(self, uri: str) -> URIFilterResult:
        """
        Determines if an URI is allowed or forbidden.

        :param uri: The URI to check.
        :return: :py:class:`URIFilterAllowed` if the URI is allowed,
            :py:class:`URIFilterForbidden` if the URI is forbidden.
        """
        ...

    def wrap_opener(self, urlopener: _URLOpenerType) -> _URLOpenerType:
        def _wrapper(request: Request) -> addinfourl:
            result = self.check_uri(request.full_url)
            if isinstance(result, URIFilterForbidden):
                raise URIForbiddenError(result.reason, request.full_url)
            return urlopener(request)

        return _wrapper


# class MappedURI(abc.ABC):
#     @property
#     @abc.abstractmethod
#     def uri(self) -> str:
#         ...

#     @property
#     @abc.abstractmethod
#     def redirects(self) -> Sequence[str]:
#         ...

# @dataclass(frozen=True)
# class SimpleMappedURI(MappedURI):
#     uri: str
#     redirects: Sequence[str] = field(default_factory=list)


class URIMapper(abc.ABC):
    """
    Maps one URI to another
    """

    @abc.abstractmethod
    def map_uri(self, uri: str) -> Optional[str]:
        """
        Maps one URI to another.

        :param uri: The URI to map.
        :return: The mapped URI, or :py:obj:`None` if the URI remains untouched.
        """
        ...

    def map_or_return_uri(self, uri: str) -> str:
        """
        Maps one URI to another or returns the original URI if the mapper does
        not map the URI.

        :param uri: The URI to map.
        :return: The mapped URI or if the mapper does not map the URI then the
            original URI is returned.
        """
        mapped_uri = self.map_uri(uri)
        return uri if mapped_uri is None else mapped_uri

    def wrap_opener(self, urlopener: _URLOpenerType) -> _URLOpenerType:
        def _wrapper(request: Request) -> addinfourl:
            mapped_uri = self.map_uri(request.full_url)
            if mapped_uri is not None:
                request = _copy_request(request, url=mapped_uri)
            return urlopener(request)

        return _wrapper


@dataclass
class URIFitlerSequence(URIFitler):
    """
    A sequence of URI filters.

    The filters are checked in order, and the first filter that returns result
    (i.e. not `None`) is used. If no filters return a result then the default
    result is returned.

    :param filters: The filters to check.
    :param default_result: The result to return if no filters return a result.
    """

    filters: MutableSequence[OptionalURIFitler] = field(default_factory=list)
    default_result: URIFilterResult = field(default_factory=URIFilterAllowed)

    def check_uri(self, uri: str) -> URIFilterResult:
        """
        Determines if an URI is allowed or forbidden.

        :param uri: The URI to check.
        :return: :py:class:`URIFilterAllowed` if the URI is allowed,
            :py:class:`URIFilterForbidden` if the URI is forbidden.
        """
        for filter in self.filters:
            result = filter.check_uri(uri)
            if result is not None:
                return result
        return self.default_result


@dataclass
class GenericURIFitler(OptionalURIFitler):
    """
    A generic URI filter that uses a callable to determine if a URI is allowed
    or forbidden.

    :param filter: A callable that takes a URI and returns
        :py:class:`URIFilterAllowed` if the URI is allowed,
        :py:class:`URIFilterForbidden` if the URI is forbidden, or
        :py:obj:`None` if the filter makes no pronouncement on the supplied
        URI.
    """

    filter: Callable[[str, Optional[str]], Optional[URIFilterResult]]

    def check_uri(
        self, uri: str, mime_type: Optional[str] = None
    ) -> Optional[URIFilterResult]:
        """
        Determines if an URI is allowed or forbidden.

        :param uri: The URI to check.
        :return: :py:class:`URIFilterAllowed` if the URI is allowed,
            :py:class:`URIFilterForbidden` if the URI is forbidden, or
            :py:obj:`None` if the filter makes no pronouncement on the supplied
            URI.
        """
        return self.filter(uri, mime_type)

    @classmethod
    def from_regex(
        cls, pattern: Pattern[str], result: URIFilterResult
    ) -> OptionalURIFitler:
        """
        Creates a URI filter from a regular expression.

        :param pattern: The regular expression to match against.
        :param result: The result to return if the URI matches the regular
            expression.
        """
        return GenericURIFitler(
            lambda uri, mime_type: result if pattern.match(uri) else None
        )

    @classmethod
    def from_prefix(cls, prefix: str, result: URIFilterResult) -> OptionalURIFitler:
        """
        Creates a URI filter from a prefix.

        :param prefix: The prefix to match against.
        :param result: The result to return if the URI starts with the prefix.
        """
        return GenericURIFitler(
            lambda uri, mime_type: result if uri.startswith(prefix) else None
        )

    @classmethod
    def from_string(
        cls, string: Pattern[str], result: URIFilterResult
    ) -> OptionalURIFitler:
        """
        Creates a URI filter from a string.

        This is useful for allowlisting or denylisting a specific URI.

        :param string: The string to match against.
        :param result: The result to return if the URI is equal to the string.
        """
        return GenericURIFitler(
            lambda uri, mime_type: result if uri == string else None
        )


def _replace_prefix(value: str, prefix: str, replacement: str) -> Optional[str]:
    """
    Replaces the prefix of a string with a replacement.
    """
    if value.startswith(prefix):
        return f"{replacement}:{value[len(prefix):]}"
    return None


@dataclass
class GenericURIMapper(URIMapper):
    """
    A generic URI mapper that maps a URI to another URI based on fixed string
    mappings or prefix mappings.

    :param uri_mappings: A mapping of URIs to URIs.
    :param prefix_mappings: A sequence of prefix mappings. Each prefix mapping
        is a tuple of a prefix and a replacement. If a URI starts with the
        prefix then the prefix is replaced with the replacement.
    """

    uri_mappings: MutableMapping[str, str] = field(default_factory=dict)
    prefix_mappings: MutableSequence[Tuple[str, str]] = field(default_factory=list)

    def map_uri(self, uri: str) -> str:
        """
        Maps one URI to another.

        :param uri: The URI to map.
        :return: The mapped URI or :py:obj:`None` if the URI is not mapped.
        """
        try:
            return self.uri_mappings[uri]
        except KeyError:
            # no exact mapping, try prefixes
            pass
        for prefix, replacement in self.prefix_mappings:
            replaced = _replace_prefix(uri, prefix, replacement)
            if replaced is not None:
                return replaced
        return uri


# @dataclass
# class FilteringURIMapper(URIMapper):
#     """
#     A URI mapper that applies a URI filter to the mapped URI if the URI is
#     re-mapped, or to the supplied URI if the URI is not re-mapped.

#     :param mapper: The URI mapper to use, defaults to
#         :py:class:`GenericURIMapper`.
#     :param filter: The URI filter to use, defaults to
#         :py:class:`URIFitlerSequence`.
#     """

#     mapper: Optional[URIMapper] = field(default_factory=GenericURIMapper)
#     filter: Optional[URIFitler] = field(default_factory=URIFitlerSequence)

#     def map_uri(self, uri: str) -> Optional[str]:
#         """
#         Maps one URI to another.

#         :param uri: The URI to map.
#         :return: The mapped URI or :py:obj:`None` if the URI is not mapped.
#         """
#         mapped_uri: Optional[str] = None
#         if self.mapper is not None:
#             mapped_uri = self.mapper.map_uri(uri)
#             # if mapped_uri is not None:
#             #     uri = mapped_uri

#         uri_to_filter = mapped_uri if mapped_uri is not None else uri
#         if self.filter is not None:
#             filter_result = self.filter.check_uri(uri_to_filter)
#             if isinstance(filter_result, URIFilterForbidden):
#                 raise URIForbiddenError(uri_to_filter, filter_result.reason)

#         return mapped_uri
#         # # mapped_uri = self.mapper.map_uri(uri, mime_type)
#         # # if self.filter.check_uri(mapped_uri, mime_type) is not None:
#         # #     return mapped_uri
#         # return uri


# URI_MAPPER = FilteringURIMapper()


# @dataclass
# class GenericURILoader(URILoader):
#     mapper: Optional[URIMapper] = field(default_factory=GenericURIMapper)
#     filter: Optional[URIFitler] = field(default_factory=URIFitlerSequence)
#     loader: URILoader = field(default_factory=URILoaderSequence)

#     def load_uri(self, uri: str, mime_type: Optional[str] = None) -> InputSource:
#         if self.mapper is not None:
#             mapped_uri = self.mapper.map_uri(uri)
#             if mapped_uri is not None:

#                 uri = mapped_uri
#         if self.filter is not None:
#             filter_result = self.filter.check_uri(uri)
#             if isinstance(filter_result, URIForbidden):
#                 raise URIForbiddenError(uri, mime_type, filter_result.reason)
#         return self.loader.load_uri(uri, mime_type)


# class SimpleURILoader(URILoader):
#     def load_uri(self, uri: str, mime_type: Optional[str] = None) -> InputSource:


# def _none() -> None:
#     opener_director = OpenerDirector()
#     result = opener_director.open("http://example.com")
#     result.read()
