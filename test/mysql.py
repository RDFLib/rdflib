from n3_2 import testN3Store,testN3,implies
from rdflib.Graph import SubGraph,QuotedGraph
from rdflib.backends.MySQL import REGEXTerm
from rdflib import *
configString="user=root,password=1618,host=localhost,db=rdflib_db"

def testRegex():
    g = Graph(backend='MySQL')
    g.open(configString)    
    g.parse(StringInputSource(testN3), format="n3") 
    try:
        for s,p,o in g.triples((None,implies,None)):
            formulaA = s
            formulaB = o

        assert type(formulaA)==QuotedGraph and type(formulaB)==QuotedGraph
        a = URIRef('http://test/a')
        b = URIRef('http://test/b')
        c = URIRef('http://test/c')
        d = URIRef('http://test/d')

        #REGEX triple matching
        assert len(list(g.triples((None,REGEXTerm('.*22-rdf-syntax-ns.*'),None))))==1
        assert len(list(g.triples((None,REGEXTerm('.*'),None))))==3
        assert len(list(g.triples((REGEXTerm('.*formula.*$'),None,None))))==1
        assert len(list(g.triples((None,None,REGEXTerm('.*formula.*$')))))==1
        assert len(list(g.triples((None,REGEXTerm('.*implies$'),None))))==1
        for s,p,o in g.triples((None,REGEXTerm('.*test.*'),None)):
            assert s==a
            assert o==c

        for s,p,o in formulaA.triples((None,REGEXTerm('.*type.*'),None)):
            assert o!=c or isinstance(o,BNode)

        #REGEX context matching
        assert len(list(g.contexts((None,None,REGEXTerm('.*schema.*')))))==1
        assert len(list(g.contexts((None,REGEXTerm('.*'),None))))==3

    except:
        g.backend.destroy(configString)
        raise

if __name__=='__main__':
    testN3Store('MySQL',configString)
    testRegex()
