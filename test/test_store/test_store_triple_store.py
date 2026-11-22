import pytest

from rdflib.graph import Graph
from rdflib.namespace import RDFS
from rdflib.term import BNode, Literal

remove_me = (BNode(), RDFS.label, Literal("remove_me"))


@pytest.fixture(scope="function")
def get_store(request):
    store = Graph(store="default")
    store.open("store")
    store.add(remove_me)

    yield store

    store.close()


def test_add(get_store):
    store = get_store
    subject = BNode()
    store.add((subject, RDFS.label, Literal("foo")))


def test_remove(get_store):
    store = get_store
    store.remove(remove_me)
    store.remove((None, None, None))


def test_triples(get_store):
    store = get_store
    for s, p, o in store:
        pass
