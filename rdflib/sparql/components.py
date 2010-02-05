from rdflib.term import URIRef, BNode, Variable
from rdflib.term import Identifier
from rdflib.namespace import Namespace


class ListRedirect(object):
    """
    A utility class for lists of items joined by an operator.  ListRedirects with length 1
    are a special case and are considered equivalent to the item instead of a list containing it.
    The reduce function is used for normalizing ListRedirect to the single item (and calling reduce on it recursively)
    """
    reducable = True
    def __getattr__(self, attr):
        if hasattr(self._list, attr):
            return getattr(self._list, attr)
        raise AttributeError, '%s has no such attribute %s' % (repr(self), attr)

    def __iter__(self):
        for i in self._list:
            yield i

    def __len__(self):
        return len(self._list)

    def reduce(self):
        if self.reducable and len(self._list) == 1:
            singleItem = self._list[0]
            if isinstance(singleItem,ListRedirect):
                return singleItem.reduce()
            else:
                return singleItem
        else:
            return type(self)([isinstance(item,ListRedirect) and item.reduce() or item for item in self._list])

#Utility function for adding items to the front of a list
def ListPrepend(item,list):
    #print "adding %s to front of %s"%(item,list)
    return [item] + list

# Bindings

EMPTY_STRING=""

class PrefixDeclaration(object):
    """
    PrefixDecl ::= 'PREFIX' QNAME_NS Q_IRI_REF
    See: http://www.w3.org/TR/rdf-sparql-query/#rPrefixDecl
    """
    def __init__(self,qName,iriRef):
        self.namespaceMapping = Namespace(iriRef)
        self.qName = qName[:-1]
        self.base = iriRef
        #print self.base,self.qName,self.namespaceMapping.knows

    def __repr__(self):
        return "%s -> %s"%(self.base,self.qName)

    def __eq__(self, other):
        return (self.namespaceMapping == other.namespaceMapping and
                self.qName == other.qName)

class BaseDeclaration(URIRef):
    """
    BaseDecl ::= 'BASE' Q_IRI_REF
    See: http://www.w3.org/TR/rdf-sparql-query/#rBaseDecl
    """
    pass
    

# Expression

class ParsedConditionalAndExpressionList(ListRedirect):
    """
    A list of ConditionalAndExpressions, joined by '||'
    """
    pyBooleanOperator = ' or '
    def __init__(self,conditionalAndExprList):
        if isinstance(conditionalAndExprList,list):
            self._list = conditionalAndExprList
        else:
            self._list = [conditionalAndExprList]

    def __repr__(self):
        return "<ConditionalExpressionList: %s>"%self._list

class ParsedRelationalExpressionList(ListRedirect):
    """
    A list of RelationalExpressions, joined by '&&'s
    """
    pyBooleanOperator = ' and '
    def __init__(self,relationalExprList):        
        if isinstance(relationalExprList,list):
            self._list = relationalExprList
        else:
            self._list = [relationalExprList]
    def __repr__(self):
        return "<RelationalExpressionList: %s>"%self._list

class ParsedPrefixedMultiplicativeExpressionList(ListRedirect):
    """
    A ParsedMultiplicativeExpressionList lead by a '+' or '-'
    """
    def __init__(self,prefix,mulExprList):
        self.prefix = prefix
        assert prefix != '-',"arithmetic '-' operator not supported"
        if isinstance(mulExprList,list):
            self._list = mulExprList
        else:
            self._list = [mulExprList]
    def __repr__(self):
        return "%s %s"%(self.prefix,self.reduce())

class ParsedMultiplicativeExpressionList(ListRedirect):
    """
    A list of UnaryExpressions, joined by '/' or '*' s
    """
    def __init__(self,unaryExprList):
        if isinstance(unaryExprList,list):
            self._list = unaryExprList
        else:
            self._list = [unaryExprList]
    def __repr__(self):
        #return "<MultiplicativeExpressionList: %s>"%self.reduce()
        return "<MultiplicativeExpressionList: %s>"%self._list

    def __eq__(self, other):
        return self._list == other._list
        

