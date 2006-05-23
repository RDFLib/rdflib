#from rdflib.sparql.graphPattern import GraphPattern as GraphPatternImpl
#from rdflib.sparql.sparql import SPARQL as SPARQLImpl
"""
See: http://www.w3.org/TR/rdf-sparql-query/#GraphPattern
[20] GraphPattern ::=  FilteredBasicGraphPattern ( GraphPatternNotTriples '.'? GraphPattern )?
[21] FilteredBasicGraphPattern ::= BlockOfTriples? ( Constraint '.'? FilteredBasicGraphPattern )?
[23] GraphPatternNotTriples  ::=  OptionalGraphPattern | GroupOrUnionGraphPattern | GraphGraphPattern
[24] OptionalGraphPattern  ::=  'OPTIONAL' GroupGraphPattern
[25] GraphGraphPattern  ::=  'GRAPH' VarOrBlankNodeOrIRIref GroupGraphPattern
[26] GroupOrUnionGraphPattern ::=  GroupGraphPattern ( 'UNION' GroupGraphPattern )*
[27] Constraint ::= 'FILTER' ( BrackettedExpression | BuiltInCall | FunctionCall )
"""

class ParsedGraphPattern(object):
    def __init__(self,graphPatterns):
        self.graphPatterns = graphPatterns
    def __repr__(self):
        return repr(self.graphPatterns)
    
class BlockOfTriples(object):
    def __init__(self,statementList):
        self.statementList = statementList
    def __repr__(self):
        return "<SPARQLParser.BasicGraphPattern: %s>"%repr(self.statementList)
    
class GraphPattern(object):
    def __init__(self,triples,nonTripleGraphPattern=None):
        triples = triples and triples or []
        #print nonTripleGraphPattern,graphPattern
        self.triples = triples
        self.nonTripleGraphPattern = nonTripleGraphPattern

    def __repr__(self):
        if not self.triples and self.nonTripleGraphPattern is None:
            return "<SPARQLParser.EmptyGraphPattern>"
        return "<SPARQLParser.GraphPattern: %s%s>"%(
                    self.triples is not None and self.triples or '',
                    self.nonTripleGraphPattern is not None and ' %s'%self.nonTripleGraphPattern or '')
        
class ParsedOptionalGraphPattern(object):
    """
    Optional Graph patterns, where additional patterns may extend the solution
    """
    def __init__(self,graphPatterns):    
        self.graphPatterns = graphPatterns
        
    def __repr__(self):
        return "OPTIONAL {%s}"%self.graphPatterns
    
class ParsedAlternativeGraphPattern(object):
    """
    Alternative Graph Pattern, where two or more possible patterns are tried
    """
    def __init__(self,startPattern,alternativePatterns):
        print alternativePatterns, startPattern
        self.alternativePatterns  = alternativePatterns
        self.startPattern = startPattern
    def __repr__(self):
        return " UNION ".join(["{%s}"%g for g in [self.startPattern]+self.alternativePatterns])
    
class ParsedGraphGraphPattern(object):
    """
    Patterns on Named Graphs, where patterns are matched against named graphs
    """
    def __init__(self,graphName,groupGraphPattern):
        self.name = graphName
        self.graphPattern = groupGraphPattern
    def __repr__(self):
        return "GRAPH %s { %s }"%(self.name,self.graphPattern)
        
    