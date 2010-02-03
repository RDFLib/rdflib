import rdflib
from rdflib.sparql.bison import Parse
from rdflib.sparql.bison.Query import *
from rdflib.sparql.bison.GraphPattern import *
from rdflib.sparql.bison.Operators import *
from rdflib.sparql.bison.FunctionLibrary import *
from rdflib.sparql.bison.Util import ListRedirect
from rdflib.sparql.bison.Expression import *
from rdflib.Variable import Variable
from rdflib.Literal import Literal

def QueryStats(queryString, log):
    
    log['queryString'] = queryString
    
    # use the SPARQL parser
    try:
        q = Parse(queryString)
        log['ParseError'] = 0
    except Exception, e:
        print 'PARSE ERROR: %s' % e
        q = None
        log['ParseError'] = 1
        return False
    
    GetQueryInfo(q, log)           
    return True

def GetQueryInfo(q,log):
    if isinstance(q.query, SelectQuery):
        log['queryType'] = 'Select'
    elif isinstance(q.query, AskQuery):
        log['queryType'] = 'Ask'
    elif isinstance(q.query, ConstructQuery):
        log['queryType'] = 'Construct'
    elif isinstance(q.query, DescribeQuery):
        log['queryType'] = 'Describe'
    
    log['distinct'] = 0
    if q.query.distinct:
        log['distinct'] = 1

    log['limit'] = 0 
    log['offset'] = 0
    log['order'] = 0
    
    vars = dict()
    
    if q.query.solutionModifier.limitClause:
        log['limit'] = 1 # q.query.solutionModifier.limitClause
    if q.query.solutionModifier.offsetClause:
        log['offset'] = 1 #q.query.solutionModifier.offsetClause
    if q.query.solutionModifier.orderClause:
        log['order'] = 1 #q.query.solutionModifier.orderClause
    
    log['triple'] = 0
    log['group'] = 0
    log['optional'] = 0
    log['union'] = 0
    log['graph'] = 0
    log['filter'] = 0
    
    # FROM?  FROM NAMED?
    
    if q.query.whereClause:
        GetQueryWhereInfo(q.query.whereClause.parsedGraphPattern,None,vars,log)
        
    log['selectVars'] = len(q.query.variables)
    log['allVars'] = len(vars)
    if len(q.query.variables) < 1:
        log['selectVars'] = len(vars) # SELECT *
    
def GetQueryWhereInfo(pat, context, vars, log):
    foundType = False
    
    if isinstance(pat, ParsedGraphGraphPattern):
        foundType = True
        if isinstance(pat.name, Variable):
            context = '?'
        else:
            context = 'c'
        log['graph'] = log['graph'] + 1
    
    if isinstance(pat, ParsedAlternativeGraphPattern): # not a group
        foundType = True
        log['union'] = log['union'] + 1
        for a in pat.alternativePatterns:
            GetQueryWhereInfo(a, context, vars, log)
    
    if isinstance(pat, ParsedOptionalGraphPattern):
        foundType = True
        log['optional'] = log['optional'] + 1
    
    if isinstance(pat, ParsedGroupGraphPattern):
        foundType = True
        log['group'] = log['group'] + 1
        for p in pat.graphPatterns:
            GetQueryWhereInfo(p, context, vars, log)
                
    if isinstance(pat, GraphPattern):
        foundType = True
        for s in pat.triples:
            for p in s.propVals:
                for o in p.objects:
                    GetTripleInfo(s.identifier, p.property, o, context, vars, log)
        if pat.nonTripleGraphPattern:
            GetQueryWhereInfo(pat.nonTripleGraphPattern, context, vars, log)
        if pat.filter:
            log['filter'] = log['filter'] + 1
            GetQueryFilterInfo(pat.filter.filter, log)
            
    if not foundType:
        print 'Unexpected type: %s' % pat.type
        raise Exception('Unexpected type: %s' % pat.type)
 

def GetTripleInfo(s,p,o,context,vars,log):
    log['triple'] = log['triple'] + 1
    si = 's'
    pi = 'p'
    oi = 'o'
    if isinstance(s, Variable):
        si = '?'
        GetVarInfo(s, vars)
    if isinstance(p, Variable):
        pi = '?'        
        GetVarInfo(p, vars)
    if isinstance(o, Variable):
        oi = '?'
        GetVarInfo(o, vars)
    
    if context:
        quadPat = 'AP(%s,%s,%s,%s)' % (si,pi,oi,context)
        if not log.has_key(quadPat):
            log[quadPat] = 1
        else:
            log[quadPat] = log[quadPat] + 1
    else:
        triplePat = 'AP(%s,%s,%s)' % (si,pi,oi)    
        if not log.has_key(triplePat):
            log[triplePat] = 1
        else:
            log[triplePat] = log[triplePat] + 1

def GetVarInfo(v, vars):
    if not vars.has_key(v):
        vars[v] = 1
    else:
        vars[v] = vars[v] + 1
        
def GetQueryFilterInfo(filter, log):
    op = None
    if filter == None:
        return
    if isinstance(filter, Variable):
        return
    if isinstance(filter, Literal):
        return

    if isinstance(filter, BinaryOperator):
        op = 'OP-B' + filter.NAME
        GetQueryFilterInfo(filter.left, log)
        GetQueryFilterInfo(filter.right, log)
    if isinstance(filter, UnaryOperator):
        op = 'OP-U' + filter.NAME
        GetQueryFilterInfo(filter.argument, log)
    
    if isinstance(filter, ParsedREGEXInvocation):
        op = 'OP-REGEX'
        GetQueryFilterInfo(filter.arg1, log)
        GetQueryFilterInfo(filter.arg2, log)
        GetQueryFilterInfo(filter.arg3, log)
        
    if isinstance(filter, ParsedDatatypedLiteral):
        op = 'OP-TLit-' + filter.dataType
        
    if isinstance(filter, ListRedirect):
        for f in filter:
           GetQueryFilterInfo(f, log)
        if isinstance(filter, ParsedConditionalAndExpressionList):
            op = 'OP-OR'
        if isinstance(filter, ParsedRelationalExpressionList):
            op = 'OP-AND' 
        if isinstance(filter, ParsedPrefixedMultiplicativeExpressionList):
            op = 'OP' + filter.prefix
                        
    if not op:
        print 'Unknown filter operator: %s' % filter
        raise Exception('Unknown filter operator: %s' % filter)
        
    if not log.has_key(op):
        log[op] = 1
    else:
        log[op] = log[op] + 1
    
def GetQueryStats(queryEntries):
    colDict = dict()
    cols = []
    entries = []
    entryCount = 0
    distinctQueries = dict()
    for log in queryEntries:
        entryCount = entryCount + 1
        #print "=== Entry %s (%s) ===" % (entryCount, log['lineNum'])
        if QueryStats(log['queryString'], log):
            if not distinctQueries.has_key(log['queryString'].strip()):
                distinctQueries[log['queryString'].strip()] = len(distinctQueries) + 1
            
            log['queryNum'] = distinctQueries[log['queryString'].strip()]
            entries.append(log)
            # get column names
            for k in log:
                if not colDict.has_key(k):
                    colDict[k] = k
                    cols.append(k)
    
    cols.sort()
    return (cols, entries)