class ParsedAdditiveExpressionList(ListRedirect):
    """
    A list of MultiplicativeExpressions, joined by '+' or '-' s
    """
    def __init__(self,multiplicativeExprList):
        if isinstance(multiplicativeExprList,list):
            self._list = multiplicativeExprList
        else:
            self._list = [multiplicativeExprList]
    def __repr__(self):
        return "<AdditiveExpressionList: %s>"%self._list

    def __eq__(self, other):
        return self._list == other._list

class ParsedString(unicode):

    def __new__(cls, value=None):
        value = value is None and u"" or value
        return unicode.__new__(cls,value)


class ParsedDatatypedLiteral(object):
    """
    Placeholder for Datatyped literals
    This is neccessary (instead of instanciating Literals directly)
    when datatypes IRIRefs are QNames (in which case the prefix needs to be resolved at some point)
    """
    def __init__(self,value,dType):
        self.value = value
        self.dataType = dType

    def __repr__(self):
        return "'%s'^^%s"%(self.value,self.dataType)

    def __eq__(self, other):
        return (self.value == other.value and
                self.dataType == other.dataType)

# Filter

class ParsedFilter(object):
    def __init__(self,filter):
        self.filter = filter

    def __repr__(self):
        return "FILTER %s"%self.filter

class ParsedExpressionFilter(ParsedFilter):
    def __repr__(self):
        return "FILTER %s"%(isinstance(self.filter,ListRedirect) and self.filter.reduce() or self.filter)

class ParsedFunctionFilter(ParsedFilter):
    pass

# Functional Library

"""
[28] FunctionCall ::= IRIref ArgList
http://www.w3.org/TR/rdf-sparql-query/#evaluation
"""

STR         = 0
LANG        = 1
LANGMATCHES = 2
DATATYPE    = 3
BOUND       = 4
isIRI       = 5
isURI       = 6
isBLANK     = 7
isLITERAL   = 8
sameTERM    = 9

FUNCTION_NAMES = {
    STR : 'STR',
    LANG : 'LANG',
    LANGMATCHES : 'LANGMATCHES',
    DATATYPE : 'DATATYPE',
    BOUND : 'BOUND',
    isIRI : 'isIRI',
    isURI : 'isURI',
    isBLANK : 'isBLANK',
    isLITERAL : 'isLITERAL',
    sameTERM : 'sameTERM'
}

class FunctionCall(object):
    def __init__(self,name,arguments=None):
        self.name = name
        self.arguments = arguments is None and [] or arguments

    def __repr__(self):
        return "%s(%s)"%(self.name,','.join([isinstance(i,ListRedirect) and i.reduce() or i for i in self.arguments]))

class ParsedArgumentList(ListRedirect):
    def __init__(self,arguments):
        self._list = arguments

class ParsedREGEXInvocation(object):
    def __init__(self,arg1,arg2,arg3=None):
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def __repr__(self):
        return "REGEX(%s,%s%s)"%(
                                 isinstance(self.arg1,ListRedirect) and self.arg1.reduce() or self.arg1,
                                 isinstance(self.arg2,ListRedirect) and self.arg2.reduce() or self.arg2,
                                 isinstance(self.arg3,ListRedirect) and self.arg3.reduce() or self.arg3,)

class BuiltinFunctionCall(FunctionCall):
    def __init__(self,name,arg1,arg2=None):
        if arg2:
            arguments = [arg1,arg2]
        else:
            arguments = [arg1]
        super(BuiltinFunctionCall,self).__init__(name,arguments)

    def __repr__(self):
        #print self.name
        #print [type(i) for i in self.arguments]
        return "%s(%s)"%(FUNCTION_NAMES[self.name],','.join([isinstance(i,ListRedirect) and str(i.reduce()) or repr(i) for i in self.arguments]))

# Graph Pattern

