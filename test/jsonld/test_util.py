import pytest

from rdflib import Graph, URIRef
from rdflib.plugins.shared.jsonld.util import norm_url


@pytest.mark.parametrize(
    ["base", "url", "expected_result"],
    [
        (
            "git+ssh://example.com:1231/some/thing/",
            "a",
            "git+ssh://example.com:1231/some/thing/a",
        ),
        ("http://example.org/", "/one", "http://example.org/one"),
        ("http://example.org/", "/one#", "http://example.org/one#"),
        ("http://example.org/one", "two", "http://example.org/two"),
        ("http://example.org/one/", "two", "http://example.org/one/two"),
        (
            "http://example.org/",
            "http://example.net/one",
            "http://example.net/one",
        ),
        (
            "",
            "1 2 3",
            "1 2 3",
        ),
        (
            "http://example.org/",
            "http://example.org//one",
            "http://example.org//one",
        ),
        ("", "http://example.org", "http://example.org"),
        ("", "http://example.org/", "http://example.org/"),
        ("", "mailto:name@example.com", "mailto:name@example.com"),
        (
            "http://example.org/",
            "mailto:name@example.com",
            "mailto:name@example.com",
        ),
        ("http://example.org/a/b/c", "../../z", "http://example.org/z"),
        ("http://example.org/a/b/c", "../", "http://example.org/a/"),
        (
            "",
            "git+ssh://example.com:1231/some/thing",
            "git+ssh://example.com:1231/some/thing",
        ),
        (
            "git+ssh://example.com:1231/some/thing",
            "",
            "git+ssh://example.com:1231/some/thing",
        ),
        (
            "http://example.com/RDFLib/rdflib",
            "http://example.org",
            "http://example.org",
        ),
        (
            "http://example.com/RDFLib/rdflib",
            "http://example.org/",
            "http://example.org/",
        ),
    ],
)
def test_norm_url(base: str, url: str, expected_result: str) -> None:
    assert expected_result == norm_url(base, url)


# RFC 3986, section 5.4: the normal and abnormal examples of resolving a
# reference against the base below.
RFC3986_BASE = "http://a/b/c/d;p?q"
RFC3986_EXAMPLES = {
    "g:h": "g:h",
    "g": "http://a/b/c/g",
    "./g": "http://a/b/c/g",
    "g/": "http://a/b/c/g/",
    "/g": "http://a/g",
    "//g": "http://g",
    "?y": "http://a/b/c/d;p?y",
    "g?y": "http://a/b/c/g?y",
    "#s": "http://a/b/c/d;p?q#s",
    "g#s": "http://a/b/c/g#s",
    "g?y#s": "http://a/b/c/g?y#s",
    ";x": "http://a/b/c/;x",
    "g;x": "http://a/b/c/g;x",
    "g;x?y#s": "http://a/b/c/g;x?y#s",
    "": "http://a/b/c/d;p?q",
    ".": "http://a/b/c/",
    "./": "http://a/b/c/",
    "..": "http://a/b/",
    "../": "http://a/b/",
    "../g": "http://a/b/g",
    "../..": "http://a/",
    "../../": "http://a/",
    "../../g": "http://a/g",
    "../../../g": "http://a/g",
    "../../../../g": "http://a/g",
    "/./g": "http://a/g",
    "/../g": "http://a/g",
    "g.": "http://a/b/c/g.",
    ".g": "http://a/b/c/.g",
    "g..": "http://a/b/c/g..",
    "..g": "http://a/b/c/..g",
    "./../g": "http://a/b/g",
    "./g/.": "http://a/b/c/g/",
    "g/./h": "http://a/b/c/g/h",
    "g/../h": "http://a/b/c/h",
    "g;x=1/./y": "http://a/b/c/g;x=1/y",
    "g;x=1/../y": "http://a/b/c/y",
    "g?y/./x": "http://a/b/c/g?y/./x",
    "g?y/../x": "http://a/b/c/g?y/../x",
    "g#s/./x": "http://a/b/c/g#s/./x",
    "g#s/../x": "http://a/b/c/g#s/../x",
    "http:g": "http:g",
}


