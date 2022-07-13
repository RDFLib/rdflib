"""
JSON-LD Context Spec
"""

import json
from functools import wraps
from typing import Any, Dict  # noqa F401

from rdflib.parser import StringInputSource
from rdflib.plugins.shared.jsonld import errors
from rdflib.plugins.shared.jsonld.context import Context
from rdflib.resolver import Resolver, url_resolver


# exception utility (see also nose.tools.raises)
def _expect_exception(expected_error):
    def _try_wrapper(f):
        @wraps(f)
        def _try():
            try:
                f()
                assert e == expected_error
            except Exception as e:
                success = e == expected_error
            else:
                success = False
            assert success, "Expected %r" % expected_error

        return _try

    return _try_wrapper


def test_create_context():
    ctx = Context()
    ctx.add_term("label", "http://example.org/ns/label")
    term = ctx.terms.get("label")

    assert term.name == "label"
    assert ctx.find_term("http://example.org/ns/label") is term


def test_select_term_based_on_value_characteristics():
    ctx = Context()

    ctx.add_term("updated", "http://example.org/ns/updated")
    ctx.add_term(
        "updatedDate",
        "http://example.org/ns/updated",
        coercion="http://www.w3.org/2001/XMLSchema#date",
    )

    assert ctx.find_term("http://example.org/ns/updated").name == "updated"
    assert (
        ctx.find_term(
            "http://example.org/ns/updated",
            coercion="http://www.w3.org/2001/XMLSchema#date",
        ).name
        == "updatedDate"
    )

    # ctx.find_term('http://example.org/ns/title_sv', language='sv')

    # ctx.find_term('http://example.org/ns/authorList', container='@set')

    # ctx.find_term('http://example.org/ns/creator', reverse=True)


def test_getting_keyword_values_from_nodes():
    ctx = Context()
    assert ctx.get_id({"@id": "urn:x:1"}) == "urn:x:1"
    assert ctx.get_language({"@language": "en"}) == "en"


def test_parsing_a_context_expands_prefixes():
    ctx = Context(
        {
            "@vocab": "http://example.org/ns/",
            "x": "http://example.org/ns/",
            "label": "x:label",
            "x:updated": {"@type": "x:date"},
        }
    )

    term = ctx.terms.get("label")

    assert term.id == "http://example.org/ns/label"

    term = ctx.terms.get("x:updated")
    assert term.id == "http://example.org/ns/updated"
    assert term.type == "http://example.org/ns/date"

    # test_expanding_terms():
    assert ctx.expand("term") == "http://example.org/ns/term"
    assert ctx.expand("x:term") == "http://example.org/ns/term"

    # test_shrinking_iris():
    assert ctx.shrink_iri("http://example.org/ns/term") == "x:term"
    assert ctx.to_symbol("http://example.org/ns/term") == "term"


def test_resolving_iris():
    ctx = Context({"@base": "http://example.org/path/leaf"})
    assert ctx.resolve("/") == "http://example.org/"
    assert ctx.resolve("/trail") == "http://example.org/trail"
    assert ctx.resolve("../") == "http://example.org/"
    assert ctx.resolve("../../") == "http://example.org/"


def test_accessing_keyword_values_by_alias():
    ctx = Context({"iri": "@id", "lang": "@language"})
    assert ctx.get_id({"iri": "urn:x:1"}) == "urn:x:1"
    assert ctx.get_language({"lang": "en"}) == "en"

    # test_standard_keywords_still_work():
    assert ctx.get_id({"@id": "urn:x:1"}) == "urn:x:1"

    # test_representing_keywords_by_alias():
    assert ctx.id_key == "iri"
    assert ctx.lang_key == "lang"


def test_creating_a_subcontext():
    ctx = Context()
    ctx4 = ctx.subcontext({"lang": "@language"})
    assert ctx4.get_language({"lang": "en"}) == "en"


def test_prefix_like_vocab():
    ctx = Context({"@vocab": "ex:", "term": "ex:term"})
    term = ctx.terms.get("term")
    assert term.id == "ex:term"


SOURCES = {}


class MockContextResolver(Resolver):
    def __init__(self, contexts):
        self.contexts = contexts

    def is_resolution_allowed(self, scheme: str, location: str) -> bool:
        return str(location) in self.contexts

    @url_resolver(schemes={"http", "https"})
    def resolve_http(self, url, format, scheme, trust=False):
        return StringInputSource(
            json.dumps(self.contexts[str(url)]),
            system_id=str(url),
        )


def test_loading_contexts():
    # Given context data:
    source1 = "http://example.org/base.jsonld"
    source2 = "http://example.org/context.jsonld"
    SOURCES[source1] = {"@context": {"@vocab": "http://example.org/vocab/"}}
    SOURCES[source2] = {"@context": [source1, {"n": "name"}]}

    # Create a context:
    ctx = Context(source2, resolver=MockContextResolver(SOURCES))
    assert ctx.expand("n") == "http://example.org/vocab/name"

    # Context can be a list:
    ctx = Context([source2], resolver=MockContextResolver(SOURCES))
    assert ctx.expand("n") == "http://example.org/vocab/name"


def test_use_base_in_local_context():
    ctx = Context({"@base": "/local"})
    assert ctx.base == "/local"


def test_override_base():
    ctx = Context(
        base="http://example.org/app/data/item", source={"@base": "http://example.org/"}
    )
    assert ctx.base == "http://example.org/"


def test_resolve_relative_base():
    ctx = Context(base="http://example.org/app/data/item", source={"@base": "../"})
    assert ctx.base == "http://example.org/app/"
    assert ctx.resolve_iri("../other") == "http://example.org/other"


def test_set_null_base():
    ctx = Context(base="http://example.org/app/data/item", source={"@base": None})
    assert ctx.base is None
    assert ctx.resolve_iri("../other") == "../other"


def test_ignore_base_remote_context():
    ctx_url = "http://example.org/remote-base.jsonld"
    ctx = Context(
        ctx_url,
        resolver=MockContextResolver({ctx_url: {"@context": {"@base": "/remote"}}}),
    )
    assert ctx.base == None


@_expect_exception(errors.RECURSIVE_CONTEXT_INCLUSION)
def test_recursive_context_inclusion_error():
    ctx_url = "http://example.org/recursive.jsonld"
    Context(ctx_url, resolver=MockContextResolver({ctx_url: {"@context": ctx_url}}))


@_expect_exception(errors.INVALID_REMOTE_CONTEXT)
def test_invalid_remote_context():
    ctx_url = "http://example.org/recursive.jsonld"
    Context(ctx_url, resolver=MockContextResolver({ctx_url: {"key": "value"}}))
