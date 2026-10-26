from __future__ import annotations

from collections.abc import Generator
from typing import Optional

import pytest

from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.graph import _ContextType, _TripleType
from rdflib.plugins.stores.memory import Memory


class CountingMemory(Memory):
    def __init__(self) -> None:
        super().__init__()
        self.yielded_contexts = 0

    def contexts(
        self, triple: Optional[_TripleType] = None
    ) -> Generator[_ContextType, None, None]:
        for context in super().contexts(triple):
            self.yielded_contexts += 1
            yield context


@pytest.mark.parametrize("operation, op_code", [("add", "A"), ("remove", "D")])
def test_patch_export_enumerates_graphs_once(operation: str, op_code: str) -> None:
    store = CountingMemory()
    dataset = Dataset(store=store)
    triple = (URIRef("urn:subject"), URIRef("urn:predicate"), Literal("object"))
    graph_count = 32
    for index in range(graph_count):
        dataset.graph(URIRef(f"urn:graph:{index}")).add(triple)
    dataset.default_graph.add(triple)
    store.yielded_contexts = 0

    result = dataset.serialize(format="patch", operation=operation)

    assert store.yielded_contexts <= graph_count + 1
    expected_rows = {
        f'{op_code} <urn:subject> <urn:predicate> "object" <urn:graph:{index}> .'
        for index in range(graph_count)
    }
    expected_rows.add(f'{op_code} <urn:subject> <urn:predicate> "object" .')
    assert {
        line for line in result.splitlines() if line.startswith(f"{op_code} ")
    } == expected_rows


def test_add_quad():
    ds = Dataset()
    ds.add(
        (
            URIRef("http://example.org/subject1"),
            URIRef("http://example.org/predicate2"),
            Literal("object2"),
            Graph(identifier=URIRef("http://example.org/graph1")),
        )
    )
    result = ds.serialize(format="patch", operation="add")
    assert (
        """A <http://example.org/subject1> <http://example.org/predicate2> "object2" <http://example.org/graph1> .
"""
        in result
    )


def test_delete_quad():
    ds = Dataset()
    ds.add(
        (
            URIRef("http://example.org/subject1"),
            URIRef("http://example.org/predicate2"),
            Literal("object2"),
            Graph(identifier=URIRef("http://example.org/graph1")),
        )
    )
    result = ds.serialize(format="patch", operation="remove")
    assert (
        """D <http://example.org/subject1> <http://example.org/predicate2> "object2" <http://example.org/graph1> .
"""
        in result
    )


def test_diff_quad():
    quad_1 = (
        URIRef("http://example.org/subject1"),
        URIRef("http://example.org/predicate2"),
        Literal("object2"),
        Graph(identifier=URIRef("http://example.org/graph1")),
    )
    quad_2 = (
        URIRef("http://example.org/subject2"),
        URIRef("http://example.org/predicate3"),
        Literal("object3"),
        Graph(identifier=URIRef("http://example.org/graph2")),
    )
    ds1 = Dataset()
    ds2 = Dataset()
    ds1.add(quad_1)
    ds2.addN([quad_1, quad_2])
    result = ds1.serialize(format="patch", target=ds2)
    assert (
        """A <http://example.org/subject2> <http://example.org/predicate3> "object3" <http://example.org/graph2> ."""
        in result
    )


def test_add_triple():
    ds = Dataset()
    ds.add(
        (
            URIRef("http://example.org/subject1"),
            URIRef("http://example.org/predicate2"),
            Literal("object2"),
        )
    )
    result = ds.serialize(format="patch", operation="add")
    assert (
        """A <http://example.org/subject1> <http://example.org/predicate2> "object2" ."""
        in result
    )


def test_delete_triple():
    ds = Dataset()
    ds.add(
        (
            URIRef("http://example.org/subject1"),
            URIRef("http://example.org/predicate2"),
            Literal("object2"),
        )
    )
    result = ds.serialize(format="patch", operation="remove")
    assert (
        """D <http://example.org/subject1> <http://example.org/predicate2> "object2" ."""
        in result
    )


def test_diff_triple():
    triple_1 = (
        URIRef("http://example.org/subject1"),
        URIRef("http://example.org/predicate2"),
        Literal("object2"),
    )
    triple_2 = (
        URIRef("http://example.org/subject2"),
        URIRef("http://example.org/predicate3"),
        Literal("object3"),
    )
    ds1 = Dataset()
    ds2 = Dataset()
    ds1.add(triple_1)
    ds2.add(triple_1)
    ds2.add(triple_2)
    result = ds1.serialize(format="patch", target=ds2)
    assert (
        """A <http://example.org/subject2> <http://example.org/predicate3> "object3" ."""
        in result
    )


def test_diff_quad_overlap():
    quad_1 = (
        URIRef("http://example.org/subject1"),
        URIRef("http://example.org/predicate1"),
        Literal("object1"),
        Graph(identifier=URIRef("http://example.org/graph1")),
    )
    quad_2 = (
        URIRef("http://example.org/subject2"),
        URIRef("http://example.org/predicate2"),
        Literal("object2"),
        Graph(identifier=URIRef("http://example.org/graph2")),
    )
    quad_3 = (
        URIRef("http://example.org/subject3"),
        URIRef("http://example.org/predicate3"),
        Literal("object3"),
        Graph(identifier=URIRef("http://example.org/graph3")),
    )
    ds1 = Dataset()
    ds2 = Dataset()
    ds1.addN([quad_1, quad_2])
    ds2.addN([quad_2, quad_3])
    result = ds1.serialize(format="patch", target=ds2)
    # first quad needs to be removed
    assert (
        """D <http://example.org/subject1> <http://example.org/predicate1> "object1" <http://example.org/graph1> ."""
        in result
    )
    # third quad needs to be added
    assert (
        """A <http://example.org/subject3> <http://example.org/predicate3> "object3" <http://example.org/graph3> ."""
        in result
    )


def test_header_id():
    ds = Dataset()
    ds.add(
        (
            URIRef("http://example.org/subject1"),
            URIRef("http://example.org/predicate2"),
            Literal("object2"),
        )
    )
    result = ds.serialize(format="patch", operation="add", header_id="uuid:123")
    assert """H id <uuid:123>""" in result


def test_prev_header():
    ds = Dataset()
    ds.add(
        (
            URIRef("http://example.org/subject1"),
            URIRef("http://example.org/predicate2"),
            Literal("object2"),
        )
    )
    result = ds.serialize(format="patch", operation="add", header_prev="uuid:123")
    assert """H prev <uuid:123>""" in result
