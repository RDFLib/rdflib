# test for https://github.com/RDFLib/rdflib/issues/554

import rdflib

def test_sparql_empty_no_row():
    g = rdflib.Graph()
    q = 'select ?whatever { }'
    r = list(g.query(q))
    assert r == [], \
        'sparql query %s should return empty list but returns %s' % (q, r)


if __name__ == '__main__':
    test_sparql_empty_no_row()
