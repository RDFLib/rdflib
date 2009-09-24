from codecs import getreader
from StringIO import StringIO

from rdflib.term import URIRef
from rdflib.graph import Graph

rdf = u"""@prefix skos:
<http://www.w3.org/2004/02/skos/core#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix : <http://www.test.org/#> .

:world rdf:type skos:Concept;
    skos:prefLabel "World"@en.
:africa rdf:type skos:Concept;
    skos:prefLabel "Africa"@en;
    skos:broaderTransitive :world.
:CI rdf:type skos:Concept;
    skos:prefLabel "C\u00f4te d'Ivoire"@en;
    skos:broaderTransitive :africa.    
"""

rdf_utf8 = rdf.encode('utf-8')

rdf_reader = getreader('utf-8')(StringIO(rdf.encode('utf-8')))


        
def test_a():
    g = Graph()
    g.parse(data=rdf, format='n3')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==u"C\u00f4te d'Ivoire"

def test_b():
    g = Graph()
    g.parse(data=rdf_utf8, format='n3')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==u"C\u00f4te d'Ivoire"

def test_c():
    g = Graph()
    g.parse(source=rdf_reader, format='n3')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==u"C\u00f4te d'Ivoire"


