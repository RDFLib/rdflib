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
""".encode('utf-8')
        
def test_issue():
    g = Graph()
    g.parse(data=rdf, format='n3')
    v = g.value(subject=URIRef("http://www.test.org/#CI"), predicate=URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
    assert v==u"C\u00f4te d'Ivoire"

