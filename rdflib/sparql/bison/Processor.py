from rdflib import sparql
from rdflib.sparql.bison.Query import Query, Prolog
from rdflib.sparql.bison import Parse, Evaluate        

#from cStringIO import StringIO

class Processor(sparql.Processor):

    def __init__(self, graph):
        self.graph = graph
        
    def query(self, strOrQuery, initBindings={}, initNs={}, DEBUG=False):
        assert isinstance(strOrQuery, (basestring, Query)), "%s must be a string or an rdflib.sparql.bison.Query.Query instance"%strOrQuery
        if isinstance(strOrQuery, basestring):
            strOrQuery = Parse(strOrQuery, DEBUG)                 
        if not strOrQuery.prolog:
                strOrQuery.prolog = Prolog(None, [])
                strOrQuery.prolog.prefixBindings.update(initNs)
        else:
            for prefix, nsInst in initNs.items():
                if prefix not in strOrQuery.prolog.prefixBindings:
                    strOrQuery.prolog.prefixBindings[prefix] = nsInst                
        return  Evaluate(self.graph, strOrQuery, initBindings, DEBUG=DEBUG)