@pytest.mark.parametrize(("url", "expected"), RFC3986_EXAMPLES.items())
def test_norm_url_resolves_the_rfc3986_examples(url: str, expected: str) -> None:
    assert norm_url(RFC3986_BASE, url) == expected


@pytest.mark.parametrize(
    ("base", "url", "expected"),
    [
        pytest.param(
            "http://example.org/a", "//example.net", "http://example.net", id="host"
        ),
        pytest.param(
            "http://example.org", "?q", "http://example.org?q", id="query-no-path"
        ),
        pytest.param(
            "http://example.org/a", "b?", "http://example.org/b?", id="empty-query"
        ),
        pytest.param(
            "http://example.org/a", "b//c", "http://example.org/b//c", id="double-slash"
        ),
        pytest.param(
            "http://example.org/a",
            "b?c=d:e&u=http://example.net/",
            "http://example.org/b?c=d:e&u=http://example.net/",
            id="iri-in-query",
        ),
        pytest.param(
            "http://example.org/a/b",
            "g#x/../y#z",
            "http://example.org/a/g#x/../y#z",
            id="hash-in-fragment",
        ),
        pytest.param(
            "http://user@[::1]:8080/a/b",
            "../c",
            "http://user@[::1]:8080/c",
            id="ipv6-userinfo-port",
        ),
        pytest.param(
            "HTTP://Example.org/a/b", "c", "HTTP://Example.org/a/c", id="uppercase"
        ),
        pytest.param(
            "http://example.org/a#f", "?q", "http://example.org/a?q", id="base-fragment"
        ),
        pytest.param("s3://bucket/a/b", "../c", "s3://bucket/c", id="other-scheme"),
        pytest.param("file:/a/b", "c", "file:/a/c", id="no-authority"),
        pytest.param("urn:ns:test", "?q", "urn:ns:test?q", id="urn-query"),
        pytest.param(
            "tag:example.org,2026:a", "?q", "tag:example.org,2026:a?q", id="tag-query"
        ),
        pytest.param(
            "mailto:a@example.org", "?q", "mailto:a@example.org?q", id="mailto-query"
        ),
    ],
)
def test_norm_url_keeps_what_rfc3986_keeps(base: str, url: str, expected: str) -> None:
    assert norm_url(base, url) == expected


@pytest.mark.parametrize(
    ("base", "url", "expected"),
    [
        pytest.param(
            "http://example.org/a/",
            "2024:report",
            "http://example.org/a/2024:report",
            id="colon-without-scheme",
        ),
        pytest.param(
            "http://example.org/a/", "urn:x:y", "urn:x:y", id="absolute-not-resolved"
        ),
        pytest.param(
            "http://example.org/a",
            "b?u=http://example.net/",
            "b?u=http://example.net/",
            id="authority-after-first-colon",
        ),
        pytest.param(
            "http://example.org/a",
            "b#http://example.net/",
            "b#http://example.net/",
            id="authority-after-first-colon-in-fragment",
        ),
        pytest.param("urn:ns:test", "two", "urn:ns:test/two", id="urn-path"),
        pytest.param("tag:example.org,2026:a", "b", "b", id="tag-path"),
        pytest.param("", "x?q", "x?q", id="no-base"),
    ],
)
def test_norm_url_guards(base: str, url: str, expected: str) -> None:
    """Guard: these were already resolved this way.

    A value whose part after the first colon begins with "//" is not resolved
    (JSON-LD 1.1 API, IRI Expansion, step 6.2).
    """
    assert norm_url(base, url) == expected


def test_the_parser_resolves_references_as_rfc3986_does() -> None:
    doc = """{
        "@context": {"@base": "http://example.org"},
        "@id": "?q",
        "http://example.org/p": [{"@id": "//example.net"}, {"@id": "/x?"}]
    }"""

    g = Graph().parse(data=doc, format="json-ld")

    assert set(g) == {
        (URIRef("http://example.org?q"), URIRef("http://example.org/p"), o)
        for o in (URIRef("http://example.net"), URIRef("http://example.org/x?"))
    }
