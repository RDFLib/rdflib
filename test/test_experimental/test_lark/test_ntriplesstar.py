import rdflib

rdflib.plugin.register(
    "larkntstar",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larkntriplesstar",
    "LarkNTriplesStarParser",
)

rdflib.plugin.register(
    "rdna",
    rdflib.serializer.Serializer,
    "rdflib.plugins.serializers.rdna",
    "RDNASerializer",
)

rdflib.plugin.register(
    "ntstar",
    rdflib.serializer.Serializer,
    "rdflib.plugins.serializers.ntriples-star",
    "NTriplesStarSerializer",
)

embedded_subject = """<http://example/x> <http://example/p> <http://example/X> .
<< <http://example/s> <http://example/p> <http://example/o> >> <http://example/p> <http://example/z> ."""


def test_larkntriples_embedded_subject():
    g = rdflib.Graph().parse(data=embedded_subject, format="larkntstar")
    assert sorted(list(g)) == [
        (
            rdflib.term.RDFStarTriple("025cf368e1e95366cbb063dfbb3b41af"),
            rdflib.term.URIRef("http://example/p"),
            rdflib.term.URIRef("http://example/z"),
        ),
        (
            rdflib.term.URIRef("http://example/x"),
            rdflib.term.URIRef("http://example/p"),
            rdflib.term.URIRef("http://example/X"),
        ),
    ]

    rt = sorted(list(g))[0][0]

    assert rt.subject() == rdflib.term.URIRef("http://example/s")
    assert rt.predicate() == rdflib.term.URIRef("http://example/p")
    assert rt.object() == rdflib.term.URIRef("http://example/o")

    # print(g.serialize(format="nt", unstar=True))

    print(g.serialize(format="ntstar"))


embedded_object = """<http://example/x> <http://example/p> <http://example/X> .
<http://example/x> <http://example/p> << <http://example/s> <http://example/p> <http://example/o> >> ."""


def test_larkntriples_embedded_object():
    g = rdflib.Graph().parse(data=embedded_object, format="larkntstar")
    assert sorted(list(g)) == [
        (
            rdflib.term.URIRef("http://example/x"),
            rdflib.term.URIRef("http://example/p"),
            rdflib.term.RDFStarTriple("025cf368e1e95366cbb063dfbb3b41af"),
        ),
        (
            rdflib.term.URIRef("http://example/x"),
            rdflib.term.URIRef("http://example/p"),
            rdflib.term.URIRef("http://example/X"),
        ),
    ]

    print(g.serialize(format="ntstar"))


triply_embedded = """<< <http://example/a> <http://example/name> "Alice" >> <http://example/reportedBy> <http://example/charlie> .
<http://example/charlie> <http://example/reported> << <http://example/a> <http://example/name> "Alice" >> .
<< <http://example/a> <http://example/name> "Alice" >> <http://example/reportedBy> << <http://example/b> <http://example/name> "Bob" >> .
<< << << <http://example/a> <http://example/name> "Alice" >> <http://example/reportedBy> <http://example/charlie> >> <http://example/thoughtBy> <http://example/bob> >> <http://example/writtenBy> <http://example/mary> ."""


# @pytest.mark.xfail(reason="Doesn't plumb triply embedded")
def test_larkntriples_triply_embedded():
    g = rdflib.Graph().parse(data=triply_embedded, format="larkntstar")

    assert sorted(list(g)) == [
        (
            rdflib.term.RDFStarTriple("4c8191e1f49bc3349602caaf14e1a616"),
            rdflib.term.URIRef("http://example/reportedBy"),
            rdflib.term.RDFStarTriple("05ea7dce344742501fd2a19a5b19c0e0"),
        ),
        (
            rdflib.term.RDFStarTriple("4c8191e1f49bc3349602caaf14e1a616"),
            rdflib.term.URIRef("http://example/reportedBy"),
            rdflib.term.URIRef("http://example/charlie"),
        ),
        (
            rdflib.term.RDFStarTriple("9d42da967276f3f0ffae41b13613c6c8"),
            rdflib.term.URIRef("http://example/writtenBy"),
            rdflib.term.URIRef("http://example/mary"),
        ),
        (
            rdflib.term.URIRef("http://example/charlie"),
            rdflib.term.URIRef("http://example/reported"),
            rdflib.term.RDFStarTriple("4c8191e1f49bc3349602caaf14e1a616"),
        ),
    ]

    print(g.serialize(format="ntstar"))
