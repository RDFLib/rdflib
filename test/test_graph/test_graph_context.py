import sys
import os
import unittest

from tempfile import mkdtemp, mkstemp
import shutil

import pytest
from rdflib import Graph, Dataset, URIRef, BNode, plugin
import test.data
from test.data import (
    michel,
    tarek,
    bob,
    likes,
    hates,
    pizza,
    cheese,
    context1,
    context2,
)

c1 = test.data.context1
c2 = test.data.context2

class ContextTestCase(unittest.TestCase):
    store = "default"
    michel = test.data.michel
    tarek = test.data.tarek
    bob = test.data.bob
    likes = test.data.likes
    hates = test.data.hates
    pizza = test.data.pizza
    cheese = test.data.cheese
    c1 = test.data.context1
    c2 = test.data.context2

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

        # delete the graph for each test!
        self.graph.remove((None, None, None))

    def tearDown(self):
        self.graph.close()
        if os.path.isdir(self.tmppath):
            shutil.rmtree(self.tmppath)
        else:
            os.remove(self.tmppath)

    def addStuff(self):
        graph = Graph(self.graph.store, c1)

        graph.add((tarek, likes, pizza))
        graph.add((tarek, likes, cheese))
        graph.add((michel, likes, pizza))
        graph.add((michel, likes, cheese))
        graph.add((bob, likes, cheese))
        graph.add((bob, hates, pizza))
        graph.add((bob, hates, michel))  # gasp!

    def removeStuff(self):
        graph = Graph(self.graph.store, c1)

        graph.remove((tarek, likes, pizza))
        graph.remove((tarek, likes, cheese))
        graph.remove((michel, likes, pizza))
        graph.remove((michel, likes, cheese))
        graph.remove((bob, likes, cheese))
        graph.remove((bob, hates, pizza))
        graph.remove((bob, hates, michel))  # gasp!

    def addStuffInMultipleContexts(self):
        triple = (self.pizza, self.hates, self.tarek)  # revenge!

        # add to default context
        self.graph.add(triple)
        # add to context 1
        graph = Graph(self.graph.store, c1)
        graph.add(triple)
        # add to context 2
        graph = Graph(self.graph.store, c2)
        graph.add(triple)

    def testConjunction(self):
        self.addStuffInMultipleContexts()
        triple = (self.pizza, self.likes, self.pizza)
        # add to context 1
        graph = Graph(self.graph.store, self.c1)
        graph.add(triple)
        assert len(self.graph) == len(graph)

    def testAdd(self):
        self.addStuff()

    def testRemove(self):
        self.addStuff()
        self.removeStuff()

    def testLenInOneContext(self):
        c1 = self.c1
        # make sure context is empty

        self.graph.remove_graph(self.graph.graph(c1))
        graph = Graph(self.graph.store, c1)
        oldLen = len(self.graph)

        for i in range(0, 10):
            graph.add((BNode(), self.hates, self.hates))
        assert len(graph) == oldLen + 10
        assert len(self.graph.get_context(c1)) == oldLen + 10
        self.graph.remove_graph(self.graph.graph(c1))
        assert len(self.graph) == oldLen
        assert len(graph) == 0

    def testLenInMultipleContexts(self):
        oldLen = len(self.graph)
        self.addStuffInMultipleContexts()

        # addStuffInMultipleContexts is adding the same triple to
        # three different contexts. So it's only + 1
        assert len(self.graph) == oldLen + 1

        graph = Graph(self.graph.store, self.c1)
        assert len(graph) == oldLen + 1

    def testRemoveInMultipleContexts(self):
        triple = (self.pizza, self.hates, self.tarek)  # revenge!

        self.addStuffInMultipleContexts()

        # triple should be still in store after removing it from c1 + c2
        assert triple in self.graph
        graph = Graph(self.graph.store, c1)
        graph.remove(triple)
        assert triple in self.graph
        graph = Graph(self.graph.store, c2)
        graph.remove(triple)
        assert triple in self.graph
        self.graph.remove(triple)
        # now gone!
        assert triple not in self.graph

        # add again and see if remove without context removes all triples!
        self.addStuffInMultipleContexts()
        self.graph.remove(triple)
        assert triple not in self.graph

    def testContexts(self):
        triple = (self.pizza, self.hates, self.tarek)  # revenge!

        self.addStuffInMultipleContexts()

        assert self.c1 in self.graph.contexts()
        assert self.c2 in self.graph.contexts()

        contextList = list(self.graph.contexts(triple))
        assert self.c1 in contextList, (self.c1, contextList)
        assert self.c2 in contextList, (self.c2, contextList)

    def testRemoveContext(self):

        self.addStuffInMultipleContexts()
        assert len(Graph(self.graph.store, c1)) == 1
        assert len(self.graph.get_context(c1)) == 1

        self.graph.remove_graph(self.graph.graph(c1))
        assert self.c1 not in self.graph.contexts()

    def testRemoveAny(self):
        Any = None
        self.addStuffInMultipleContexts()
        self.graph.remove((Any, Any, Any))
        assert len(self.graph) == 0

    def testTriples(self):
        triples = self.graph.triples
        graph = self.graph
        c1graph = Graph(self.graph.store, c1)
        c1triples = c1graph.triples
        Any = None

        self.addStuff()

        # unbound subjects with context
        assert len(list(c1triples((Any, likes, pizza)))) == 2
        assert len(list(c1triples((Any, hates, pizza)))) == 1
        assert len(list(c1triples((Any, likes, cheese)))) == 3
        assert len(list(c1triples((Any, hates, cheese)))) == 0

        # unbound subjects without context, same results!
        assert len(list(triples((Any, likes, pizza)))) == 2
        assert len(list(triples((Any, hates, pizza)))) == 1
        assert len(list(triples((Any, likes, cheese)))) == 3
        assert len(list(triples((Any, hates, cheese)))) == 0

        # unbound objects with context
        assert len(list(c1triples((michel, likes, Any)))) == 2
        assert len(list(c1triples((tarek, likes, Any)))) == 2
        assert len(list(c1triples((bob, hates, Any)))) == 2
        assert len(list(c1triples((bob, likes, Any)))) == 1

        # unbound objects without context, same results!
        assert len(list(triples((michel, likes, Any)))) == 2
        assert len(list(triples((tarek, likes, Any)))) == 2
        assert len(list(triples((bob, hates, Any)))) == 2
        assert len(list(triples((bob, likes, Any)))) == 1

        # unbound predicates with context
        assert len(list(c1triples((michel, Any, cheese)))) == 1
        assert len(list(c1triples((tarek, Any, cheese)))) == 1
        assert len(list(c1triples((bob, Any, pizza)))) == 1
        assert len(list(c1triples((bob, Any, michel)))) == 1

        # unbound predicates without context, same results!
        assert len(list(triples((michel, Any, cheese)))) == 1
        assert len(list(triples((tarek, Any, cheese)))) == 1
        assert len(list(triples((bob, Any, pizza)))) == 1
        assert len(list(triples((bob, Any, michel)))) == 1

        # unbound subject, objects with context
        assert len(list(c1triples((Any, hates, Any)))) == 2
        assert len(list(c1triples((Any, likes, Any)))) == 5

        # unbound subject, objects without context, same results!
        assert len(list(triples((Any, hates, Any)))) == 2
        assert len(list(triples((Any, likes, Any)))) == 5

        # unbound predicates, objects with context
        assert len(list(c1triples((michel, Any, Any)))) == 2
        assert len(list(c1triples((bob, Any, Any)))) == 3
        assert len(list(c1triples((tarek, Any, Any)))) == 2

        # unbound predicates, objects without context, same results!
        assert len(list(triples((michel, Any, Any)))) == 2
        assert len(list(triples((bob, Any, Any)))) == 3
        assert len(list(triples((tarek, Any, Any)))) == 2

        # unbound subjects, predicates with context
        assert len(list(c1triples((Any, Any, pizza)))) == 3
        assert len(list(c1triples((Any, Any, cheese)))) == 3
        assert len(list(c1triples((Any, Any, michel)))) == 1

        # unbound subjects, predicates without context, same results!
        assert len(list(triples((Any, Any, pizza)))) == 3
        assert len(list(triples((Any, Any, cheese)))) == 3
        assert len(list(triples((Any, Any, michel)))) == 1

        # all unbound with context
        assert len(list(c1triples((Any, Any, Any)))) == 7
        # all unbound without context, same result!
        assert len(list(triples((Any, Any, Any)))) == 7

        for c in [graph, self.graph.get_context(c1)]:
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

            assert set(c.triples((None, None, None))) == set(
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
        self.removeStuff()
        assert len(list(c1triples((Any, Any, Any)))) == 0
        assert len(list(triples((Any, Any, Any)))) == 0


# dynamically create classes for each registered Store
pluginname = None
if __name__ == "__main__":
    if len(sys.argv) > 1:
        pluginname = sys.argv[1]

tests = 0
for s in plugin.plugins(pluginname, plugin.Store):
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
