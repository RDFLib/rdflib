import pytest

from rdflib import Graph
from rdflib.plugins.stores.auditable import AuditableStore
from test.utils.namespace import EGDO


@pytest.fixture
def get_graph():
    g = Graph("Memory")

    g.add((EGDO.s0, EGDO.p0, EGDO.o0))
    g.add((EGDO.s0, EGDO.p0, EGDO.o0bis))

    t = Graph(AuditableStore(g.store), g.identifier)

    yield g, t


def test_add_commit(get_graph):
    g, t = get_graph
    t.add((EGDO.s1, EGDO.p1, EGDO.o1))
    assert set(t) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
            (EGDO.s1, EGDO.p1, EGDO.o1),
        ]
    )

    t.commit()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
            (EGDO.s1, EGDO.p1, EGDO.o1),
        ]
    )


def test_remove_commit(get_graph):
    g, t = get_graph
    t.remove((EGDO.s0, EGDO.p0, EGDO.o0))
    assert set(t) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )
    t.commit()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_multiple_remove_commit(get_graph):
    g, t = get_graph
    t.remove((EGDO.s0, EGDO.p0, None))
    assert set(t) == set([])
    t.commit()
    assert set(g) == set([])


def test_noop_add_commit(get_graph):
    g, t = get_graph
    t.add((EGDO.s0, EGDO.p0, EGDO.o0))
    assert set(t) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )
    t.commit()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_noop_remove_commit(get_graph):
    g, t = get_graph
    t.add((EGDO.s0, EGDO.p0, EGDO.o0))
    assert set(t) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )

    t.commit()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_add_remove_commit(get_graph):
    g, t = get_graph
    t.add((EGDO.s1, EGDO.p1, EGDO.o1))
    t.remove((EGDO.s1, EGDO.p1, EGDO.o1))
    assert set(t) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )
    t.commit()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_remove_add_commit(get_graph):
    g, t = get_graph
    t.remove((EGDO.s1, EGDO.p1, EGDO.o1))
    t.add((EGDO.s1, EGDO.p1, EGDO.o1))
    assert set(t) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
            (EGDO.s1, EGDO.p1, EGDO.o1),
        ]
    )
    t.commit()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
            (EGDO.s1, EGDO.p1, EGDO.o1),
        ]
    )


def test_add_rollback(get_graph):
    g, t = get_graph
    t.add((EGDO.s1, EGDO.p1, EGDO.o1))
    t.rollback()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_remove_rollback(get_graph):
    g, t = get_graph
    t.remove((EGDO.s0, EGDO.p0, EGDO.o0))
    t.rollback()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_multiple_remove_rollback(get_graph):
    g, t = get_graph
    t.remove((EGDO.s0, EGDO.p0, None))
    t.rollback()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_noop_add_rollback(get_graph):
    g, t = get_graph
    t.add((EGDO.s0, EGDO.p0, EGDO.o0))
    t.rollback()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_noop_remove_rollback(get_graph):
    g, t = get_graph
    t.add((EGDO.s0, EGDO.p0, EGDO.o0))
    t.rollback()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_add_remove_rollback(get_graph):
    g, t = get_graph
    t.add((EGDO.s1, EGDO.p1, EGDO.o1))
    t.remove((EGDO.s1, EGDO.p1, EGDO.o1))
    t.rollback()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_remove_add_rollback(get_graph):
    g, t = get_graph
    t.remove((EGDO.s1, EGDO.p1, EGDO.o1))
    t.add((EGDO.s1, EGDO.p1, EGDO.o1))
    t.rollback()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


@pytest.fixture
def get_empty_graph():
    g = Graph("Memory")

    t = Graph(AuditableStore(g.store), g.identifier)

    yield g, t


def test_add_commit_empty(get_empty_graph):
    g, t = get_empty_graph
    t.add((EGDO.s1, EGDO.p1, EGDO.o1))
    assert set(t) == set(
        [
            (EGDO.s1, EGDO.p1, EGDO.o1),
        ]
    )
    t.commit()
    assert set(g) == set(
        [
            (EGDO.s1, EGDO.p1, EGDO.o1),
        ]
    )


