#!/d/Bin/Python/python.exe
# -*- coding: utf-8 -*-
#
#
# $Date: 2005/04/02 07:30:02 $, by $Author: ivan $, $Revision: 1.1 $
#
"""

"""
import sys, os, time, datetime, imp, sys, StringIO
sys.path.insert(0,"../")

from testSPARQL import ns_rdf
from testSPARQL import ns_rdfs
from testSPARQL import ns_foaf
from testSPARQL import ns_vcard
from testSPARQL import ns_person

from rdflib.sparql import sparqlGraph
from rdflib.FileInputSource import FileInputSource

tests = {
        1021: "Test10_21",
        1022: "Test10_22",
        1023: "Test10_23",
}

Debug = False



def run(modName) :
        # Import the python module
        defs = None
        (fl,realpath,descr) = imp.find_module(modName,["."])
        mod = imp.load_module(modName,fl,realpath,descr)
        defs = mod.__dict__

        ##################################################
        # Two ways of identifying the RDF data:
        # 1. A Triple Store generated in the module
        graph = None
        try :
                graph = defs["graph"]
        except :
                pass
        # 2. Directly in the test module as a string
        rdfData = None
        try :
                rdfData     = defs["rdfData"]
        except :
                pass

        # Get the final of the triple store...
        if graph == None :
                stream = FileInputSource(StringIO.StringIO(rdfData))
                graph = sparqlGraph.SPARQLGraph()
                graph.parse(stream,format="xml")

        ###############################################
        # Retrive the query data
        pattern     = defs["pattern"]
        optPattern  = defs["optional"]	
        construct   = defs["construct"]	


        ###############################################		
        print "\n============= Test Module: %s =============" % modName			

        results     = graph.queryObject(pattern,optPattern)
        graph = results.construct(construct)
        graph.serialize("output.rdf")

        print "=== generated RDF file (output.rdf):\n"
        for l in file("output.rdf") :
                sys.stdout.write(l)

if __name__ == '__main__' :
        if len(sys.argv) == 1 :
                #print "Usage: %s modname1 modname2 ..." % sys.argv[0]
                for mod in tests.values():
                        run(mod)
        else :
                for mod in sys.argv[1:] :
                        if mod.endswith(".py") :
                                run(mod[0:-3])
                        else :
                                run(mod)


