from __future__ import annotations

# from rdflib._provisional.uri_handling import URI_MAPPER
import urllib.request
from typing import TYPE_CHECKING, Callable, Optional, Union
from urllib.error import HTTPError

if TYPE_CHECKING:
    # from http.client import HTTPMessage, HTTPResponse
    from urllib.request import Request
    from urllib.response import addinfourl

    # from rdflib import Graph
    _URLOpenerType = Callable[[Request], addinfourl]


__all__ = ["_get_accept_header", "URL_OPENER", "_urlopen_shim"]


# def _copy_request(req: Request, *, url: Optional[str]) -> Request:
#     """
#     Copy a request object and replace the supplied kwargs.

#     :param req: The request to copy.
#     :param url: The URL to use in the copy.
#     :return: The copy of the request.
#     """
#     return Request(
#         url if url is not None else req.full_url,
#         req.data,
#         req.headers,
#         req.origin_req_host,
#         req.unverifiable,
#         req.method,
#     )


def _urlopen(req: Request) -> addinfourl:
    """
    Wrapper around urllib.request.urlopen that handles HTTP 308 redirects.

    This is a temporary workaround for https://bugs.python.org/issue40321

    :param req: The request to open.
    :return: The response which is the same as :py:func:`urllib.request.urlopen`
        responses.
    """
    try:
        return urllib.request.urlopen(req)
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


URL_OPENER: _URLOpenerType = _urlopen
"""
The function used by RDFLib to open URLs. This is compatible with
:py:func:`urllib.request.urlopen` but more restricted for simplicity.
"""


def _urlopen_shim(
    req: Request, *, url_opener: Optional[_URLOpenerType] = None
) -> addinfourl:
    """
    Shim that either calls the provided URL opener if it is not `None` or
    `URL_OPENER` if the provided URL opener is `None`.

    :param url_opener: The URL opener to use if it is not `None`.
    :param req: The request to open.
    :return: The response which is the same as :py:func:`urllib.request.urlopen`
    """
    if url_opener is None:
        return URL_OPENER(req)
    return url_opener(req)


# _URLOPENER: _URLOpenerType = _urlopen


def _get_accept_header(format: Optional[str]) -> str:
    """
    Create an Accept header for the given format.

    :param format: The format to create an Accept header for.
    :return: The Accept header value.
    """
    if format == "xml":
        return "application/rdf+xml, */*;q=0.1"
    elif format == "n3":
        return "text/n3, */*;q=0.1"
    elif format in ["turtle", "ttl"]:
        return "text/turtle, application/x-turtle, */*;q=0.1"
    elif format == "nt":
        return "text/plain, */*;q=0.1"
    elif format == "trig":
        return "application/trig, */*;q=0.1"
    elif format == "trix":
        return "application/trix, */*;q=0.1"
    elif format == "json-ld":
        return "application/ld+json, application/json;q=0.9, */*;q=0.1"
    else:
        # if format not given, create an Accept header from all registered
        # parser Media Types
        from rdflib.parser import Parser
        from rdflib.plugin import plugins

        acc = []
        for p in plugins(kind=Parser):  # only get parsers
            if "/" in p.name:  # all Media Types known have a / in them
                acc.append(p.name)

        return ", ".join(acc)
