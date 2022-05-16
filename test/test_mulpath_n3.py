from rdflib import URIRef
from rdflib.paths import ZeroOrMore


def test_mulpath_n3():
    uri = "http://example.com/foo"
    n3 = (URIRef(uri) * ZeroOrMore).n3()
    assert n3 == "<" + uri + ">*"
