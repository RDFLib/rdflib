from textwrap import dedent

from rdflib import RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.compare import isomorphic
from rdflib.plugins.serializers.turtle import TurtleSerializer


def test_turtle_final_dot():
    """
    https://github.com/RDFLib/rdflib/issues/282
    """

    g = Graph()
    u = URIRef("http://ex.org/bob.")
    g.bind("ns", "http://ex.org/")
    g.add((u, u, u))
    s = g.serialize(format="turtle", encoding="latin-1")
    assert b"ns:bob." not in s


def test_turtle_bool_list():
    subject = URIRef("http://localhost/user")
    predicate = URIRef("http://localhost/vocab#hasList")
    g1 = Graph()
    list_item1 = BNode()
    list_item2 = BNode()
    list_item3 = BNode()
    g1.add((subject, predicate, list_item1))
    g1.add((list_item1, RDF.first, Literal(True)))
    g1.add((list_item1, RDF.rest, list_item2))
    g1.add((list_item2, RDF.first, Literal(False)))
    g1.add((list_item2, RDF.rest, list_item3))
    g1.add((list_item3, RDF.first, Literal(True)))
    g1.add((list_item3, RDF.rest, RDF.nil))

    ttl_dump = g1.serialize(format="turtle")
    g2 = Graph()
    g2.parse(data=ttl_dump, format="turtle")

    list_id = g2.value(subject, predicate)
    bool_list = [i.toPython() for i in Collection(g2, list_id)]
    assert bool_list == [True, False, True]


def test_unicode_escaping():
    turtle_string = " <http://example.com/A> <http://example.com/B> <http://example.com/aaa\\u00F3bbbb> . <http://example.com/A> <http://example.com/C> <http://example.com/zzz\\U00100000zzz> . <http://example.com/A> <http://example.com/D> <http://example.com/aaa\\u00f3bbb> ."
    g = Graph()

    # shouldn't get an exception
    g.parse(data=turtle_string, format="turtle")
    triples = sorted(list(g))
    assert len(triples) == 3
    print(triples)
    # Now check that was decoded into python values properly
    assert triples[0][2] == URIRef("http://example.com/aaa\xf3bbbb")
    assert triples[1][2] == URIRef("http://example.com/zzz\U00100000zzz")
    assert triples[2][2] == URIRef("http://example.com/aaa\xf3bbb")


def test_turtle_valid_list():
    ns = Namespace("http://example.org/ns/")
    g = Graph()
    g.parse(
        data="""
            @prefix : <{0}> .
            :s :p (""), (0), (false) .
            """.format(
            ns
        ),
        format="turtle",
    )

    turtle_serializer = TurtleSerializer(g)

    for o in g.objects(ns.s, ns.p):
        assert turtle_serializer.isValidList(o)


def test_turtle_shared_list_tail_round_trips():
    """
    A list cell that is pointed to from more than one place (here, the tail of
    one list is also referenced directly by another subject) cannot be safely
    written with ``( … )`` collection syntax: the inline form only defines the
    cell once, at whichever reference happens to consume it, leaving the other
    reference dangling in the output.

    https://github.com/RDFLib/rdflib/issues/282 and related discussions cover
    the general "isValidList" heuristic; this specifically covers sharing of
    interior cells (not just of the list head).
    """
    ns = Namespace("http://example.org/ns/")
    g = Graph()
    tail = BNode()
    head = BNode()
    g.add((tail, RDF.first, Literal("b")))
    g.add((tail, RDF.rest, RDF.nil))
    g.add((head, RDF.first, Literal("a")))
    g.add((head, RDF.rest, tail))
    g.add((ns.s1, ns.p, head))
    g.add((ns.s2, ns.p, tail))

    turtle_serializer = TurtleSerializer(g)
    # The shared tail must not be considered part of a safely-inlineable list.
    assert turtle_serializer.isValidList(head) is False
    assert turtle_serializer.isValidList(tail) is False

    ttl_dump = g.serialize(format="turtle")
    g2 = Graph()
    g2.parse(data=ttl_dump, format="turtle")
    assert len(g2) == len(g)
    assert isomorphic(g, g2)


def test_turtle_private_list_still_uses_collection_syntax():
    """A list that nothing else points into should still serialize compactly."""
    ns = Namespace("http://example.org/ns/")
    g = Graph()
    g.parse(
        data="""
            @prefix : <{0}> .
            :s :p ("a" "b" "c") .
            """.format(
            ns
        ),
        format="turtle",
    )
    output = g.serialize(format="turtle")
    assert "(" in output
    g2 = Graph()
    g2.parse(data=output, format="turtle")
    assert isomorphic(g, g2)


def test_turtle_namespace():
    graph = Graph()
    graph.bind("OBO", "http://purl.obolibrary.org/obo/")
    graph.bind("GENO", "http://purl.obolibrary.org/obo/GENO_")
    graph.bind("RO", "http://purl.obolibrary.org/obo/RO_")
    graph.bind("RO_has_phenotype", "http://purl.obolibrary.org/obo/RO_0002200")
    graph.bind("SERIAL", "urn:ISSN:")
    graph.bind("EX", "http://example.org/")
    graph.add(
        (
            URIRef("http://example.org"),
            URIRef("http://purl.obolibrary.org/obo/RO_0002200"),
            URIRef("http://purl.obolibrary.org/obo/GENO_0000385"),
        )
    )
    graph.add(
        (
            URIRef("urn:ISSN:0167-6423"),
            RDFS.label,
            Literal("Science of Computer Programming"),
        )
    )
    graph.add(
        (
            URIRef("http://example.org/name_with_(parenthesis)"),
            RDFS.label,
            Literal("URI with parenthesis"),
        )
    )
    output = [
        val
        for val in graph.serialize(format="turtle").splitlines()
        if not val.startswith("@prefix")
    ]
    output = " ".join(output)
    assert "RO_has_phenotype:" in output
    assert "GENO:0000385" in output
    assert "SERIAL:0167-6423" in output
    assert r"EX:name_with_\(parenthesis\)" in output


def test_turtle_undeclared_prefix_when_using_base():
    """
    See https://github.com/RDFLib/rdflib/issues/3160
    """
    from rdflib import Graph, Literal, URIRef

    g = Graph()
    g.add(
        (
            URIRef("https://example.com/subject"),
            URIRef("https://example.com/p/predicate"),
            Literal("object"),
        )
    )
    output = g.serialize(format="turtle", base="https://example.com/")
    expected = dedent(
        """
        @base <https://example.com/> .
        @prefix ns1: <https://example.com/p/> .

        <subject> ns1:predicate "object" .
    """
    )
    assert output.strip() == expected.strip()
