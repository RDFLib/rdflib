import rdflib
from rdflib.experimental.plugins.parsers.larknquads import LarkNQuadsParser

rdflib.plugin.register(
    "larknq",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larknquads",
    "LarkNQuadsParser",
)


def test_parse_ntriples_named_nodes():
    test_nquads = """<http://example/objects/1> <http://example/predicates/1> <http://example/objects/2> .
<http://example/objects/2> <http://example/predicates/2> <http://example/objects/1> .
"""
    g = rdflib.ConjunctiveGraph()
    LarkNQuadsParser().parse(test_nquads, g)
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


def test_parse_ntriples_bare_literals():
    test_nquads = """<http://example/objects/1> <http://example/predicates/1> "Foo" .
<http://example/objects/2> <http://example/predicates/2> "Bar" .
"""
    g = rdflib.ConjunctiveGraph()
    LarkNQuadsParser().parse(test_nquads, g)
    assert len(g) == 2

    assert (
        rdflib.URIRef("http://example/objects/1"),
        rdflib.URIRef("http://example/predicates/1"),
        rdflib.Literal("Foo"),
    ) in g

    assert (
        rdflib.URIRef("http://example/objects/2"),
        rdflib.URIRef("http://example/predicates/2"),
        rdflib.Literal("Bar"),
    ) in g


def test_parse_ntriples_language_literals():
    test_nquads = """<http://example/objects/1> <http://example/predicates/1> "Foo"@en-US .
<http://example/objects/2> <http://example/predicates/2> "Bar"@fr .
"""
    g = rdflib.ConjunctiveGraph()
    LarkNQuadsParser().parse(test_nquads, g)
    assert len(g) == 2
    assert (
        rdflib.URIRef("http://example/objects/1"),
        rdflib.URIRef("http://example/predicates/1"),
        rdflib.Literal("Foo", lang="en-US"),
    ) in g
    assert (
        rdflib.URIRef("http://example/objects/2"),
        rdflib.URIRef("http://example/predicates/2"),
        rdflib.Literal("Bar", lang="fr"),
    ) in g


def test_parse_ntriples_datatyped_literals():
    test_nquads = """<http://example/objects/1> <http://example/predicates/1> "Foo"^^<http://www.w3.org/2001/XMLSchema#string> .
<http://example/objects/2> <http://example/predicates/2> "9.99"^^<http://www.w3.org/2001/XMLSchema#decimal> .
"""
    g = rdflib.ConjunctiveGraph()
    LarkNQuadsParser().parse(test_nquads, g)
    assert len(g) == 2
    assert (
        rdflib.URIRef("http://example/objects/1"),
        rdflib.URIRef("http://example/predicates/1"),
        rdflib.Literal(
            "Foo", datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#string")
        ),
    ) in g
    assert (
        rdflib.URIRef("http://example/objects/2"),
        rdflib.URIRef("http://example/predicates/2"),
        rdflib.Literal(
            "9.99",
            datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#decimal"),
        ),
    ) in g


def test_parse_ntriples_mixed_literals():
    test_nquads = """<http://example/objects/1> <http://example/predicates/1> "Foo"@en-US .
<http://example/objects/2> <http://example/predicates/2> "9.99"^^<http://www.w3.org/2001/XMLSchema#decimal> .
"""
    g = rdflib.ConjunctiveGraph()
    LarkNQuadsParser().parse(test_nquads, g)
    assert len(g) == 2
    assert (
        rdflib.URIRef("http://example/objects/1"),
        rdflib.URIRef("http://example/predicates/1"),
        rdflib.Literal("Foo", lang="en-US"),
    ) in g
    assert (
        rdflib.URIRef("http://example/objects/2"),
        rdflib.URIRef("http://example/predicates/2"),
        rdflib.Literal(
            "9.99",
            datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#decimal"),
        ),
    ) in g


def test_parse_ntriples_bnodes():
    test_nquads = """<http://example/objects/1> <http://example/predicates/1> _:A1 .
_:A1 <http://example/predicates/2> <http://example/objects/1> .
"""
    g = rdflib.ConjunctiveGraph()
    LarkNQuadsParser().parse(test_nquads, g)
    assert len(g) == 2
    assert isinstance(
        list(
            g.objects(
                rdflib.URIRef("http://example/objects/1"),
                rdflib.URIRef("http://example/predicates/1"),
            )
        )[0],
        rdflib.BNode,
    )
    assert isinstance(
        list(
            g.subjects(
                rdflib.URIRef("http://example/predicates/2"),
                rdflib.URIRef("http://example/objects/1"),
            )
        )[0],
        rdflib.BNode,
    )


