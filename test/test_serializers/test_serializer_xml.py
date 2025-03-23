from io import BytesIO

from rdflib.graph import Dataset
from rdflib.namespace import RDFS
from rdflib.plugins.serializers.rdfxml import XMLSerializer
from rdflib.term import BNode, URIRef


class SerializerTestBase:
    repeats = 8

    def setup_method(self):
        graph = Dataset(default_union=True)
        graph.parse(data=self.test_content, format=self.test_content_format)
        self.source_graph = graph

    def test_serialize_and_reparse(self):
        reparsed_graph = serialize_and_load(self.source_graph, self.serializer)
        _assert_equal_graphs(self.source_graph, reparsed_graph)

    def test_multiple(self):
        """Repeats ``test_serialize`` ``self.repeats`` times, to reduce sucess based on in-memory ordering."""
        for i in range(self.repeats):
            self.test_serialize_and_reparse()

    # test_multiple.slowtest=True # not really slow?


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
    """Makes a copy of the graph, replacing all bnodes with the bnode ``_blank``."""
    gcopy = Dataset()

    def isbnode(v):
        return isinstance(v, BNode)

    for s, p, o, c in g:
        if isbnode(s):
            s = _blank
        if isbnode(p):
            p = _blank
        if isbnode(o):
            o = _blank
        gcopy.add((s, p, o))
    return gcopy


def serialize(source_graph, make_serializer, get_value=True, extra_args={}):
    serializer = make_serializer(source_graph)
    stream = BytesIO()
    serializer.serialize(stream, **extra_args)
    return get_value and stream.getvalue() or stream


def serialize_and_load(source_graph, make_serializer):
    stream = serialize(source_graph, make_serializer, False)
    stream.seek(0)
    reparsed_graph = Dataset(default_union=True)
    reparsed_graph.parse(stream, format="xml")
    return reparsed_graph


class TestXMLSerializer(SerializerTestBase):
    serializer = XMLSerializer

    test_content = """
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
    test_content_format = "n3"

    def test_result_fragments(self):
        rdf_xml = serialize(self.source_graph, self.serializer)
        # print "--------"
        # print rdf_xml
        # print "--------"
        assert (
            '<rdf:Description rdf:about="http://example.org/data/a">'.encode("latin-1")
            in rdf_xml
        )
        assert (
            '<rdf:type rdf:resource="http://example.org/model/test#Test"/>'.encode(
                "latin-1"
            )
            in rdf_xml
        )
        assert (
            '<rdf:Description rdf:about="http://example.org/data/b">'.encode("latin-1")
            in rdf_xml
        )
        assert '<name xml:lang="en">Bee</name>'.encode("latin-1") in rdf_xml
        assert (
            '<value rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">3</value>'.encode(
                "latin-1"
            )
            in rdf_xml
        )
        assert (
            '<rdf:Description rdf:nodeID="'.encode("latin-1") in rdf_xml
        ), "expected one identified bnode in serialized graph"

    def test_result_fragments_with_base(self):
        rdf_xml = serialize(
            self.source_graph,
            self.serializer,
            extra_args={
                "base": "http://example.org/",
                "xml_base": "http://example.org/",
            },
        )
        # print "--------"
        # print rdf_xml
        # print "--------"
        assert 'xml:base="http://example.org/"'.encode("latin-1") in rdf_xml
        assert '<rdf:Description rdf:about="data/a">'.encode("latin-1") in rdf_xml
        assert '<rdf:type rdf:resource="model/test#Test"/>'.encode("latin-1") in rdf_xml
        assert '<rdf:Description rdf:about="data/b">'.encode("latin-1") in rdf_xml
        assert (
            '<value rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">3</value>'.encode(
                "latin-1"
            )
            in rdf_xml
        )
        assert (
            '<rdf:Description rdf:nodeID="'.encode("latin-1") in rdf_xml
        ), "expected one identified bnode in serialized graph"

    def test_subclass_of_objects(self):
        reparsed_graph = serialize_and_load(self.source_graph, self.serializer)
        _assert_expected_object_types_for_predicates(
            reparsed_graph, [RDFS.seeAlso, RDFS.subClassOf], [URIRef, BNode]
        )


def _assert_expected_object_types_for_predicates(graph, predicates, types):
    for s, p, o, c in graph:
        if p in predicates:
            some_true = [isinstance(o, t) for t in types]
            assert (
                True in some_true
            ), "Bad type %s for object when predicate is <%s>." % (type(o), p)
