# -*- coding: UTF-8 -*-
#=======================================================================
from rdflib import ConjunctiveGraph, BNode
from StringIO import StringIO
#=======================================================================


class SerializerTestBase(object):

    repeats = 8

    def setup(self):
        graph = ConjunctiveGraph()
        graph.load(StringIO(self.testContent), format=self.testContentFormat)
        self.sourceGraph = graph

    def test_serialize_and_reparse(self):
        reparsedGraph = serialize_and_load(self.sourceGraph, self.serializer)
        _assert_equal_graphs(self.sourceGraph, reparsedGraph)

    def test_multiple(self):
        """Repeats ``test_serialize`` ``self.repeats`` times, to reduce sucess based on in-memory ordering."""
        for i in range(self.repeats):
            self.test_serialize_and_reparse()

    #test_multiple.slowtest=True # not really slow?


def _assert_equal_graphs(g1, g2):
    assert len(g1) == len(g2), "Serialized graph not same size as source graph."
    g1copy = _mangled_copy(g1)
    g2copy = _mangled_copy(g2)
    g1copy -= _mangled_copy(g2)
    g2copy -= _mangled_copy(g1)
    assert len(g1copy) == 0, "Source graph larger than serialized graph."
    assert len(g2copy) == 0, "Serialized graph larger than source graph."

_blank = BNode()

def _mangled_copy(g):
    "Makes a copy of the graph, replacing all bnodes with the bnode ``_blank``."
    gcopy = ConjunctiveGraph()
    isbnode = lambda v: isinstance(v, BNode)
    for s, p, o in g:
        if isbnode(s): s = _blank
        if isbnode(p): p = _blank
        if isbnode(o): o = _blank
        gcopy.add((s, p, o))
    return gcopy


def serialize(sourceGraph, makeSerializer, getValue=True):
    serializer = makeSerializer(sourceGraph)
    stream = StringIO()
    serializer.serialize(stream)
    return getValue and stream.getvalue() or stream

def serialize_and_load(sourceGraph, makeSerializer):
    stream = serialize(sourceGraph, makeSerializer, False)
    stream.seek(0)
    reparsedGraph = ConjunctiveGraph()
    reparsedGraph.load(stream)
    return reparsedGraph


