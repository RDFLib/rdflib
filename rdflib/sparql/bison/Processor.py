from rdflib import sparql
import rdflib.sparql.parser

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
        from rdflib.namespace import RDFS, RDF, OWL
        initNs.update({u'rdfs':RDFS.uri, u'owl':OWL.uri, u'rdf':RDF.uri}) 
        from rdflib.sparql.bison.Query import Query, Prolog
        assert isinstance(strOrQuery, (basestring, Query)),"%s must be a string or an rdflib.sparql.bison.Query.Query instance"%strOrQuery
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
        #from rdflib.store.MySQL import SQL
        if False and isinstance(self.graph.store,SQL) and not \
            (hasattr(self.graph.store,'originalInMemorySQL') and self.graph.store.originalInMemorySQL):
            from rdflib.sparql.sql.RelationalAlgebra import TopEvaluate
            from rdflib.sparql.sql.RdfSqlBuilder import DEFAULT_OPT_FLAGS
            opts = self.graph.store.optimizations and self.graph.store.optimizations or DEFAULT_OPT_FLAGS  
            return TopEvaluate(strOrQuery,
                               self.graph,
                               initBindings,
                               DEBUG=DEBUG,
                               optimizations=opts,
                               dataSetBase=dataSetBase,
                               extensionFunctions=extensionFunctions)
        else:
            from rdflib.sparql.Algebra import TopEvaluate
            return TopEvaluate(strOrQuery,
                               self.graph,
                               initBindings,
                               DEBUG=DEBUG,
                               dataSetBase=dataSetBase,
                               extensionFunctions=extensionFunctions)
