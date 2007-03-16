from n3_2 import testN3Store,testN3,implies
from rdflib.Graph import QuotedGraph
try:
    from rdflib.store.MySQL import REGEXTerm
except ImportError, e:
    print "Can not test REGEX bits:", e
from rdflib import *
configString="user=,password=,host=localhost,db=test"

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

        universe = ConjunctiveGraph(g.backend)

        #REGEX triple matching
        assert len(list(universe.triples((None,REGEXTerm('.*22-rdf-syntax-ns.*'),None))))==1
        assert len(list(universe.triples((None,REGEXTerm('.*'),None))))==3
        assert len(list(universe.triples((REGEXTerm('.*formula.*$'),None,None))))==1
        assert len(list(universe.triples((None,None,REGEXTerm('.*formula.*$')))))==1
        assert len(list(universe.triples((None,REGEXTerm('.*implies$'),None))))==1
        for s,p,o in universe.triples((None,REGEXTerm('.*test.*'),None)):
            assert s==a
            assert o==c

        for s,p,o in formulaA.triples((None,REGEXTerm('.*type.*'),None)):
            assert o!=c or isinstance(o,BNode)

        #REGEX context matching
        assert len(list(universe.contexts((None,None,REGEXTerm('.*schema.*')))))==1
        assert len(list(universe.contexts((None,REGEXTerm('.*'),None))))==3

        #test optimized interfaces
        assert len(list(g.backend.subjects(RDF.type,[RDFS.Class,c])))==1
        for subj in g.backend.subjects(RDF.type,[RDFS.Class,c]):
            assert isinstance(subj,BNode)

        assert len(list(g.backend.subjects(implies,[REGEXTerm('.*')])))==1

        for subj in g.backend.subjects(implies,[formulaB,RDFS.Class]):
            assert subj.identifier == formulaA.identifier

        assert len(list(g.backend.subjects(REGEXTerm('.*'),[formulaB,c])))==2
        assert len(list(g.backend.subjects(None,[formulaB,c])))==2
        assert len(list(g.backend.subjects(None,[formulaB,c])))==2
        assert len(list(g.backend.subjects([REGEXTerm('.*rdf-syntax.*'),d],None)))==2

        assert len(list(g.backend.objects(None,RDF.type)))==1
        assert len(list(g.backend.objects(a,[d,RDF.type])))==1
        assert len(list(g.backend.objects(a,[d])))==1
        assert len(list(g.backend.objects(a,None)))==1
        assert len(list(g.backend.objects(a,[REGEXTerm('.*')])))==1
        assert len(list(g.backend.objects([a,c],None)))==1

    except:
        g.backend.destroy(configString)
        raise

def testRun():
    testN3Store('MySQL',configString)
    testRegex()

def profileTests():
    from hotshot import Profile, stats
    p = Profile('rdflib-mysql.profile')
    p.runcall(testRun)
    p.close()

    s = stats.load('rdflib-mysql.profile')
    s.strip_dirs()
    s.sort_stats('time','cumulative','pcalls')
    #s.sort_stats('time','pcalls')
    s.print_stats(.1)
    s.print_callers(.1)
    s.print_callees(.1)


if __name__=='__main__':
    testN3Store('MySQL',configString)
    testRegex()
    #profileTests()

