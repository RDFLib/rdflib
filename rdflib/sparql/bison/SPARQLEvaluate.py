### Utilities for evaluating a parsed SPARQL expression using sparql-p
from rdflib.sparql import sparqlGraph
from rdflib.sparql.graphPattern import BasicGraphPattern
from rdflib.sparql.sparql import Unbound,PatternBNode
from rdflib.Graph import ConjunctiveGraph, Graph, BackwardCompatGraph
from rdflib import URIRef,Variable,BNode
from IRIRef import NamedGraph
from GraphPattern import ParsedAlternativeGraphPattern,ParsedOptionalGraphPattern
from Resource import *
from Triples import ParsedConstrainedTriples
from QName import *

def convertTerm(term,queryProlog):
    """
    Utility function  for converting parsed Triple components into Unbound / PatternBNode
    """
    if isinstance(term,Variable):
        return Unbound(term[1:])
    elif isinstance(term,BNode):
        return PatternBNode(term)
    elif isinstance(term,QName):        
        return URIRef(queryProlog.prefixBindings[term.prefix] + term.localname)
    elif isinstance(term,QNamePrefix):
        return URIRef(queryProlog.baseDeclaration + term)    
    else:
        return term

def unRollTripleItems(items,queryProlog):    
    """
    Takes a list of Triples (nested lists or ParsedConstrainedTriples)
    """
    if isinstance(items,ParsedConstrainedTriples)    :
        raise NotImplemented(FILTERS_NOT_SUPPORTED,items)
    for item in items:        
        additionalTriples = []
        if isinstance(item,(Resource,TwiceReferencedBlankNode)):
            for propVal in item.propVals:
                for propObj in propVal.objects:
                    if isinstance(propObj,ParsedCollection):
                        for colObj in propObj._list:
                            yield (convertTerm(item.identifier,queryProlog),
                                   convertTerm(propVal.property,queryProlog),
                                   convertTerm(colObj,queryProlog))
                    elif isinstance(propObj,(Resource,TwiceReferencedBlankNode)):                    
                        additionalTriples.append(propObj)
                        yield (convertTerm(item.identifier,queryProlog),
                               convertTerm(propVal.property,queryProlog),
                               convertTerm(propObj.identifier,queryProlog))
                    else:                       
                       yield (convertTerm(item.identifier,queryProlog),
                              convertTerm(propVal.property,queryProlog),
                              convertTerm(propObj,queryProlog))
                
        for additionalItem in additionalTriples:
            for item in unRollTripleItems(additionalItem,queryProlog):
                yield item

def createGraphPattern(pattern,prolog,optionalAllowed = True):
    """
    Create two rdflib.sparql.graphPattern.BasicGraphPatterns (the main pattern and an optional pattern)
    """
    patternList = []
    for item in pattern.triples:        
        for t in unRollTripleItems(item,prolog):            
            patternList.append(t)

    basicGraphPattern = BasicGraphPattern(patternList)
    if not optionalAllowed and pattern.nonTripleGraphPattern:
        raise NotImplemented(OPTIONALS_NOT_SUPPORTED,pattern)
    optionalGraphPattern = None
    if pattern.nonTripleGraphPattern and pattern.nonTripleGraphPattern.graphPatterns:
        optionalGraphPattern = validateGroupGraphPattern(pattern.nonTripleGraphPattern.graphPatterns)
        optionalGraphPattern = createGraphPattern(optionalGraphPattern,prolog,optionalAllowed = False)[0]
    return basicGraphPattern,optionalGraphPattern
                
def validateGroupGraphPattern(patterns):
    """
    Ensures that the GraphPattern is supported
    """
    if len([p for p in patterns if p.triples or p.nonTripleGraphPattern]) != 1:
        raise NotImplemented(GRAPH_PATTERN_NOT_SUPPORTED%patterns)
    pattern = patterns[0]
    if pattern.nonTripleGraphPattern:
        if not isinstance(pattern.nonTripleGraphPattern,ParsedOptionalGraphPattern):
            raise NotImplemented(GRAPH_PATTERN_NOT_SUPPORTED ,"%s is not ParsedOptionalGraphPattern"%pattern.nonTripleGraphPattern)
    return pattern

def Evaluate(store,query):
    """
    Takes a store instance and a SPARQL query instance (parsed using the BisonGen parser)
    returns the result
    """
    if query.query.dataSets:
        tripleStore = sparqlGraph.SPARQLGraph(ReadOnlyGraphAggregate(store,query.query.dataSets))
    else:        
        tripleStore = sparqlGraph.SPARQLGraph(BackwardCompatGraph(store))    
        
    if query.query.variables:
        query.query.variables = [convertTerm(item,query.prolog) for item in query.query.variables]
    else:
        query.query.variables = '*'

    pattern = validateGroupGraphPattern(query.query.whereClause.parsedGraphPattern.graphPatterns)
    basicPatterns,optionalPattern = createGraphPattern(pattern,query.prolog)
#    print "## Select Variables ##\n",query.query.variables
#    print "## Patterns ##\n",basicPatterns
#    print "## OptionalPatterns ##\n",optionalPattern
    return tripleStore.query(query.query.variables,basicPatterns,optionalPattern)
        
class ReadOnlyGraphAggregate:
    """
    Utility abstraction of Graph for read operations over the union of several named Graphs
    This 1) should be integrated into Graph.py 2) can be *vastly* optimized by store implementations
    """
    def __init__(self, store, identifiers=None):
        self.__store = store
        self.identifiers = identifiers is None and [] or identifiers
        
    def __get_store(self):
        return self.__store
    store = property(__get_store)

    def __get_identifier(self):
        raise Exception("This is a GraphAggregate, it is associated with *multiple* identifiers")
    identifier = property(__get_identifier)
    
    def triples(self, (s, p, o)):
        for identifier in self.identifiers:
            for (s, p, o), cg in self.__store.triples((s, p, o), context=Graph(self.__store,identifier)):
                yield (s, p, o)

    def __len__(self):
        return reduce(lambda x,y: x+y,[self.__store.__len__(context=Graph(self.__store,identifier)) for identifier in self.identifiers])

    def __iter__(self):
        return self.triples((None, None, None))

    def __contains__(self, triple):
        for triple in self.triples(triple):
            return 1
        return 0

FILTERS_NOT_SUPPORTED       = 0
OPTIONALS_NOT_SUPPORTED     = 1
GRAPH_PATTERN_NOT_SUPPORTED = 2
    
ExceptionMessages = {
    FILTERS_NOT_SUPPORTED       : 'FILTERs not currently supported',
    OPTIONALS_NOT_SUPPORTED     : 'Nested OPTIONAL not currently supported',
    GRAPH_PATTERN_NOT_SUPPORTED : 'Graph Pattern not currently supported',
}


class NotImplemented(Exception):    
    def __init__(self,code,msg):
        self.code = code
        self.msg = msg
    def __str__(self):
        return ExceptionMessages[self.code] + ' :' + self.msg