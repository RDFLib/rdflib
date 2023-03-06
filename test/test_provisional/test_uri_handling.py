import re
from typing import Optional
import pytest
from rdflib._provisional.uri_handling import (
    URI_FILTER_ALLOWED,
    GenericURIFitler,
    GenericURIMapper,
    URIFilterForbidden,
    URIFitler,
    URIMapper,
    URIFilterResult,
    URIFitler,
    _replace_prefix,
)


@pytest.mark.parametrize(
    ["filter", "uri", "expected_result"],
    [
        (
            GenericURIFitler().with_prefix(
                "http://", URIFilterForbidden("http is forbidden")
            ),
            "http://example.com",
            URIFilterForbidden("http is forbidden"),
        ),
        (
            GenericURIFitler()
            .with_string("http://example.com", URI_FILTER_ALLOWED)
            .with_prefix("http://", URIFilterForbidden("http is forbidden")),
            "http://example.com",
            URI_FILTER_ALLOWED,
        ),
        (
            GenericURIFitler()
            .with_prefix("http://", URIFilterForbidden("http is forbidden"))
            .with_string("http://example.com", URI_FILTER_ALLOWED),
            "http://example.com",
            URIFilterForbidden("http is forbidden"),
        ),
        (
            GenericURIFitler().with_callable(
                lambda uri: URIFilterForbidden("callable forbade it")
                if uri.endswith(".com")
                else URI_FILTER_ALLOWED
            ),
            "http://example.com",
            URIFilterForbidden("callable forbade it"),
        ),
        (
            GenericURIFitler(URIFilterForbidden("No filters matched"))
            .with_prefix("https://", URI_FILTER_ALLOWED)
            .with_string("http://example.com/bypass", URI_FILTER_ALLOWED)
            .with_regex(
                re.compile(r"^http://example.com/.*/backdoor/$"), URI_FILTER_ALLOWED
            ),
            "http://example.com",
            URIFilterForbidden("No filters matched"),
        ),
        (
            GenericURIFitler(URIFilterForbidden("No filters matched"))
            .with_prefix("https://", URI_FILTER_ALLOWED)
            .with_string("http://example.com/bypass", URI_FILTER_ALLOWED)
            .with_regex(
                re.compile(r"^http://example.com/.*/backdoor/$"), URI_FILTER_ALLOWED
            ),
            "https://example.com",
            URI_FILTER_ALLOWED,
        ),
        (
            GenericURIFitler(URIFilterForbidden("No filters matched"))
            .with_prefix("https://", URI_FILTER_ALLOWED)
            .with_string("http://example.com/bypass", URI_FILTER_ALLOWED)
            .with_regex(
                re.compile(r"^http://example.com/.*/backdoor/$"), URI_FILTER_ALLOWED
            ),
            "http://example.com/bypass",
            URI_FILTER_ALLOWED,
        ),
        (
            GenericURIFitler(URIFilterForbidden("No filters matched"))
            .with_prefix("https://", URI_FILTER_ALLOWED)
            .with_string("http://example.com/bypass", URI_FILTER_ALLOWED)
            .with_regex(
                re.compile(r"^http://example.com/.*/backdoor/$"), URI_FILTER_ALLOWED
            ),
            "http://example.com/zzz/backdoor/",
            URI_FILTER_ALLOWED,
        ),
    ],
)
def test_filter(filter: URIFitler, uri: str, expected_result: URIFilterResult) -> None:
    assert filter.check_uri(uri) == expected_result


@pytest.mark.parametrize(
    ["mapper", "uri", "expected_result"],
    [
        (GenericURIMapper(), "http://example.com", None),
        (
            GenericURIMapper({"http://example.com": "http://example.net"}),
            "http://example.com",
            "http://example.net",
        ),
        (
            # URI is only mapped once
            GenericURIMapper(
                {"http://example.com": "http://example.net"}, [("http://", "https://")]
            ),
            "http://example.com",
            "http://example.net",
        ),
        (
            # URI is only mapped once
            GenericURIMapper(
                {"http://example.com": "http://example.net"}, [("http://", "https://")]
            ),
            "http://example.net",
            "https://example.net",
        ),
    ],
)
def test_mapper(mapper: URIMapper, uri: str, expected_result: Optional[str]) -> None:
    actual_result = mapper.map_uri(uri)
    assert expected_result == actual_result
    if actual_result is None:
        assert uri == mapper.map_or_return_uri(uri)


@pytest.mark.parametrize(
    ["value", "prefix", "replacement", "expected_result"],
    [
        ("http://example.com", "http://", "https://", "https://example.com"),
        ("http://example.com", "https://", "https://", None),
    ],
)
def test__replace_prefix(
    value: str, prefix: str, replacement: str, expected_result: Optional[str]
) -> None:
    """
    `_replace_prefix` returns the expected result for the given value, prefix
    and replacement.
    """
    assert expected_result == _replace_prefix(value, prefix, replacement)

def _file_uri_open()

def test_filter_wrapper() -> None:
