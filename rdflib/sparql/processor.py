from rdflib import sparql
import rdflib.sparql.parser
from rdflib.sparql.Algebra import TopEvaluate
from rdflib.namespace import RDFS, RDF, OWL
from rdflib.sparql.components import Query, Prolog

class Processor(sparql.Processor):

    def __init__(self, graph):
        self.graph = graph

    def query(self, 
              strOrQuery, 
              initBindings={}, 
              initNs={}, 
              DEBUG=False,
              PARSE_DEBUG=False,
              dataSetBase=None,
              extensionFunctions={},
              USE_PYPARSING=False):

        initNs.update({u'rdfs':RDFS.uri, u'owl':OWL.uri, u'rdf':RDF.uri}) 

        assert isinstance(strOrQuery, (basestring, Query)),"%s must be a string or an rdflib.sparql.components.Query instance"%strOrQuery
        if isinstance(strOrQuery, basestring):
            strOrQuery = sparql.parser.parse(strOrQuery)
        if not strOrQuery.prolog:
            strOrQuery.prolog = Prolog(None, [])
            strOrQuery.prolog.prefixBindings.update(initNs)
        else:
            for prefix, nsInst in initNs.items():
                if prefix not in strOrQuery.prolog.prefixBindings:
                    strOrQuery.prolog.prefixBindings[prefix] = nsInst
                    
        global prolog            
        prolog = strOrQuery.prolog

        return TopEvaluate(strOrQuery,
                           self.graph,
                           initBindings,
                           DEBUG=DEBUG,
                           dataSetBase=dataSetBase,
                           extensionFunctions=extensionFunctions)
