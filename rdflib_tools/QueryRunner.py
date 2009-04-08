# -*- coding: utf-8 -*-

from __future__ import generators

import rdflib
from rdflib.Graph import ConjunctiveGraph
from rdflib import plugin
from rdflib.store import Store, NO_STORE, VALID_STORE
from rdflib import Namespace
from rdflib import Literal
from rdflib import URIRef
import time
from os.path import dirname

from Ft.Xml import Parse
from datetime import datetime

from CSVWriter import CSVWriter, WriteAllResults
from rdflib.sparql.sql.DatabaseStats import *

ResultsColumns = ['time','comment','dsName', 'dsSize', 'query', 'sparql', 'rc', 'totalQueryTime','mainQueryCount','mainQueryTime','rowPrepQueryCount','rowPrepQueryTime','sqlQueries', 'err'] #list[0].keys()

def Query(graph, queryName, sparql, dsProps={}, initNamespaces={}, clearCache=False):    
    graph.store.resetPerfLog(clearCache) # clear cache?
    print "      Query '%s': " % (queryName),
    #print sparql
    
    startTime = time.time()
    try:
        results = graph.query(sparql, initNs=initNamespaces, DEBUG=False)
        rc = len(results)
        err = ""
    except Exception,ex:
        results = []
        rc = "Error"
        err = repr(ex)
        
    elapsed = time.time()-startTime
    perfLog = graph.store.getPerfLog()
    print rc, "in", elapsed, "ms total"
    #print "  PerfLog:", perfLog
      
#    if resultPattern != "" and diplayResults:
#        for row in results:
#            print resultPattern % row
#    print "-------------"

    # add more info to query results
    perfLog['time'] = "'" + str(datetime.now()) + "'" # make date field text in Excel    
    perfLog['query'] = queryName
    perfLog['sparql'] = sparql.strip()
    perfLog['rc'] = rc
    perfLog['err'] = err
    perfLog['totalQueryTime'] = elapsed
    for k in dsProps.keys(): # add data set properties
        perfLog[k] = dsProps[k]
        
    return perfLog

def OpenGraph(storeType, configStr, graphUri, storeName='rdfstore'):   
    # Get the mysql plugin. You may have to install the python mysql libraries
    store = plugin.get(storeType, Store)(storeName,debug=False,perfLog=True)
    
    # Open previously created store, or create it if it doesn't exist yet
    rt = store.open(configStr,create=False)
    assert rt != NO_STORE,"'%s' store '%s' not found using config string '%s!'" % (storeType, storeName, configStr)
    assert rt == VALID_STORE or rt is not None,"There underlying store is corrupted"
        
    #There is a store, use it; use ConjunctiveGraph to see everything!
    graph = ConjunctiveGraph(store, identifier = URIRef(graphUri))
    
    return graph

def SetupGraph(storeType, configStr, graphUri, storeName, commonNS, owlFile=None):
    graph = OpenGraph(storeType, configStr, graphUri, storeName=storeName)
    dsProps = {'dsName':storeName, 'dsSize':len(graph.store)}
    # search for schema in a specified owl file
    if False:#owlFile != None:
        ontGraph=Graph().parse(owlFile)
        for litProp,resProp in ontGraph.query(
    """
    SELECT ?literalProperty ?resourceProperty
    WHERE {
        { ?literalProperty a owl:DatatypeProperty }
                        UNION
        { ?resourceProperty a ?propType 
          FILTER( 
            ?propType = owl:ObjectProperty || 
            ?propType = owl:TransitiveProperty ||
            ?propType = owl:SymmetricProperty ||
            ?propType = owl:InverseFunctionalProperty )  }
    }"""
    ,
          initNs={u'owl':OWL_NS}):
            if litProp:
                graph.store.literal_properties.add(litProp)
            if resProp:
                #Need to account for OWL Full, where datatype properties
                #can be IFPs
                if (resProp,
                    RDF.type,
                    OWL_NS.DatatypeProperty) not in ontGraph:
                    graph.store.resource_properties.add(resProp)
            
    return graph, dsProps #, commonNS  

   
