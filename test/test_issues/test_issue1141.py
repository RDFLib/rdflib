from rdflib import Graph
from rdflib.plugins.stores.auditable import AuditableStore
from rdflib.plugins.stores.memory import Memory, SimpleMemory

"""
Tests is Turtle and TriG parsing works with a store with or without formula support
"""


def test_issue_1141_1():
    file = b"@prefix : <http://example.com/> . :s :p :o ."

    for format in ("turtle", "trig"):
        # with formula
        graph = Graph()
        assert graph.store.formula_aware
        graph.parse(data=file, format=format)
        assert len(graph) == 1

        # without
        graph = Graph(store=AuditableStore(Memory()))
        assert not graph.store.formula_aware
        graph.parse(data=file, format=format)
        assert len(graph) == 1


def test_issue_1141_2():
    file = b"@prefix : <http://example.com/> . :s :p :o ."
    # with formula
    graph = Graph(store=Memory())
    assert graph.store.formula_aware
    graph.parse(data=file, format="turtle")
    assert len(graph) == 1

    # without
    graph = Graph(store=SimpleMemory())
    assert not graph.store.formula_aware
    graph.parse(data=file, format="turtle")
    assert len(graph) == 1


def test_issue_1141_3():
    file = b"<a:> <b:> <c:> ."
    # with contexts
    graph = Graph(store=Memory())
    assert graph.store.context_aware
    assert graph.store.formula_aware
    graph.parse(data=file, format="nt")
    assert len(graph) == 1

    # without
    graph = Graph(store=SimpleMemory())
    assert not graph.store.context_aware
    assert not graph.store.formula_aware
    graph.parse(data=file, format="nt")
    assert len(graph) == 1