"""
See: http://www.w3.org/TR/rdf-sparql-query/#GraphPattern
[20] GroupGraphPattern ::= '{' TriplesBlock? ( ( GraphPatternNotTriples | Filter ) '.'? TriplesBlock? )* '}'
[22] GraphPatternNotTriples ::= OptionalGraphPattern | GroupOrUnionGraphPattern | GraphGraphPattern
[26] Filter ::= 'FILTER' Constraint
[27] Constraint ::= BrackettedExpression | BuiltInCall | FunctionCall
[56] BrackettedExpression  ::= '(' ConditionalOrExpression ')'
[24] OptionalGraphPattern  ::=  'OPTIONAL' GroupGraphPattern
[25] GraphGraphPattern  ::=  'GRAPH' VarOrBlankNodeOrIRIref GroupGraphPattern
[26] GroupOrUnionGraphPattern ::=  GroupGraphPattern ( 'UNION' GroupGraphPattern )*
"""

class ParsedGroupGraphPattern(object):
    """
    See: http://www.w3.org/TR/rdf-sparql-query/#GroupPatterns
    A group graph pattern GP is a set of graph patterns, GPi.
    This class is defined to behave (literally) like a set of GraphPattern instances.
    """
    def __init__(self,triples,graphPatterns):
        self.triples=triples
        self._graphPatterns = graphPatterns
        _g=[]
        if triples:
            _g=[GraphPattern(triples=triples)]
        if graphPatterns:
            _g.extend(graphPatterns)
        self.graphPatterns = _g
        
    def __iter__(self):
        for g in self.graphPatterns:
            if isinstance(g,GraphPattern):
                if not g.triples and g.nonTripleGraphPattern is None:
                    continue
                else:
                    yield g
            else:
                yield GraphPattern(triples=self.triples)

    def __len__(self):
        return len([g for g in self.graphPatterns 
                    if isinstance(g,GraphPattern) and (g.triples or g.nonTripleGraphPattern) is not None])
    def __getitem__(self, k):
        return list(self.graphPatterns)[k]
    def __repr__(self):
        return "{ %s }"%repr(list(self))

class BlockOfTriples(object):
    """
    A Basic Graph Pattern is a set of Triple Patterns.
    """
    def __init__(self,statementList):
        self.statementList = statementList
    def __getattr__(self, attr):
        if hasattr(self.statementList, attr):
            return getattr(self.statementList, attr)
        raise AttributeError, '%s has no such attribute %s' % (repr(self), attr)
    def __repr__(self):
        return "<SPARQLParser.BasicGraphPattern: %s>"%repr(self.statementList)

class GraphPattern(object):
    """
    Complex graph patterns can be made by combining simpler graph patterns. The ways of creating graph patterns are:
    * Basic Graph Patterns, where a set of triple patterns must match
    * Group Graph Pattern, where a set of graph patterns must all match using the same variable substitution
    * Value constraints, which restrict RDF terms in a solution
    * Optional Graph patterns, where additional patterns may extend the solution
    * Alternative Graph Pattern, where two or more possible patterns are tried
    * Patterns on Named Graphs, where patterns are matched against named graphs

    ( GraphPatternNotTriples | Filter ) '.'? TriplesBlock?
    """
    def __init__(self,nonTripleGraphPattern=None,filter=None,triples=None):
        #print "GraphPattern(..)",triples,filter,nonTripleGraphPattern
        triples = triples and triples or []
        self.filter=filter
        self.triples = triples
        self.nonTripleGraphPattern = nonTripleGraphPattern

    def __repr__(self):
        if not self.triples and self.nonTripleGraphPattern is None:
            return "<SPARQLParser.EmptyGraphPattern>"
        elif self.triples and not self.nonTripleGraphPattern and not self.filter:
            return repr(self.triples)
        return "( %s '.'? %s )"%(
                    self.filter is not None and self.filter or self.nonTripleGraphPattern,
                    self.triples is not None and self.triples or '')        
        
#        return "<SPARQLParser.GraphPattern: %s%s>"%(
#                    self.triples is not None and self.triples or '',
#                    self.nonTripleGraphPattern is not None and ' %s'%self.nonTripleGraphPattern or '')

