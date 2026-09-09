from rdflib import RDF, BNode, Graph, Literal, Namespace
from rdflib.compare import isomorphic
from rdflib.plugins.serializers.jsonld import Converter
from rdflib.plugins.shared.jsonld.context import Context


def _shared_tail_graph():
    """Two lists whose final cell is the same node, not a copy of it."""
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
    return g, ns, head, tail


def test_jsonld_shared_list_tail_round_trips():
    """
    A list cell pointed to from more than one place cannot be written as
    ``@list``: that form inlines the whole chain at a single reference and
    writes its cells nowhere else, so any other statement referring to one of
    those cells is left pointing at a node the output never defines.

    Rendering each list independently instead emitted the shared cell once per
    referring list, so the round-tripped graph gained triples: 6 in, 8 out,
    non-isomorphic.

    Same defect class as ``test_turtle_shared_list_tail_round_trips`` and
    ``test_longturtle_shared_list_tail_round_trips``; the JSON-LD converter has
    its own chain walk and so needed the same reference check.
    """
    g, _ns, _head, _tail = _shared_tail_graph()

    data = g.serialize(format="json-ld")
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert len(g2) == len(g)
    assert isomorphic(g, g2)
    # The chain is stated explicitly rather than inlined. ``"@list": []`` may
    # still appear: that is ``rdf:nil``, a single IRI, not a list structure.
    assert '"@list": [\n' not in data.replace('"@list": []', "")
    assert len(list(g2.triples((None, RDF.first, None)))) == 2
    assert len(list(g2.triples((None, RDF.rest, None)))) == 2


def test_to_collection_rejects_a_multiply_referenced_cell():
    """The decision itself, so the reason survives a refactor of the caller."""
    g, _ns, head, tail = _shared_tail_graph()
    converter = Converter(Context(), False, None)

    assert converter.to_collection(g, head) is None
    assert converter.to_collection(g, tail) is None


def test_a_privately_owned_list_is_still_written_as_a_list():
    """The fix must not stop ordinary lists from using ``@list``."""
    ns = Namespace("http://example.org/ns/")
    g = Graph()
    g.add((ns.s, ns.p, RDF.nil))
    collection = BNode()
    second = BNode()
    g.add((collection, RDF.first, Literal("a")))
    g.add((collection, RDF.rest, second))
    g.add((second, RDF.first, Literal("b")))
    g.add((second, RDF.rest, RDF.nil))
    g.add((ns.owner, ns.items, collection))

    data = g.serialize(format="json-ld")
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert "@list" in data
    assert isomorphic(g, g2)


def test_a_shared_list_head_round_trips():
    """Sharing the head, not an interior cell, must round-trip too."""
    ns = Namespace("http://example.org/ns/")
    g = Graph()
    head = BNode()
    g.add((head, RDF.first, Literal("a")))
    g.add((head, RDF.rest, RDF.nil))
    g.add((ns.s1, ns.p, head))
    g.add((ns.s2, ns.p, head))

    data = g.serialize(format="json-ld")
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert len(g2) == len(g)
    assert isomorphic(g, g2)
