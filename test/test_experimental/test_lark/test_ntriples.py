import rdflib

rdflib.plugin.register(
    "larknt",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larkntriples",
    "LarkNTriplesParser",
)


def test_parse_ntriples_named_nodes():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> <http://example.com/objects/2> .
<http://example.com/objects/2> <http://example.com/predicates/2> <http://example.com/objects/1> .
"""
    g = rdflib.Graph()
    p = LarkNTriplesParser()
    p.parse(test_ntriples, g)
    assert len(g) == 2
    assert (
        rdflib.URIRef("http://example.com/objects/1"),
        rdflib.URIRef("http://example.com/predicates/1"),
        rdflib.URIRef("http://example.com/objects/2"),
    ) in g
    assert (
        rdflib.URIRef("http://example.com/objects/2"),
        rdflib.URIRef("http://example.com/predicates/2"),
        rdflib.URIRef("http://example.com/objects/1"),
    ) in g


def test_parse_ntriples_bare_literals():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> "Foo" .
<http://example.com/objects/2> <http://example.com/predicates/2> "Bar" .
"""
    g = rdflib.Graph()
    LarkNTriplesParser().parse(test_ntriples, g)
    assert len(g) == 2

    assert (
        rdflib.URIRef("http://example.com/objects/1"),
        rdflib.URIRef("http://example.com/predicates/1"),
        rdflib.Literal("Foo"),
    ) in g

    assert (
        rdflib.URIRef("http://example.com/objects/2"),
        rdflib.URIRef("http://example.com/predicates/2"),
        rdflib.Literal("Bar"),
    ) in g


def test_parse_ntriples_language_literals():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> "Foo"@en-US .
<http://example.com/objects/2> <http://example.com/predicates/2> "Bar"@fr .
"""
    g = rdflib.Graph()
    LarkNTriplesParser().parse(test_ntriples, g)
    assert len(g) == 2
    assert (
        rdflib.URIRef("http://example.com/objects/1"),
        rdflib.URIRef("http://example.com/predicates/1"),
        rdflib.Literal("Foo", lang="en-US"),
    ) in g
    assert (
        rdflib.URIRef("http://example.com/objects/2"),
        rdflib.URIRef("http://example.com/predicates/2"),
        rdflib.Literal("Bar", lang="fr"),
    ) in g


def test_parse_ntriples_datatyped_literals():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> "Foo"^^<http://www.w3.org/2001/XMLSchema#string> .
<http://example.com/objects/2> <http://example.com/predicates/2> "9.99"^^<http://www.w3.org/2001/XMLSchema#decimal> .
"""
    g = rdflib.Graph()
    LarkNTriplesParser().parse(test_ntriples, g)
    assert len(g) == 2
    assert (
        rdflib.URIRef("http://example.com/objects/1"),
        rdflib.URIRef("http://example.com/predicates/1"),
        rdflib.Literal(
            "Foo", datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#string")
        ),
    ) in g
    assert (
        rdflib.URIRef("http://example.com/objects/2"),
        rdflib.URIRef("http://example.com/predicates/2"),
        rdflib.Literal(
            "9.99",
            datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#decimal"),
        ),
    ) in g


def test_parse_ntriples_mixed_literals():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> "Foo"@en-US .
<http://example.com/objects/2> <http://example.com/predicates/2> "9.99"^^<http://www.w3.org/2001/XMLSchema#decimal> .
"""
    g = rdflib.Graph()
    LarkNTriplesParser().parse(test_ntriples, g)
    assert len(g) == 2
    assert (
        rdflib.URIRef("http://example.com/objects/1"),
        rdflib.URIRef("http://example.com/predicates/1"),
        rdflib.Literal("Foo", lang="en-US"),
    ) in g
    assert (
        rdflib.URIRef("http://example.com/objects/2"),
        rdflib.URIRef("http://example.com/predicates/2"),
        rdflib.Literal(
            "9.99",
            datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#decimal"),
        ),
    ) in g


def test_parse_ntriples_bnodes():
    test_ntriples = """<http://example.com/objects/1> <http://example.com/predicates/1> _:A1 .
