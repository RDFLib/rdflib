### Utilities for evaluating a parsed SPARQL expression using sparql-p
from rdflib.sparql import sparqlGraph, sparqlOperators
from rdflib.sparql.sparqlOperators import getValue
from rdflib.sparql.graphPattern import BasicGraphPattern
from rdflib.sparql.sparql import Unbound,PatternBNode, SPARQLError
from rdflib.Graph import ConjunctiveGraph, Graph, BackwardCompatGraph
from rdflib import URIRef,Variable,BNode, Literal, plugin
from rdflib.Literal import XSDToPython
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
from SolutionModifier import DESCENDING_ORDER
from Query import AskQuery, SelectQuery

DEBUG = False

BinaryOperatorMapping = {
    LessThanOperator           : 'sparqlOperators.lt(%s,%s)%s',
    EqualityOperator           : 'sparqlOperators.eq(%s,%s)%s',
    NotEqualOperator           : 'not(sparqlOperators.eq(%s,%s)%s)',
    LessThanOrEqualOperator    : 'sparqlOperators.le(%s,%s)%s',
    GreaterThanOperator        : 'sparqlOperators.gt(%s,%s)%s',
    GreaterThanOrEqualOperator : 'sparqlOperators.ge(%s,%s)%s',
}

UnaryOperatorMapping = {
    LogicalNegation : 'not(%s)',
    NumericNegative : '-(%s)',
}

