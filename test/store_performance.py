import unittest
import os
import gc
import itertools
from time import time
from random import random

from tempfile import mkdtemp
import shutil

from rdflib.term import URIRef
from rdflib.graph import Graph


def random_uri():
    return URIRef("%s" % random())


class StoreTestCase(unittest.TestCase):
    """
    Test case for testing store performance... probably should be
    something other than a unit test... but for now we'll add it as a
    unit test.
    """

    store = "default"
    tmppath = None
    configString = os.environ.get("DBURI", "dburi")

    def setUp(self):
        self.gcold = gc.isenabled()
        gc.collect()
        gc.disable()
        self.graph = Graph(store=self.store)
        if self.store == "MySQL":
            # from test.mysql import configString
            from rdflib.store.MySQL import MySQL

            path = self.configString
            MySQL().destroy(path)
        else:
            self.tmppath = mkdtemp()
        self.graph.open(self.tmppath, create=True)
        self.input = input = Graph()
        input.parse("http://eikeon.com")

    def tearDown(self):
        self.graph.close()
        if self.gcold:
            gc.enable()
        del self.graph
        shutil.rmtree(self.tmppath)

    def testTime(self):
        number = 1
        print(self.store)
        print("input:", end=" ")
        for i in itertools.repeat(None, number):
            self._testInput()
        print("random:", end=" ")
        for i in itertools.repeat(None, number):
            self._testRandom()
        print(".")

    def _testRandom(self):
        number = len(self.input)
        store = self.graph

        def add_random():
            s = random_uri()
            p = random_uri()
            o = random_uri()
            store.add((s, p, o))

        it = itertools.repeat(None, number)
        t0 = time()
        for _i in it:
            add_random()
        t1 = time()
        print("%.3g" % (t1 - t0), end=" ")

    def _testInput(self):
        number = 1
        store = self.graph

        def add_from_input():
            for t in self.input:
                store.add(t)

        it = itertools.repeat(None, number)
        t0 = time()
        for _i in it:
            add_from_input()
        t1 = time()
        print("%.3g" % (t1 - t0), end=" ")


class MemoryStoreTestCase(StoreTestCase):
    store = "Memory"


if __name__ == "__main__":
    unittest.main()