_:A1 <http://example.com/predicates/2> <http://example.com/objects/1> .
"""
    g = rdflib.Graph()
    LarkNTriplesParser().parse(test_ntriples, g)
    assert len(g) == 2
    assert isinstance(
        list(
            g.objects(
                rdflib.URIRef("http://example.com/objects/1"),
                rdflib.URIRef("http://example.com/predicates/1"),
            )
        )[0],
        rdflib.BNode,
    )
    assert isinstance(
        list(
            g.subjects(
                rdflib.URIRef("http://example.com/predicates/2"),
                rdflib.URIRef("http://example.com/objects/1"),
            )
        )[0],
        rdflib.BNode,
    )


def test_larkntriples_basic():

    testdata = """<http://example/s1> <http://example/p> <http://example/o> .
    <http://example/s1> <http://example/name> "Alice"^^<http://www.w3/2001/XMLSchema#string> .
    <http://example/s1> <http://example/age> "23"^^<http://www.w3/2001/XMLSchema#integer> .
    <http://example/s2> <http://example/name> "Bob"@en ."""

    lg = sorted(list(rdflib.Graph().parse(data=testdata, format="larknt")))

    assert lg == [
        (
            rdflib.URIRef("http://example/s1"),
            rdflib.URIRef("http://example/age"),
            rdflib.Literal(
                "23", datatype=rdflib.URIRef("http://www.w3/2001/XMLSchema#integer")
            ),
        ),
        (
            rdflib.URIRef("http://example/s1"),
            rdflib.URIRef("http://example/name"),
            rdflib.Literal(
                "Alice", datatype=rdflib.URIRef("http://www.w3/2001/XMLSchema#string")
            ),
        ),
        (
            rdflib.URIRef("http://example/s1"),
            rdflib.URIRef("http://example/p"),
            rdflib.URIRef("http://example/o"),
        ),
        (
            rdflib.URIRef("http://example/s2"),
            rdflib.URIRef("http://example/name"),
            rdflib.Literal("Bob", lang="en"),
        ),
    ]


def test_larkntriples_minimal_whitespace_preserving_bnode_ids():

    testdata = """<http://example/s><http://example/p><http://example/o>.
    <http://example/s><http://example/p>"Alice".
    <http://example/s><http://example/p>_:o.
    _:s<http://example/p><http://example/o>.
    _:s<http://example/p>"Alice".
    _:s<http://example/p>_:bnode1."""

    lg = sorted(
        list(
            rdflib.Graph().parse(
                data=testdata, format="larknt", preserve_bnode_ids=True
            )
        )
    )

    assert lg == [
        (rdflib.BNode("s"), rdflib.URIRef("http://example/p"), rdflib.BNode("bnode1")),
        (
            rdflib.BNode("s"),
            rdflib.URIRef("http://example/p"),
            rdflib.URIRef("http://example/o"),
        ),
        (rdflib.BNode("s"), rdflib.URIRef("http://example/p"), rdflib.Literal("Alice")),
        (
            rdflib.URIRef("http://example/s"),
            rdflib.URIRef("http://example/p"),
            rdflib.BNode("o"),
        ),
        (
            rdflib.URIRef("http://example/s"),
            rdflib.URIRef("http://example/p"),
            rdflib.URIRef("http://example/o"),
        ),
        (
            rdflib.URIRef("http://example/s"),
            rdflib.URIRef("http://example/p"),
            rdflib.Literal("Alice"),
        ),
    ]


def test_wip_bid_prefix():
    testdata = """<http://example/s> <http://example/p> _:a .
    _:a  <http://example/p> <http://example/o> .
    <http://example/s> <http://example/p> _:b .
    _:b  <http://example/p> <http://example/o> .
"""
    r = rdflib.Graph().parse(data=testdata, format="larknt")
    assert len(list(r)) == 4
