### Utilities for performing preprocessing (flattening and reordering) of Group Graph Patterns
from sets import Set
from GraphPattern import ParsedAlternativeGraphPattern,ParsedOptionalGraphPattern,ParsedGraphGraphPattern,ParsedGroupGraphPattern
from Triples import ParsedConstrainedTriples

def flattenGroupGraphPattern(groupGraphPattern):
    """
    Recursively 'Flattens' nested Group Graph Patterns using the reduction below
    { patternA { patternB } } => { patternA. patternB }
    """
    for g in groupGraphPattern:
        if g.nonTripleGraphPattern:
            if isinstance(g.nonTripleGraphPattern,ParsedAlternativeGraphPattern):
                #It's a union graph pattern, flatten each group graph pattern
                g.nonTripleGraphPattern.alternativePatterns \
                    = Set([ParsedGroupGraphPattern(list(flattenGroupGraphPattern(gGP))) for gGP in g.nonTripleGraphPattern])
                yield g
            elif isinstance(g.nonTripleGraphPattern,ParsedOptionalGraphPattern):
                #A parsed optional group graph pattern, flatten it (in place)
                g.nonTripleGraphPattern.graphPatterns = \
                    Set(flattenGroupGraphPattern(g.nonTripleGraphPattern))
                yield g
            elif isinstance(g.nonTripleGraphPattern,ParsedGraphGraphPattern):
                #A graph graph patten, flatten it (in place)
                g.nonTripleGraphPattern.graphPatterns = \
                    Set(flattenGroupGraphPattern(g.nonTripleGraphPattern))
                yield g
            else:
                #It's a nested Group Graph Patter, flatten it into
                for g in flattenGroupGraphPattern(g.nonTripleGraphPattern):
                    yield g
        else:
            #It's a Basic Graph Patternr
            yield g

def reorderBasicGraphPattern(filteredBasicGraphPattern):
    """
    Takes a list of Triples (nested lists or ParsedConstrainedTriples),
    collects the constraints, and returns the TriplePatterns and a list of global constraints
    """
    triplePatterns = []
    constraints = []
    #print "Reordering Basic Graph Pattern: ", filteredBasicGraphPattern
    for tripleList in filteredBasicGraphPattern.triples:
        #print type(tripleList)
        if isinstance(tripleList,ParsedConstrainedTriples):
            if tripleList.triples:
                triplePatterns.extend(tripleList.triples)
            constraints.append(tripleList.constraint)
        else:
            for item in tripleList:
                if isinstance(item,ParsedConstrainedTriples):
                    if item.triples:
                        triplePatterns.extend(item.triples)
                    constraints.append(item.constraint)
                else:
                    triplePatterns.append(item)
    #print "Results: ",triplePatterns,constraints
    return triplePatterns,constraints

def reorderGroupGraphPattern(groupGraphPattern):
    """
    Recursively reorders Group Graph Patterns by shifting BasicGraphPatterns to the front

    { basicGraphPatternA OPTIONAL { .. } basicGraphPatternB }
      =>
    { basicGraphPatternA+B OPTIONAL { .. }}
    """
    #print "Reordering: ", groupGraphPattern
    firstGraphPattern = groupGraphPattern[0]
    otherGraphPatterns = len(groupGraphPattern) > 1 and groupGraphPattern[1:] or []
    reorderCandidates = []
    prunedGraphPatterns = []
    #Iterate through the GP2,GP3,... removing their triples to merge into GP1
    for g in otherGraphPatterns:
        if g.nonTripleGraphPattern:
            if isinstance(g.nonTripleGraphPattern,(ParsedGroupGraphPattern)):
                #Group Graph Patterns should be reordered 'in=place'
                g.nonTripleGraphPattern = reorderGroupGraphPattern(g.nonTripleGraphPattern)
            elif isinstance(g.nonTripleGraphPattern,ParsedAlternativeGraphPattern):
                #Each Group Graph Pattern in a Alternative graph pattern should be reordered in-place
                g.nonTripleGraphPattern.alternativePatterns \
                    = Set([ParsedGroupGraphPattern(list(flattenGroupGraphPattern(gGP))) for gGP in g.nonTripleGraphPattern])
        #Tally up the Basic Graph Patterns
        reorderCandidates.append(g.triples)
        #Remove them from their source
        g.triples = []
        #Tally up the remaining non-triple graph patterns
        prunedGraphPatterns.append(g)

    firstGraphPattern.triples.extend(reorderCandidates)
    rt=type(groupGraphPattern)(ParsedGroupGraphPattern([firstGraphPattern]+prunedGraphPatterns))
    #print "Reordered to ", rt
    return rt

