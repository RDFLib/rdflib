from rdflib import RDF, BNode, ConjunctiveGraph, Graph, Literal, Namespace
from rdflib.collection import Collection

target1xml = """\
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:ns1="http://www.example.org/foo/ns/"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <ns1:Other rdf:about="http://www.example.org/example/foo/thing">
    <rdf:first>
      <ns1:Item rdf:about="http://www.example.org/example/foo/a"/>
    </rdf:first>
    <ns1:property>Some Value</ns1:property>
    <rdf:rest rdf:parseType="Collection">
      <rdf:Description rdf:about="http://www.example.org/example/foo/b"/>
      <rdf:Description rdf:about="http://www.example.org/example/foo/c"/>
    </rdf:rest>
  </ns1:Other>
  <ns1:Item rdf:about="http://www.example.org/example/foo/b"/>
  <ns1:Item rdf:about="http://www.example.org/example/foo/c"/>
</rdf:RDF>"""

target2xml = """\
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:ns1="http://www.example.org/foo/ns/"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <ns1:Wrapper rdf:about="http://www.example.org/example/foo/wrapper">
    <ns1:wraps rdf:parseType="Collection">
      <rdf:Description rdf:about="http://www.example.org/example/foo/a"/>
      <rdf:Description rdf:about="http://www.example.org/example/foo/b"/>
      <rdf:Description rdf:about="http://www.example.org/example/foo/c"/>
    </ns1:wraps>
  </ns1:Wrapper>
  <ns1:Item rdf:about="http://www.example.org/example/foo/b"/>
  <ns1:Item rdf:about="http://www.example.org/example/foo/c"/>
  <ns1:Item rdf:about="http://www.example.org/example/foo/a"/>
</rdf:RDF>"""


def test_collection_render():
    foo = Namespace("http://www.example.org/foo/ns/")
    ex = Namespace("http://www.example.org/example/foo/")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    # Works:  x a rdf:List, a foo:Other ;
    # Fails:  y a foo:Wrapper, foo:wraps x; x a rdf:List, a foo:Other ;

    target1 = ConjunctiveGraph()
    target1.parse(data=target1xml, format="xml")

    g = ConjunctiveGraph()
    bits = [ex["a"], ex["b"], ex["c"]]
    l = Collection(g, ex["thing"], bits)  # noqa: E741, F841
    triple = (ex["thing"], rdf["type"], foo["Other"])
    g.add(triple)
    triple = (ex["thing"], foo["property"], Literal("Some Value"))
    g.add(triple)
    for b in bits:
        triple = (b, rdf["type"], foo["Item"])
        g.add(triple)
    assert g.isomorphic(target1) is True

    g.add((ex["wrapper"], rdf["type"], foo["Wrapper"]))
    g.add((ex["wrapper"], foo["wraps"], ex["thing"]))
    resxml = g.serialize(format="pretty-xml")
    roundtrip = Graph()
    roundtrip.parse(data=resxml, format="xml")
    assert roundtrip.isomorphic(g) is True


def test_bnode_list_with_extra_predicates_and_shared_tail() -> None:
    foo = Namespace("http://www.example.org/foo/ns/")
    ex = Namespace("http://www.example.org/example/foo/")

    g = Graph()
    tail = BNode()
    head = BNode()
    g.add((tail, RDF.first, ex["b"]))
    g.add((tail, RDF.rest, RDF.nil))
    g.add((head, RDF.first, ex["a"]))
    g.add((head, RDF.rest, tail))
    g.add((head, foo["extra"], Literal("keep")))
    g.add((ex["holder"], foo["wraps"], head))
    g.add((ex["other"], foo["tail"], tail))

    resxml = g.serialize(format="pretty-xml")
    roundtrip = Graph().parse(data=resxml, format="xml")
    assert roundtrip.isomorphic(g) is True


def test_pure_bnode_list_uses_collection_parsetype() -> None:
    foo = Namespace("http://www.example.org/foo/ns/")
    ex = Namespace("http://www.example.org/example/foo/")

    g = Graph()
    head = BNode()
    Collection(g, head, [ex["a"], ex["b"]])
    g.add((ex["holder"], foo["wraps"], head))

    resxml = g.serialize(format="pretty-xml")
    assert 'rdf:parseType="Collection"' in resxml
    roundtrip = Graph().parse(data=resxml, format="xml")
    assert roundtrip.isomorphic(g) is True
