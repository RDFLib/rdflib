from rdflib.term import URIRef, BNode, Literal, Variable
from rdflib.namespace import Namespace, RDF, RDFS
from rdflib.store import Store, VALID_STORE, CORRUPTED_STORE, NO_STORE, UNKNOWN
from rdflib import plugin
from rdflib.parser import StringInputSource
from rdflib.graph import Graph, ReadOnlyGraphAggregate, ConjunctiveGraph
import unittest,sys
from pprint import pprint

class TestSPARQLToldBNodes(unittest.TestCase):

    sparql = True

    def setUp(self):
        NS = u"http://example.org/"
        self.graph = Graph(store)
        self.graph.parse(StringInputSource("""
           @prefix    : <http://example.org/> .
           @prefix rdf: <%s> .
           @prefix rdfs: <%s> .
           [ :prop :val ].
           [ a rdfs:Class ]."""%(RDF, RDFS)), format="n3")
    def testToldBNode(self):
        for s,p,o in self.graph.triples((None,RDF.type,None)):
            pass
        query = """SELECT ?obj WHERE { %s ?prop ?obj }"""%s.n3()
        print query
        rt = self.graph.query(query,DEBUG=debug)
        self.failUnless(len(rt) == 1,"BGP should only match the 'told' BNode by name (result set size: %s)"%len(rt))
        bindings = {Variable('subj'):s}
        query = """SELECT ?obj WHERE { ?subj ?prop ?obj }"""
        print query
        rt = self.graph.query(query,initBindings=bindings,DEBUG=debug)
        self.failUnless(len(rt) == 1,"BGP should only match the 'told' BNode by name (result set size: %s, BNode: %s)"%(len(rt),s.n3()))        

    def testFilterBNode(self):
        for s,p,o in self.graph.triples((None,RDF.type,None)):
            pass        
        query2 = """SELECT ?subj WHERE { ?subj ?prop ?obj FILTER( ?subj != %s ) }"""%s.n3()
        print query2
        rt = self.graph.query(query2,DEBUG=True)
        self.failUnless(len(rt) == 1,"FILTER should exclude 'told' BNodes by name (result set size: %s, BNode excluded: %s)"%(len(rt),s.n3()))                

    def tearDown(self):
        self.graph.store.rollback()

if __name__ == '__main__':
    import doctest, sys
    from optparse import OptionParser
    usage = '''usage: %prog [options]'''
    op = OptionParser(usage=usage)
    op.add_option('-s','--storeKind',default="IOMemory",
      help="The (class) name of the store to use for persistence")

    op.add_option('-c','--config',default='',
      help="Configuration string to use for connecting to persistence store")

    op.add_option('-i','--identifier',default='',
      help="Store identifier")
    
    op.add_option('-d','--debug',action="store_true",default=False,
      help="Debug flag")

    (options, args) = op.parse_args()
    
    global store,debug
    debug = options.debug
    store = plugin.get(options.storeKind,Store)(options.identifier)
    store.open(options.config,create=False)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSPARQLToldBNodes)
    unittest.TextTestRunner(verbosity=2).run(suite)    
