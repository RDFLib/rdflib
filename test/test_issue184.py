from rdflib.term import Literal
from rdflib.term import URIRef
from rdflib.graph import ConjunctiveGraph

def test_escaping_of_triple_doublequotes():
    """
    Issue 186 - Check escaping of multiple doublequotes.
    A serialization/deserialization roundtrip of a certain class of 
    Literals fails when there are both, newline characters and multiple subsequent 
    quotation marks in the lexical form of the Literal. In this case invalid N3
    is emitted by the serializer, which in turn cannot be parsed correctly.
    """
    g=ConjunctiveGraph()
    g.add((URIRef('http://foobar'), URIRef('http://fooprop'), Literal('abc\ndef"""""')))
    # assert g.serialize(format='n3') == '@prefix ns1: <http:// .\n\nns1:foobar ns1:fooprop """abc\ndef\\"\\"\\"\\"\\"""" .\n\n'
    g2=ConjunctiveGraph()
    g2.parse(data=g.serialize(format='n3'), format='n3')
    assert g.isomorphic(g2) is True