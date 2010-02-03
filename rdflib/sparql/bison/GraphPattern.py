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

