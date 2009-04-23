import rdflib
from rdflib.sparql.parser import parse
from rdflib.sparql.bison.Query import *
from rdflib.sparql.bison.QName import *
from rdflib.sparql.bison.GraphPattern import *
from rdflib.sparql.bison.Operators import *
from rdflib.sparql.bison.FunctionLibrary import *
from rdflib.sparql.bison.Util import ListRedirect
from rdflib.sparql.bison.Expression import *
from rdflib.term import Variable, Literal

printDepth = 0
depthPrintEnabled = False

def ResetDepth():
    printDepth = 0

def AddDepth():
    ChangeDepth(2)
    
def SubDepth():
    ChangeDepth(-2)

def ChangeDepth(change):
    global printDepth
    printDepth += change
    if printDepth < 0:
        printDepth = 0
    
def DepthPrint(str):
    global printDepth, depthPrintEnabled
    if not depthPrintEnabled:
        return 
    pad = ""
    for d in range(printDepth):
        pad += " " 
    print pad + str
    

def QueryStats(queryString, log, depthPrint = False):
    global depthPrintEnabled
    depthPrintEnabled = depthPrint
    
    log['queryString'] = queryString
    
    # use the SPARQL parser
    try:
        q = parse(queryString)
        log['ParseError'] = 0
    except Exception, e:
        print 'PARSE ERROR: %s' % e
        q = None
        log['ParseError'] = 1
        return False
    
    ResetDepth()
    GetQueryInfo(q, log)           
    return True

def PrintSyntaxTree(q):
    global depthPrintEnabled
    depthPrintEnabled = True
    log = {}
    ResetDepth()
    GetQueryInfo(q, log)               

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
    if isinstance(q.query, SelectQuery) and q.query.distinct:
        log['distinct'] = 1

    log['limit'] = 0 
    log['offset'] = 0
    log['order'] = 0
    
    vars = dict()
    
    if not isinstance(q.query, AskQuery):
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
    
    DepthPrint("%s"%(log['queryType']))
    
    if q.query.whereClause:
        GetQueryWhereInfo(q.query.whereClause.parsedGraphPattern,None,vars,log)
        
    if isinstance(q.query, SelectQuery):
        log['selectVars'] = len(q.query.variables)
    log['allVars'] = len(vars)
    if isinstance(q.query, SelectQuery) and len(q.query.variables) < 1:
        log['selectVars'] = len(vars) # SELECT *
    
def GetQueryWhereInfo(pat, context, vars, log):
    AddDepth()
    
    if isinstance(pat, ParsedGraphGraphPattern):
        if isinstance(pat.name, Variable):
            DepthPrint("GRAPH %s"%(pat.name))
            context = '?'
        else:
            DepthPrint("GRAPH")
            context = 'c'
        log['graph'] = log['graph'] + 1    
    elif isinstance(pat, ParsedAlternativeGraphPattern): # not a group
        log['union'] = log['union'] + 1
        DepthPrint("UNION")
        for a in pat.alternativePatterns:
            GetQueryWhereInfo(a, context, vars, log)    
    elif isinstance(pat, ParsedOptionalGraphPattern):
        log['optional'] = log['optional'] + 1    
        DepthPrint("OPTIONAL")
        for p in pat.graphPatterns:
            GetQueryWhereInfo(p, context, vars, log)
    elif isinstance(pat, ParsedGroupGraphPattern):
        log['group'] = log['group'] + 1
        DepthPrint("GROUP")
        for p in pat.graphPatterns:
            GetQueryWhereInfo(p, context, vars, log)
    elif isinstance(pat, GraphPattern):
        DepthPrint("BGP")
    else:
        print 'Unexpected type: %s' % pat
        raise Exception('Unexpected type: %s' % pat.type)
                        
    if isinstance(pat, GraphPattern):
        AddDepth()
        DepthPrint("{")
        AddDepth()
        for s in pat.triples:
            for p in s.propVals:
                for o in p.objects:
                    GetTripleInfo(s.identifier, p.property, o, context, vars, log)
        SubDepth()
        DepthPrint("}")
        if pat.filter:
            log['filter'] = log['filter'] + 1
            DepthPrint("FILTER")
            GetQueryFilterInfo(pat.filter.filter, log)
        SubDepth()
        
        if pat.nonTripleGraphPattern:
            GetQueryWhereInfo(pat.nonTripleGraphPattern, context, vars, log)
            
#    if not foundType:
#        print 'Unexpected type: %s' % pat.type
#        raise Exception('Unexpected type: %s' % pat.type)
    
    SubDepth()

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
        DepthPrint("(%s,%s,%s,%s)"%(s,p,o,context))
        quadPat = 'AP(%s,%s,%s,%s)' % (si,pi,oi,context)
        if not log.has_key(quadPat):
            log[quadPat] = 1
        else:
            log[quadPat] = log[quadPat] + 1
    else:
        DepthPrint("(%s,%s,%s)"%(s,p,o))
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

    AddDepth()
    
    if isinstance(filter, Variable):
        DepthPrint("Var: %s"%(filter))
        SubDepth()
        return
    if isinstance(filter, QName):
        DepthPrint("QName: %s"%(filter))
        SubDepth()
        return    
    if isinstance(filter, Literal):
        DepthPrint("Lit: %s"%(filter))
        SubDepth()
        return

    if isinstance(filter, BinaryOperator):
        op = 'OP-B' + filter.NAME
        DepthPrint("%s"%(op))
        GetQueryFilterInfo(filter.left, log)
        GetQueryFilterInfo(filter.right, log)
    if isinstance(filter, UnaryOperator):
        op = 'OP-U' + filter.NAME
        DepthPrint("%s"%(op))
        GetQueryFilterInfo(filter.argument, log)
    
    if isinstance(filter, ParsedREGEXInvocation):
        op = 'OP-REGEX'
        DepthPrint("%s"%(op))
        GetQueryFilterInfo(filter.arg1, log)
        GetQueryFilterInfo(filter.arg2, log)
        GetQueryFilterInfo(filter.arg3, log)
        
    if isinstance(filter, ParsedDatatypedLiteral):
        op = 'OP-TLit-' + filter.dataType
        DepthPrint("%s"%(op))
        
    if isinstance(filter, ListRedirect):
        if isinstance(filter, ParsedConditionalAndExpressionList):
            op = 'OP-OR'
        if isinstance(filter, ParsedRelationalExpressionList):
            op = 'OP-AND' 
        if isinstance(filter, ParsedPrefixedMultiplicativeExpressionList):
            op = 'OP' + filter.prefix
        DepthPrint("%s"%(op))
        for f in filter:
           GetQueryFilterInfo(f, log)
    if isinstance(filter, FunctionCall):
        if isinstance(filter, BuiltinFunctionCall):
            op = 'Func-' + FUNCTION_NAMES[filter.name]
        else:
            op = 'Func-' + filter.name
        DepthPrint("%s"%(op))
        for a in filter.arguments:
            GetQueryFilterInfo(a, log)
    
    SubDepth()
    
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
        
