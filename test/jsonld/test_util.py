import unittest
from typing import NamedTuple

from rdflib.plugins.shared.jsonld.util import norm_url


class URLTests(unittest.TestCase):
    @unittest.expectedFailure
    def test_norm_url_xfail(self):
        class TestSpec(NamedTuple):
            base: str
            url: str
            result: str

        tests = [
            TestSpec(
                "git+ssh://example.com:1231/some/thing/",
                "a",
                "git+ssh://example.com:1231/some/thing/a",
            ),
        ]

        for test in tests:
            (base, url, result) = test
            with self.subTest(base=base, url=url):
                self.assertEqual(norm_url(base, url), result)

    def test_norm_url(self):
        class TestSpec(NamedTuple):
            base: str
            url: str
            result: str

        tests = [
            TestSpec("http://example.org/", "/one", "http://example.org/one"),
            TestSpec("http://example.org/", "/one#", "http://example.org/one#"),
            TestSpec("http://example.org/one", "two", "http://example.org/two"),
            TestSpec("http://example.org/one/", "two", "http://example.org/one/two"),
            TestSpec(
                "http://example.org/",
                "http://example.net/one",
                "http://example.net/one",
            ),
            TestSpec(
                "",
                "1 2 3",
                "1 2 3",
            ),
            TestSpec(
                "http://example.org/",
                "http://example.org//one",
                "http://example.org//one",
            ),
            TestSpec("", "http://example.org", "http://example.org"),
            TestSpec("", "http://example.org/", "http://example.org/"),
            TestSpec("", "mailto:name@example.com", "mailto:name@example.com"),
            TestSpec(
                "http://example.org/",
                "mailto:name@example.com",
                "mailto:name@example.com",
            ),
            TestSpec("http://example.org/a/b/c", "../../z", "http://example.org/z"),
            TestSpec("http://example.org/a/b/c", "../", "http://example.org/a/"),
            TestSpec(
                "",
                "git+ssh://example.com:1231/some/thing",
                "git+ssh://example.com:1231/some/thing",
            ),
            TestSpec(
                "git+ssh://example.com:1231/some/thing",
                "",
                "git+ssh://example.com:1231/some/thing",
            ),
            TestSpec(
                "http://example.com/RDFLib/rdflib",
                "http://example.org",
                "http://example.org",
            ),
            TestSpec(
                "http://example.com/RDFLib/rdflib",
                "http://example.org/",
                "http://example.org/",
            ),
        ]

        for test in tests:
            (base, url, result) = test
            with self.subTest(base=base, url=url):
                self.assertEqual(norm_url(base, url), result)
