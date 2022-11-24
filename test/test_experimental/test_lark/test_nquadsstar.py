import rdflib
from rdflib.experimental.plugins.parsers.larknquadsstar import LarkNQuadsStarParser

rdflib.plugin.register(
    "larknqstar",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larknquadsstar",
    "LarkNQuadsStarParser",
)

rdflib.plugin.register(
    "rdna",
    rdflib.serializer.Serializer,
    "rdflib.plugins.serializers.rdna",
    "RDNASerializer",
)


def test_parse_ntriples_named_nodes():
    test_nquads = """<http://example/objects/1> <http://example/predicates/1> <http://example/objects/2> <http://example/graphs/1> .
<http://example/objects/2> <http://example/predicates/2> <http://example/objects/1> <http://example/graphs/1> .
"""
    ds = rdflib.ConjunctiveGraph()
    LarkNQuadsStarParser().parse(test_nquads, ds)
    g = ds.graph(rdflib.URIRef("http://example/graphs/1"))
    assert len(g) == 2
    assert (
        rdflib.URIRef("http://example/objects/1"),
        rdflib.URIRef("http://example/predicates/1"),
        rdflib.URIRef("http://example/objects/2"),
    ) in g
    assert (
        rdflib.URIRef("http://example/objects/2"),
        rdflib.URIRef("http://example/predicates/2"),
        rdflib.URIRef("http://example/objects/1"),
    ) in g


def test_larknquads_parser_with_quoted_triple_and_default_context():
    testnquads = """<http://example/s> <http://example/p> <http://example/o> .
    _:g1220 <http://example/q> <<<http://example/s1> <http://example/p1> <http://example/o1>>> .
    _:g1220 <http://example/b> <http://example/c> ."""
    ds = rdflib.ConjunctiveGraph()
    LarkNQuadsStarParser().parse(testnquads, ds, preserve_bnode_ids=True)
    g = ds.default_context
    assert len(g) == 3
    assert (
        rdflib.URIRef("http://example/s"),
        rdflib.URIRef("http://example/p"),
        rdflib.URIRef("http://example/o"),
    ) in g


def test_parse_ntriples_named_nodes_and_graph():
    test_nquads = """<http://example/objects/1> <http://example/predicates/1> <http://example/objects/2> .
<http://example/objects/2> <http://example/predicates/2> <http://example/objects/1> .
"""
    ds = rdflib.ConjunctiveGraph()
    LarkNQuadsStarParser().parse(test_nquads, ds)
    g = ds.default_context
    assert len(g) == 2
    assert (
        rdflib.URIRef("http://example/objects/1"),
        rdflib.URIRef("http://example/predicates/1"),
        rdflib.URIRef("http://example/objects/2"),
    ) in g
    assert (
        rdflib.URIRef("http://example/objects/2"),
        rdflib.URIRef("http://example/predicates/2"),
        rdflib.URIRef("http://example/objects/1"),
    ) in g


def test_larknquads_literal_string():
    testdata = """<http://example.org/a> <http://example.org/name> "Alice"^^<http://www.w3.org/2001/XMLSchema#string> <http://example.org/x> ."""
    ds = rdflib.ConjunctiveGraph()
    ds.parse(
        data=testdata,
        format="larknqstar",
        preserve_bnode_ids=True,
    )

    assert list(ds)[0][2] == rdflib.Literal(
        "Alice", datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#string")
    )


def test_larknquads_with_default_context():
    testdata = """<http://example/s> <http://example/p> <http://example/o> .
    _:g1220 <http://example/q> <<<http://example/s1> <http://example/p1> <http://example/o1>>> .
    _:g1220 <http://example/b> <http://example/c> ."""
    ds = rdflib.ConjunctiveGraph()
    ds.parse(data=testdata, format="larknqstar", preserve_bnode_ids=True)

    assert ds.serialize(format="rdna") == (
        "<http://example/s> <http://example/p> <http://example/o> .\n"
        "_:c14n0 <http://example/b> <http://example/c> .\n"
        "_:c14n0 <http://example/q> 82496401bcf33100b7a0f03189bc2e49 .\n"
    )


def test_larknquads_with_named_graph():
    testdata = """<http://example/s> <http://example/p> <http://example/o> <http://example/f> .
    _:g1220 <http://example/q> <<<http://example/s1> <http://example/p1> <http://example/o1>>> <http://example/g> .
    _:g1220 <http://example/b> <http://example/c> <http://example/h> ."""

    ds = rdflib.ConjunctiveGraph()
    ds.parse(data=testdata, format="larknqstar", preserve_bnode_ids=True)

    assert rdflib.URIRef("http://example/f") in list(ds.contexts())
    assert rdflib.URIRef("http://example/g") in list(ds.contexts())

    assert ds.serialize(format="rdna") == (
        "<http://example/s> <http://example/p> <http://example/o> <http://example/f> .\n"
        "_:c14n0 <http://example/b> <http://example/c> <http://example/h> .\n"
        "_:c14n0 <http://example/q> 82496401bcf33100b7a0f03189bc2e49 <http://example/g> .\n"
    )