# Test the parser itself
def test_parse_nquads_named_nodes():
    test_nquads = """<http://example/objects/1> <http://example/predicates/1> <http://example/objects/2> <http://example/graphs/1> .
<http://example/objects/2> <http://example/predicates/2> <http://example/objects/1> <http://example/graphs/1> .
"""
    cg = rdflib.ConjunctiveGraph()
    LarkNQuadsParser().parse(test_nquads, cg)
    g = cg.get_context(rdflib.URIRef("http://example/graphs/1"))
    assert len(g) == 2
    assert (
        rdflib.URIRef("http://example/objects/1"),
        rdflib.URIRef("http://example/predicates/1"),
        rdflib.URIRef("http://example/objects/2"),
        rdflib.URIRef("http://example/graphs/1"),
    ) in g
    assert (
        rdflib.URIRef("http://example/objects/2"),
        rdflib.URIRef("http://example/predicates/2"),
        rdflib.URIRef("http://example/objects/1"),
        rdflib.URIRef("http://example/graphs/1"),
    ) in g


# Test the parser via the ConjunctiveGraph API
def test_larknquads_basic():

    from rdflib.graph import ConjunctiveGraph

    data = """
    <http://example/s1> <http://example/p> <http://example/o> <http://example/g1> .
    <http://example/s1> <http://example/name> "Alice"^^<http://www.w3.org/2001/XMLSchema#string> <http://example/g1> .
    <http://example/s1> <http://example/age> "23"^^<http://www.w3.org/2001/XMLSchema#integer> <http://example/g1> .
    <http://example/s1> <http://example/name> "Bob"@en  <http://example/g2> .
    _:bnode1 <http://example/name> "Bob"@en  <http://example/g2> ."""

    dl = sorted(
        list(
            # rdflib.ConjunctiveGraph().parse(
            ConjunctiveGraph().parse(data=data, format="larknq", preserve_bnode_ig=True)
        )
    )

    assert dl == [
        (
            rdflib.BNode("bnode1"),
            rdflib.URIRef("http://example/name"),
            rdflib.Literal("Bob", lang="en"),
            rdflib.URIRef("http://example/g2"),
        ),
        (
            rdflib.URIRef("http://example/s1"),
            rdflib.URIRef("http://example/age"),
            rdflib.Literal(
                "23", datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#integer")
            ),
            rdflib.URIRef("http://example/g1"),
        ),
        (
            rdflib.URIRef("http://example/s1"),
            rdflib.URIRef("http://example/name"),
            rdflib.Literal(
                "Alice",
                datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#string"),
            ),
            rdflib.URIRef("http://example/g1"),
        ),
        (
            rdflib.URIRef("http://example/s1"),
            rdflib.URIRef("http://example/name"),
            rdflib.Literal("Bob", lang="en"),
            rdflib.URIRef("http://example/g2"),
        ),
        (
            rdflib.URIRef("http://example/s1"),
            rdflib.URIRef("http://example/p"),
            rdflib.URIRef("http://example/o"),
            rdflib.URIRef("http://example/g1"),
        ),
    ]


def test_larknquads_parse_ntriples():
    from rdflib.graph import ConjunctiveGraph

    testntriples = """<http://example/s> <http://example/p> <http://example/o> ."""
    # d = rdflib.ConjunctiveGraph().parse(data=testntriples, format="larknq")
    d = ConjunctiveGraph().parse(data=testntriples, format="larknq")

    assert len(list(d)) == 1

    assert len(list(d.default_context)) == 1


def test_larknquads_parse_nquads():
    from rdflib.graph import ConjunctiveGraph

    testnquads = """<http://example/s> <http://example/p> <http://example/o> <http://example/1> ."""
    # d = rdflib.ConjunctiveGraph().parse(data=testnquads, format="larknq")
    d = ConjunctiveGraph().parse(data=testnquads, format="larknq")

    assert len(list(d)) == 1

    assert len(list(d.default_context)) == 0

    assert len(list(d.graph(rdflib.URIRef("http://example/1")))) == 1


# Investigating a test peculiarity
def test_larknquads_parse_minimal_whitespace():
    from rdflib.graph import ConjunctiveGraph

    testminwhitespace = """
    <http://example/s><http://example/p>"Alice".
    <http://example/s><http://example/p><http://example/o>.
    <http://example/s><http://example/p>_:o.
    _:s<http://example/p>"Alice".
    _:s<http://example/p><http://example/o>.
    _:s<http://example/p>_:bnode1."""

    # d = rdflib.ConjunctiveGraph().parse(
    #     data=testminwhitespace, format="larknq", preserve_bnode_ig=True
    # )
    d = ConjunctiveGraph().parse(
        data=testminwhitespace, format="larknq", preserve_bnode_ig=True
    )

    assert len(d) == 6

    assert len(d.default_context) == 6

    assert (
        (
            rdflib.URIRef("http://example/s"),
            rdflib.URIRef("http://example/p"),
            rdflib.Literal("Alice"),
        )
    ) in d.default_context

    gtr = "\n".join(
        [ln for ln in sorted(d.serialize(format="nt").split("\n")) if ln != ""]
    )

    assert gtr == (
        '<http://example/s> <http://example/p> "Alice" .\n'
        "<http://example/s> <http://example/p> <http://example/o> .\n"
        "<http://example/s> <http://example/p> _:o .\n"
        '_:s <http://example/p> "Alice" .\n'
        "_:s <http://example/p> <http://example/o> .\n"
        "_:s <http://example/p> _:bnode1 ."
    )
