### Utilities for evaluating a parsed SPARQL expression using sparql-p
import rdflib
from rdflib.sparql import sparqlGraph, sparqlOperators, SPARQLError
from rdflib.sparql.sparqlOperators import getValue
from rdflib.sparql.graphPattern import BasicGraphPattern
from rdflib.sparql.Unbound import Unbound
from rdflib.sparql.Query import _variablesToArray, queryObject, SessionBNode
from rdflib.Graph import ConjunctiveGraph, Graph, BackwardCompatGraph,ReadOnlyGraphAggregate
from rdflib import URIRef,Variable,BNode, Literal, plugin, RDF
from rdflib.store import Store
from rdflib.Literal import XSDToPython
from IRIRef import NamedGraph,RemoteGraph
from GraphPattern import *
from Resource import *
from Triples import ParsedConstrainedTriples
from QName import *
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
    Utility function  for converting parsed Triple components into Unbound 
    """
    if isinstance(term,Variable):
        return Unbound(term[1:])
    elif isinstance(term,BNode):
        return term
    elif isinstance(term,QName):
        #QNames and QName prefixes are the same in the grammar
        if not term.prefix:
            if queryProlog is None:
                return URIRef(term.localname)
            else:
                base = queryProlog.baseDeclaration and queryProlog.baseDeclaration or\
                       queryProlog.prefixBindings[u'']
                return URIRef(base + term.localname)
        elif term.prefix == '_':
            #Told BNode See: http://www.w3.org/2001/sw/DataAccess/issues#bnodeRef
            import warnings
            warnings.warn("The verbatim interpretation of explicit bnode identifiers is contrary to (current) DAWG stance",SyntaxWarning)
            return SessionBNode(term.localname)        
        else:
            return URIRef(queryProlog.prefixBindings[term.prefix] + term.localname)
    elif isinstance(term,QNamePrefix):
        if queryProlog is None:
            return URIRef(term)
        else:
            return URIRef(queryProlog.baseDeclaration + term)
    elif isinstance(term,ParsedString):
        return Literal(term)
    elif isinstance(term,ParsedDatatypedLiteral):
        dT = term.dataType
        if isinstance(dT,QName):
            dT = convertTerm(dT,queryProlog)
        return Literal(term.value,datatype=dT)
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
    elif isinstance(items,ParsedConstrainedTriples):
        assert isinstance(items.triples,list)
        for item in items.triples:
            if isinstance(item,RDFTerm):
                for i in unRollRDFTerm(item,queryProlog):
                    yield i
            else:
                for i in unRollTripleItems(item,queryProlog):
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
    elif isinstance(expr,ParsedDatatypedLiteral):
        return repr(Literal(expr.value,datatype=convertTerm(expr.dataType,prolog)))
    elif isinstance(expr,Literal):
        return repr(expr)
    elif isinstance(expr,URIRef):
        import warnings
        warnings.warn("There is the possibility of __repr__ being deprecated in python3K",DeprecationWarning,stacklevel=3)        
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

CONSTRUCT_NOT_SUPPORTED                   = 1

ExceptionMessages = {
    CONSTRUCT_NOT_SUPPORTED                   : '"Construct" is not (currently) supported',
}

class NotImplemented(Exception):
    def __init__(self,code,msg):
        self.code = code
        self.msg = msg
    def __str__(self):
        return ExceptionMessages[self.code] + ' :' + self.msg
