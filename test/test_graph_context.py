import os
import shutil
import tempfile

import pytest

from rdflib import BNode, ConjunctiveGraph, Graph, URIRef, plugin
from rdflib.store import VALID_STORE

michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")


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
        continue  # inappropriate for these tests

    pluginstores.append(s.name)


@pytest.fixture(
    scope="function",
    params=pluginstores,
)
def get_graph(request):
    store = request.param
    path = tempfile.mktemp()
    try:
        shutil.rmtree(path)
    except Exception:
        pass

    try:
        graph = ConjunctiveGraph(store=store)
    except ImportError:
        pytest.skip("Dependencies for store '%s' not available!" % store)

    if store != "default":
        rt = graph.open(configuration=path, create=True)
        assert rt == VALID_STORE, "The underlying store is corrupt"

    assert len(graph) == 0, "There must be zero triples in the graph just after store (file) creation"

    yield graph

    graph.close()
    graph.store.destroy(path)

    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


def populate_c1(graph):
    context1 = Graph(graph.store, c1)

    context1.add((tarek, likes, pizza))
    context1.add((tarek, likes, cheese))
    context1.add((michel, likes, pizza))
    context1.add((michel, likes, cheese))
    context1.add((bob, likes, cheese))
    context1.add((bob, hates, pizza))
    context1.add((bob, hates, michel))  # gasp!


def depopulate_c1(graph):
    context1 = Graph(graph.store, c1)

    context1.remove((tarek, likes, pizza))
    context1.remove((tarek, likes, cheese))
    context1.remove((michel, likes, pizza))
    context1.remove((michel, likes, cheese))
    context1.remove((bob, likes, cheese))
    context1.remove((bob, hates, pizza))
    context1.remove((bob, hates, michel))  # gasp!


def add_triple_to_default_context_context1_and_context2(graph):
    triple = (pizza, hates, tarek)  # revenge!

    # add to default context
    graph.add(triple)

    # add to context 1
    context1 = Graph(graph.store, c1)
    context1.add(triple)

    # add to context 2
    context2 = Graph(graph.store, c2)
    context2.add(triple)


def test_conjunction(get_graph):
    graph = get_graph

    if graph.store == "Shelf":
        pytest.skip("Skipping known issue with __len__")

    add_triple_to_default_context_context1_and_context2(graph)
    triple = (pizza, likes, pizza)

    # add to context 1
    context1 = Graph(graph.store, c1)
    context1.add(triple)
    assert len(context1) == len(graph)


def test_add(get_graph):
    graph = get_graph

    populate_c1(graph)


def test_remove(get_graph):
    graph = get_graph

    populate_c1(graph)
    depopulate_c1(graph)


def test_len_in_one_context(get_graph):
    graph = get_graph
    # make sure context is empty

    graph.remove_context(graph.get_context(c1))
    context1 = Graph(graph.store, c1)
    oldLen = len(graph)

    for i in range(0, 10):
        context1.add((BNode(), hates, hates))
    assert len(context1) == oldLen + 10

    assert len(graph.get_context(c1)) == oldLen + 10

    graph.remove_context(graph.get_context(c1))

    assert len(graph) == oldLen
    assert len(graph) == 0


def test_len_in_multiple_contexts(get_graph):
    graph = get_graph

    if graph.store == "Shelf":
        pytest.skip("Skipping known issue with __len__")

    oldLen = len(graph)
    add_triple_to_default_context_context1_and_context2(graph)

    # add_triple_to_default_context_context1_and_context2 is adding the same triple to
    # three different contexts. So it's only + 1
    assert len(graph) == oldLen + 1

    context1 = Graph(graph.store, c1)
    assert len(context1) == oldLen + 1


def test_remove_in_multiple_contexts(get_graph):
    graph = get_graph

    triple = (pizza, hates, tarek)  # revenge!

    add_triple_to_default_context_context1_and_context2(graph)

    # triple should be still in store after removing it from c1 + c2
    assert triple in graph
    context1 = Graph(graph.store, c1)
    context1.remove(triple)

    assert triple in graph
    context2 = Graph(graph.store, c2)
    context2.remove(triple)
    assert triple in graph
    graph.remove(triple)
    # now gone!
    assert triple not in graph

    # add again and see if remove without context removes all triples!
    add_triple_to_default_context_context1_and_context2(graph)
    graph.remove(triple)
    assert triple not in graph


def test_contexts(get_graph):
    graph = get_graph
    triple = (pizza, hates, tarek)  # revenge!

    add_triple_to_default_context_context1_and_context2(graph)

    def cid(c):
        return c.identifier

    assert c1 in map(cid, graph.contexts())
    assert c2 in map(cid, graph.contexts())

    contextList = list(map(cid, list(graph.contexts(triple))))
    assert c1 in contextList, (c1, contextList)
    assert c2 in contextList, (c2, contextList)


def test_remove_context(get_graph):
    graph = get_graph

    add_triple_to_default_context_context1_and_context2(graph)

    assert len(Graph(graph.store, c1)) == 1
    assert len(graph.get_context(c1)) == 1

    graph.remove_context(graph.get_context(c1))
    assert c1 not in graph.contexts()


def test_remove_any(get_graph):
    graph = get_graph
    Any = None
    add_triple_to_default_context_context1_and_context2(graph)
    graph.remove((Any, Any, Any))
    assert len(graph) == 0


