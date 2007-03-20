### Utilities for evaluating a parsed SPARQL expression using sparql-p
from rdflib.sparql import sparqlGraph, sparqlOperators
from rdflib.sparql.sparqlOperators import getValue
from rdflib.sparql.graphPattern import BasicGraphPattern
from rdflib.sparql.sparql import Unbound,PatternBNode, SPARQLError,_variablesToArray
from rdflib.Graph import ConjunctiveGraph, Graph, BackwardCompatGraph,ReadOnlyGraphAggregate
from rdflib import URIRef,Variable,BNode, Literal, plugin, RDF
from rdflib.store import Store
from rdflib.Literal import XSDToPython
from IRIRef import NamedGraph,RemoteGraph
from GraphPattern import ParsedAlternativeGraphPattern,ParsedOptionalGraphPattern
from Resource import *
from Triples import ParsedConstrainedTriples
from QName import *
from PreProcessor import *
from Expression import *
from Util import ListRedirect
from Operators import *
from FunctionLibrary import *
from SolutionModifier import ASCENDING_ORDER
from Query import AskQuery, SelectQuery

DEBUG = False

BinaryOperatorMapping = {
    LessThanOperator           : 'sparqlOperators.lt(%s,%s)%s',
    EqualityOperator           : 'sparqlOperators.eq(%s,%s)%s',
    NotEqualOperator           : 'sparqlOperators.neq(%s,%s)%s',
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
        return term
    elif isinstance(term,QName):
        #QNames and QName prefixes are the same in the grammar
        if not term.prefix:
            return URIRef(queryProlog.baseDeclaration + term.localname)
        else:
            return URIRef(queryProlog.prefixBindings[term.prefix] + term.localname)
    elif isinstance(term,QNamePrefix):
        return URIRef(queryProlog.baseDeclaration + term)
    elif isinstance(term,ParsedString):
        return Literal(term)
    else:
        return term

def unRollCollection(collection,queryProlog):
    nestedComplexTerms = []
    listStart = convertTerm(collection.identifier,queryProlog)
    if not collection._list:
        yield (listStart,RDF.rest,RDF.nil)
    elif len(collection._list) == 1:
        singleItem = collection._list[0]
        if isinstance(singleItem,RDFTerm):
            nestedComplexTerms.append(singleItem)
            yield (listStart,RDF.first,convertTerm(singleItem.identifier,queryProlog))
        else:
            yield (listStart,RDF.first,convertTerm(singleItem,queryProlog))
        yield (listStart,RDF.rest,RDF.nil)
    else:
        yield (listStart,RDF.first,collection._list[0].identifier)
        prevLink = listStart
        for colObj in collection._list[1:]:
            linkNode = convertTerm(BNode(),queryProlog)
            if isinstance(colObj,RDFTerm):
                nestedComplexTerms.append(colObj)
                yield (linkNode,RDF.first,convertTerm(colObj.identifier,queryProlog))
            else:
                yield (linkNode,RDF.first,convertTerm(colObj,queryProlog))            
            yield (prevLink,RDF.rest,linkNode)            
            prevLink = linkNode                        
        yield (prevLink,RDF.rest,RDF.nil)
    
    for additionalItem in nestedComplexTerms:
        for item in unRollRDFTerm(additionalItem,queryProlog):
            yield item    

def unRollRDFTerm(item,queryProlog):
    nestedComplexTerms = []
    for propVal in item.propVals:
        for propObj in propVal.objects:
            if isinstance(propObj,RDFTerm):
                nestedComplexTerms.append(propObj)
                yield (convertTerm(item.identifier,queryProlog),
                       convertTerm(propVal.property,queryProlog),
                       convertTerm(propObj.identifier,queryProlog))
            else:
               yield (convertTerm(item.identifier,queryProlog),
                      convertTerm(propVal.property,queryProlog),
                      convertTerm(propObj,queryProlog))
    if isinstance(item,ParsedCollection):
        for rt in unRollCollection(item,queryProlog):
            yield rt  
    for additionalItem in nestedComplexTerms:
        for item in unRollRDFTerm(additionalItem,queryProlog):
            yield item

def unRollTripleItems(items,queryProlog):
    """
    Takes a list of Triples (nested lists or ParsedConstrainedTriples)
    and (recursively) returns a generator over all the contained triple patterns
    """    
    if isinstance(items,RDFTerm):
        for item in unRollRDFTerm(items,queryProlog):
            yield item
    else:
        for item in items:
            if isinstance(item,RDFTerm):
                for i in unRollRDFTerm(item,queryProlog):
                    yield i
            else:
                for i in unRollTripleItems(item,queryProlog):
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
                                                 expr.arg3 and ',"'+expr.arg3 + '"' or '',
                                                 combinationInvokation)
    elif isinstance(expr,BuiltinFunctionCall):
        normBuiltInName = FUNCTION_NAMES[expr.name].lower()
        normBuiltInName = CAMEL_CASE_BUILTINS.get(normBuiltInName,'sparqlOperators.'+normBuiltInName)
        return "%s(%s)%s"%(normBuiltInName,",".join([mapToOperator(i,prolog,combinationArg) for i in expr.arguments]),combinationInvokation)
    elif isinstance(expr,Literal):
        return str(expr)
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
        if isinstance(expr,ListRedirect):
            expr = expr.reduce()
            if expr.pyBooleanOperator:
                return expr.pyBooleanOperator.join([mapToOperator(i,prolog) for i in expr]) 
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
        #((P1 UNION P2) FILTER R) AND ((P1 FILTER R) UNION (P2 FILTER R)).
        for alternativeGPBlock in alternativeGraphPatterns:
            for alternativeGPs in alternativeGPBlock.nonTripleGraphPattern:
                triples,constraints = reorderBasicGraphPattern(alternativeGPs[0])
                constraints.extend(globalConstraints)
                alternativeGPInst = BasicGraphPattern([t for t in unRollTripleItems(triples,prolog)])
                alternativeGPInst.addConstraints([createSPARQLPConstraint(constr,prolog) for constr in constraints])
                basicGraphPatterns.append(alternativeGPInst)
    elif graphGraphPatterns:
        triples,constraints = reorderBasicGraphPattern(graphGraphPatterns[0].nonTripleGraphPattern[0])
        for t in unRollTripleItems(triples,prolog):
            patternList.append(t)
        basicGraphPattern = BasicGraphPattern(patternList)
        for constr in constraints:
            basicGraphPattern.addConstraint(createSPARQLPConstraint(constr,prolog))
        basicGraphPatterns.append(basicGraphPattern)
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

