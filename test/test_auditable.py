# -*- coding=utf8 -*-
from __future__ import unicode_literals
from nose.tools import assert_items_equal
import unittest

from rdflib import Graph, Namespace
from rdflib.plugins.stores.auditable import AuditableStore

EX = Namespace("http://example.org/")


class TestAuditableStore(unittest.TestCase):

    def setUp(self):
        self.g = Graph()
        self.g.add((EX.s0, EX.p0, EX.o0))
        self.g.add((EX.s0, EX.p0, EX.o0bis))

        self.t = Graph(AuditableStore(self.g.store),
                       self.g.identifier)

    def test_add_commit(self):
        self.t.add((EX.s1, EX.p1, EX.o1))
        assert_items_equal(self.t, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
            (EX.s1, EX.p1, EX.o1),
        ])
        self.t.commit()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
            (EX.s1, EX.p1, EX.o1),
        ])

    def test_remove_commit(self):
        self.t.remove((EX.s0, EX.p0, EX.o0))
        assert_items_equal(self.t, [
            (EX.s0, EX.p0, EX.o0bis),
        ])
        self.t.commit()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_multiple_remove_commit(self):
        self.t.remove((EX.s0, EX.p0, None))
        assert_items_equal(self.t, [
        ])
        self.t.commit()
        assert_items_equal(self.g, [
        ])

    def test_noop_add_commit(self):
        self.t.add((EX.s0, EX.p0, EX.o0))
        assert_items_equal(self.t, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])
        self.t.commit()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_noop_remove_commit(self):
        self.t.add((EX.s0, EX.p0, EX.o0))
        assert_items_equal(self.t, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])
        self.t.commit()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_add_remove_commit(self):
        self.t.add((EX.s1, EX.p1, EX.o1))
        self.t.remove((EX.s1, EX.p1, EX.o1))
        assert_items_equal(self.t, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])
        self.t.commit()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_remove_add_commit(self):
        self.t.remove((EX.s1, EX.p1, EX.o1))
        self.t.add((EX.s1, EX.p1, EX.o1))
        assert_items_equal(self.t, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
            (EX.s1, EX.p1, EX.o1),
        ])
        self.t.commit()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
            (EX.s1, EX.p1, EX.o1),
        ])

    def test_add_rollback(self):
        self.t.add((EX.s1, EX.p1, EX.o1))
        self.t.rollback()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_remove_rollback(self):
        self.t.remove((EX.s0, EX.p0, EX.o0))
        self.t.rollback()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_multiple_remove_rollback(self):
        self.t.remove((EX.s0, EX.p0, None))
        self.t.rollback()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_noop_add_rollback(self):
        self.t.add((EX.s0, EX.p0, EX.o0))
        self.t.rollback()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_noop_remove_rollback(self):
        self.t.add((EX.s0, EX.p0, EX.o0))
        self.t.rollback()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_add_remove_rollback(self):
        self.t.add((EX.s1, EX.p1, EX.o1))
        self.t.remove((EX.s1, EX.p1, EX.o1))
        self.t.rollback()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_remove_add_rollback(self):
        self.t.remove((EX.s1, EX.p1, EX.o1))
        self.t.add((EX.s1, EX.p1, EX.o1))
        self.t.rollback()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])


class TestAuditableStoreEmptyGraph(unittest.TestCase):

    def setUp(self):
        self.g = Graph()
        self.t = Graph(AuditableStore(self.g.store),
                       self.g.identifier)

    def test_add_commit(self):
        self.t.add((EX.s1, EX.p1, EX.o1))
        assert_items_equal(self.t, [
            (EX.s1, EX.p1, EX.o1),
        ])
        self.t.commit()
        assert_items_equal(self.g, [
            (EX.s1, EX.p1, EX.o1),
        ])

    def test_add_rollback(self):
        self.t.add((EX.s1, EX.p1, EX.o1))
        self.t.rollback()
        assert_items_equal(self.g, [
        ])


class TestAuditableStoreConccurent(unittest.TestCase):

    def setUp(self):
        self.g = Graph()
        self.g.add((EX.s0, EX.p0, EX.o0))
        self.g.add((EX.s0, EX.p0, EX.o0bis))
        self.t1 = Graph(AuditableStore(self.g.store),
                        self.g.identifier)
        self.t2 = Graph(AuditableStore(self.g.store),
                        self.g.identifier)
        self.t1.add((EX.s1, EX.p1, EX.o1))
        self.t2.add((EX.s2, EX.p2, EX.o2))
        self.t1.remove((EX.s0, EX.p0, EX.o0))
        self.t2.remove((EX.s0, EX.p0, EX.o0bis))

    def test_commit_commit(self):
        self.t1.commit()
        self.t2.commit()
        assert_items_equal(self.g, [
            (EX.s1, EX.p1, EX.o1),
            (EX.s2, EX.p2, EX.o2),
        ])

    def test_commit_rollback(self):
        self.t1.commit()
        self.t2.rollback()
        assert_items_equal(self.g, [
            (EX.s1, EX.p1, EX.o1),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_rollback_commit(self):
        self.t1.rollback()
        self.t2.commit()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s2, EX.p2, EX.o2),
        ])

    def test_rollback_rollback(self):
        self.t1.rollback()
        self.t2.rollback()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])


class TestAuditableStoreEmbeded(unittest.TestCase):

    def setUp(self):
        self.g = Graph()
        self.g.add((EX.s0, EX.p0, EX.o0))
        self.g.add((EX.s0, EX.p0, EX.o0bis))

        self.t1 = Graph(AuditableStore(self.g.store),
                        self.g.identifier)
        self.t1.add((EX.s1, EX.p1, EX.o1))
        self.t1.remove((EX.s0, EX.p0, EX.o0bis))

        self.t2 = Graph(AuditableStore(self.t1.store),
                        self.t1.identifier)
        self.t2.add((EX.s2, EX.p2, EX.o2))
        self.t2.remove((EX.s1, EX.p1, EX.o1))

    def test_commit_commit(self):
        assert_items_equal(self.t2, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s2, EX.p2, EX.o2),
        ])
        self.t2.commit()
        assert_items_equal(self.t1, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s2, EX.p2, EX.o2),
        ])
        self.t1.commit()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s2, EX.p2, EX.o2),
        ])

    def test_commit_rollback(self):
        self.t2.commit()
        self.t1.rollback()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

    def test_rollback_commit(self):
        self.t2.rollback()
        assert_items_equal(self.t1, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s1, EX.p1, EX.o1),
        ])
        self.t1.commit()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s1, EX.p1, EX.o1),
        ])

    def test_rollback_rollback(self):
        self.t2.rollback()
        self.t1.rollback()
        assert_items_equal(self.g, [
            (EX.s0, EX.p0, EX.o0),
            (EX.s0, EX.p0, EX.o0bis),
        ])

