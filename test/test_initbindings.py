
from nose import SkipTest

from rdflib.plugins.sparql import prepareQuery


from rdflib import ConjunctiveGraph, URIRef, Literal, Namespace, Variable
g = ConjunctiveGraph()


def testStr():
    a = set(g.query("SELECT (STR(?target) AS ?r) WHERE { }", initBindings={'target': URIRef('example:a')}))
    b = set(g.query("SELECT (STR(?target) AS ?r) WHERE { } VALUES (?target) {(<example:a>)}"))
    assert a==b, "STR: %r != %r"%(a,b)

def testIsIRI():
    a = set(g.query("SELECT (isIRI(?target) AS ?r) WHERE { }", initBindings={'target': URIRef('example:a')}))
    b = set(g.query("SELECT (isIRI(?target) AS ?r) WHERE { } VALUES (?target) {(<example:a>)}"))
    assert a==b, "isIRI: %r != %r"%(a,b)

def testIsBlank():
    a = set(g.query("SELECT (isBlank(?target) AS ?r) WHERE { }", initBindings={'target': URIRef('example:a')}))
    b = set(g.query("SELECT (isBlank(?target) AS ?r) WHERE { } VALUES (?target) {(<example:a>)}"))
    assert a==b, "isBlank: %r != %r"%(a,b)

