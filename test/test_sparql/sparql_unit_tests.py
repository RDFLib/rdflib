# -*- coding: UTF-8 -*-
from cStringIO import StringIO
from rdflib import plugin
from rdflib.term import URIRef, Literal
from rdflib.namespace import RDFS
from rdflib.graph import Graph, ConjunctiveGraph
from optparse import OptionParser
from xml.sax import  SAXParseException
from rdflib.store import Store, VALID_STORE, CORRUPTED_STORE, NO_STORE, UNKNOWN

import unittest, getpass

class AbstractSPARQLUnitTestCase(unittest.TestCase):
    """
    This is the base class for all unit tests in this module
    If TEST_FACTS is specified (as a class-level attribute), 
    then it is assumed to be a filesystem path to an RDF/XML 
    document that will be parsed and used as the set of facts 
    for the test case
    
    Note, an RDF graph is not required for tests that only exercise
    syntax alone (like the TestOPTVariableCorrelationTest below)
    """

    sparql = True

    TEST_FACT = None
    TEST_FACT_FORMAT = 'xml'
    def setUp(self):        
        if singleGraph:
            self.graph = singleGraph
        else:
            self.graph = Graph(store)
        if self.TEST_FACT:
            print self.graph.store
            self.graph = Graph(self.graph.store)
            print "Parsed %s facts for test (as %s)"%(len(self.graph.parse(self.TEST_FACT,
                                                                          format=self.TEST_FACT_FORMAT)),
                                                      self.TEST_FACT_FORMAT)

BROKEN_OPTIONAL=\
"""
PREFIX ptrec: <tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#>
PREFIX ex: <http://example.org/>
SELECT ?INTERVAL2
WHERE {
  ex:interval1 ptrec:hasDateTimeMax ?END1 .
  OPTIONAL {
    ?INTERVAL2 ptrec:hasDateTimeMax ?END2 .
    FILTER (?END1 > ?END2)
  }
}"""

BROKEN_OPTIONAL_DATA=\
""" 
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
@prefix ptrec: <tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#> .
@prefix ex: <http://example.org/>.

ex:interval1 ptrec:hasDateTimeMax "2008-02-01"^^xsd:date .
ex:interval2 ptrec:hasDateTimeMax "2008-04-01"^^xsd:date .
ex:interval3 ptrec:hasDateTimeMax "2008-01-01"^^xsd:date .
"""

#A unit test that reproduces the OPTIONAL variable correlation issue
#This is specifically a problem where the filter within the OPTIONAL
#involves a comparison that requires the lexical value of a term
#(not just its hash as is the case with a simple equality comparison)
class TestOPTVariableCorrelationTest(AbstractSPARQLUnitTestCase):
    TEST_FACT=StringIO(BROKEN_OPTIONAL_DATA)
    TEST_FACT_FORMAT = 'n3'
    def test_OPT_FILTER(self):
        rt=list(self.graph.query(BROKEN_OPTIONAL,
                                 DEBUG=True))
        self.assertEqual(len(rt),1)
        self.failUnless(rt[0][0]==URIRef('http://example.org/interval3'),
                        "ex:interval3 is the only other interval that preceeded interval1")

#This master list of unit tests needs to be updated as more are added
#to this module
UNIT_TESTS = [
    TestOPTVariableCorrelationTest,
]

if __name__ == "__main__":
    global singleGraph, options, store
        
    op = OptionParser('usage: %prog [options]')
    op.add_option('-u','--user', default=None,
      help = 'The user name to use to connect to the MySQL database')
    op.add_option('-d','--database', default=None,
      help = 'The MySQL database to connect to')    
    op.add_option('-s','--host', default='localhost',
      help = 'The hostname of the MySQL server (localhost by default)')    
    op.add_option('-i', '--identifier', default=None,
      help = 'The identifier associated with the RDF dataset')
    op.add_option('-f', '--facts', default=None,
      help = 'The path to an RDF document to use as the set of facts for the included unit tests')    
    op.add_option('-l', '--liveDB', action='store_true',default=False,
      help = 'Whether or not to use the connected RDF dataset for all unit tests')        
    op.add_option('--format', default='xml',
      help = 'The serialization format of the RDF document specified via -f/--facts (RDF/XML is the default)')        
    op.add_option('-p','--password', default=None,
      help = 'The password to use in authenticating with the given user (you will be prompted for one otherwise)')    
    (options, args) = op.parse_args()
    pw = options.password and options.password or getpass.getpass('Enter password for %s:'%(options.user))
    
    if options.facts and options.liveDB:
        op.error("options -l/--liveDB and -f/--facts are mutually exclusive!")    
    
    #SPARQL queries w/out GRAPH operators should range over all named graphs
    from rdflib.sparql import algebra
    algebra.DAWG_DATASET_COMPLIANCE = False
    
    #We setup a global store.  A store is what a Graph instance uses to manage the persistence of RDF statements
    #We want to create a connection to the specified MySQL dataset as a store
    store = plugin.get('MySQL',Store)(options.identifier)
    configurationString = 'user=%s,host=%s,db=%s,password=%s'%(
                             options.user,
                             options.host,
                             options.database,
                             pw)
    rt = store.open(configurationString,create=False)
    if not options.liveDB:
        #if we aren't working with a live database, then create a fresh
        #store using the given connection
        if rt == NO_STORE:
            store.open(configurationString,create=True)
        else:
            #Note, if the store exists, it will be destroyed before use!
            store.destroy(configurationString)
            store.open(configurationString,create=True)
    
    #We setup a global variable for the single graph to use for all the unit tests 
    if options.facts:
        singleGraph = Graph().parse(options.facts,format=options.format)
    else:
        singleGraph = options.liveDB and ConjunctiveGraph(store) or None
        
    for suite in UNIT_TESTS: 
        unittest.TextTestRunner(verbosity=5).run(unittest.makeSuite(suite))
        store.rollback()        