class ParsedOptionalGraphPattern(ParsedGroupGraphPattern):
    """
    An optional graph pattern is a combination of a pair of graph patterns.
    The second pattern modifies pattern solutions of the first pattern but
    does not fail matching of the overall optional graph pattern.
    """
    def __init__(self,groupGraphPattern):
        self.triples=groupGraphPattern.triples
        self.graphPatterns = groupGraphPattern.graphPatterns
#        
#        super(ParsedOptionalGraphPattern,self).__init__(triples,graphPatterns)

    def __repr__(self):
        if self.graphPatterns is not None:
            return "OPTIONAL {%s %s}"%(self.triples,self.graphPatterns)
        else:
            return "OPTIONAL {%s}"%self.triples

class ParsedAlternativeGraphPattern(object):
    """
    A union graph pattern is a set of group graph patterns GPi.
    A union graph pattern matches a graph G with solution S
    if there is some GPi such that GPi matches G with solution S.
    """
    def __init__(self,alternativePatterns):
        self.alternativePatterns = alternativePatterns
    def __repr__(self):
        return " UNION ".join(["{%s}"%g for g in self.alternativePatterns])
    def __iter__(self):
        for g in self.alternativePatterns:
            yield g
    def __len__(self):
        return len(self.alternativePatterns)

class ParsedGraphGraphPattern(ParsedGroupGraphPattern):
    """
    Patterns on Named Graphs, where patterns are matched against named graphs
    """
    def __init__(self,graphName,groupGraphPattern):
        self.name = graphName
        self.triples=groupGraphPattern.triples
        self.graphPatterns = groupGraphPattern.graphPatterns

    def __repr__(self):
        return "GRAPH %s { %s }"%(self.name,self.graphPatterns)

# IRIRef

"""
DatasetClause ::= 'FROM' ( IRIref | 'NAMED' IRIref )
See: http://www.w3.org/TR/rdf-sparql-query/#specifyingDataset

'A SPARQL query may specify the dataset to be used for matching.  The FROM clauses
give IRIs that the query processor can use to create the default graph and the
FROM NAMED clause can be used to specify named graphs. '
"""

class IRIRef(URIRef):
    pass

class RemoteGraph(URIRef):
    pass

class NamedGraph(IRIRef):
    pass

# Operators

