"""
JSON-LD Context Spec
"""

from __future__ import annotations

import json
from functools import wraps
from pathlib import Path
from typing import Any, Literal, Optional, Union, assert_type

import pytest

from rdflib import Graph, URIRef
from rdflib import Literal as RDFLiteral
from rdflib.namespace import PROV, RDF, XSD, Namespace
from rdflib.plugins.shared.jsonld import context, errors
from rdflib.plugins.shared.jsonld.context import UNDEF, Context, Defined


# exception utility (see also nose.tools.raises)
def _expect_exception(expected_error):
    def _try_wrapper(f):
        @wraps(f)
        def _try():
            try:
                f()
                assert e == expected_error  # noqa: F821
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


# Mock external sources loading
SOURCES: dict[str, dict[str, Any]] = {}
# type error: Module "rdflib.plugins.shared.jsonld.context" does not explicitly export attribute "source_to_json"
_source_to_json = context.source_to_json  # type: ignore[attr-defined]


def _mock_source_loader(f):
    @wraps(f)
    def _wrapper():
        try:
            context.source_to_json = lambda source: (SOURCES.get(source), None)
            f()
        finally:
            context.source_to_json = _source_to_json

    return _wrapper


@_mock_source_loader
def test_loading_contexts():
    # Given context data:
    source1 = "http://example.org/base.jsonld"
    source2 = "http://example.org/context.jsonld"
    SOURCES[source1] = {"@context": {"@vocab": "http://example.org/vocab/"}}
    SOURCES[source2] = {"@context": [source1, {"n": "name"}]}

    # Create a context:
    ctx = Context(source2)
    assert ctx.expand("n") == "http://example.org/vocab/name"

    # Context can be a list:
    ctx = Context([source2])
    assert ctx.expand("n") == "http://example.org/vocab/name"


@_mock_source_loader
def test_use_base_in_local_context():
    ctx = Context({"@base": "/local"})
    assert ctx.base == "/local"


@_mock_source_loader
def test_override_base():
    ctx = Context(
        base="http://example.org/app/data/item", source={"@base": "http://example.org/"}
    )
    assert ctx.base == "http://example.org/"


@_mock_source_loader
def test_resolve_relative_base():
    ctx = Context(base="http://example.org/app/data/item", source={"@base": "../"})
    assert ctx.base == "http://example.org/app/"
    assert ctx.resolve_iri("../other") == "http://example.org/other"


@_mock_source_loader
def test_set_null_base():
    ctx = Context(base="http://example.org/app/data/item", source={"@base": None})
    assert ctx.base is None
    assert ctx.resolve_iri("../other") == "../other"


@_mock_source_loader
def test_ignore_base_remote_context():
    ctx_url = "http://example.org/remote-base.jsonld"
    SOURCES[ctx_url] = {"@context": {"@base": "/remote"}}
    ctx = Context(ctx_url)
    assert ctx.base is None


@_expect_exception(errors.RECURSIVE_CONTEXT_INCLUSION)
@_mock_source_loader
def test_recursive_context_inclusion_error():
    ctx_url = "http://example.org/recursive.jsonld"
    SOURCES[ctx_url] = {"@context": ctx_url}
    ctx = Context(ctx_url)  # noqa: F841


@_expect_exception(errors.INVALID_REMOTE_CONTEXT)
@_mock_source_loader
def test_invalid_remote_context():
    ctx_url = "http://example.org/recursive.jsonld"
    SOURCES[ctx_url] = {"key": "value"}
    ctx = Context(ctx_url)  # noqa: F841


def test_file_source(tmp_path: Path) -> None:
    """
    A file URI source to `Context` gets processed correctly.
    """
    file = tmp_path / "context.jsonld"
    file.write_text(r"""{ "@context": { "ex": "http://example.com/" } }""")
    ctx = Context(source=file.as_uri())
    assert "http://example.com/" == ctx.terms["ex"].id


def test_dict_source(tmp_path: Path) -> None:
    """
    A dictionary source to `Context` gets processed correctly.
    """
    file = tmp_path / "context.jsonld"
    file.write_text(r"""{ "@context": { "ex": "http://example.com/" } }""")
    ctx = Context(source=[{"@context": file.as_uri()}])
    assert "http://example.com/" == ctx.terms["ex"].id


EG = Namespace("https://example.com/")

