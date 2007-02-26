#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/04/02 07:29:46 $, by $Author: ivan $, $Revision: 1.1 $
#
"""

"""
import sys, os, time, datetime, imp, sys, StringIO

sys.path.insert(0,"../")

from rdflib import sparql
from rdflib.sparql import sparqlGraph
from testSPARQL import ns_rdf
from testSPARQL import ns_rdfs
from testSPARQL import ns_dc
from testSPARQL import ns_dc0
from testSPARQL import ns_foaf
from rdflib.FileInputSource import FileInputSource

def run(modName) :
        # Import the python module
        defs = None
        (fl,realpath,descr) = imp.find_module(modName,["."])
        mod = imp.load_module(modName,fl,realpath,descr)
        defs = mod.__dict__

        ##################################################
        # Three ways of identifying the RDF data:
        # 1. A Triple Store generated in the module
        tripleStore = None
        try :
                tripleStore = defs["tripleStore"]
        except :
                pass
        # 2. A reference to a set of RDF Files
        fils = None
        try :
                fils        = defs["datafiles"]
        except :
                pass
        # 3. Directly in the test module as a string
        rdfData = None
        try :
                rdfData     = defs["rdfData"]
        except :
                pass

        # Get the final of the triple store...
        if tripleStore == None :
                if rdfData == None :
                        tripleStore = retrieveRDFFiles(fils)
                else :
                        stream = StringIO.StringIO(rdfData)
                        tripleStore = sparqlGraph.SPARQLGraph()
                        tripleStore.parse(FileInputSource(stream),format="xml")

        ###############################################
        # Retrive the query data
        pattern     = defs["pattern"]
        optPattern  = defs["optional"]	
        select      = defs["select"]


        ###############################################		
        print "\n============= Test Module: %s =============" % modName			
        # better test modules describe their expected results...
        try :
                expected = defs["expected"]
                print "expected: %s" % expected
                print "=======\n"
        except :
                pass

        # Run the query and print the results						
        results = tripleStore.query(select,pattern,optPattern)
        num = len(results)
        print "Number of hits: %d" % num
        print
        for i in range(0,num) :
                hit = results[i]
                if len(select) == 1 :
                        print "%s: %s" % (select[0],hit)
                else :
                        for j in range(0,len(select)) :
                                var = select[j]
                                val = hit[j]
                                print "%s: %s" % (var,val)
                        print

if __name__ == '__main__' :
        if len(sys.argv) == 1 :
                print "Usage: %s modname1 modname2 ..." % sys.argv[0]
        else :
                for mod in sys.argv[1:] :
                        if mod.endswith(".py") :
                                run(mod[0:-3])
                        else :
                                run(mod)


