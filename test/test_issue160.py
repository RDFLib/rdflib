from unittest import TestCase
from rdflib import ConjunctiveGraph
from rdflib import Namespace, Literal
from rdflib.collection import Collection
from nose.exc import SkipTest



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

class CollectionTest(TestCase):

    def test_collection_render(self):
        foo = Namespace('http://www.example.org/foo/ns/')
        ex = Namespace('http://www.example.org/example/foo/')
        rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

        # Works:  x a rdf:List, a foo:Other ;
        # Fails:  y a foo:Wrapper, foo:wraps x; x a rdf:List, a foo:Other ;

        target1 = ConjunctiveGraph()
        target1.parse(data=target1xml)
        target2 = ConjunctiveGraph()
        target2.parse(data=target2xml)

        g = ConjunctiveGraph()
        bits = [ex['a'], ex['b'], ex['c']]
        l = Collection(g, ex['thing'], bits)
        triple = (ex['thing'], rdf['type'], foo['Other'])
        g.add(triple)
        triple = (ex['thing'], foo['property'], Literal('Some Value'))
        g.add(triple)
        for b in bits:
            triple = (b, rdf['type'], foo['Item'])
            g.add(triple)
        self.assertEqual(g.isomorphic(target1), True)

        # g.add((ex['wrapper'], rdf['type'], foo['Wrapper']))
        # g.add((ex['wrapper'], foo['wraps'], ex['thing']))
        # # resn3 = g.serialize(format="n3")
        # # print(resn3)
        # resxml = g.serialize(format="pretty-xml")
        # # print(resxml)
        # self.assertEqual(g.isomorphic(target2), True)