class BinaryOperator(object):
    NAME = ''
    def __init__(self,left,right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "(%s %s %s)"%(
            isinstance(self.left,ListRedirect) and self.left.reduce() or self.left,
            self.NAME,
            isinstance(self.right,ListRedirect) and self.right.reduce() or self.right)

class EqualityOperator(BinaryOperator):
    NAME = '='

class NotEqualOperator(BinaryOperator):
    NAME = '!='

class LessThanOperator(BinaryOperator):
    NAME = '<'

class LessThanOrEqualOperator(BinaryOperator):
    NAME = '<='

class GreaterThanOperator(BinaryOperator):
    NAME = '>'

class GreaterThanOrEqualOperator(BinaryOperator):
    NAME = '>='

class UnaryOperator(object):
    NAME = ''
    def __init__(self,argument):
        self.argument = argument
    def __repr__(self):
        return "(%s %s)"%(
            self.NAME,
            isinstance(self.argument,ListRedirect) and self.argument.reduce() or self.argument)

class LogicalNegation(UnaryOperator):
    NAME = '!'

class NumericPositive(UnaryOperator):
    NAME = '+'

class NumericNegative(UnaryOperator):
    NAME = '-'        

# QName

class QName(Identifier):
    __slots__ = ("localname", "prefix")
    def __new__(cls,value):
        try:
            inst = unicode.__new__(cls,value)
        except UnicodeDecodeError:
            inst = unicode.__new__(cls,value,'utf-8')

        inst.prefix,inst.localname = value.split(':')
        return inst

class QNamePrefix(Identifier):
    def __init__(self,prefix):
        super(QNamePrefix,self).__init__(prefix)

# Query

class Query(object):
    """
    Query ::= Prolog ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery )
    See: http://www.w3.org/TR/rdf-sparql-query/#rQuery
    """
    def __init__(self,prolog,query):
        self.prolog = prolog
        self.query = query

    def __repr__(self):
        return repr(self.query)

class WhereClause(object):
    """
    The where clause is essentially a wrapper for an instance of a ParsedGraphPattern
    """
    def __init__(self,parsedGraphPattern):
        self.parsedGraphPattern = parsedGraphPattern

class RecurClause(object):
    def __init__(self, maps, parsedGraphPattern):
        self.maps = maps
        self.parsedGraphPattern = parsedGraphPattern

class SelectQuery(object):
    """
    SelectQuery ::= 'SELECT' 'DISTINCT'? ( Var+ | '*' ) DatasetClause* WhereClause RecurClause? SolutionModifier
    See: http://www.w3.org/TR/rdf-sparql-query/#rSelectQuery
    """
    def __init__(self, variables, dataSetList, whereClause,
                 recurClause, solutionModifier, distinct=None):
        self.variables = variables is not None and variables or []
        self.dataSets = dataSetList and dataSetList or []
        self.whereClause = whereClause
        self.solutionModifier = solutionModifier
        self.distinct = distinct is not None
        self.recurClause = recurClause

    def __repr__(self):
        return "SELECT %s %s %s %s %s"%(self.distinct and 'DISTINCT' or '',self.variables and self.variables or '*',self.dataSets,self.whereClause.parsedGraphPattern,self.solutionModifier and self.solutionModifier or '')

class AskQuery(object):
    """
    AskQuery ::= 'ASK' DatasetClause* WhereClause
    See: http://www.w3.org/TR/rdf-sparql-query/#rAskQuery
    """
    def __init__(self,dataSetList,whereClause):
        self.dataSets = dataSetList and dataSetList or []
        self.whereClause = whereClause

    def __repr__(self):
        return "ASK %s %s"%(self.dataSets,self.whereClause.parsedGraphPattern)

class ConstructQuery(object):
    """
    ConstructQuery ::= 'CONSTRUCT' ConstructTemplate DatasetClause* WhereClause SolutionModifier
    See: http://www.w3.org/TR/rdf-sparql-query/#rConstructQuery
    """
    def __init__(self,triples,dataSetList,whereClause,solutionModifier):
        self.triples = GraphPattern(triples=triples)
        self.dataSets = dataSetList and dataSetList or []
        self.whereClause = whereClause
        self.solutionModifier = solutionModifier

class DescribeQuery(object):
    """
    DescribeQuery ::= 'DESCRIBE' ( VarOrIRIref+ | '*' ) DatasetClause* WhereClause? SolutionModifier
    http://www.w3.org/TR/rdf-sparql-query/#rConstructQuery
    """
    def __init__(self,variables,dataSetList,whereClause,solutionModifier):
        self.describeVars = variables is not None and variables or []
        self.dataSets = dataSetList and dataSetList or []
        self.whereClause = whereClause
        self.solutionModifier = solutionModifier

    def __repr__(self):
        return "DESCRIBE %s %s %s %s"%(
                       self.describeVars,
                       self.dataSets,
                       self.whereClause.parsedGraphPattern,
                       self.solutionModifier)


class Prolog(object):
    """
    Prolog ::= BaseDecl? PrefixDecl*
    See: http://www.w3.org/TR/rdf-sparql-query/#rProlog
    """
    def __init__(self,baseDeclaration,prefixDeclarations):
        self.baseDeclaration = baseDeclaration
        # answerList and eagerLimit are used to enable
        # efficient LIMIT processing
        self.answerList = []
        self.eagerLimit = None
        self.extensionFunctions={}
        self.prefixBindings = {}
        if prefixDeclarations:
            for prefixBind in prefixDeclarations:
                if hasattr(prefixBind,'base'):
                    self.prefixBindings[prefixBind.qName] = prefixBind.base 

    def __repr__(self):
        return repr(self.prefixBindings)
    
# Resource

class RDFTerm(object):
    """
    Common class for RDF terms
    """

class Resource(RDFTerm):
    """
    Represents a sigle resource in a triple pattern.  It consists of an identifier
    (URIRef or BNode) and a list of rdflib.sparql.bison.Triples.PropertyValue instances
    """
    def __init__(self,identifier=None,propertyValueList=None):
        self.identifier = identifier is not None and identifier or BNode()
        self.propVals = propertyValueList is not None and propertyValueList or []

    def __repr__(self):
        resId = isinstance(self.identifier,BNode) and '_:'+self.identifier or self.identifier
        #print type(self.identifier)
        return "%s%s"%(resId,self.propVals and ' %s'%self.propVals or '')

    def extractPatterns(self) :
        for prop,objs in self.propVals:
            for obj in objs:
                yield (self.identifier,prop,obj)

    def __eq__(self, other):
        return (self.identifier == other.identifier and
                self.propVals == other.propVals)

class TwiceReferencedBlankNode(RDFTerm):
    """
    Represents BNode in triple patterns in this form:
    [ :prop1 :val1 ] :prop2 :val2
    """
    def __init__(self,props1,props2):
        self.identifier = BNode()
        self.propVals = list(set(props1+props2))

class ParsedCollection(ListRedirect,RDFTerm):
    """
    An RDF Collection
    """
    reducable = False
    def __init__(self,graphNodeList=None):
        self.propVals = []
        if graphNodeList:
            self._list = graphNodeList
            self.identifier = Variable(BNode())
        else:
            self._list = graphNodeList and graphNodeList or []
            self.identifier = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#nil')
        
    def setPropertyValueList(self,propertyValueList):
        self.propVals = propertyValueList
        
    def __repr__(self):
        return "<RDF Collection: %s>"%self._list
        
# Solution Modifier

ASCENDING_ORDER   = 1
DESCENDING_ORDER  = 2
UNSPECIFIED_ORDER = 3

ORDER_VALUE_MAPPING = {
    ASCENDING_ORDER   : 'Ascending',
    DESCENDING_ORDER  : 'Descending',
    UNSPECIFIED_ORDER : 'Default',
}

class SolutionModifier(object):
    def __init__(self,orderClause=None,limitClause=None,offsetClause=None):
        self.orderClause = orderClause
        self.limitClause = limitClause
        self.offsetClause = offsetClause

    def __repr__(self):
        if not(self.orderClause or self.limitClause or self.offsetClause):
            return ""
        return "<SoutionModifier:%s%s%s>"%(
            self.orderClause and  ' ORDER BY %s'%self.orderClause or '',
            self.limitClause and  ' LIMIT %s'%self.limitClause or '',
            self.offsetClause and ' OFFSET %s'%self.offsetClause or '')

class ParsedOrderConditionExpression(object):
    """
    A list of OrderConditions
    OrderCondition ::= (('ASC'|'DESC')BrackettedExpression )|(FunctionCall|Var|BrackettedExpression)
    """
    def __init__(self,expression,order):
        self.expression = expression
        self.order = order

    def __repr__(self):
        return "%s(%s)"%(ORDER_VALUE_MAPPING[self.order],self.expression.reduce())

# Triples

class PropertyValue(object):
    def __init__(self,property,objects):
        self.property = property
        self.objects = objects
        #print

    def __repr__(self):
        #return "%s %s"%(self.property,self.objects)
        return "%s: %s" % (repr(self.property), repr(self.objects))

    def __eq__(self, other):
        return (self.property == other.property and
                self.objects == other.objects)

class ParsedConstrainedTriples(object):
    """
    A list of Resources associated with a constraint
    """
    def __init__(self,triples,constraint):
        self.triples = triples
        self.constraint = constraint

    def __repr__(self):
        return "%s%s"%(self.triples,self.constraint and ' %s'%self.constraint or '')

