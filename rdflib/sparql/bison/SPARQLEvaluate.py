### Utilities for evaluating a parsed SPARQL expression using sparql-p
from rdflib.sparql import sparqlGraph
from rdflib.sparql.sparqlOperators import *
from rdflib.sparql.graphPattern import BasicGraphPattern
from rdflib.sparql.sparql import Unbound,PatternBNode
from rdflib.Graph import ConjunctiveGraph, Graph, BackwardCompatGraph
from rdflib import URIRef,Variable,BNode, Literal
from IRIRef import NamedGraph
from GraphPattern import ParsedAlternativeGraphPattern,ParsedOptionalGraphPattern
from Resource import *
from Triples import ParsedConstrainedTriples
from QName import *
from PreProcessor import *
from Expression import *
from Util import ListRedirect
from Operators import *
from FunctionLibrary import *

DEBUG = False

BinaryOperatorMapping = {
    LessThanOperator        : 'lt(%s,%s)%s',
    EqualityOperator        : 'eq(%s,%s)%s',
    NotEqualOperator        : 'not(eq(%s,%s)%s)',
    LessThanOrEqualOperator : 'le(%s,%s)%s',
    GreaterThanOperator     : 'gt(%s,%s)%s',
    GreaterThanOrEqualOperator : 'ge(%s,%s)%s',
}

