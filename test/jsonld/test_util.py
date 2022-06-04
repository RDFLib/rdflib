import pytest

from rdflib.plugins.shared.jsonld.util import norm_url


@pytest.mark.parametrize(
    ["base", "url", "expected_result"],
    [
        pytest.param(
            "git+ssh://example.com:1231/some/thing/",
            "a",
            "git+ssh://example.com:1231/some/thing/a",
            marks=pytest.mark.xfail(
                reason="""
    URL normalizes to the wrong thing.

    AssertionError: assert 'git+ssh://example.com:1231/some/thing/a' == 'a'
    """,
                raises=AssertionError,
            ),
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
def test_norm_url_xfail(base: str, url: str, expected_result: str) -> None:
    assert expected_result == norm_url(base, url)