def test_triples(get_graph):
    graph = get_graph

    triples = graph.triples
    Any = None
    populate_c1(graph)

    context1 = Graph(graph.store, c1)
    context1triples = context1.triples

    # unbound subjects with context
    assert len(list(context1triples((Any, likes, pizza)))) == 2, graph.store
    assert len(list(context1triples((Any, hates, pizza)))) == 1
    assert len(list(context1triples((Any, likes, cheese)))) == 3
    assert len(list(context1triples((Any, hates, cheese)))) == 0

    # unbound subjects without context, same results!
    assert len(list(triples((Any, likes, pizza)))) == 2
    assert len(list(triples((Any, hates, pizza)))) == 1
    assert len(list(triples((Any, likes, cheese)))) == 3
    assert len(list(triples((Any, hates, cheese)))) == 0

    # unbound objects with context
    assert len(list(context1triples((michel, likes, Any)))) == 2
    assert len(list(context1triples((tarek, likes, Any)))) == 2
    assert len(list(context1triples((bob, hates, Any)))) == 2
    assert len(list(context1triples((bob, likes, Any)))) == 1

    # unbound objects without context, same results!
    assert len(list(triples((michel, likes, Any)))) == 2
    assert len(list(triples((tarek, likes, Any)))) == 2
    assert len(list(triples((bob, hates, Any)))) == 2
    assert len(list(triples((bob, likes, Any)))) == 1

    # unbound predicates with context
    assert len(list(context1triples((michel, Any, cheese)))) == 1
    assert len(list(context1triples((tarek, Any, cheese)))) == 1
    assert len(list(context1triples((bob, Any, pizza)))) == 1
    assert len(list(context1triples((bob, Any, michel)))) == 1

    # unbound predicates without context, same results!
    assert len(list(triples((michel, Any, cheese)))) == 1
    assert len(list(triples((tarek, Any, cheese)))) == 1
    assert len(list(triples((bob, Any, pizza)))) == 1
    assert len(list(triples((bob, Any, michel)))) == 1

    # unbound subject, objects with context
    assert len(list(context1triples((Any, hates, Any)))) == 2
    assert len(list(context1triples((Any, likes, Any)))) == 5

    # unbound subject, objects without context, same results!
    assert len(list(triples((Any, hates, Any)))) == 2
    assert len(list(triples((Any, likes, Any)))) == 5

    # unbound predicates, objects with context
    assert len(list(context1triples((michel, Any, Any)))) == 2
    assert len(list(context1triples((bob, Any, Any)))) == 3
    assert len(list(context1triples((tarek, Any, Any)))) == 2

    # unbound predicates, objects without context, same results!
    assert len(list(triples((michel, Any, Any)))) == 2
    assert len(list(triples((bob, Any, Any)))) == 3
    assert len(list(triples((tarek, Any, Any)))) == 2

    # unbound subjects, predicates with context
    assert len(list(context1triples((Any, Any, pizza)))) == 3
    assert len(list(context1triples((Any, Any, cheese)))) == 3
    assert len(list(context1triples((Any, Any, michel)))) == 1

    # unbound subjects, predicates without context, same results!
    assert len(list(triples((Any, Any, pizza)))) == 3
    assert len(list(triples((Any, Any, cheese)))) == 3
    assert len(list(triples((Any, Any, michel)))) == 1

    # all unbound with context
    assert len(list(context1triples((Any, Any, Any)))) == 7
    # all unbound without context, same result!
    assert len(list(triples((Any, Any, Any)))) == 7

    for c in [graph, graph.get_context(c1)]:
        # unbound subjects
        assert set(c.subjects(likes, pizza)) == set((michel, tarek))
        assert set(c.subjects(hates, pizza)) == set((bob,))
        assert set(c.subjects(likes, cheese)) == set([tarek, bob, michel])
        assert set(c.subjects(hates, cheese)) == set()

        # unbound objects
        assert set(c.objects(michel, likes)) == set([cheese, pizza])
        assert set(c.objects(tarek, likes)) == set([cheese, pizza])
        assert set(c.objects(bob, hates)) == set([michel, pizza])
        assert set(c.objects(bob, likes)) == set([cheese])

        # unbound predicates
        assert set(c.predicates(michel, cheese)) == set([likes])
        assert set(c.predicates(tarek, cheese)) == set([likes])
        assert set(c.predicates(bob, pizza)) == set([hates])
        assert set(c.predicates(bob, michel)) == set([hates])

        assert set(c.subject_objects(hates)) == set([(bob, pizza), (bob, michel)])
        assert set(c.subject_objects(likes)) == set(
            [
                (tarek, cheese),
                (michel, cheese),
                (michel, pizza),
                (bob, cheese),
                (tarek, pizza),
            ]
        )

        assert set(c.predicate_objects(michel)) == set([(likes, cheese), (likes, pizza)])
        assert set(c.predicate_objects(bob)) == set([(likes, cheese), (hates, pizza), (hates, michel)])
        assert set(c.predicate_objects(tarek)) == set([(likes, cheese), (likes, pizza)])

        assert set(c.subject_predicates(pizza)) == set([(bob, hates), (tarek, likes), (michel, likes)])
        assert set(c.subject_predicates(cheese)) == set([(bob, likes), (tarek, likes), (michel, likes)])
        assert set(c.subject_predicates(michel)) == set([(bob, hates)])

        assert set(c) == set(
            [
                (bob, hates, michel),
                (bob, likes, cheese),
                (tarek, likes, pizza),
                (michel, likes, pizza),
                (michel, likes, cheese),
                (bob, hates, pizza),
                (tarek, likes, cheese),
            ]
        )
    # remove stuff and make sure the graph is empty again
    depopulate_c1(graph)
    assert len(list(context1triples((Any, Any, Any)))) == 0
    assert len(list(triples((Any, Any, Any)))) == 0