def testIsLiteral():
    a = set(g.query("SELECT (isLiteral(?target) AS ?r) WHERE { }", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT (isLiteral(?target) AS ?r) WHERE { } VALUES (?target) {('example')}"))
    assert a==b, "isLiteral: %r != %r"%(a,b)

def testUCase():
    a = set(g.query("SELECT (UCASE(?target) AS ?r) WHERE { }", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT (UCASE(?target) AS ?r) WHERE { } VALUES (?target) {('example')}"))
    assert a==b, "UCASE: %r != %r"%(a,b)

def testNoFunc():
    a = set(g.query("SELECT ?target WHERE { }", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT ?target WHERE { } VALUES (?target) {('example')}"))
    assert a==b, "no func: %r != %r"%(a,b)

def testOrderBy():
    a = set(g.query("SELECT ?target WHERE { } ORDER BY ?target", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT ?target WHERE { } ORDER BY ?target VALUES (?target) {('example')}"))
    assert a==b, "orderby: %r != %r"%(a,b)

def testOrderByFunc():
    a = set(g.query("SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target VALUES (?target) {('example')} "))
    assert a==b, "orderbyFunc: %r != %r"%(a,b)

def testNoFuncLimit():
    a = set(g.query("SELECT ?target WHERE { } LIMIT 1", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT ?target WHERE { } LIMIT 1 VALUES (?target) {('example')}"))
    assert a==b, "limit: %r != %r"%(a,b)

def testOrderByLimit():
    a = set(g.query("SELECT ?target WHERE { } ORDER BY ?target LIMIT 1", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT ?target WHERE { } ORDER BY ?target LIMIT 1 VALUES (?target) {('example')}"))
    assert a==b, "orderbyLimit: %r != %r"%(a,b)

def testOrderByFuncLimit():
    a = set(g.query("SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target LIMIT 1", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target LIMIT 1 VALUES (?target) {('example')}"))
    assert a==b, "orderbyFuncLimit: %r != %r"%(a,b)

def testNoFuncOffset():
    a = set(g.query("SELECT ?target WHERE { } OFFSET 1", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT ?target WHERE { } OFFSET 1 VALUES (?target) {('example')}"))
    assert a==b, "offset: %r != %r"%(a,b)

def testNoFuncLimitOffset():
    a = set(g.query("SELECT ?target WHERE { } LIMIT 1 OFFSET 1", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT ?target WHERE { } LIMIT 1 OFFSET 1 VALUES (?target) {('example')}"))
    assert a==b, "limitOffset: %r != %r"%(a,b)

def testOrderByLimitOffset():
    a = set(g.query("SELECT ?target WHERE { } ORDER BY ?target LIMIT 1 OFFSET 1", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT ?target WHERE { } ORDER BY ?target LIMIT 1 OFFSET 1 VALUES (?target) {('example')}"))
    assert a==b, "orderbyLimitOffset: %r != %r"%(a,b)

def testOrderByFuncLimitOffset():
    a = set(g.query("SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target LIMIT 1 OFFSET 1", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT (UCASE(?target) as ?r) WHERE { } ORDER BY ?target LIMIT 1 OFFSET 1 VALUES (?target) {('example')}"))
    assert a==b, "orderbyFuncLimitOffset: %r != %r"%(a,b)

def testDistinct():
    a = set(g.query("SELECT DISTINCT ?target WHERE { }", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT DISTINCT ?target WHERE { } VALUES (?target) {('example')}"))
    assert a==b, "distinct: %r != %r"%(a,b)

def testDistinctOrderBy():
    a = set(g.query("SELECT DISTINCT ?target WHERE { } ORDER BY ?target", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT DISTINCT ?target WHERE { } ORDER BY ?target VALUES (?target) {('example')}"))
    assert a==b, "distinctOrderby: %r != %r"%(a,b)

def testDistinctOrderByLimit():
    a = set(g.query("SELECT DISTINCT ?target WHERE { } ORDER BY ?target LIMIT 1", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT DISTINCT ?target WHERE { } ORDER BY ?target LIMIT 1 VALUES (?target) {('example')}"))
    assert a==b, "distinctOrderbyLimit: %r != %r"%(a,b)

def testPrepare():
    q = prepareQuery('SELECT ?target WHERE { }')
    r = list(g.query(q))
    e = []
    assert r == e, 'prepare: %r != %r'%(r,e)

    r = list(g.query(q, initBindings={'target': Literal('example')}))
    e = [(Literal('example'),)]
    assert r == e, 'prepare: %r != %r'%(r, e)

    r = list(g.query(q))
    e = []
    assert r == e, 'prepare: %r != %r'%(r,e)


def testData():
    data = ConjunctiveGraph()
    data += [ ( URIRef('urn:a'), URIRef('urn:p'), Literal('a') ),
              ( URIRef('urn:b'), URIRef('urn:p'), Literal('b') ) ]

    a = set(g.query("SELECT ?target WHERE { ?target <urn:p> ?val }", initBindings={'val': Literal('a')}))
    b = set(g.query("SELECT ?target WHERE { ?target <urn:p> ?val } VALUES (?val) {('a')}"))
    assert a==b, "data: %r != %r"%(a,b)

def testAsk():
    a = set(g.query("ASK { }", initBindings={'target': Literal('example')}))
    b = set(g.query("ASK { } VALUES (?target) {('example')}"))
    assert a==b, "ask: %r != %r"%(a,b)


EX = Namespace("http://example.com/")
g2 = ConjunctiveGraph()
g2.bind('', EX)
g2.add((EX['s1'], EX['p'], EX['o1']))
g2.add((EX['s2'], EX['p'], EX['o2']))

def testStringKey():
    results = list(g2.query("SELECT ?o WHERE { ?s :p ?o }", initBindings={"s": EX['s1']}))
    assert len(results) == 1, results

def testStringKeyWithQuestionMark():
    results = list(g2.query("SELECT ?o WHERE { ?s :p ?o }", initBindings={"?s": EX['s1']}))
    assert len(results) == 1, results

def testVariableKey():
    results = list(g2.query("SELECT ?o WHERE { ?s :p ?o }", initBindings={Variable("s"): EX['s1']}))
    assert len(results) == 1, results

def testVariableKeyWithQuestionMark():
    results = list(g2.query("SELECT ?o WHERE { ?s :p ?o }", initBindings={Variable("?s"): EX['s1']}))
    assert len(results) == 1, results

def testFilter():
    results = list(g2.query("SELECT ?o WHERE { ?s :p ?o FILTER (?s = ?x)}", initBindings={Variable("?x"): EX['s1']}))
    assert len(results) == 1, results

if __name__ == "__main__":

    import sys
    import nose
    if len(sys.argv)==1:
        nose.main(defaultTest=sys.argv[0])