DIVERSE_CONTEXT = json.loads(
    """
        {
            "@context": {
                "ex": "https://example.com/",
                "generatedAt": { "@id": "http://www.w3.org/ns/prov#generatedAtTime", "@type": "http://www.w3.org/2001/XMLSchema#dateTime" },
                "graphMap": { "@id": "https://example.com/graphMap", "@container": ["@graph", "@id"] },
                "occupation_en": { "@id": "https://example.com/occupation", "@language": "en" },
                "children": { "@reverse": "https://example.com/parent" }
            }
        }
        """
)


def test_parsing() -> None:
    """
    A `Context` can be parsed from a dict.
    """
    ctx = Context(DIVERSE_CONTEXT)
    assert f"{EG}" == ctx.terms["ex"].id
    assert f"{PROV.generatedAtTime}" == ctx.terms["generatedAt"].id
    assert f"{XSD.dateTime}" == ctx.terms["generatedAt"].type
    assert f"{EG.graphMap}" == ctx.terms["graphMap"].id
    assert {"@graph", "@id"} == ctx.terms["graphMap"].container
    assert f"{EG.occupation}" == ctx.terms["occupation_en"].id
    assert "en" == ctx.terms["occupation_en"].language
    assert False is ctx.terms["occupation_en"].reverse
    assert True is ctx.terms["children"].reverse
    assert f"{EG.parent}" == ctx.terms["children"].id


def test_to_dict() -> None:
    """
    A `Context` can be converted to a dictionary.
    """
    ctx = Context()
    ctx.add_term("ex", f"{EG}")
    ctx.add_term("generatedAt", f"{PROV.generatedAtTime}", coercion=f"{XSD.dateTime}")
    ctx.add_term("graphMap", f"{EG.graphMap}", container=["@graph", "@id"])
    ctx.add_term("occupation_en", f"{EG.occupation}", language="en")
    ctx.add_term("children", f"{EG.parent}", reverse=True)
    result = ctx.to_dict()
    result["graphMap"]["@container"] = sorted(result["graphMap"]["@container"])
    assert DIVERSE_CONTEXT["@context"] == result


def test_undef_is_falsy() -> None:
    assert not UNDEF


@pytest.mark.parametrize(
    ("value", "is_undef"),
    [
        (UNDEF, True),
        ("", False),
        ("@id", False),
    ],
)
def test_undef_identity_narrowing(value: Union[str, Defined], is_undef: bool) -> None:
    """
    Test that `value is UNDEF` will narrow the type to exclude `Defined` entirely
    """
    if value is UNDEF:
        assert_type(value, Literal[Defined.UNDEF])
        assert is_undef
    else:
        assert_type(value, str)
        assert not is_undef


@pytest.mark.parametrize(
    ("source", "base", "expected_vocab"),
    [
        pytest.param(
            [{"@vocab": "http://example.com/"}, {"@vocab": "vocab/"}],
            None,
            "http://example.com/vocab/",
            id="relative-to-previous-vocab",
        ),
        pytest.param(
            {"@base": "http://example/document", "@vocab": "#"},
            None,
            "http://example/document#",
            id="relative-to-base-in-same-context",
        ),
        pytest.param(
            {"@vocab": "#"},
            "http://example/document",
            "http://example/document#",
            id="relative-to-document-base",
        ),
        pytest.param(
            {"@base": "http://example.com/dir/file", "@vocab": "/relative"},
            None,
            "http://example.com/relative",
            id="absolute-path",
        ),
        pytest.param(
            {"@base": "http://example.com/dir/", "@vocab": ""},
            None,
            "http://example.com/dir/",
            id="empty-is-base",
        ),
        pytest.param(
            {"@base": "http://example.com", "@vocab": ""},
            None,
            "http://example.com",
            id="empty-is-base-without-path",
        ),
        pytest.param(
            {"@base": "http://example.com", "@vocab": "#"},
            None,
            "http://example.com#",
            id="fragment-is-base-without-path",
        ),
        pytest.param(
            {"@vocab": ""},
            "urn:example:document",
            "urn:example:document",
            id="empty-is-urn-base",
        ),
        pytest.param(
            {"@vocab": "#"},
            "urn:example:document",
            "urn:example:document#",
            id="fragment-is-urn-base",
        ),
        pytest.param(
            [{"ex": "http://example.org/"}, {"@vocab": "ex"}],
            None,
            "http://example.org/",
            id="term",
        ),
        pytest.param(
            [{"ex": "http://example.org/"}, {"@vocab": "ex:ns/"}],
            None,
            "http://example.org/ns/",
            id="compact-iri",
        ),
        pytest.param(
            {"@vocab": "http://example.org/ns/"},
            "http://example/document",
            "http://example.org/ns/",
            id="absolute-iri-unchanged",
        ),
        pytest.param({"@vocab": "#"}, None, "#", id="no-base-unchanged"),
        pytest.param(
            [{"@vocab": "http://example.com/"}, {"@vocab": None}],
            None,
            None,
            id="null-clears",
        ),
    ],
)
def test_relative_vocab(source: Any, base: Optional[str], expected_vocab: Any) -> None:
    """
    A relative `@vocab` is resolved against the current vocabulary mapping, or
    against the base IRI if there is no vocabulary mapping.
    """
    ctx = Context(source, base=base)
    assert ctx.vocab == expected_vocab
    if expected_vocab is not None:
        assert ctx.expand("name") == f"{expected_vocab}name"


