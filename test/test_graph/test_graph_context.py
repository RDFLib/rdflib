from __future__ import annotations

import os
import shutil
import sys
import unittest
from tempfile import mkdtemp, mkstemp
from typing import Optional

import pytest

from rdflib import BNode, Dataset, Graph, URIRef, plugin
from rdflib.store import Store


class ContextTestCase(unittest.TestCase):
    store = "default"
    slow = True
    tmppath: Optional[str] = None

    def setUp(self):
        try:
            self.graph = Dataset(store=self.store, default_union=True)
        except ImportError:
            pytest.skip("Dependencies for store '%s' not available!" % self.store)
        if self.store == "SQLite":
            _, self.tmppath = mkstemp(prefix="test", dir="/tmp", suffix=".sqlite")
        else:
            self.tmppath = mkdtemp()
        self.graph.open(self.tmppath, create=True)
        self.michel = URIRef("michel")
        self.tarek = URIRef("tarek")
        self.bob = URIRef("bob")
        self.likes = URIRef("likes")
        self.hates = URIRef("hates")
        self.pizza = URIRef("pizza")
        self.cheese = URIRef("cheese")

        self.c1 = URIRef("context-1")
        self.c2 = URIRef("context-2")

        # delete the graph for each test!
        self.graph.remove((None, None, None))

    def tearDown(self):
        self.graph.close()
        if os.path.isdir(self.tmppath):
            shutil.rmtree(self.tmppath)
        else:
            os.remove(self.tmppath)

    def add_stuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        c1 = self.c1
        graph = Graph(self.graph.store, c1)

        graph.add((tarek, likes, pizza))
        graph.add((tarek, likes, cheese))
        graph.add((michel, likes, pizza))
        graph.add((michel, likes, cheese))
        graph.add((bob, likes, cheese))
        graph.add((bob, hates, pizza))
        graph.add((bob, hates, michel))  # gasp!

    def remove_stuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        c1 = self.c1
        graph = Graph(self.graph.store, c1)

        graph.remove((tarek, likes, pizza))
        graph.remove((tarek, likes, cheese))
        graph.remove((michel, likes, pizza))
        graph.remove((michel, likes, cheese))
        graph.remove((bob, likes, cheese))
        graph.remove((bob, hates, pizza))
        graph.remove((bob, hates, michel))  # gasp!

    def add_stuff_in_multiple_contexts(self):
        c1 = self.c1
        c2 = self.c2
        triple = (self.pizza, self.hates, self.tarek)  # revenge!

        # add to default context
        self.graph.add(triple)
        # add to context 1
        graph = Graph(self.graph.store, c1)
        graph.add(triple)
        # add to context 2
        graph = Graph(self.graph.store, c2)
        graph.add(triple)

    def test_conjunction(self):
        if self.store == "SQLite":
            pytest.skip("Skipping known issue with __len__")
        self.add_stuff_in_multiple_contexts()
        triple = (self.pizza, self.likes, self.pizza)
        # add to context 1
        graph = Graph(self.graph.store, self.c1)
        graph.add(triple)
        self.assertEqual(len(self.graph), len(graph))

    def test_add(self):
        self.add_stuff()

    def test_remove(self):
        self.add_stuff()
        self.remove_stuff()

    def test_len_in_one_context(self):
        c1 = self.c1
        # make sure context is empty

        self.graph.remove_context(self.graph.get_context(c1))
        graph = Graph(self.graph.store, c1)
        old_len = len(self.graph)

        for i in range(0, 10):
            graph.add((BNode(), self.hates, self.hates))
        self.assertEqual(len(graph), old_len + 10)
        self.assertEqual(len(self.graph.get_context(c1)), old_len + 10)
        self.graph.remove_context(self.graph.get_context(c1))
        self.assertEqual(len(self.graph), old_len)
        self.assertEqual(len(graph), 0)

    def test_len_in_multiple_contexts(self):
        if self.store == "SQLite":
            pytest.skip("Skipping known issue with __len__")
        old_len = len(self.graph)
        self.add_stuff_in_multiple_contexts()

        # add_stuff_in_multiple_contexts is adding the same triple to
        # three different contexts. So it's only + 1
        self.assertEqual(len(self.graph), old_len + 1)

        graph = Graph(self.graph.store, self.c1)
        self.assertEqual(len(graph), old_len + 1)

    def test_remove_in_multiple_contexts(self):
        c1 = self.c1
        c2 = self.c2
        triple = (self.pizza, self.hates, self.tarek)  # revenge!

        self.add_stuff_in_multiple_contexts()

        # triple should be still in store after removing it from c1 + c2
        self.assertTrue(triple in self.graph)
        graph = Graph(self.graph.store, c1)
        graph.remove(triple)
        self.assertTrue(triple in self.graph)
        graph = Graph(self.graph.store, c2)
        graph.remove(triple)
        self.assertTrue(triple in self.graph)
        self.graph.remove(triple)
        # now gone!
        self.assertTrue(triple not in self.graph)

        # add again and see if remove without context removes all triples!
        self.add_stuff_in_multiple_contexts()
        self.graph.remove(triple)
        self.assertTrue(triple not in self.graph)

    def test_contexts(self):
        triple = (self.pizza, self.hates, self.tarek)  # revenge!

        self.add_stuff_in_multiple_contexts()

        def cid(c):
            return c.identifier

        self.assertTrue(self.c1 in map(cid, self.graph.contexts()))
        self.assertTrue(self.c2 in map(cid, self.graph.contexts()))

        context_list = list(map(cid, list(self.graph.contexts(triple))))
        self.assertTrue(self.c1 in context_list, (self.c1, context_list))
        self.assertTrue(self.c2 in context_list, (self.c2, context_list))

    def test_remove_context(self):
        c1 = self.c1

        self.add_stuff_in_multiple_contexts()
        self.assertEqual(len(Graph(self.graph.store, c1)), 1)
        self.assertEqual(len(self.graph.get_context(c1)), 1)

        self.graph.remove_context(self.graph.get_context(c1))
        self.assertTrue(self.c1 not in self.graph.contexts())

    def test_remove_any(self):
        any = None
        self.add_stuff_in_multiple_contexts()
        self.graph.remove((any, any, any))
        self.assertEqual(len(self.graph), 0)

    def test_triples(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        c1 = self.c1
        asserte = self.assertEqual
        triples = self.graph.triples
        graph = self.graph
        c1graph = Graph(self.graph.store, c1)
        c1triples = c1graph.triples
        any = None

        self.add_stuff()

        # unbound subjects with context
        asserte(len(list(c1triples((any, likes, pizza)))), 2)
        asserte(len(list(c1triples((any, hates, pizza)))), 1)
        asserte(len(list(c1triples((any, likes, cheese)))), 3)
        asserte(len(list(c1triples((any, hates, cheese)))), 0)

        # unbound subjects without context, same results!
        asserte(len(list(triples((any, likes, pizza)))), 2)
        asserte(len(list(triples((any, hates, pizza)))), 1)
        asserte(len(list(triples((any, likes, cheese)))), 3)
        asserte(len(list(triples((any, hates, cheese)))), 0)

        # unbound objects with context
        asserte(len(list(c1triples((michel, likes, any)))), 2)
        asserte(len(list(c1triples((tarek, likes, any)))), 2)
        asserte(len(list(c1triples((bob, hates, any)))), 2)
        asserte(len(list(c1triples((bob, likes, any)))), 1)

        # unbound objects without context, same results!
        asserte(len(list(triples((michel, likes, any)))), 2)
        asserte(len(list(triples((tarek, likes, any)))), 2)
        asserte(len(list(triples((bob, hates, any)))), 2)
        asserte(len(list(triples((bob, likes, any)))), 1)

        # unbound predicates with context
        asserte(len(list(c1triples((michel, any, cheese)))), 1)
        asserte(len(list(c1triples((tarek, any, cheese)))), 1)
        asserte(len(list(c1triples((bob, any, pizza)))), 1)
        asserte(len(list(c1triples((bob, any, michel)))), 1)

        # unbound predicates without context, same results!
        asserte(len(list(triples((michel, any, cheese)))), 1)
        asserte(len(list(triples((tarek, any, cheese)))), 1)
        asserte(len(list(triples((bob, any, pizza)))), 1)
        asserte(len(list(triples((bob, any, michel)))), 1)

        # unbound subject, objects with context
        asserte(len(list(c1triples((any, hates, any)))), 2)
        asserte(len(list(c1triples((any, likes, any)))), 5)

        # unbound subject, objects without context, same results!
        asserte(len(list(triples((any, hates, any)))), 2)
        asserte(len(list(triples((any, likes, any)))), 5)

        # unbound predicates, objects with context
        asserte(len(list(c1triples((michel, any, any)))), 2)
        asserte(len(list(c1triples((bob, any, any)))), 3)
        asserte(len(list(c1triples((tarek, any, any)))), 2)

        # unbound predicates, objects without context, same results!
        asserte(len(list(triples((michel, any, any)))), 2)
        asserte(len(list(triples((bob, any, any)))), 3)
        asserte(len(list(triples((tarek, any, any)))), 2)

        # unbound subjects, predicates with context
        asserte(len(list(c1triples((any, any, pizza)))), 3)
        asserte(len(list(c1triples((any, any, cheese)))), 3)
        asserte(len(list(c1triples((any, any, michel)))), 1)

        # unbound subjects, predicates without context, same results!
        asserte(len(list(triples((any, any, pizza)))), 3)
        asserte(len(list(triples((any, any, cheese)))), 3)
        asserte(len(list(triples((any, any, michel)))), 1)

        # all unbound with context
        asserte(len(list(c1triples((any, any, any)))), 7)
        # all unbound without context, same result!
        asserte(len(list(triples((any, any, any)))), 7)

        for c in [graph, self.graph.get_context(c1)]:
            # unbound subjects
            asserte(set(c.subjects(likes, pizza)), {michel, tarek})
            asserte(set(c.subjects(hates, pizza)), {bob})
            asserte(set(c.subjects(likes, cheese)), {tarek, bob, michel})
            asserte(set(c.subjects(hates, cheese)), set())

            # unbound objects
            asserte(set(c.objects(michel, likes)), {cheese, pizza})
            asserte(set(c.objects(tarek, likes)), {cheese, pizza})
            asserte(set(c.objects(bob, hates)), {michel, pizza})
            asserte(set(c.objects(bob, likes)), {cheese})

            # unbound predicates
            asserte(set(c.predicates(michel, cheese)), {likes})
            asserte(set(c.predicates(tarek, cheese)), {likes})
            asserte(set(c.predicates(bob, pizza)), {hates})
            asserte(set(c.predicates(bob, michel)), {hates})

            asserte(set(c.subject_objects(hates)), {(bob, pizza), (bob, michel)})
            asserte(
                set(c.subject_objects(likes)),
                {
                    (tarek, cheese),
                    (michel, cheese),
                    (michel, pizza),
                    (bob, cheese),
                    (tarek, pizza),
                },
            )

            asserte(set(c.predicate_objects(michel)), {(likes, cheese), (likes, pizza)})
            asserte(
                set(c.predicate_objects(bob)),
                {(likes, cheese), (hates, pizza), (hates, michel)},
            )
            asserte(set(c.predicate_objects(tarek)), {(likes, cheese), (likes, pizza)})

            asserte(
                set(c.subject_predicates(pizza)),
                {(bob, hates), (tarek, likes), (michel, likes)},
            )
            asserte(
                set(c.subject_predicates(cheese)),
                {(bob, likes), (tarek, likes), (michel, likes)},
            )
            asserte(set(c.subject_predicates(michel)), {(bob, hates)})

            d = set()
            for x in c:
                d.add(x[0:3])
            asserte(
                set(d),
                {
                    (bob, hates, michel),
                    (bob, likes, cheese),
                    (tarek, likes, pizza),
                    (michel, likes, pizza),
                    (michel, likes, cheese),
                    (bob, hates, pizza),
                    (tarek, likes, cheese),
                },
            )

        # remove stuff and make sure the graph is empty again
        self.remove_stuff()
        asserte(len(list(c1triples((any, any, any)))), 0)
        asserte(len(list(triples((any, any, any)))), 0)


# dynamically create classes for each registered Store
pluginname = None
if __name__ == "__main__":
    if len(sys.argv) > 1:
        pluginname = sys.argv[1]

tests = 0
for s in plugin.plugins(pluginname, Store):
    if s.name in (
        "default",
        "Memory",
        "Auditable",
        "Concurrent",
        "SPARQLStore",
        "SPARQLUpdateStore",
    ):
        continue  # these are tested by default
    if not s.getClass().context_aware:
        continue

    locals()["t%d" % tests] = type(
        "%sContextTestCase" % s.name, (ContextTestCase,), {"store": s.name}
    )
    tests += 1


if __name__ == "__main__":
    unittest.main()
