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

class ParsedGroupGraphPattern(object):
    """
    See: http://www.w3.org/TR/rdf-sparql-query/#GroupPatterns
    A group graph pattern GP is a set of graph patterns, GPi.
    This class is defined to behave (literally) like a set of GraphPattern instances.
    """
    def __init__(self,graphPatterns):    
        self.graphPatterns = graphPatterns
    def __iter__(self):
        for g in self.graphPatterns:
            if not g.triples and g.nonTripleGraphPattern is None:
                continue
            else:
                yield g
    def __len__(self):
        return len([g for g in self.graphPatterns if g.triples or g.nonTripleGraphPattern is not None])
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
    
    This class is defined as a direct analogy of Grammar rule [20]:
s    """
    def __init__(self,triples,nonTripleGraphPattern=None):
        triples = triples and triples or []
        self.triples = triples
        self.nonTripleGraphPattern = nonTripleGraphPattern

    def __repr__(self):
        if not self.triples and self.nonTripleGraphPattern is None:
            return "<SPARQLParser.EmptyGraphPattern>"
        return "<SPARQLParser.GraphPattern: %s%s>"%(
                    self.triples is not None and self.triples or '',
                    self.nonTripleGraphPattern is not None and ' %s'%self.nonTripleGraphPattern or '')
        
class ParsedOptionalGraphPattern(ParsedGroupGraphPattern):
    """
    An optional graph pattern is a combination of a pair of graph patterns.
    The second pattern modifies pattern solutions of the first pattern but 
    does not fail matching of the overall optional graph pattern.
    """
    def __init__(self,groupGraphPattern):    
        super(ParsedOptionalGraphPattern,self).__init__(groupGraphPattern.graphPatterns)
        
    def __repr__(self):
        return "OPTIONAL {%s}"%self.graphPatterns
    
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
        super(ParsedGraphGraphPattern,self).__init__(groupGraphPattern.graphPatterns)
        
    def __repr__(self):
        return "GRAPH %s { %s }"%(self.name,self.graphPatterns)
        
    