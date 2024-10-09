from __future__ import annotations

from contextlib import ExitStack
from copy import deepcopy
from typing import Any, Dict, Iterable, Optional, Type, TypeVar, Union
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request

import pytest
from _pytest.mark.structures import ParameterSet

from rdflib._networking import _make_redirect_request
from test.utils.http import headers_as_message as headers_as_message
from test.utils.outcome import ExceptionChecker

AnyT = TypeVar("AnyT")


def with_attrs(object: AnyT, **kwargs: Any) -> AnyT:
    for key, value in kwargs.items():
        setattr(object, key, value)
    return object


class RaisesIdentity:
    pass


def generate_make_redirect_request_cases() -> Iterable[ParameterSet]:
    yield pytest.param(
        Request("http://example.com/data.ttl"),
        HTTPError(
            "",
            308,
            "Permanent Redirect",
            headers_as_message({}),
            None,
        ),
        RaisesIdentity,
        {},
        id="Exception passes through if no Location header is present",
    )
    yield pytest.param(
        Request("http://example.com/data.ttl"),
        HTTPError(
            "",
            308,
            "Permanent Redirect",
            headers_as_message({"Location": [100]}),  # type: ignore[arg-type]
            None,
        ),
        ExceptionChecker(ValueError, "Location header 100 is not a string"),
        {},
        id="Location must be a string",
    )
    yield pytest.param(
        Request("http://example.com/data.ttl"),
        HTTPError(
            "",
            308,
            "Permanent Redirect",
            headers_as_message({"Location": ["example:data.ttl"]}),
            None,
        ),
        ExceptionChecker(
            HTTPError,
            "HTTP Error 308: Permanent Redirect - Redirection to url 'example:data.ttl' is not allowed",
            {"code": 308},
        ),
        {},
        id="Error passes through with a slight alterations if the Location header is not a supported URL",
    )

    url_prefix = "http://example.com"
    for request_url_suffix, redirect_location, new_url_suffix in [
        ("/data.ttl", "", "/data.ttl"),
        ("", "", ""),
        ("/data.ttl", "a", "/a"),
        ("", "a", "/a"),
        ("/a/b/c/", ".", "/a/b/c/"),
        ("/a/b/c", ".", "/a/b/"),
        ("/a/b/c/", "..", "/a/b/"),
        ("/a/b/c", "..", "/a/"),
        ("/a/b/c/", "/", "/"),
        ("/a/b/c/", "/x/", "/x/"),
        ("/a/b/c/", "/x/y", "/x/y"),
        ("/a/b/c/", f"{url_prefix}", ""),
        ("/a/b/c/", f"{url_prefix}/", "/"),
        ("/a/b/c/", f"{url_prefix}/a/../b", "/a/../b"),
        ("/", f"{url_prefix}/   /data.ttl", "/%20%20%20/data.ttl"),
    ]:
        request_url = f"http://example.com{request_url_suffix}"
        new_url = f"http://example.com{new_url_suffix}"
        yield pytest.param(
            Request(request_url),
            HTTPError(
                "",
                308,
                "Permanent Redirect",
                headers_as_message({"Location": [redirect_location]}),
                None,
            ),
            Request(new_url, unverifiable=True),
            {new_url: 1},
            id=f"Redirect from {request_url!r} to {redirect_location!r} is correctly handled",
        )

    yield pytest.param(
        Request(
            "http://example.com/data.ttl",
            b"foo",
            headers={
                "Content-Type": "text/plain",
                "Content-Length": "3",
                "Accept": "text/turtle",
            },
        ),
        HTTPError(
            "",
            308,
            "Permanent Redirect",
            headers_as_message({"Location": ["http://example.org/data.ttl"]}),
            None,
        ),
        Request(
            "http://example.org/data.ttl",
            headers={"Accept": "text/turtle"},
            origin_req_host="example.com",
            unverifiable=True,
        ),
        {"http://example.org/data.ttl": 1},
        id="Headers transfer correctly",
    )

    yield pytest.param(
        with_attrs(
            Request(
                "http://example.com/data1.ttl",
            ),
            redirect_dict=dict(
                (f"http://example.com/redirect/{index}", 1)
                for index in range(HTTPRedirectHandler.max_redirections)
            ),
        ),
        HTTPError(
            "",
            308,
            "Permanent Redirect",
            headers_as_message({"Location": ["http://example.org/data2.ttl"]}),
            None,
        ),
        ExceptionChecker(
            HTTPError,
            f"HTTP Error 308: {HTTPRedirectHandler.inf_msg}Permanent Redirect",
        ),
        {},
        id="Max redirects is respected",
    )

    yield pytest.param(
        with_attrs(
            Request(
                "http://example.com/data1.ttl",
            ),
            redirect_dict={
                "http://example.org/data2.ttl": HTTPRedirectHandler.max_repeats
            },
        ),
        HTTPError(
            "",
            308,
            "Permanent Redirect",
            headers_as_message({"Location": ["http://example.org/data2.ttl"]}),
            None,
        ),
        ExceptionChecker(
            HTTPError,
            f"HTTP Error 308: {HTTPRedirectHandler.inf_msg}Permanent Redirect",
        ),
        {},
        id="Max repeats is respected",
    )


@pytest.mark.parametrize(
    ("http_request", "http_error", "expected_result", "expected_redirect_dict"),
    generate_make_redirect_request_cases(),
)
def test_make_redirect_request(
    http_request: Request,
    http_error: HTTPError,
    expected_result: Union[Type[RaisesIdentity], ExceptionChecker, Request],
    expected_redirect_dict: Dict[str, int],
) -> None:
    """
    `_make_redirect_request` correctly handles redirects.
    """
    catcher: Optional[pytest.ExceptionInfo[Exception]] = None
    result: Optional[Request] = None
    with ExitStack() as stack:
        if isinstance(expected_result, ExceptionChecker):
            catcher = stack.enter_context(expected_result.context())
        elif expected_result is RaisesIdentity:
            catcher = stack.enter_context(pytest.raises(HTTPError))
        result = _make_redirect_request(http_request, http_error)

    if isinstance(expected_result, ExceptionChecker):
        assert catcher is not None
    elif isinstance(expected_result, type):
        assert catcher is not None
        assert http_error is catcher.value
    else:
        assert expected_redirect_dict == getattr(result, "redirect_dict", None)
        assert expected_redirect_dict == getattr(http_request, "redirect_dict", None)
        check = deepcopy(expected_result)
        check.unverifiable = True
        check = with_attrs(check, redirect_dict=expected_redirect_dict)
        assert vars(check) == vars(result)
