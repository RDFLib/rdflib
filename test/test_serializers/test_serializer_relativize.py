import pytest

from rdflib import Dataset, Graph, URIRef
from rdflib.plugins.serializers.turtle import RecursiveSerializer
from rdflib.serializer import Serializer


@pytest.mark.parametrize("serializer_class", [Serializer, RecursiveSerializer])
@pytest.mark.parametrize("term_class", [str, URIRef])
@pytest.mark.parametrize(
    "base, uri, expected",
    [
        (None, "http://example.org/a", "http://example.org/a"),
        ("http://other.org/", "http://example.org/a", "http://example.org/a"),
        ("http://example.org/dir/", "http://example.org/dir/a", "a"),
        ("http://example.org/dir/", "http://example.org/dir/", ""),
        (
            "http://example.org/doc#",
            "http://example.org/doc#a",
            "http://example.org/doc#a",
        ),
        (
            "http://example.org/doc#",
            "http://example.org/doc#",
            "http://example.org/doc#",
        ),
        (
            "http://example.org/doc#f",
            "http://example.org/doc#foo",
            "http://example.org/doc#foo",
        ),
        (
            "http://example.org/a/b",
            "http://example.org/a/bc",
            "http://example.org/a/bc",
        ),
        (
            "http://example.org/dir/",
            "http://example.org/dir/a:b",
            "http://example.org/dir/a:b",
        ),
        (
            "http://example.org/dir/",
            "http://example.org/dir/1:a",
            "http://example.org/dir/1:a",
        ),
        (
            "http://example.org/dir/",
            "http://example.org/dir/é:a",
            "http://example.org/dir/é:a",
        ),
        (
            "http://example.org",
            "http://example.org.other/a",
            "http://example.org.other/a",
        ),
        (
            "http://example.org/doc?q=",
            "http://example.org/doc?q=a",
            "http://example.org/doc?q=a",
        ),
        (
            "http://example.org/dir/",
            "http://example.org/dir/.",
            "http://example.org/dir/.",
        ),
        ("http://example.org/dir/", "http://example.org/dir/%2e", "%2e"),
        ("http://example.org/dir/", "http://example.org/dir/café", "café"),
        ("http://example.org/dir/", "http://example.org/dir/a?b:c", "a?b:c"),
        ("local:/dir/", "local:/dir/a", "local:/dir/a"),
        ("urn:example:", "urn:example:a", "urn:example:a"),
        ("http://[invalid/", "http://[invalid/a", "http://[invalid/a"),
    ],
)
def test_relativize_preserves_iri(
    serializer_class: type[Serializer],
    term_class: type[str],
    base: str | None,
    uri: str,
    expected: str,
) -> None:
    serializer = serializer_class(Graph())
    serializer.base = base
    result = serializer.relativize(term_class(uri))
    assert str(result) == expected
    if expected != uri:
        assert isinstance(result, URIRef)


@pytest.mark.parametrize("serializer_class", [Serializer, RecursiveSerializer])
@pytest.mark.parametrize("term_class", [str, URIRef])
@pytest.mark.parametrize("base", [None, "http://other.org/", "http://example.org/doc#"])
def test_relativize_keeps_original_term(
    serializer_class: type[Serializer], term_class: type[str], base: str | None
) -> None:
    serializer = serializer_class(Graph())
    serializer.base = base
    uri = term_class("http://example.org/doc#a")
    assert serializer.relativize(uri) is uri


@pytest.mark.parametrize("relative", ["a/b", "a#fragment", "a/b:c", "a#b:c"])
def test_recursive_relativize_keeps_path_and_fragment_restrictions(
    relative: str,
) -> None:
    base = "http://example.org/"
    uri = URIRef(base + relative)
    serializer = Serializer(Graph())
    serializer.base = base
    assert serializer.relativize(uri) == URIRef(relative)
    recursive = RecursiveSerializer(Graph())
    recursive.base = base
    assert recursive.relativize(uri) is uri


@pytest.mark.parametrize(
    "format", ["turtle", "trig", "n3", "longturtle", "xml", "pretty-xml"]
)
@pytest.mark.parametrize(
    "base, uri",
    [
        ("http://example.org/doc#", "http://example.org/doc#a"),
        ("http://example.org/a/b", "http://example.org/a/bc"),
        ("http://example.org/dir/", "http://example.org/dir/a:b"),
        ("http://example.org/dir/", "http://example.org/dir/1:a"),
        ("http://example.org/dir/", "http://example.org/dir/é:a"),
        ("http://example.org/doc?q=", "http://example.org/doc?q=a"),
        ("http://example.org/dir/", "http://example.org/dir/a"),
        ("http://example.org/dir/", "http://example.org/dir/%2e"),
        ("http://example.org/dir/", "http://example.org/dir/café"),
        ("local:/dir/", "local:/dir/a"),
    ],
)
def test_serialize_with_base_preserves_iri(format: str, base: str, uri: str) -> None:
    graph = Graph()
    graph.add((URIRef(uri), URIRef("http://example.net/p"), URIRef(uri)))
    graph.add(
        (URIRef("http://example.net/s"), URIRef(uri), URIRef("http://example.net/o"))
    )
    serialized = graph.serialize(format=format, base=base)
    parser_format = {"longturtle": "turtle", "pretty-xml": "xml"}.get(format, format)
    parsed = Dataset(default_union=True).parse(data=serialized, format=parser_format)
    assert set(parsed.triples((None, None, None))) == set(graph)
