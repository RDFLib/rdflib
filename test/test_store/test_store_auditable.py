# -*- coding=utf8 -*-
import shutil
import tempfile

import pytest

from rdflib import Graph, Namespace, plugin
from rdflib.plugins.stores.auditable import AuditableStore
from rdflib.store import VALID_STORE

EX = Namespace("http://example.org/")


def get_plugin_stores():
    pluginstores = []

    for s in plugin.plugins(None, plugin.Store):
        if s.name in (
            "default",
            "Memory",
            "Auditable",
            "Concurrent",
            "SimpleMemory",
            "SPARQLStore",
            "SPARQLUpdateStore",
        ):
            continue  # excluded from these tests

        try:
            graph = Graph(store=s.name)
            pluginstores.append(s.name)
        except ImportError:
            pass
    return pluginstores


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_graph(request):
    storename = request.param

    g = Graph(store=storename)

    path = tempfile.mktemp()

    try:
        shutil.rmtree(path)
    except Exception:
        pass

    rt = g.open(configuration=path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"

    g.add((EX.s0, EX.p0, EX.o0))
    g.add((EX.s0, EX.p0, EX.o0bis))

    t = Graph(AuditableStore(g.store), g.identifier)

    yield g, t

    g.close()

    g.destroy(configuration=path)

    try:
        shutil.rmtree(path)
    except Exception:
        pass


def test_add_commit(get_graph):
    g, t = get_graph
    t.add((EX.s1, EX.p1, EX.o1))
    assert set(t) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
            (EX.s1, EX.p1, EX.o1),
        ]
    )

    t.commit()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
            (EX.s1, EX.p1, EX.o1),
        ]
    )


def test_remove_commit(get_graph):
    g, t = get_graph
    t.remove((EX.s0, EX.p0, EX.o0))
    assert set(t) == set(
        [
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )
    t.commit()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_multiple_remove_commit(get_graph):
    g, t = get_graph
    t.remove((EX.s0, EX.p0, None))
    assert set(t) == set([])
    t.commit()
    assert set(g) == set([])


def test_noop_add_commit(get_graph):
    g, t = get_graph
    t.add((EX.s0, EX.p0, EX.o0))
    assert set(t) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )
    t.commit()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_noop_remove_commit(get_graph):
    g, t = get_graph
    t.add((EX.s0, EX.p0, EX.o0))
    assert set(t) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )

    t.commit()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_add_remove_commit(get_graph):
    g, t = get_graph
    t.add((EX.s1, EX.p1, EX.o1))
    t.remove((EX.s1, EX.p1, EX.o1))
    assert set(t) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )
    t.commit()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_remove_add_commit(get_graph):
    g, t = get_graph
    t.remove((EX.s1, EX.p1, EX.o1))
    t.add((EX.s1, EX.p1, EX.o1))
    assert set(t) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
            (EX.s1, EX.p1, EX.o1),
        ]
    )
    t.commit()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
            (EX.s1, EX.p1, EX.o1),
        ]
    )


