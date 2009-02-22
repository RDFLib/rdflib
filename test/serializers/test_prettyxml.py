from rdflib.term import  URIRef, BNode
from rdflib import RDFS

from rdflib.syntax.serializers.PrettyXMLSerializer import PrettyXMLSerializer
from test.serializers import SerializerTestBase, serialize, serialize_and_load



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


