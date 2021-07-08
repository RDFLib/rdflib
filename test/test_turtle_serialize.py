from rdflib import Graph, URIRef, BNode, RDF, RDFS, Literal, Namespace
from rdflib.collection import Collection
from rdflib.plugins.serializers.turtle import TurtleSerializer


def testTurtleFinalDot():
    """
    https://github.com/RDFLib/rdflib/issues/282
    """

    g = Graph()
    u = URIRef("http://ex.org/bob.")
    g.bind("ns", "http://ex.org/")
    g.add((u, u, u))
    s = g.serialize(format="turtle", encoding="latin-1")
    assert b"ns:bob." not in s


def testTurtleBoolList():
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


def testUnicodeEscaping():
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
    NS = Namespace("http://example.org/ns/")
    g = Graph()
    g.parse(
        data="""
            @prefix : <{0}> .
            :s :p (""), (0), (false) .
            """.format(
            NS
        ),
        format="turtle",
    )

    turtle_serializer = TurtleSerializer(g)

    for o in g.objects(NS.s, NS.p):
        assert turtle_serializer.isValidList(o)


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
    assert "EX:name_with_(parenthesis)" in output


if __name__ == "__main__":
    import nose
    import sys

    nose.main(defaultTest=sys.argv[0])
