
from nose import SkipTest
raise SkipTest('skipped - pending fix for #294')


from rdflib import ConjunctiveGraph, URIRef, Literal
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


if __name__ == "__main__":

    import sys
    import nose
    if len(sys.argv)==1: 
        nose.main(defaultTest=sys.argv[0])