def Evaluate(graph,query,passedBindings = {},DEBUG = False):
    """
    Takes:
        1. a rdflib.Graph.Graph instance 
        2. a SPARQL query instance (parsed using the BisonGen parser)
        3. A dictionary of initial variable bindings (varName -> .. rdflib Term .. )
        4. DEBUG Flag

    Returns a list of tuples - each a binding of the selected variables in query order
    """
    if query.query.dataSets:
        graphs = []
        for dtSet in query.query.dataSets:
            if isinstance(dtSet,NamedGraph):
                graphs.append(Graph(graph.store,dtSet))
            else:
                memStore = plugin.get('IOMemory',Store)()
                memGraph = Graph(memStore)
                try:
                    memGraph.parse(dtSet,format='n3')
                except:
                    #Parse as RDF/XML instead
                    memGraph.parse(dtSet)
                graphs.append(memGraph)
        tripleStore = sparqlGraph.SPARQLGraph(ReadOnlyGraphAggregate(graphs))
    else:        
        tripleStore = sparqlGraph.SPARQLGraph(graph)    

    #Interpret Graph Graph Patterns as Named Graphs
    graphGraphPatterns = categorizeGroupGraphPattern(query.query.whereClause.parsedGraphPattern)[0]
    if graphGraphPatterns:
        graphGraphP = graphGraphPatterns[0].nonTripleGraphPattern
        if isinstance(graphGraphP.name,Variable):
            if graphGraphP.name in passedBindings:
                tripleStore = sparqlGraph.SPARQLGraph(Graph(graph.store,passedBindings[graphGraphP.name]))
            else: 
                raise Exception("Graph Graph Patterns can only be used with variables bound at the top level or a URIRef or BNode term")
                tripleStore = sparqlGraph.SPARQLGraph(graph,logicalPattern=True)
        else:
            graphName =  isinstance(graphGraphP.name,Variable) and passedBindings[graphGraphP.name] or graphGraphP.name
            tripleStore = sparqlGraph.SPARQLGraph(Graph(graph.store,graphName))

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
                # is it a variable?
                if isinstance(orderCond,Variable):
                    orderBy.append(orderCond)
                    orderAsc.append(ASCENDING_ORDER)
                # is it another expression, only variables are supported
                else:
                    expr = orderCond.expression
                    assert isinstance(expr,Variable),"Support for ORDER BY with anything other than a variable is not supported: %s"%expr
                    orderBy.append(expr)                    
                    orderAsc.append(orderCond.order == ASCENDING_ORDER)

        limit = query.query.solutionModifier.limitClause and int(query.query.solutionModifier.limitClause) or None

        offset = query.query.solutionModifier.offsetClause and int(query.query.solutionModifier.offsetClause) or 0
        return result.select(query.query.variables,
                             query.query.distinct,
                             limit,
                             orderBy,
                             orderAsc,
                             offset
                             ),_variablesToArray(query.query.variables,"selection"),result._getAllVariables(),orderBy,query.query.distinct
    else:
        raise NotImplemented(CONSTRUCT_NOT_SUPPORTED,repr(query))

OPTIONALS_NOT_SUPPORTED                   = 1
#GRAPH_PATTERN_NOT_SUPPORTED               = 2
UNION_GRAPH_PATTERN_NOT_SUPPORTED         = 3
GRAPH_GRAPH_PATTERN_NOT_SUPPORTED         = 4
GROUP_GRAPH_PATTERN_NESTING_NOT_SUPPORTED = 5
CONSTRUCT_NOT_SUPPORTED                   = 6

ExceptionMessages = {
    OPTIONALS_NOT_SUPPORTED                   : 'Nested OPTIONAL not currently supported',
    #GRAPH_PATTERN_NOT_SUPPORTED               : 'Graph Pattern not currently supported',
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
