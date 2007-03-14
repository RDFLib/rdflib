# -*- coding: UTF-8 -*-
#=======================================================================
from rdflib import ConjunctiveGraph, URIRef, Literal, BNode, RDFS
from rdflib.syntax.serializers.PrettyXMLSerializer import PrettyXMLSerializer
from test.serializers import SerializerTestBase, serialize, serialize_and_load
#=======================================================================


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
            rdfs:seeAlso <http://example.org/data/b> .

        <http://example.org/data/b> :name "B"@en .

        <http://example.org/data/c> a rdfs:Resource;
            rdfs:seeAlso <http://example.org/data/c> .

        <http://example.org/data/d> a rdfs:Resource;
            rdfs:seeAlso <http://example.org/data/c> ;
            rdfs:seeAlso <http://example.org/data/b> ;
            rdfs:seeAlso <http://example.org/data/a> .

        _:abc1 a :BNode;
            rdfs:seeAlso _:abc2 .

        _:abc2 a :BNode ;
            rdfs:seeAlso _:abc3 .

        _:abc3 a :BNode ;
            rdfs:seeAlso _:abc2 .

        """
    testContentFormat = 'n3'

    def test_result_fragments(self):
        rdfXml = serialize(self.sourceGraph, self.serializer)
        assert '<Test rdf:about="http://example.org/data/a">' in rdfXml
        assert '<rdf:Description rdf:about="http://example.org/data/b">' in rdfXml
        assert '<name xml:lang="en">B</name>' in rdfXml
        onlyBNodesMsg = "expected only inlined bnodes in serialized graph"
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


