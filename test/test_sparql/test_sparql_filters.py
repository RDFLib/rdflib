from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef, Literal
from StringIO import StringIO


testContent = """
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    <http://example.org/doc/1> rdfs:label "Document 1"@en, "Dokument 1"@sv .
    <http://example.org/doc/2> rdfs:label "Document 2"@en, "Dokument 2"@sv .
    <http://example.org/doc/3> rdfs:label "Document 3"@en, "Dokument 3"@sv .
"""
graph = ConjunctiveGraph()
graph.load(StringIO(testContent), format='n3')

doc1 = URIRef("http://example.org/doc/1")

PROLOGUE = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""


def test_filter_by_lang():
    testdata = [
            ("en", u'"Document 1"@en'),
            ("sv", u'"Dokument 1"@sv')
        ]

    query = PROLOGUE+'''
        SELECT ?label WHERE {
            '''+doc1.n3()+''' rdfs:label ?label .
            FILTER(LANG(?label) = "%s")
        }
    '''

    for lang, literal in testdata:
        res = graph.query(query % lang)
        actual = [binding.n3() for binding in res.selected]
        expected = [literal]
        yield assert_equal, actual, expected


def assert_equal(v1, v2):
    assert v1 == v2, "Expected %r == %s" % (v1, v2)