def RunRepository(w, fileName, repos, store, repeatTimes, clearCache, storeType, configString, commonNS, comment):
    
    # get repository name
    storeName = repos.attributes[(None,'name')].value    
    print "  ---------------------------"
    print "  Repository: ", storeName

    graph,dsProps = LoadGraph(fileName, repos, storeType, configString, commonNS)
    
    dsProps['comment'] = comment
 
    queries = store.xpath('./Queries/Query')
 
    # repeat n times
    for k in range(repeatTimes):
        print "    Repeat %s/%s..." %(k+1,repeatTimes)
        # for each query
        for query in queries:  
            queryName = query.attributes[(None,'name')].value
            sparqlQuery = query.childNodes[0].nodeValue # text node
            w.WriteEntry(Query(graph, queryName, sparqlQuery, dsProps, commonNS, clearCache))

def LoadGraph(fileName, repos, storeType, configString, commonNS):
    storeName = repos.attributes[(None,'name')].value    
    graphUri = repos.attributes[(None, 'graphUri')].value
    owlFile = None
    if repos.attributes.has_key((None, 'owlFile')):
        owlFile = repos.attributes[(None, 'owlFile')].value
        if len(owlFile.strip()) > 0:
            owlFile = os.path.join(dirname(fileName), owlFile)
        else:
            owlFile = None
            # load graph
    graph, dsProps = SetupGraph(storeType, configString, graphUri, storeName, commonNS, owlFile)
    return graph, dsProps

    
def RunStore(w, fileName, store, repeatTimes, clearCache, comment):
    
    # get store config
    storeType = store.attributes[(None,'type')].value
    configString = store.attributes[(None,'configString')] .value
     
    commonNS = GetCommonNS(store)
        
    print "================================================="
    print "Processing %s Store '%s'" % (storeType, configString)    
        
    # for each repository    
    repositories = store.xpath('./Repositories/Repository')
    for repos in repositories:
        RunRepository(w, fileName, repos, store, repeatTimes, clearCache, storeType, configString, commonNS, comment)

def GetCommonNS(store):    
    # get common name space prefixes
    commonNS = dict()
    prefixes = store.xpath('./CommonPrefixes/Prefix')
    for prefix in prefixes:
        commonNS[prefix.attributes[(None, 'name')].value] = Namespace(prefix.attributes[(None, 'value')].value)
    
    return commonNS

def GetQueryEntries(root):
    queryEntries = []
    stores = root.xpath('./Store')
    for store in stores:
        GetStoreQueryEntries(queryEntries, store)
    
    return queryEntries
    
def GetStoreQueryEntries(queryEntries, store):
    commonNS = GetCommonNS(store)
    queries = store.xpath('./Queries/Query')
    for query in queries:
        queryName = query.attributes[(None, 'name')].value
        sparqlQuery = query.childNodes[0].nodeValue # text node
        queryEntries.append(dict(queryName=queryName, 
                                 queryString=sparqlQuery, 
                                 lineNum=queryName))
        
def RunQueryFile(fileName, comment, options):
    
    doc = Parse(fileName)
    #doc.xpath('string(ham//em[1])')
    
    # read overall benchmark settings 
    root = doc.rootNode.childNodes[0]
    repeatTimes = int(root.attributes[(None,'repeatTimes')].value)
    clearCache = root.attributes[(None,'clearCache')].value == "True"

    if options.runQueries:
        # setup output
        w = CSVWriter()
        w.Open(ResultsColumns, fileName + '.out.txt')
            
        # for each store
        stores = root.xpath('./Store')
        for store in stores:
            RunStore(w, fileName, store, repeatTimes, clearCache, comment)
        
        w.Close()
    
    print "Done."
    

    
if __name__ == '__main__':
   from optparse import OptionParser
   usage = '''usage: %prog [options] queryFile [comment]'''
   op = OptionParser(usage=usage)
   #op.add_option('--buildOWL',action="store_true",default=True,
   #    help = 'Build OWL from components')
   op.add_option('--noExecution',action='store_false',default=True, dest='runQueries', help='Execute the SPARQL queries in the XML file.')
   op.add_option('--sql',action='store_true',default=False, dest='sql', help='Generate SQL from SPARQL.')
   (options, args) = op.parse_args()
   RunQueryFile(args[0], args[1] or '', options)