def test_add_rollback_empty(get_empty_graph):
    g, t = get_empty_graph
    t.add((EGDO.s1, EGDO.p1, EGDO.o1))
    t.rollback()
    assert set(g) == set([])


@pytest.fixture
def get_concurrent_graph():
    g = Graph("Memory")

    g.add((EGDO.s0, EGDO.p0, EGDO.o0))
    g.add((EGDO.s0, EGDO.p0, EGDO.o0bis))
    t1 = Graph(AuditableStore(g.store), g.identifier)
    t2 = Graph(AuditableStore(g.store), g.identifier)
    t1.add((EGDO.s1, EGDO.p1, EGDO.o1))
    t2.add((EGDO.s2, EGDO.p2, EGDO.o2))
    t1.remove((EGDO.s0, EGDO.p0, EGDO.o0))
    t2.remove((EGDO.s0, EGDO.p0, EGDO.o0bis))

    yield g, t1, t2


def test_commit_commit(get_concurrent_graph):
    g, t1, t2 = get_concurrent_graph
    t1.commit()
    t2.commit()
    assert set(g) == set(
        [
            (EGDO.s1, EGDO.p1, EGDO.o1),
            (EGDO.s2, EGDO.p2, EGDO.o2),
        ]
    )


def test_commit_rollback(get_concurrent_graph):
    g, t1, t2 = get_concurrent_graph
    t1.commit()
    t2.rollback()
    assert set(g) == set(
        [
            (EGDO.s1, EGDO.p1, EGDO.o1),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_rollback_commit(get_concurrent_graph):
    g, t1, t2 = get_concurrent_graph
    t1.rollback()
    t2.commit()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s2, EGDO.p2, EGDO.o2),
        ]
    )


def test_rollback_rollback(get_concurrent_graph):
    g, t1, t2 = get_concurrent_graph
    t1.rollback()
    t2.rollback()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


@pytest.fixture
def get_embedded_graph():
    g = Graph("Memory")

    g.add((EGDO.s0, EGDO.p0, EGDO.o0))
    g.add((EGDO.s0, EGDO.p0, EGDO.o0bis))

    t1 = Graph(AuditableStore(g.store), g.identifier)
    t1.add((EGDO.s1, EGDO.p1, EGDO.o1))
    t1.remove((EGDO.s0, EGDO.p0, EGDO.o0bis))

    t2 = Graph(AuditableStore(t1.store), t1.identifier)
    t2.add((EGDO.s2, EGDO.p2, EGDO.o2))
    t2.remove((EGDO.s1, EGDO.p1, EGDO.o1))

    yield g, t1, t2


def test_commit_commit_embedded(get_embedded_graph):
    g, t1, t2 = get_embedded_graph
    assert set(t2) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s2, EGDO.p2, EGDO.o2),
        ]
    )
    t2.commit()
    assert set(t1) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s2, EGDO.p2, EGDO.o2),
        ]
    )
    t1.commit()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s2, EGDO.p2, EGDO.o2),
        ]
    )


def test_commit_rollback_embedded(get_embedded_graph):
    g, t1, t2 = get_embedded_graph
    t2.commit()
    t1.rollback()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )


def test_rollback_commit_embedded(get_embedded_graph):
    g, t1, t2 = get_embedded_graph
    t2.rollback()
    assert set(t1) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s1, EGDO.p1, EGDO.o1),
        ]
    )
    t1.commit()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s1, EGDO.p1, EGDO.o1),
        ]
    )


def test_rollback_rollback_embedded(get_embedded_graph):
    g, t1, t2 = get_embedded_graph
    t2.rollback()
    t1.rollback()
    assert set(g) == set(
        [
            (EGDO.s0, EGDO.p0, EGDO.o0),
            (EGDO.s0, EGDO.p0, EGDO.o0bis),
        ]
    )
