#!/usr/bin/env python
from pprint import pprint
from sets import Set
from rdflib.Namespace import Namespace
from rdflib import plugin,RDF,RDFS,URIRef,URIRef,Literal,Variable
from rdflib.store import Store
from cStringIO import StringIO
from rdflib.Graph import Graph,ReadOnlyGraphAggregate,ConjunctiveGraph
from rdflib.syntax.NamespaceManager import NamespaceManager
import unittest

RDFLIB_CONNECTION=''
RDFLIB_STORE='IOMemory'

import getopt, sys

def usage():
    print """USAGE: RDFPipe.py [options]
    
    Options:
    
      --stdin                     Parse RDF from STDIN (useful for piping)
      --help                      
      --input-format              Format of the input document(s).  One of:
                                  'xml','trix','n3','nt','rdfa'
      --output                    Format of the final serialized RDF graph.  One of:
                                  'n3','xml','pretty-xml','turtle',or 'nt'
      --ns=prefix=namespaceUri    Register a namespace binding (QName prefix to a 
                                  base URI).  This can be used more than once"""

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["output=","ns=","input=","stdin","help","input-format="])
    except getopt.GetoptError, e:
        # print help information and exit:
        print e
        usage()
        sys.exit(2)

    factGraphs = []
    factFormat = 'xml'
    useRuleFacts = False
    nsBinds = {
        'rdf' : RDF.RDFNS,
        'rdfs': RDFS.RDFSNS,
        'owl' : "http://www.w3.org/2002/07/owl#",       
        'dc'  : "http://purl.org/dc/elements/1.1/",
        'foaf': "http://xmlns.com/foaf/0.1/",
        'wot' : "http://xmlns.com/wot/0.1/"        
    }
    outMode = 'n3'
    stdIn = False
    if not opts:
        usage()
        sys.exit()        
    for o, a in opts:
        if o == '--input-format':
            factFormat = a
        elif o == '--stdin':
            stdIn = True
        elif o == '--output':
            outMode = a
            assert a in ['xml','n3']
        elif o == '--ns':            
            pref,nsUri = a.split('=')
            nsBinds[pref]=nsUri
        elif o == "--input":
            factGraphs = a.split(',')
        elif o == "--help":
            usage()
            sys.exit()
        
    store = plugin.get(RDFLIB_STORE,Store)()        
    store.open(RDFLIB_CONNECTION)
    namespace_manager = NamespaceManager(Graph())
    for prefix,uri in nsBinds.items():
        namespace_manager.bind(prefix, uri, override=False)    
    factGraph = Graph(store) 
    factGraph.namespace_manager = namespace_manager
    if factGraphs:
        for fileN in factGraphs:
            factGraph.parse(open(fileN),format=factFormat)
    if stdIn:
        factGraph.parse(sys.stdin,format=factFormat)
    print factGraph.serialize(destination=None, format=outMode, base=None)
    store.rollback()

if __name__ == "__main__":
    main()