UnaryOperatorMapping = {
    LogicalNegation : 'not(%s)',
    NumericNegative : '-(%s)',
}

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
    and (recursively) returns a generator over all the contained triple patterns
    """
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

def add(*args):
    """
    SPARQL numeric '+ operator
    """
    return lambda(bindings): reduce(lambda x,y: getValue(x)(bindings)+getValue(y)(bindings),list(args))

def mapToOperator(expr,prolog,combinationArg=None):    
    """
    Reduces certain expressions (operator expressions, function calls, terms, and combinator expressions)
    into strings of their Python expression equivalent
    """
    combinationInvokation = combinationArg and '(%s)'%combinationArg or ""
    if isinstance(expr,ListRedirect):        
        expr = expr.reduce()
    if isinstance(expr,UnaryOperator):
        return UnaryOperatorMapping[type(expr)]%mapToOperator(expr.argument,prolog,combinationArg)
    elif isinstance(expr,BinaryOperator):
        return BinaryOperatorMapping[type(expr)]%(mapToOperator(expr.left,prolog,combinationArg),mapToOperator(expr.right,prolog,combinationArg),combinationInvokation)
    elif isinstance(expr,(Variable,Unbound)):
        return '"%s"'%expr
    elif isinstance(expr,BuiltinFunctionCall):
        return "%s(%s)%s"%(FUNCTION_NAMES[expr.name].lower(),",".join([mapToOperator(i,prolog,combinationArg) for i in expr.arguments]),combinationInvokation)
    elif isinstance(expr,(QName,basestring)):
        return "'%s'"%convertTerm(expr,prolog)
    elif isinstance(expr,Literal):
        return repr(expr)
    elif isinstance(expr,ParsedAdditiveExpressionList):
        return 'Literal(add(%s)%s)'%(','.join([mapToOperator(item,prolog,combinationArg='i') for item in expr]),combinationInvokation)
    else:
        raise Exception("What do i do with %s (a %s)?"%(expr,type(expr).__name__))

def createSPARQLPConstraint(filter,prolog):
    """
    Takes an instance of either ParsedExpressionFilter or ParsedFunctionFilter
    and converts it to a sparql-p operator by composing a python string of lambda functions and SPARQL operators
    This string is than evaluated to return the actual function for sparql-p
    """
    reducedFilter = filter.filter.reduce()
    if isinstance(reducedFilter,ParsedConditionalAndExpressionList):
        combinationLambda = 'lambda(i): %s'%(' or '.join(['%s'%mapToOperator(expr,prolog,combinationArg='i') for expr in reducedFilter]))
        if prolog.DEBUG:
            print "sparql-p operator(s): %s"%combinationLambda
        return eval(combinationLambda)
    elif isinstance(reducedFilter,ParsedRelationalExpressionList):
        combinationLambda = 'lambda(i): %s'%(' and '.join(['%s'%mapToOperator(expr,prolog,combinationArg='i') for expr in reducedFilter]))
        if prolog.DEBUG:
            print "sparql-p operator(s): %s"%combinationLambda
        return eval(combinationLambda)
    else:
        rt=mapToOperator(reducedFilter)
        if prolog.DEBUG:
            print "sparql-p operator(s): %s"%rt
        return eval(rt)

def sparqlPSetup(groupGraphPattern,prolog):
    """
    This core function takes Where Clause and two lists of rdflib.sparql.graphPattern.BasicGraphPatterns 
    (the main patterns - connected by UNION - and an optional patterns)
    This is the core SELECT API of sparql-p
    """
    basicGraphPatterns = []
    patternList = []
    graphGraphPatterns,optionalGraphPatterns,alternativeGraphPatterns = categorizeGroupGraphPattern(groupGraphPattern)
    #UNION alternative graph patterns
    if alternativeGraphPatterns:        
        globalTPs,globalConstraints = reorderBasicGraphPattern(groupGraphPattern[0])    
        #Global constraints / optionals must be distributed within each alternative GP via:
        #((P1 UNION P2) FILTER R) ≡ ((P1 FILTER R) UNION (P2 FILTER R)).        
        for alternativeGPBlock in alternativeGraphPatterns:
            for alternativeGPs in alternativeGPBlock.nonTripleGraphPattern:
                triples,constraints = reorderBasicGraphPattern(alternativeGPs[0])
                constraints.extend(globalConstraints)
                alternativeGPInst = BasicGraphPattern([t for t in unRollTripleItems(triples,prolog)])
                alternativeGPInst.addConstraints([createSPARQLPConstraint(constr,prolog) for constr in constraints])
                basicGraphPatterns.append(alternativeGPInst)
    else:
        triples,constraints = reorderBasicGraphPattern(groupGraphPattern[0])    
        for t in unRollTripleItems(triples,prolog):            
            patternList.append(t)
        basicGraphPattern = BasicGraphPattern(patternList)    
        for constr in constraints:
            basicGraphPattern.addConstraint(createSPARQLPConstraint(constr,prolog))
        basicGraphPatterns.append(basicGraphPattern)
        
    #Global optional patterns
    rtOptionalGraphPatterns = []
    for opGGP in [g.nonTripleGraphPattern for g in optionalGraphPatterns]:
        opTriples,opConstraints = reorderBasicGraphPattern(opGGP[0])
        opPatternList = []
        for t in unRollTripleItems(opTriples,prolog):            
            opPatternList.append(t)
        opBasicGraphPattern = BasicGraphPattern(opPatternList)
        for constr in opConstraints:# + constraints:
            opBasicGraphPattern.addConstraint(createSPARQLPConstraint(constr,prolog))
        rtOptionalGraphPatterns.append(opBasicGraphPattern)
    return basicGraphPatterns,rtOptionalGraphPatterns

def isTriplePattern(nestedTriples):
    """
    Determines (recursively) if the BasicGraphPattern contains any Triple Patterns
    returning a boolean flag indicating if it does or not
    """
    if isinstance(nestedTriples,list):
        for i in nestedTriples:
            if isTriplePattern(i):
                return True
            return False
    elif isinstance(nestedTriples,ParsedConstrainedTriples):
        if nestedTriples.triples:
            return isTriplePattern(nestedTriples.triples)
        else:
            return False
    elif isinstance(nestedTriples,ParsedConstrainedTriples) and not nestedTriples.triples:
        return isTriplePattern(nestedTriples.triples)    
    else:
        return True

def categorizeGroupGraphPattern(gGP):
    """
    Breaks down a ParsedGroupGraphPattern into mutually exclusive sets of
    ParsedGraphGraphPattern, ParsedOptionalGraphPattern, and ParsedAlternativeGraphPattern units
    """
    assert isinstance(gGP,ParsedGroupGraphPattern), "%s is not a ParsedGroupGraphPattern"%gGP
    graphGraphPatterns       = [gP for gP in gGP if gP.nonTripleGraphPattern and isinstance(gP.nonTripleGraphPattern,ParsedGraphGraphPattern)]
    optionalGraphPatterns    = [gP for gP in gGP if gP.nonTripleGraphPattern and isinstance(gP.nonTripleGraphPattern,ParsedOptionalGraphPattern)]
    alternativeGraphPatterns = [gP for gP in gGP if gP.nonTripleGraphPattern and isinstance(gP.nonTripleGraphPattern,ParsedAlternativeGraphPattern)]
    return graphGraphPatterns,optionalGraphPatterns,alternativeGraphPatterns
                
def validateGroupGraphPattern(gGP,noNesting = False):
    """
    Verifies (recursively) that the Group Graph Pattern is supported
    """
    firstGP = gGP[0]
    #print "Validating ", gGP
    graphGraphPatternNo,optionalGraphPatternNo,alternativeGraphPatternNo = [len(gGPKlass) for gGPKlass in categorizeGroupGraphPattern(gGP)]
#    for g in gGP:
#        print g
    #print len(gGP),len([gP for gP in gGP if gP.nonTripleGraphPattern and isinstance(gP.nonTripleGraphPattern,(ParsedGraphGraphPattern,ParsedOptionalGraphPattern))])
    if firstGP.triples and isTriplePattern(firstGP.triples) and  isinstance(firstGP.nonTripleGraphPattern,ParsedAlternativeGraphPattern):        
        raise NotImplemented(UNION_GRAPH_PATTERN_NOT_SUPPORTED,"%s"%firstGP)
    elif firstGP.triples and graphGraphPatternNo:
        raise NotImplemented(GRAPH_GRAPH_PATTERN_NOT_SUPPORTED,"%s"%gGP)
    elif graphGraphPatternNo > 1 or graphGraphPatternNo and alternativeGraphPatternNo:
        raise NotImplemented(GRAPH_GRAPH_PATTERN_NOT_SUPPORTED,"%s"%gGP)
    for gP in gGP:        
        if noNesting and isinstance(gP.nonTripleGraphPattern,(ParsedOptionalGraphPattern,ParsedGraphGraphPattern,ParsedAlternativeGraphPattern)):
            raise NotImplemented(GROUP_GRAPH_PATTERN_NESTING_NOT_SUPPORTED,"%s"%gGP)
        if isinstance(gP.nonTripleGraphPattern,ParsedAlternativeGraphPattern):
            for _gGP in gP.nonTripleGraphPattern:
                validateGroupGraphPattern(_gGP,noNesting = True)
        elif gP.nonTripleGraphPattern:            
            validateGroupGraphPattern(gP.nonTripleGraphPattern,noNesting = True)

def Evaluate(store,query,passedBindings = {},DEBUG = False):
    """
    Takes:
        1. an rdflib.store.Store instance
        2. a SPARQL query instance (parsed using the BisonGen parser)
        3. A dictionry of initial variable bindings (varName -> .. rdflib Term .. )
        4. DEBUG Flag
        
    Currently returns a variable binding tuple per solution (this is what sparql-p returns)
    """
    if query.query.dataSets:
        tripleStore = sparqlGraph.SPARQLGraph(ReadOnlyGraphAggregate(store,query.query.dataSets))
    else:        
        tripleStore = sparqlGraph.SPARQLGraph(BackwardCompatGraph(store))    
        
    if query.query.variables:
        query.query.variables = [convertTerm(item,query.prolog) for item in query.query.variables]
    else:
        query.query.variables = '*'
    gp = reorderGroupGraphPattern(query.query.whereClause.parsedGraphPattern)
    validateGroupGraphPattern(gp)
    
    query.prolog.DEBUG = DEBUG
    
    basicPatterns,optionalPatterns = sparqlPSetup(gp,query.prolog)
    
    if DEBUG:
        print "## Select Variables ##\n",query.query.variables
        print "## Patterns ##\n",basicPatterns
        print "## OptionalPatterns ##\n",optionalPatterns
    return tripleStore.query(query.query.variables,basicPatterns,optionalPatterns,passedBindings)
        
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

OPTIONALS_NOT_SUPPORTED                   = 1
GRAPH_PATTERN_NOT_SUPPORTED               = 2
UNION_GRAPH_PATTERN_NOT_SUPPORTED         = 3
GRAPH_GRAPH_PATTERN_NOT_SUPPORTED         = 4
GROUP_GRAPH_PATTERN_NESTING_NOT_SUPPORTED = 5
    
ExceptionMessages = {
    OPTIONALS_NOT_SUPPORTED                   : 'Nested OPTIONAL not currently supported',
    GRAPH_PATTERN_NOT_SUPPORTED               : 'Graph Pattern not currently supported',
    UNION_GRAPH_PATTERN_NOT_SUPPORTED         : 'UNION Graph Pattern (currently) can only be combined with OPTIONAL Graph Patterns',
    GRAPH_GRAPH_PATTERN_NOT_SUPPORTED         : 'Graph Graph Pattern (currently) cannot only be used once by themselves or with OPTIONAL Graph Patterns',
    GROUP_GRAPH_PATTERN_NESTING_NOT_SUPPORTED : 'Nesting of Group Graph Pattern (currently) not supported',
}


class NotImplemented(Exception):    
    def __init__(self,code,msg):
        self.code = code
        self.msg = msg
    def __str__(self):
        return ExceptionMessages[self.code] + ' :' + self.msg