# test for https://github.com/RDFLib/rdflib/issues/523

import rdflib


def test_issue523():
    g = rdflib.Graph()
    r = g.query(
        "SELECT (<../baz> as ?test) WHERE {}",
        base=rdflib.URIRef("http://example.org/foo/bar"),
    )
    res = r.serialize(format="csv", encoding="utf-8")
    assert res == b"test\r\nhttp://example.org/baz\r\n", repr(res)
    res = r.serialize(format="csv")
    assert res == "test\r\nhttp://example.org/baz\r\n", repr(res)
    # expected result:
    # test
    # http://example.org/baz

    # actual result;
    # test
    # http://example.org/foo/bar../baz
