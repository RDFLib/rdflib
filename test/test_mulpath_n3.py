from rdflib.paths import ZeroOrMore

from rdflib import RDFS, URIRef


def test_mulpath_n3():
    uri = 'http://example.com/foo'
    n3 = (URIRef(uri) * ZeroOrMore).n3()
    assert n3 == '<' + uri + '>*'