def test_relative_vocab_in_document() -> None:
    """
    The resolved `@vocab` is used for properties and types, and for terms
    defined in the same context.
    """
    data = {
        "@context": {
            "@version": 1.1,
            "@base": "http://example/document",
            "@vocab": "#",
            "knows": {"@type": "@id"},
        },
        "@id": "BrewEats",
        "@type": "Restaurant",
        "name": "Brew Eats",
        "knows": "Other",
    }
    graph = Graph().parse(data=json.dumps(data), format="json-ld")
    doc = Namespace("http://example/document#")
    subject = URIRef("http://example/BrewEats")
    assert set(graph) == {
        (subject, RDF.type, doc.Restaurant),
        (subject, doc.name, RDFLiteral("Brew Eats")),
        (subject, doc.knows, URIRef("http://example/Other")),
    }


@pytest.mark.parametrize(
    ("base", "vocab", "expected_vocab"),
    [
        pytest.param(
            "http://example.com",
            "",
            "http://example.com",
            id="empty-without-path",
        ),
        pytest.param(
            "http://example.com",
            "#",
            "http://example.com#",
            id="fragment-without-path",
        ),
        pytest.param(
            "http://example.com",
            "#terms-",
            "http://example.com#terms-",
            id="named-fragment-without-path",
        ),
        pytest.param(
            "http://example.com",
            "#http://terms/",
            "http://example.com#http://terms/",
            id="fragment-containing-scheme",
        ),
        pytest.param(
            "http://example.com?version=1",
            "",
            "http://example.com?version=1",
            id="empty-preserves-query",
        ),
        pytest.param(
            "http://example.com?version=1",
            "#",
            "http://example.com?version=1#",
            id="fragment-preserves-query",
        ),
        pytest.param(
            "urn:example:document",
            "",
            "urn:example:document",
            id="empty-urn",
        ),
        pytest.param(
            "urn:example:document",
            "#",
            "urn:example:document#",
            id="fragment-urn",
        ),
        pytest.param(
            "urn:example:document",
            "#terms-",
            "urn:example:document#terms-",
            id="named-fragment-urn",
        ),
    ],
)
@pytest.mark.parametrize("base_in_context", [False, True])
def test_relative_vocab_preserves_base_in_document(
    base: str, vocab: str, expected_vocab: str, base_in_context: bool
) -> None:
    """Empty and fragment-only vocabularies leave the base path unchanged."""
    source = {"@vocab": vocab}
    if base_in_context:
        source["@base"] = base
    data = {
        "@context": source,
        "@id": "urn:example:subject",
        "@type": "Person",
        "name": "Name",
    }
    graph = Graph().parse(data=json.dumps(data), format="json-ld", publicID=base)
    subject = URIRef("urn:example:subject")
    assert set(graph) == {
        (subject, RDF.type, URIRef(f"{expected_vocab}Person")),
        (subject, URIRef(f"{expected_vocab}name"), RDFLiteral("Name")),
    }


def test_property_scoped_context_overrides_protected_term() -> None:
    """
    Only a property-scoped context can redefine a protected term, see
    https://www.w3.org/TR/json-ld11/#protected-term-definitions
    """
    redefine = {"bar": "http://example.org/other"}
    ctx = Context(
        {
            "@protected": True,
            "bar": "http://ignored.org/bar",
            "foo": {"@id": "http://example.org/foo", "@context": redefine},
            "Foo": {"@id": "http://example.org/Foo", "@context": redefine},
        }
    )
    property_scoped = ctx.get_context_for_term(ctx.terms["foo"])
    assert property_scoped.expand("bar") == "http://example.org/other"
    # Embedded and type-scoped contexts keep the protected definition.
    assert ctx.subcontext(redefine).expand("bar") == "http://ignored.org/bar"
    type_scoped = ctx.get_context_for_type({"@type": "Foo"})
    assert type_scoped is not None
    assert type_scoped.expand("bar") == "http://ignored.org/bar"
