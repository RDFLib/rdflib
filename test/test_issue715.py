"""
Issue 715 - path query chaining issue
Some incorrect matches were found when using oneOrMore ('+') and
zeroOrMore ('*') property paths and specifying neither the
subject or the object.
"""

from rdflib import URIRef, Graph


def test_issue_715():
    g = Graph()
    a, b, x, y, z = [URIRef(s) for s in "abxyz"]
    isa = URIRef('isa')
    g.add((a, isa, x))
    g.add((a, isa, y))
    g.add((b, isa, x))
    l1 = list(g.query('SELECT ?child ?parent WHERE {?child <isa> ?parent .}'))
    l2 = list(g.query('SELECT ?child ?parent WHERE {?child <isa>+ ?parent .}'))
    assert len(l1) == len(l2)
    assert set(l1) == set(l2)
    l3 = list(g.query('SELECT ?child ?parent WHERE {?child <isa>* ?parent .}'))
    assert len(l3) == 7
    assert set(l3) == set(l1).union({(URIRef(n), URIRef(n)) for
                                     n in (a, b, x, y)})
    g.add((y, isa, z))
    l4 = list(g.query('SELECT ?child ?parent WHERE {?child <isa>* ?parent .}'))
    assert len(l4) == 10
    assert (a, z) in l4
