from rdflib import ConjunctiveGraph, URIRef
import rdflib.plugin


def testFinalNewline():
    """
    http://code.google.com/p/rdflib/issues/detail?id=5
    """

    graph = ConjunctiveGraph()
    graph.add(
        (
            URIRef("http://ex.org/a"),
            URIRef("http://ex.org/b"),
            URIRef("http://ex.org/c"),
        )
    )

    failed = set()
    for p in rdflib.plugin.plugins(None, rdflib.plugin.Serializer):
        v = graph.serialize(format=p.name, encoding="utf-8")
        lines = v.split("\n".encode("utf-8"))
        if b"\n" not in v or (lines[-1] != b""):
            failed.add(p.name)
    # JSON-LD does not require a final newline (because JSON doesn't)
    failed = failed.difference({"json-ld", "application/ld+json"})
    assert len(failed) == 0, "No final newline for formats: '%s'" % failed
