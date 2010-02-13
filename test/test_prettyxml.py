from rdflib.term import  URIRef, BNode
from rdflib.namespace import RDFS

from rdflib.plugins.serializers.rdfxml import PrettyXMLSerializer

from rdflib.graph import ConjunctiveGraph
from StringIO import StringIO


class SerializerTestBase(object):

    repeats = 8

    def setup(self):
        graph = ConjunctiveGraph()
        graph.parse(data=self.testContent, format=self.testContentFormat)
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


class TestPrettyXmlSerializer(SerializerTestBase):

    serializer = PrettyXMLSerializer

    testContent = """
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix owl:  <http://www.w3.org/2002/07/owl#> .
        @prefix : <http://example.org/model/test#> .

        :value rdfs:domain :Test .

        :Test rdfs:subClassOf
            [ a owl:Restriction;
                owl:onProperty :value ],
            [ a owl:Restriction;
                owl:onProperty :name ] .

        <http://example.org/data/a> a :Test;
            rdfs:seeAlso <http://example.org/data/b>;
            :value "A" .

        <http://example.org/data/b>
            :name "Bee"@en, "Be"@sv;
            :value "B" .

        <http://example.org/data/c> a rdfs:Resource;
            rdfs:seeAlso <http://example.org/data/c>;
            :value 3 .

        <http://example.org/data/d> a rdfs:Resource;
            rdfs:seeAlso <http://example.org/data/c> ;
            rdfs:seeAlso <http://example.org/data/b> ;
            rdfs:seeAlso <http://example.org/data/a> .

        _:bnode1 a :BNode;
            rdfs:seeAlso _:bnode2 .

        _:bnode2 a :BNode ;
            rdfs:seeAlso _:bnode3 .

        _:bnode3 a :BNode ;
            rdfs:seeAlso _:bnode2 .

        """
    testContentFormat = 'n3'

    def test_result_fragments(self):
        rdfXml = serialize(self.sourceGraph, self.serializer)
        assert '<Test rdf:about="http://example.org/data/a">' in rdfXml
        assert '<rdf:Description rdf:about="http://example.org/data/b">' in rdfXml
        assert '<name xml:lang="en">Bee</name>' in rdfXml
        assert '<value rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">3</value>' in rdfXml
        assert '<BNode rdf:nodeID="' in rdfXml, "expected one identified bnode in serialized graph"
        #onlyBNodesMsg = "expected only inlined subClassOf-bnodes in serialized graph"
        #assert '<rdfs:subClassOf>' in rdfXml, onlyBNodesMsg
        #assert not '<rdfs:subClassOf ' in rdfXml, onlyBNodesMsg

    def test_subClassOf_objects(self):
        reparsedGraph = serialize_and_load(self.sourceGraph, self.serializer)
        _assert_expected_object_types_for_predicates(reparsedGraph,
                [RDFS.seeAlso, RDFS.subClassOf],
                [URIRef, BNode])


def _assert_expected_object_types_for_predicates(graph, predicates, types):
    for s, p, o in graph:
        if p in predicates:
            someTrue = [isinstance(o, t) for t in types]
            assert True in someTrue, \
                    "Bad type %s for object when predicate is <%s>." % (type(o), p)