def test_add_rollback(get_graph):
    g, t = get_graph
    t.add((EX.s1, EX.p1, EX.o1))
    t.rollback()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_remove_rollback(get_graph):
    g, t = get_graph
    t.remove((EX.s0, EX.p0, EX.o0))
    t.rollback()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_multiple_remove_rollback(get_graph):
    g, t = get_graph
    t.remove((EX.s0, EX.p0, None))
    t.rollback()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_noop_add_rollback(get_graph):
    g, t = get_graph
    t.add((EX.s0, EX.p0, EX.o0))
    t.rollback()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_noop_remove_rollback(get_graph):
    g, t = get_graph
    t.add((EX.s0, EX.p0, EX.o0))
    t.rollback()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_add_remove_rollback(get_graph):
    g, t = get_graph
    t.add((EX.s1, EX.p1, EX.o1))
    t.remove((EX.s1, EX.p1, EX.o1))
    t.rollback()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_remove_add_rollback(get_graph):
    g, t = get_graph
    t.remove((EX.s1, EX.p1, EX.o1))
    t.add((EX.s1, EX.p1, EX.o1))
    t.rollback()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_empty_graph(request):
    storename = request.param

    path = tempfile.mktemp()

    try:
        shutil.rmtree(path)
    except Exception:
        pass

    g = Graph(store=storename)
    rt = g.open(configuration=path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"

    t = Graph(AuditableStore(g.store), g.identifier)

    yield g, t
    g.close()
    g.destroy(configuration=path)


def test_add_commit_empty(get_empty_graph):
    g, t = get_empty_graph
    t.add((EX.s1, EX.p1, EX.o1))
    assert set(t) == set(
        [
            (EX.s1, EX.p1, EX.o1),
        ]
    )
    t.commit()
    assert set(g) == set(
        [
            (EX.s1, EX.p1, EX.o1),
        ]
    )


def test_add_rollback_empty(get_empty_graph):
    g, t = get_empty_graph
    t.add((EX.s1, EX.p1, EX.o1))
    t.rollback()
    assert set(g) == set([])


@pytest.fixture
def get_concurrent_graph():
    g = Graph()
    g.add((EX.s0, EX.p0, EX.o0))
    g.add((EX.s0, EX.p0, EX.o0bis))
    t1 = Graph(AuditableStore(g.store), g.identifier)
    t2 = Graph(AuditableStore(g.store), g.identifier)
    t1.add((EX.s1, EX.p1, EX.o1))
    t2.add((EX.s2, EX.p2, EX.o2))
    t1.remove((EX.s0, EX.p0, EX.o0))
    t2.remove((EX.s0, EX.p0, EX.o0bis))

    yield g, t1, t2


def test_commit_commit(get_concurrent_graph):
    g, t1, t2 = get_concurrent_graph
    t1.commit()
    t2.commit()
    assert set(g) == set(
        [
            (EX.s1, EX.p1, EX.o1),
            (EX.s2, EX.p2, EX.o2),
        ]
    )


def test_commit_rollback(get_concurrent_graph):
    g, t1, t2 = get_concurrent_graph
    t1.commit()
    t2.rollback()
    assert set(g) == set(
        [
            (EX.s1, EX.p1, EX.o1),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_rollback_commit(get_concurrent_graph):
    g, t1, t2 = get_concurrent_graph
    t1.rollback()
    t2.commit()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s2, EX.p2, EX.o2),
        ]
    )


def test_rollback_rollback(get_concurrent_graph):
    g, t1, t2 = get_concurrent_graph
    t1.rollback()
    t2.rollback()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


@pytest.fixture
def get_embedded_graph():
    g = Graph()
    g.add((EX.s0, EX.p0, EX.o0))
    g.add((EX.s0, EX.p0, EX.o0bis))

    t1 = Graph(AuditableStore(g.store), g.identifier)
    t1.add((EX.s1, EX.p1, EX.o1))
    t1.remove((EX.s0, EX.p0, EX.o0bis))

    t2 = Graph(AuditableStore(t1.store), t1.identifier)
    t2.add((EX.s2, EX.p2, EX.o2))
    t2.remove((EX.s1, EX.p1, EX.o1))

    yield g, t1, t2


def test_commit_commit_embedded(get_embedded_graph):
    g, t1, t2 = get_embedded_graph
    assert set(t2) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s2, EX.p2, EX.o2),
        ]
    )
    t2.commit()
    assert set(t1) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s2, EX.p2, EX.o2),
        ]
    )
    t1.commit()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s2, EX.p2, EX.o2),
        ]
    )


def test_commit_rollback_embedded(get_embedded_graph):
    g, t1, t2 = get_embedded_graph
    t2.commit()
    t1.rollback()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )


def test_rollback_commit_embedded(get_embedded_graph):
    g, t1, t2 = get_embedded_graph
    t2.rollback()
    assert set(t1) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s1, EX.p1, EX.o1),
        ]
    )
    t1.commit()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s1, EX.p1, EX.o1),
        ]
    )


def test_rollback_rollback_embedded(get_embedded_graph):
    g, t1, t2 = get_embedded_graph
    t2.rollback()
    t1.rollback()
    assert set(g) == set(
        [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ]
    )