CAMEL_CASE_BUILTINS = {
    'isuri':'sparqlOperators.isURI',
    'isiri':'sparqlOperators.isIRI',
    'isblank':'sparqlOperators.isBlank',
    'isliteral':'sparqlOperators.isLiteral',
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
    elif isinstance(term,ParsedString):
        return Literal(term)
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

def mapToOperator(expr,prolog,combinationArg=None):    
    """
    Reduces certain expressions (operator expressions, function calls, terms, and combinator expressions)
    into strings of their Python equivalent
    """
    combinationInvokation = combinationArg and '(%s)'%combinationArg or ""
    if isinstance(expr,ListRedirect):        
        expr = expr.reduce()
    if isinstance(expr,UnaryOperator):
        return UnaryOperatorMapping[type(expr)]%(mapToOperator(expr.argument,prolog,combinationArg))
    elif isinstance(expr,BinaryOperator):
        return BinaryOperatorMapping[type(expr)]%(mapToOperator(expr.left,prolog,combinationArg),mapToOperator(expr.right,prolog,combinationArg),combinationInvokation)
    elif isinstance(expr,(Variable,Unbound)):
        return '"%s"'%expr
    elif isinstance(expr,ParsedREGEXInvocation):
        return 'sparqlOperators.regex(%s,%s%s)%s'%(mapToOperator(expr.arg1,prolog,combinationArg),
                                                 mapToOperator(expr.arg2,prolog,combinationArg),
                                                 expr.arg3 and ','+expr.arg3 or '',
                                                 combinationInvokation)
    elif isinstance(expr,BuiltinFunctionCall):
        normBuiltInName = FUNCTION_NAMES[expr.name].lower()
        normBuiltInName = CAMEL_CASE_BUILTINS.get(normBuiltInName,'sparqlOperators.'+normBuiltInName)
        return "%s(%s)%s"%(normBuiltInName,",".join([mapToOperator(i,prolog,combinationArg) for i in expr.arguments]),combinationInvokation)
    elif isinstance(expr,Literal):
        return repr(expr)
    elif isinstance(expr,(QName,basestring)):
        return "'%s'"%convertTerm(expr,prolog)
    elif isinstance(expr,ParsedAdditiveExpressionList):
        return 'Literal(%s)'%(sparqlOperators.addOperator([mapToOperator(item,prolog,combinationArg='i') for item in expr],combinationArg))
    elif isinstance(expr,FunctionCall):
        if isinstance(expr.name,QName):
            fUri = convertTerm(expr.name,prolog)
        if fUri in XSDToPython:
            return "sparqlOperators.XSDCast(%s,'%s')%s"%(mapToOperator(expr.arguments[0],prolog,combinationArg='i'),fUri,combinationInvokation)
        raise Exception("Whats do i do with %s (a %s)?"%(expr,type(expr).__name__))
    else:
        raise Exception("What do i do with %s (a %s)?"%(expr,type(expr).__name__))

def createSPARQLPConstraint(filter,prolog):
    """
    Takes an instance of either ParsedExpressionFilter or ParsedFunctionFilter
    and converts it to a sparql-p operator by composing a python string of lambda functions and SPARQL operators
    This string is then evaluated to return the actual function for sparql-p
    """    
    reducedFilter = isinstance(filter.filter,ListRedirect) and filter.filter.reduce() or filter.filter
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
    elif isinstance(reducedFilter,BuiltinFunctionCall):
        rt=mapToOperator(reducedFilter,prolog)
        if prolog.DEBUG:
            print "sparql-p operator(s): %s"%rt
        return eval(rt)        
    elif isinstance(reducedFilter,(ParsedAdditiveExpressionList,UnaryOperator,FunctionCall)):
        rt='lambda(i): %s'%(mapToOperator(reducedFilter,prolog,combinationArg='i'))
        if prolog.DEBUG:
            print "sparql-p operator(s): %s"%rt
        return eval(rt)        
    else:
        rt=mapToOperator(reducedFilter,prolog)
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
    globalTPs,globalConstraints = reorderBasicGraphPattern(groupGraphPattern[0])    
    #UNION alternative graph patterns
    if alternativeGraphPatterns:                
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
        #FIXME how do deal with data/local-constr/expr-2.rq?
        #opConstraints.extend(globalConstraints)
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
    graphGraphPatternNo,optionalGraphPatternNo,alternativeGraphPatternNo = [len(gGPKlass) for gGPKlass in categorizeGroupGraphPattern(gGP)]
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
        3. A dictionary of initial variable bindings (varName -> .. rdflib Term .. )
        4. DEBUG Flag

    Returns a list of tuples - each a binding of the selected variables in query order
    """
    if query.query.dataSets:
        tripleStore = sparqlGraph.SPARQLGraph(BackwardCompatGraph(store))
        #tripleStore = sparqlGraph.SPARQLGraph(ReadOnlyGraphAggregate(store,query.query.dataSets))
    else:        
        tripleStore = sparqlGraph.SPARQLGraph(BackwardCompatGraph(store))    
        
    if isinstance(query.query,SelectQuery) and query.query.variables:
        query.query.variables = [convertTerm(item,query.prolog) for item in query.query.variables]
    else:
        query.query.variables = []
    gp = reorderGroupGraphPattern(query.query.whereClause.parsedGraphPattern)
    validateGroupGraphPattern(gp)
    
    if query.prolog:
        query.prolog.DEBUG = DEBUG
    
    basicPatterns,optionalPatterns = sparqlPSetup(gp,query.prolog)
    
    if DEBUG:
        print "## Select Variables ##\n",query.query.variables
        print "## Patterns ##\n",basicPatterns
        print "## OptionalPatterns ##\n",optionalPatterns

    result = tripleStore.queryObject(basicPatterns,optionalPatterns,passedBindings)
    if result == None :
        # generate some proper output for the exception :-)
        msg = "Errors in the patterns, no valid query object generated; "
        msg += ("pattern:\n%s\netc..." % basicPatterns[0])
        raise SPARQLError(msg)
    
    if isinstance(query.query,AskQuery):
        return result.ask()
    
    elif isinstance(query.query,SelectQuery):        
        orderBy = None
        orderAsc = None
        if query.query.solutionModifier.orderClause:
            orderBy     = []
            orderAsc    = []
            for orderCond in query.query.solutionModifier.orderClause:
                expr = orderCond.expression.reduce()
                assert isinstance(expr,Variable),"Support for ORDER BY with anything other than a variable is not supported: %s"%expr
                orderBy.append(expr)
                orderAsc.append(orderCond.order == DESCENDING_ORDER)
        offset = query.query.solutionModifier.offsetClause and int(query.query.solutionModifier.offsetClause) or 0
        return result.select(query.query.variables,
                               query.query.distinct,
                               query.query.solutionModifier.limitClause,
                               orderBy,
                               orderAsc,
                               offset
                               )
    else:
        raise NotImplemented(CONSTRUCT_NOT_SUPPORTED,repr(query))
        
OPTIONALS_NOT_SUPPORTED                   = 1
GRAPH_PATTERN_NOT_SUPPORTED               = 2
UNION_GRAPH_PATTERN_NOT_SUPPORTED         = 3
GRAPH_GRAPH_PATTERN_NOT_SUPPORTED         = 4
GROUP_GRAPH_PATTERN_NESTING_NOT_SUPPORTED = 5
CONSTRUCT_NOT_SUPPORTED                   = 6
    
ExceptionMessages = {
    OPTIONALS_NOT_SUPPORTED                   : 'Nested OPTIONAL not currently supported',
    GRAPH_PATTERN_NOT_SUPPORTED               : 'Graph Pattern not currently supported',
    UNION_GRAPH_PATTERN_NOT_SUPPORTED         : 'UNION Graph Pattern (currently) can only be combined with OPTIONAL Graph Patterns',
    GRAPH_GRAPH_PATTERN_NOT_SUPPORTED         : 'Graph Graph Pattern (currently) cannot only be used once by themselves or with OPTIONAL Graph Patterns',
    GROUP_GRAPH_PATTERN_NESTING_NOT_SUPPORTED : 'Nesting of Group Graph Pattern (currently) not supported',
    CONSTRUCT_NOT_SUPPORTED                   : '"Construct" is not (currently) supported',
}


class NotImplemented(Exception):    
    def __init__(self,code,msg):
        self.code = code
        self.msg = msg
    def __str__(self):
        return ExceptionMessages[self.code] + ' :' + self.msg