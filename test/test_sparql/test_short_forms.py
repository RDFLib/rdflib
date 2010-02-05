from rdflib.namespace import Namespace, RDF, RDFS
from rdflib.store import Store, VALID_STORE, CORRUPTED_STORE, NO_STORE, UNKNOWN
from rdflib import plugin
from rdflib.term import URIRef, Literal, BNode, Variable
from rdflib.parser import StringInputSource
from rdflib.graph import Graph, ReadOnlyGraphAggregate, ConjunctiveGraph
import unittest,sys
from pprint import pprint

problematic_query=\
"""
BASE <http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#>
PREFIX dnode: <http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#>
PREFIX owl: <http://www.w3.org/2000/07/owl#>
PREFIX ptrec: <tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sts: <tag:info@semanticdb.ccf.org,2008:STS.2.61#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?VAR0 ?VAR1 ?VAR2 ?VAR3
WHERE {
  ?VAR0 <tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#hasCardiacValveEtiology> <tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#CardiacValveEtiology_thrombosis> .
  ?VAR0 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#SurgicalProcedure_cardiac_valve_mitral_valve_repair> .
  ?VAR1 <http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#contains> ?VAR0 .
  ?VAR2 <http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#contains> ?VAR1 .
  ?VAR2 <http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#contains> ?VAR3 .
  ?VAR3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#Patient> .
} 
"""

class TestSPARQLAbbreviations(unittest.TestCase):

    sparql = True

    def setUp(self):
        NS = u"http://example.org/"
        self.graph = Graph(store)
        self.graph.parse(StringInputSource("""
           @prefix    : <http://example.org/> .
           @prefix rdf: <%s> .
           @prefix rdfs: <%s> .
           [ :prop :val ].
           [ a rdfs:Class ]."""%(RDF.RDFNS,RDFS.RDFSNS)), format="n3")

    def testTypeAbbreviation(self):
        query = """SELECT ?subj WHERE { ?subj a rdfs:Class }"""
        print query
        rt = self.graph.query(query,DEBUG=debug)
        self.failUnless(len(rt) == 1,"Should be a single match: %s"%len(rt))
        query = """SELECT ?subj WHERE { ?subj a <http://www.w3.org/2000/01/rdf-schema#Class> }"""
        print query
        rt = self.graph.query(query,DEBUG=debug)
        self.failUnless(len(rt) == 1,"Should be a single match: %s"%len(rt))
        
    def testTypeAbbreviation(self):
        query = """SELECT ?subj WHERE { ?subj a rdfs:Class }"""
        print query
        rt = self.graph.query(query,DEBUG=debug)
        self.failUnless(len(rt) == 1,"Should be a single match: %s"%len(rt))
        query = """SELECT ?subj WHERE { ?subj a <http://www.w3.org/2000/01/rdf-schema#Class> }"""
        print query
        rt = self.graph.query(query,DEBUG=debug)
        self.failUnless(len(rt) == 1,"Should be a single match: %s"%len(rt))

    def testQNameVSFull(self):
        query = """SELECT ?subj WHERE { ?subj <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> rdfs:Class }"""
        print query
        rt = self.graph.query(query,DEBUG=debug)
        self.failUnless(len(rt) == 1,"Should be a single matchL: %s"%len(rt))
        query = """SELECT ?subj WHERE { ?subj <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2000/01/rdf-schema#Class> }"""
        print query
        rt = self.graph.query(query,DEBUG=debug)
        self.failUnless(len(rt) == 1,"Should be a single match: %s"%len(rt))
        
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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSPARQLAbbreviations)
    unittest.TextTestRunner(verbosity=2).run(suite)    
