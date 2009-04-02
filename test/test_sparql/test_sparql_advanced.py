import unittest
import doctest
from rdflib.namespace import RDF, RDFS, Namespace
from rdflib.term import Variable
from rdflib.sparql import DESCRIBE
from rdflib.graph import Graph
from cStringIO import StringIO

testData="""
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
:foo :relatedTo [ a rdfs:Class ];
     :parentOf ( [ a rdfs:Class ] ).
:bar :relatedTo [ a rdfs:Resource ];
     :parentOf ( [ a rdfs:Resource ] ).
     
( [ a rdfs:Resource ] ) :childOf :bar.     
( [ a rdfs:Class ] )    :childOf :foo.
"""

testData2="""
@prefix  foaf:  <http://xmlns.com/foaf/0.1/> .

_:a    foaf:name   "Alice" .
_:a    foaf:mbox   <mailto:alice@example.org> .
"""

testGraph=Graph().parse(StringIO(testData2),
                        format='n3')

FOAF =Namespace('http://xmlns.com/foaf/0.1/')
VCARD=Namespace('http://www.w3.org/2001/vcard-rdf/3.0#')

def describeOverride(terms,bindings,graph):
    g=Graph()
    for term in terms:
        if isinstance(term,Variable) and term not in bindings:
            continue
        else:
            term=bindings.get(term,term)
        for s,p,o in graph.triples((term,FOAF.mbox,None)):
            g.add((s,p,o))
    return g

namespaces={u'rdfs' : RDF,
            u'rdf'  : RDFS,
            u'foaf' : FOAF,
            u'vcard': VCARD,
            u'ex' : Namespace('http://example.org/person#') }

for prefix,uri in namespaces.items():
    testGraph.namespace_manager.bind(prefix, uri, override=False)        

if __name__ == "__main__":
    doctest.testfile("test_sparql_advanced.txt", globs=globals(),
                     optionflags = doctest.ELLIPSIS)
