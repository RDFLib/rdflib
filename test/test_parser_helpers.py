from rdflib.plugins.sparql.parser import TriplesSameSubject
# from rdflib.plugins.sparql.algebra import triples


def pt(ts):
    for t in ts:
        print(t)


def test_1():

    t0 = TriplesSameSubject.parseString("[] ?p ?o ")
    print(t0, len(t0))
    assert len(t0) % 3 == 0

    # t=BlankNodePropertyList.parseString("[ :p ?o ]")
    t1 = TriplesSameSubject.parseString("[ ?p ?o ]")
    print(t1, len(t1))
    assert len(t1) % 3 == 0

    t2 = TriplesSameSubject.parseString("[ ?p1 ?o1 ] ?p2 ?o2 ")
    print(t2, len(t2))
    assert len(t2) % 3 == 0

    t3 = TriplesSameSubject.parseString("?s ?p1 [ ] ")
    print(t3, len(t3))
    assert len(t3) % 3 == 0

    t4 = TriplesSameSubject.parseString("?s ?p1 [ ?p2 ?o2 ] ")
    print(t4, len(t4))
    assert len(t4) % 3 == 0

    t5 = TriplesSameSubject.parseString("[ ] ?p2 [ ] ")
    print(t5, len(t5))
    assert len(t5) % 3 == 0

    t6 = TriplesSameSubject.parseString("[ ?p1 ?o1 ] ?p2 [ ?p3 ?o2 ] ")
    print(t6, len(t6))
    assert len(t6) % 3 == 0
