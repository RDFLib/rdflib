
from nose import SkipTest


from rdflib import ConjunctiveGraph, URIRef, Literal, Namespace, Variable
g = ConjunctiveGraph()


def testStr():
    raise SkipTest('skipped - pending fix for #294')
    a = set(g.query("SELECT (STR(?target) AS ?r) WHERE { }", initBindings={'target': URIRef('example:a')}))
    b = set(g.query("SELECT (STR(?target) AS ?r) WHERE { } VALUES (?target) {(<example:a>)}"))
    assert a==b, "STR: %r != %r"%(a,b)

def testIsIRI():
    raise SkipTest('skipped - pending fix for #294')
    a = set(g.query("SELECT (isIRI(?target) AS ?r) WHERE { }", initBindings={'target': URIRef('example:a')}))
    b = set(g.query("SELECT (isIRI(?target) AS ?r) WHERE { } VALUES (?target) {(<example:a>)}"))
    assert a==b, "isIRI: %r != %r"%(a,b)

def testIsBlank():
    raise SkipTest('skipped - pending fix for #294')
    a = set(g.query("SELECT (isBlank(?target) AS ?r) WHERE { }", initBindings={'target': URIRef('example:a')}))
    b = set(g.query("SELECT (isBlank(?target) AS ?r) WHERE { } VALUES (?target) {(<example:a>)}"))
    assert a==b, "isBlank: %r != %r"%(a,b)

def testIsLiteral(): 
    raise SkipTest('skipped - pending fix for #294')
    a = set(g.query("SELECT (isLiteral(?target) AS ?r) WHERE { }", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT (isLiteral(?target) AS ?r) WHERE { } VALUES (?target) {('example')}"))
    assert a==b, "isLiteral: %r != %r"%(a,b)

def testUCase(): 
    raise SkipTest('skipped - pending fix for #294')
    a = set(g.query("SELECT (UCASE(?target) AS ?r) WHERE { }", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT (UCASE(?target) AS ?r) WHERE { } VALUES (?target) {('example')}"))
    assert a==b, "UCASE: %r != %r"%(a,b)

def testNoFunc():
    a = set(g.query("SELECT ?target WHERE { }", initBindings={'target': Literal('example')}))
    b = set(g.query("SELECT ?target WHERE { } VALUES (?target) {('example')}"))
    assert a==b, "no func: %r != %r"%(a,b)


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
    
    
if __name__ == "__main__":

    import sys
    import nose
    if len(sys.argv)==1: 
        nose.main(defaultTest=sys.argv[0])
