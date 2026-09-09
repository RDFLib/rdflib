import json
from typing import Any

import pytest

from rdflib import RDF, RDFS, BNode, Dataset, Graph, Literal, Namespace
from rdflib.compare import isomorphic
from rdflib.plugins.serializers.jsonld import Converter
from rdflib.plugins.shared.jsonld.context import Context

NS = Namespace("http://example.org/ns/")
# A context whose term for ns:p writes every value of ns:p as a list.
LIST_CONTEXT = {"p": {"@id": str(NS.p), "@container": "@list"}}


def _shared_tail_graph():
    """Two lists whose final cell is the same node, not a copy of it."""
    g = Graph()
    tail = BNode()
    head = BNode()
    g.add((tail, RDF.first, Literal("b")))
    g.add((tail, RDF.rest, RDF.nil))
    g.add((head, RDF.first, Literal("a")))
    g.add((head, RDF.rest, tail))
    g.add((NS.s1, NS.p, head))
    g.add((NS.s2, NS.p, tail))
    return g, head, tail


def _shared_head_graph():
    """One list referenced from two subjects."""
    g = Graph()
    head = BNode()
    g.add((head, RDF.first, Literal("a")))
    g.add((head, RDF.rest, RDF.nil))
    g.add((NS.s1, NS.p, head))
    g.add((NS.s2, NS.p, head))
    return g, head, head


def _annotated_cell_graph():
    """A list whose cell has a property besides rdf:first and rdf:rest."""
    g = Graph()
    head = BNode()
    g.add((head, RDF.first, Literal("a")))
    g.add((head, RDF.rest, RDF.nil))
    g.add((head, RDFS.label, Literal("annotated cell")))
    g.add((NS.s, NS.p, head))
    return g, head, head


def _non_empty_lists(data: str) -> list[Any]:
    """Every non-empty ``@list`` value in a JSON-LD document.

    ``"@list": []`` is left out: it is ``rdf:nil``, a single IRI, not a list
    structure.
    """
    found: list[Any] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if value.get("@list"):
                found.append(value["@list"])
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(json.loads(data))
    return found


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
    g, _head, _tail = _shared_tail_graph()

    data = g.serialize(format="json-ld")
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert len(g2) == len(g)
    assert isomorphic(g, g2)
    # The chain is stated explicitly rather than inlined.
    assert _non_empty_lists(data) == []
    assert len(list(g2.triples((None, RDF.first, None)))) == 2
    assert len(list(g2.triples((None, RDF.rest, None)))) == 2


def test_a_shared_list_head_round_trips():
    """Sharing the head, not an interior cell, is the same defect: 4 in, 6 out."""
    g, _head, _tail = _shared_head_graph()

    data = g.serialize(format="json-ld")
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert len(g2) == len(g)
    assert isomorphic(g, g2)
    assert _non_empty_lists(data) == []


def test_to_collection_rejects_a_multiply_referenced_cell():
    """The decision itself, so the reason survives a refactor of the caller."""
    g, head, tail = _shared_tail_graph()
    converter = Converter(Context(), False, None)

    assert converter.to_collection(g, head) is None
    assert converter.to_collection(g, tail) is None


@pytest.mark.parametrize("auto_compact", [False, True])
@pytest.mark.parametrize(
    "build",
    [_shared_tail_graph, _shared_head_graph, _annotated_cell_graph],
    ids=["shared-tail", "shared-head", "annotated-cell"],
)
def test_a_list_container_term_is_not_used_for_a_chain_that_is_not_a_list(
    build, auto_compact
):
    """A term declared with ``"@container": "@list"`` is the ``@list`` form too.

    It must not be chosen for a chain that cannot be written as a list. It was
    chosen for any object with an ``rdf:first``, and the refused chain then
    raised ``TypeError: 'NoneType' object is not iterable``.
    """
    g, _head, _tail = build()

    data = g.serialize(
        format="json-ld", context=LIST_CONTEXT, auto_compact=auto_compact
    )
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert isomorphic(g, g2)


def test_a_privately_owned_list_is_still_written_as_a_list():
    """The fix must not stop ordinary lists from using ``@list``."""
    g = Graph()
    g.add((NS.s, NS.p, RDF.nil))
    collection = BNode()
    second = BNode()
    g.add((collection, RDF.first, Literal("a")))
    g.add((collection, RDF.rest, second))
    g.add((second, RDF.first, Literal("b")))
    g.add((second, RDF.rest, RDF.nil))
    g.add((NS.owner, NS.items, collection))

    data = g.serialize(format="json-ld")
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert len(_non_empty_lists(data)) == 1
    assert isomorphic(g, g2)


def test_a_privately_owned_list_still_uses_a_list_container_term():
    g = Graph()
    head = BNode()
    second = BNode()
    g.add((head, RDF.first, Literal("a")))
    g.add((head, RDF.rest, second))
    g.add((second, RDF.first, Literal("b")))
    g.add((second, RDF.rest, RDF.nil))
    g.add((NS.s, NS.p, head))

    data = g.serialize(format="json-ld", context=LIST_CONTEXT)
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert json.loads(data)["p"] == ["a", "b"]
    assert isomorphic(g, g2)


def test_a_list_cell_shared_across_named_graphs_round_trips():
    """References are counted across the whole dataset, not per graph.

    The Serialize RDF as JSON-LD Algorithm (JSON-LD 1.1 Processing Algorithms
    and API, section 8.4) keeps one "referenced once" map for all graphs, so a
    cell that another named graph points at cannot be inlined either: the
    other graph's reference would be left dangling.
    """
    ds = Dataset()
    g1, g2 = ds.graph(NS.g1), ds.graph(NS.g2)
    cell = BNode()
    g1.add((cell, RDF.first, Literal("a")))
    g1.add((cell, RDF.rest, RDF.nil))
    g1.add((NS.s1, NS.p, cell))
    g2.add((NS.s2, NS.p, cell))

    data = ds.serialize(format="json-ld")
    ds2 = Dataset()
    ds2.parse(data=data, format="json-ld")

    (in_g1,) = ds2.graph(NS.g1).objects(NS.s1, NS.p)
    (in_g2,) = ds2.graph(NS.g2).objects(NS.s2, NS.p)
    assert in_g1 == in_g2
    assert (in_g1, RDF.first, Literal("a")) in ds2.graph(NS.g1)
    assert _non_empty_lists(data) == []


def test_lists_in_separate_named_graphs_are_still_written_as_lists():
    """Counting across graphs must not reject a list each graph owns alone."""
    ds = Dataset()
    for name in ("g1", "g2"):
        graph = ds.graph(NS[name])
        head = BNode()
        graph.add((head, RDF.first, Literal(name)))
        graph.add((head, RDF.rest, RDF.nil))
        graph.add((NS.s, NS.p, head))

    data = ds.serialize(format="json-ld")

    assert len(_non_empty_lists(data)) == 2
