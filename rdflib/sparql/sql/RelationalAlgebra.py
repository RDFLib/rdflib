from rdflib.graph import Graph, ReadOnlyGraphAggregate, ConjunctiveGraph
import rdflib, time, math
from rdflib.sparql.bison.Query import *
from rdflib.sparql.bison.GraphPattern import *
from rdflib.sparql.bison.Operators import *
from rdflib.sparql.bison.FunctionLibrary import *
from rdflib.sparql.bison.Util import ListRedirect
from rdflib.sparql.bison.Expression import *
from rdflib.sparql.bison.Resource import Resource
from rdflib.sparql.bison.QName import *
from rdflib.sparql.bison.IRIRef import NamedGraph,RemoteGraph
from rdflib.term import URIRef, Variable, Literal, BNode
from rdflib.sparql.bison.SolutionModifier import ASCENDING_ORDER
from rdflib.sparql.bison.SPARQLEvaluate import unRollTripleItems
from rdflib import plugin, exceptions
from rdflib.sparql.QueryResult import SPARQLQueryResult
from collections import deque
from RdfSqlBuilder import *
from SqlBuilder import *
from RelationalOperators import RelationalTerminalExpOperator, RelationalExpOperator, \
                                RelationalOperator, NoResultsException
from QueryCostEstimator import EST_METHOD_STOCKER, EST_METHOD_HARTH, \
                               EST_METHOD_SMALL, EST_METHOD_MEDIUM, \
                               EST_METHOD_LARGE, QuerySelection, ColDistMax
from rdflib.sparql.sql.QueryStats import PrintSyntaxTree

def TopEvaluate(query,
                graph,
                passedBindings = None,
                DEBUG=False,
                exportTree=False,
                dataSetBase=None,
                extensionFunctions={},
                optimizations = DEFAULT_OPT_FLAGS):
    """ 
    THIS IS THE MAIN INTERFACE FUNCTION FOR THE SPARQL-TO-SQL IMPLEMENTATION!
    
    Converts the parsed SPARQL query syntax tree into
    an SQL query and evaluates the SQL query to obtain the results. 
    """
    #Setup prolog for subsequent use
    prolog = query.prolog    
    if query.prolog:
        query.prolog.DEBUG = DEBUG    
    
    sb = RdfSqlBuilder(graph, optimizations=optimizations)
    
    for var,term in passedBindings.items():
        sb.AddVariableBinding(var, term)
        
    try:
        if DEBUG:
            print "  Syntax Tree: "
            PrintSyntaxTree(query)
        
        # walk parse tree & build SQL
        root = ParseQuery(query,sb)
        
        if DEBUG:
            print "  RelTree: " + repr(root) # for debugging

        root.GenSql(sb)        
                
        # generate SQL & execute
        sql = sb.Sql()
        params = sb.Params()
        if DEBUG:
            print "  SQL: " + sql%params
    
        cols = root.Columns()  
        allVars = list(root.GetUsedVariables(sb, includeBNodes=True))
                
        queryInfo = {}  
        selection = []      
        for r in ExecuteSqlQuery(graph, sql, params, cols, queryInfo, sb):
            selection.append(r)

        nestedQueries = sb.rootBuilder.nestedQueries
        sqlQueries = [sql%params]
        elapsed = queryInfo['elapsed']
        joinOrderings = sb.rootBuilder.joinOrdering
        joinOrderTime = sb.rootBuilder.joinOrderTime
        joinEstimatedCost = sb.rootBuilder.joinEstimatedCost
        joinOrders = sb.rootBuilder.joinOrders
        joinEstimatedCostSum = sb.rootBuilder.joinEstimatedCostSum
        graph.resultMetadata = (nestedQueries,
                                sqlQueries,
                                elapsed,
                                joinOrderings,
                                joinOrderTime,
                                joinEstimatedCost,
                                joinOrders,
                                joinEstimatedCostSum)

        if isinstance(root,RelAskQuery):
            return bool(r)
        elif isinstance(root, RelSelectQuery):
            orderBy = root.orderBy
            distinct = root.distinct
        else:
            #TODO: implement other query types (DESCRIBE, CONSTRUCT, ASK)
            orderBy = None
            distinct = None
            #topUnion = None
            raise NotImplementedError()

        # prepare result        
        #Some extra metadata for performance stats
        return (selection, cols, allVars, orderBy, distinct, None)

        #return sparqlResult

    except NoResultsException:
        # no results are possible
        return ([], [], [], [], None, None)
        #res = plugin.get('SPARQLQueryResult',QueryResult)(
        #       [], [], [], [], None, None)
        #res.Failure = True
        #return res        


def ExecuteSqlQuery(graph, sql, params, columns, queryInfo, sqlBuilder):
    startTime = time.time()
    cursor = graph.store._db.cursor()
    rc = cursor.execute(sql, params)
    queryInfo['elapsed'] = time.time()-startTime
    if sqlBuilder.isAsk:
        for r in cursor.fetchall()[0]:
            yield r
        return
    
    # Grab a row from the big solving query, process it, and yield the
    # result, until there are no more results.
    row = cursor.fetchone()
    #TODO: get mapping of variables to columns
    columnMap = {}
    k = 0
    for d in cursor.description:
        columnMap[sqlBuilder.GetAliasForColumn(d[0])] = k
        k += 1
        
        
    while row:
        new_row = ProcessRow(columns, columnMap, graph.store.dataTypes, row)
        yield new_row

        row = cursor.fetchone()
    cursor.close()
    return
    
def GetDataTypes(store):
    #TODO: move this someplace else, probably into the store itself!
    # get data type identifier strings, make available via graph object
    dataTypeNames = {}
    startTime = time.time()
    cursor = store._db.cursor()
    cursor.execute(""" 
        SELECT DISTINCT i.id, i.lexical
        FROM %s lp INNER JOIN 
            %s i ON lp.data_type = i.id;""" %(store.literalProperties, store.idHash))
    for (id,text) in cursor.fetchall():
        dataTypeNames[id] = text
    #store.dataTypes = dataTypeNames
    elapsed = time.time()-startTime
    print "  Found %s data types used by this graph in %s s."%(len(dataTypeNames),elapsed)

    return dataTypeNames
    
    
def ProcessRow(variable_columns, columnMap, dataTypeNames, row):
    #Based on code from MySQL.py (see batch_unify())

    # Unwrap the elements of `variable_columns`, which provide the
    # original SPARQL variable names and the corresponding SQL column
    # names and management information.  Then map these SPARQL
    # variable names to the correct RDFLib node objects, using the
    # lexical information obtained using the query above.
    new_row = []
    for varname in variable_columns:
        column_name = varname #BE: treating varnames as columns for now...
        aVariable = Variable(varname)
        lexical = row[columnMap[column_name]] # prepared_map[column_name]
        term = row[columnMap[column_name + '_term']] #row_map[column_name + '_term']
    
        if lexical is None or term is None: # optional variable, not bound!
            node = None
        elif 'L' == term:
            datatype = None
            if columnMap.has_key(column_name + '_data_type'):
                datatype = row[columnMap[column_name + '_data_type']]
            if datatype:
                if dataTypeNames != None and dataTypeNames.has_key(datatype):
                    datatype = dataTypeNames[datatype] # convert from hash to lexical string
                datatype = URIRef(datatype)
            language = None
            if columnMap.has_key(column_name + '_language'):
                language = row[columnMap[column_name + '_language']]
            node = Literal(lexical, datatype=datatype, lang=language)
        elif 'B' == term:
            node = BNode(lexical)
        elif 'U' == term:
            node = URIRef(lexical)
        else:
            raise ValueError('Unknown term type %s'%term)
    
        #new_row[aVariable] = node
        new_row.append(node)
    
    if len(new_row) < 1:
        return tuple(new_row) # no columns!!
    if len(new_row) < 2:
        return new_row[0]
    return tuple(new_row)

def ParseQuery(q,sb):
    
    # process query prolog
    if q.prolog:
        if q.prolog.baseDeclaration:
            sb.baseDeclaration = q.prolog.baseDeclaration
        if q.prolog.prefixBindings:
            for pre in q.prolog.prefixBindings:
                sb.prefixBindings[pre] = q.prolog.prefixBindings[pre]
        
    if isinstance(q.query, SelectQuery):
        pq = ParseSelect(q.query,sb)
    elif isinstance(q.query, AskQuery):
        pq = ParseAsk(q.query,sb)
        sb.isAsk=True
#    elif isinstance(q.query, ConstructQuery):
#        pq = ParseConstruct(q.query)
#    elif isinstance(q.query, DescribeQuery):
#        pq = ParseDescribe(q.query)
    else:
        raise Exception("Unexpected type: %s"%(q.query))
    
    # process query prolog
    if q.prolog:
        if q.prolog.baseDeclaration:
            pq.baseDeclaration = q.prolog.baseDeclaration
        if q.prolog.prefixBindings:
            for pre in q.prolog.prefixBindings:
                pq.prefixBindings[pre] = q.prolog.prefixBindings[pre]
        
    return pq

def ParseAsk(query,prolog):
    sel = RelAskQuery()
    if len(query.dataSets) > 0:
        for d in query.dataSets:
            if isinstance(d, RemoteGraph):
                sel.fromList.append(str(d))
            elif isinstance(d, NamedGraph):
                sel.fromNamedList.append(str(d))
            else:
                raise NotImplementedError()            
    
    sel.pattern = ParseGraphPatternSimple(query.whereClause.parsedGraphPattern,prolog)

    return sel

def ParseSelect(query,prolog):
    sel = RelSelectQuery()
    
    if query.distinct:
        sel.distinct = True
        
    if query.solutionModifier.limitClause:
        sel.limit = int(query.solutionModifier.limitClause)
        
    if query.solutionModifier.offsetClause:
        sel.offset = int(query.solutionModifier.offsetClause)
        
    if query.solutionModifier.orderClause:
        sel.orderBy = []
        sel.orderAsc = []
        for orderCond in query.solutionModifier.orderClause:
            # is it a variable?
            if isinstance(orderCond,Variable):
                sel.orderBy.append(orderCond)
                sel.orderAsc.append(ASCENDING_ORDER)
            # is it another expression, only variables are supported
            else:
                expr = orderCond.expression
                assert isinstance(expr,Variable),\
                    "Support for ORDER BY with anything other than a variable is not supported: %s"%expr
                sel.orderBy.append(expr)                    
                sel.orderAsc.append(orderCond.order == ASCENDING_ORDER)
           
    if query.variables:
        for v in query.variables:
            sel.selectVariables.append(v)            

    if len(query.dataSets) > 0:
        for d in query.dataSets:
            if isinstance(d, RemoteGraph):
                sel.fromList.append(str(d))
            elif isinstance(d, NamedGraph):
                sel.fromNamedList.append(str(d))
            else:
                raise NotImplementedError()            
    
    sel.pattern = ParseGraphPatternSimple(query.whereClause.parsedGraphPattern,prolog)

    return sel

class RelQuery(RelationalOperator):
    
    def __init__(self):
        self.parent = None
        self.prefixBindings = {}
        self.baseDeclaration = None
        
    def Columns(self):
        return []
    
class RelSelectQuery(RelQuery):
    
    def __init__(self):
        RelQuery.__init__(self) 
        self.selectVariables = []
        self.distinct = False
        self.pattern = None
        self.orderBy = None
        self.orderAsc = None
        self.limit = None
        self.offset = 0
        self.fromList = []
        self.fromNamedList = []
    
    def __repr__(self):
        r = "SELECT"
        if self.distinct:
            r += " DISTINCT"
        r += " " + ", ".join(self.selectVariables)
        r += " " + repr(self.pattern)
        if self.orderBy:
            orderList = []
            for i in range(len(self.orderBy)):
                if self.orderAsc[i]:
                    orderList.append(repr(self.orderBy[i]))
                else:
                    orderList.append(repr(self.orderBy[i]) + " DESC")
            r += " ORDER BY " + ", ".join(orderList)
        if self.limit:
            r += " LIMIT %s"%(self.limit)
        if self.offset:
            r += " OFFSET %s"%(self.offset)
            
        return r
    
    def GetChildren(self):
        return [self.pattern]
    
    def Columns(self):
        return self.selectVariables
    
    def BuildSql(self, sqlBuilder, isNested):
        #NOTE: this step should never be flattened with the subquery built in BuildRootSql
        #      is that might result in too many JOINs for MySQL (>61) on complex queries.   
        #      This is a nested query BY DESIGN!
                
        # add namespace bindings
        if self.baseDeclaration:
            sqlBuilder.SetBaseDeclaration(self.baseDeclaration)
        
        # FROM and FROM NAMED
        if len(self.fromList) > 0:
            for f in self.fromList:
                sqlBuilder.AddFrom(f)
        if len(self.fromNamedList) > 0:            
            for f in self.fromNamedList:
                sqlBuilder.AddFromNamed(f)
        
        #NOTE: RDFLib's Literal table uses a case-insensitive collation!
        #      Moved DISTINCT to inner query where everything is a string hash instead!
#        # DISTINCT
#        if self.distinct:
#            sqlBuilder.SetDistinct(True)
          
        # set output fields
        if len(self.selectVariables) < 1:
            # treat as SELECT *, add all variables
            # we should have been passed all variables at this point from sub-queries
            vars = self.GetUsedVariables(sqlBuilder, includeBNodes=False) # don't return BNodes with SELECT *
            for v in vars: #sqlBuilder.GetAvailableVariables():
                self.selectVariables.append(v)
                
        #OPTIMIZE: set required variables to that need to be provided by child queries
        if sqlBuilder.UseOptimization(OPT_C6_PROJECT_EARLY):
            for vname in self.selectVariables:
                sqlBuilder.SetRequiredVariable(vname)
            if self.orderBy != None:
                for vname in self.orderBy:
                    sqlBuilder.SetRequiredVariable(vname)
                
        # build query for user that returns strings
        childBuilder = sqlBuilder.GetNestedSQLBuilder()
        self.BuildRootSql(childBuilder)
        mainTT = sqlBuilder.AddNestedTableTuple(childBuilder.Sql(),"main")
        sqlBuilder.AddChildVariables(childBuilder, mainTT)
        
        # add joins with literals/identifiers tables -- select & order by variables!
        orderByTerms = {} # keep track of SQL expression to use for vars in ORDER BY clause
        for vname in self.selectVariables:
            vars = sqlBuilder.GetAvailableVariable(vname)
            if vars != None and len(vars) > 0:
                var = vars[0] # there will be only 1
            else:
                var = EmptyVar(vname) # undefined variable, treat as NULL!
            orderByTerms[vname] = sqlBuilder.AddStringJoin(var, vname)
        # add string joins for ORDER BY variables not in SELECT
        if self.orderBy != None:
            for vname in (set(self.orderBy) - set(self.selectVariables)):
                vars = sqlBuilder.GetAvailableVariable(vname)
                if vars != None and len(vars) > 0:
                    var = vars[0] # there will be only 1
                else:
                    var = EmptyVar(vname) # undefined variable, treat as NULL!
                orderByTerms[vname] = sqlBuilder.AddStringJoin(var, vname, addOutput=False)
                                 
        # pass through term type & literal fields
        sqlBuilder.AddTermAndLiteralFields(self.selectVariables, outputVar=False)
                  
        #NOTE: order by MUST be implemented here to ensure correct string ordering!  
        # order by
        if self.orderBy:
            for i in range(len(self.orderBy)):
                sqlExp = orderByTerms[self.orderBy[i]]
                if self.orderAsc[i]:
                    sqlBuilder.AddOrderBy(sqlExp)
                else:
                    sqlBuilder.AddOrderBy(sqlExp, True)
        
        # offset
        if self.offset:
            sqlBuilder.SetOffset(self.offset)
        
        # limit
        if self.limit:
            sqlBuilder.SetLimit(self.limit)

        return self.selectVariables # don't need to return variables from main query

        
    def ProjectVariableList(self, sqlBuilder):
        selectVars = []
        returnVars = sqlBuilder.GetReturnedVariables()
        for vname in returnVars:
            found = False
            for v in self.selectVariables:
                if str(v) == vname:
                    found = True
                    break
            if found:
                selectVars.append(vname)
        return selectVars
        
    def BuildRootSql(self,sqlBuilder):
        # build the actual query, which returns ID's
        
        if sqlBuilder.UseOptimization(OPT_FLAT_SELECT) or sqlBuilder.UseOptimization(OPT_FLATTEN):
            # flatten by reusing the same builder for child pattern
            self.pattern.BuildSql(sqlBuilder, False)
        else:            
            # add child graph pattern as nested table
            (tt,childBuilder) = self.AddNestedOp(sqlBuilder, self.pattern, "sel")
                                          
        #NOTE: this query is always nested and thus must always set output
        # add variable outputs, term type & literal fields     
        fields = set(self.selectVariables)
        if self.orderBy != None:
            fields = fields | set(self.orderBy)
        sqlBuilder.AddTermAndLiteralFields(list(fields))
        
        #NOTE: this is here to avoid case-insensitivity issues 
        # DISTINCT
        if self.distinct:
            sqlBuilder.SetDistinct(True)

         
        return self.selectVariables # don't need to return variables from main query   

    def GetUsedVariables(self, sqlBuilder, includeBNodes=True):
        s = set()
        for v in self.selectVariables:
            s.add(v) #.lower()) #BE: currently assuming variables are not case-sensitive
        return s | self.pattern.GetUsedVariables(sqlBuilder, includeBNodes)
                    
class RelAskQuery(RelSelectQuery):
    def __init__(self):
        RelSelectQuery.__init__(self)
        self.isAsk=False
 
    def __repr__(self):
        r = "ASK"
        r += " " + repr(self.pattern)
        return r

def ParseGraphPattern(gp, bgpParent,prolog):
    p = None
    makeBgpChild = False # 
    if isinstance(gp, ParsedGraphGraphPattern):
        p = ParseGraph(gp,prolog)    
    elif isinstance(gp, ParsedAlternativeGraphPattern): # not a group
        p = ParseUnion(gp,prolog)
    elif isinstance(gp, ParsedOptionalGraphPattern):
        p = ParseOptional(gp,prolog)
        makeBgpChild = True
        # in the parse tree we have BGP(triples,OPTIONAL(...)), but for the
        # evaluation of OPTIONAL, we want OPTIONAL(BGP(triples),...) 
        # so we can turn it into an OUTER JOIN properly
        if p != None and bgpParent:
            # this handles the case where the required pattern is in the triple list of the same BGP node
            p.requiredPattern = bgpParent
    elif isinstance(gp, ParsedGroupGraphPattern):
        p = ParseGroup(gp,prolog)
    elif isinstance(gp, GraphPattern):
        p = ParseBGP(gp,prolog)
    else:
        raise Exception("Unexpected type: %s"%(gp))

    filter = None
    if isinstance(gp, GraphPattern) and gp.filter:
        # convert ... to FILTER(...)
        filter = ParseFilter(gp.filter,prolog)
        #filter.pattern = rv
        
    if p is None: # empty (empty optional, etc.)
        return (bgpParent,filter) 

    if bgpParent:
        if not makeBgpChild:
            # the BGP remains as the parent node in the query tree: BGP(...,Pat(...))
            bgpParent.pattern = p
            return (bgpParent,filter)

    return (p,filter)
   
def ParseGraphPatternSimple(gp,prolog):
    """
    Simplified version of ParseGraphPattern that can be used directly; returns single 
    operator and has no extra parameters.
    """    
    (ret,filter)=ParseGraphPattern(gp,None,prolog)
    
    # filter rewrite
    if filter != None:
        filter.pattern = ret
        ret = filter
    return ret
   
def ParseGraph(gp,prolog):        
#    if len(gp.graphPatterns) == 1:
#        pat = ParseGraphPattern(gp.graphPatterns[0])
#    elif len(gp.graphPatterns) > 1:
#        # if child is a list of graph patterns, add a group for them
#        pat = RelGroup()
#        pat.patternList = gp.graphPatterns
#    else:
#        pat = RelEmpty()
                
    return RelGraph(gp.name, ParseGroup(gp,prolog))
      
class RelGraph(RelationalOperator):
    def __init__(self,name,pattern):
        self.name = name
        self.pattern = pattern

    def __repr__(self):
        return "GRAPH{%s,%s}"%(repr(self.name),repr(self.pattern))
    
    def GetChildren(self):
        return [self.pattern]
    
    def BuildSql(self, sqlBuilder, isNested):
        # set the context of all descendant triples to self.context
        triples = self.pattern.GetDescendantOperators(RelTriple,[RelGraph])
        for t in triples:
            t.rawC = self.name # term will be converted later 
        
        # process child pattern (we don't need to do anything for the graph itself)
        return self.pattern.BuildSql(sqlBuilder, isNested)
    
    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        vars = self.pattern.GetUsedVariables(sqlBuilder,includeBNodes)
        if isinstance(self.name, Variable):
            vars.add(str(self.name))
        return vars 
        
def ParseUnion(gp,prolog):
    #OPTIMIZE: if frequently doing UNION of more than 2 patterns,
    #    rewrite RelUnion.BuildSql to build a single query with chained union builders.
    #    instead of converting them to a binary operator and potentially
    #    requiring additional nesting for patterns like {A}UNION{B}UNION{C}, etc. (more than 1 UNION).
    
    # convert to binary operator via nesting
    pat = None
    for p in gp.alternativePatterns:
        if pat == None:
            pat = ParseGraphPatternSimple(p,prolog)
        else:
            rightPat = ParseGraphPatternSimple(p,prolog)
            pat = RelUnion(pat, rightPat)
    
    return pat

class RelUnion(RelationalOperator):
    def __init__(self,left,right):
        self.leftPattern = left
        self.rightPattern = right  

    def __repr__(self):
        return "{%s UNION %s}"%(repr(self.leftPattern), repr(self.rightPattern))
    
    def GetChildren(self):
        return [self.leftPattern, self.rightPattern]
    
    def BuildSql(self, sqlBuilder, isNested):

        #OPTIMIZE: should probably optimize for more than 2 expressions being UNION'ed together;
        #      this would be done by rewriting this code to support a list of child operators to
        #      be UNION'ed together instead of a left and right child operator.
        #      The implementation would be to keep chaining the queries as union builders.
        
        #NOTE: Temporarily disable the EARLY PROJECTION optimization to ensure
        #    that we don't incorrectly eliminate valid bindings as duplicate.
        #    This could happen if only variables with literal are returned without the 
        #    resource variables that join them.
        #    This may be an edge case that we don't care about, 
        #    but we disable the optimization just to be case.
        if sqlBuilder.UseOptimization(OPT_C6_PROJECT_EARLY):
            projectEarly = True
            sqlBuilder.SetOptimization(OPT_C6_PROJECT_EARLY, False)
        else:
            projectEarly = False
        
        if isNested:
            # shouldn't be nested, as it needs to be embedded in parent FROM clause 
            # (we want to embed in sqlBuidler's parent!)
            leftBuilder = sqlBuilder # this is already a child builder of the query we want to modify
            if sqlBuilder.parentBuilder == None:
                raise Exception("Not expecting nested RelUnion to be the root query! May need to add an extra level of nested query here!")
            rightBuilder = sqlBuilder.parentBuilder.GetNestedSQLBuilder()
        else:
            # not nested, need to create the child builders 
            # (we want to embed in sqlBuilder directly)
            leftBuilder = sqlBuilder.GetNestedSQLBuilder()
            rightBuilder = sqlBuilder.GetNestedSQLBuilder()
                        
                                
        # add left & right children
        if sqlBuilder.UseOptimization(OPT_FLAT_UNION) or sqlBuilder.UseOptimization(OPT_FLATTEN):
            # put child queries in directly
                    
            # generate left & right as nested queries
            leftVars = self.leftPattern.BuildSql(leftBuilder, True)
            #NOTE: the following line will break if the union builder has already been set since the right hasn't built yet
            leftSql = leftBuilder.Sql() # only used if using LEFT OUTER JOIN...ON FALSE to combine schemas
                     
            rightVars = self.rightPattern.BuildSql(rightBuilder, True)        
            rightSql = rightBuilder.Sql() # only used if using LEFT OUTER JOIN...ON FALSE to combine schemas
            
        else:
            # add another level of nested queries to fix schemas (Chebotko)
            
            # generate left & right as nested queries
            leftChildBuilder = leftBuilder.GetNestedSQLBuilder()
            leftVars = self.leftPattern.BuildSql(leftChildBuilder, True)
            leftSql = leftChildBuilder.Sql()
                    
            rightChildBuilder = rightBuilder.GetNestedSQLBuilder()
            rightVars = self.rightPattern.BuildSql(rightChildBuilder, True)
            rightSql = rightChildBuilder.Sql()
                    
            leftTT = leftBuilder.AddNestedTableTuple(leftSql,"uLeft")
            leftBuilder.AddChildVariables(leftChildBuilder, leftTT)
            #for c in leftChildBuilder.GetOutputFields():
            #    leftBuilder.AddOutputField(leftTT,c,c)
            leftBuilder.AddTermAndLiteralFields(leftBuilder.GetReturnedVariables())
                    
            rightTT = rightBuilder.AddNestedTableTuple(rightSql,"uRight")
            rightBuilder.AddChildVariables(rightChildBuilder, rightTT)
            #for c in rightChildBuilder.GetOutputFields():
            #    rightBuilder.AddOutputField(rightTT,c,c)
            rightBuilder.AddTermAndLiteralFields(rightBuilder.GetReturnedVariables())
            
        #NOTE: 'UNION ALL' seems to violate SPARQL semantics by potentially adding the same binding twice if it is generated on both sides of the union
        # This seems to be a mistake in Chebotko 2007TR!
        leftBuilder.SetUnionSQLBuilder(rightBuilder, unionAll=False) 
            
            
        lset = set(leftVars)
        rset = set(rightVars)
        sharedVars = lset & rset
        leftOnlyVars = lset - rset
        rightOnlyVars = rset - lset
        bothVars = lset | rset
                
        # mark fields that can be NULL
        #leftUsedVars = self.leftPattern.GetUsedVariables(sqlBuilder)
        #rightUsedVars = self.rightPattern.GetUsedVariables(sqlBuilder)
        #commonUsedVars = leftUsedVars & rightUsedVars # set intersection
        # the left-only and right-only vars can be NULL
        #for v in (leftUsedVars-commonUsedVars) | (rightUsedVars-commonUsedVars):
        for v in leftOnlyVars | rightOnlyVars:
            sqlBuilder.SetCoalesceVariable(v)
                
        
        # shared vars and own vars will already be added by nested query;
        # just need to fill in the opposite query's parts to fix the schema            
        if sqlBuilder.UseOptimization(OPT_PAD_UNION):
            # use "'NULL' as missingColumn" for making schemas agree for UNION
                        
            #need to know the literal columns that need to be added here
            rightOnlyFields = rightBuilder.GetOutputFields() - leftBuilder.GetOutputFields()
            for c in rightOnlyFields:
                #leftBuilder.AddOutputAs("NULL",c,genSqlAlias=False)
                leftBuilder.AddOutputAs("CAST(NULL AS UNSIGNED)",c,genSqlAlias=False)            
            leftOnlyFields = leftBuilder.GetOutputFields() - rightBuilder.GetOutputFields()
            for c in leftOnlyFields:
                #rightBuilder.AddOutputAs("NULL",c,genSqlAlias=False)
                rightBuilder.AddOutputAs("CAST(NULL AS UNSIGNED)",c,genSqlAlias=False)
        else:
            # use Chebotko's method -- use 'LEFT OUTER JOIN [other side as nested query] ON FALSE' to combine schemas
            
            #NOTE: this method cannot be used in MySQL because tautologies are considered syntax errors!!!
            
            if sqlBuilder.UseOptimization(OPT_C5_SKIP_UNION_JOIN) and len(leftOnlyVars) < 1:
                # skip left outer join in UNION if schemas are the same (Chebotko 2007TR: Simp. 5)
                pass # do nothing
            else:
                rightSchemaTT = leftBuilder.AddNestedTableTuple(rightSql,"uSRight")
                leftBuilder.AddLastTupleJoin(LEFT_OUTER_JOIN, "FALSE") #BROKEN: tautology generates syntax error in MySQL!!!
                # add columns                
                #BROKEN: this is not adding the extra columns correctly!
                leftBuilder.AddTermAndLiteralFields(rightOnlyVars)

            if sqlBuilder.UseOptimization(OPT_C5_SKIP_UNION_JOIN) and len(leftOnlyVars) < 1:
                # skip left outer join in UNION if schemas are the same (Chebotko 2007TR: Simp. 5)
                pass # do nothing
            else:
                leftSchemaTT = rightBuilder.AddNestedTableTuple(rightSql,"uSLeft")
                rightBuilder.AddLastTupleJoin(LEFT_OUTER_JOIN, "FALSE") #BROKEN: tautology generates syntax error in MySQL!!!
                # add columns
                #BROKEN: this is not adding the extra columns correctly!
                rightBuilder.AddTermAndLiteralFields(leftOnlyVars)
        
        # ensure that the columns are in the same order -- we'll sort by alias
        leftBuilder.SortOutputFieldsByAlias()
        rightBuilder.SortOutputFieldsByAlias()
        
        if not isNested:
            # if not nested, it needs to add itself to parent query (Note: right builder is 'union-chained' to left builder)
            tt = sqlBuilder.AddNestedTableTuple(leftBuilder.Sql(),"union")
            sqlBuilder.AddChildVariables(leftBuilder, tt)
            
        # re-enable early projection
        if projectEarly:
            sqlBuilder.SetOptimization(OPT_C6_PROJECT_EARLY, projectEarly)
            
        # return final variables
        return list(bothVars)
    
    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        return self.leftPattern.GetUsedVariables(sqlBuilder,includeBNodes) | self.rightPattern.GetUsedVariables(sqlBuilder,includeBNodes)
    
    
class RelAnd(RelationalOperator):
    def __init__(self,left,right):
        self.leftPattern = left
        self.rightPattern = right  
        self.joinType = INNER_JOIN
        self.setRightCoalesce = False
        self.op = 'AND'

    def __repr__(self):
        return "{%s AND %s}"%(repr(self.leftPattern), repr(self.rightPattern))
    
    def GetChildren(self):
        return [self.leftPattern, self.rightPattern]
    
    def BuildSql(self, sqlBuilder, isNested):

        returnVars = None
        rightVars = None
        joinVars = None
        onClause = []     
        
        leftJoinTree = None
        rightJoinTree = None               

        # we need to determined required join variables (for use later)
        leftUsedVars = self.leftPattern.GetUsedVariables(sqlBuilder)
        rightUsedVars = self.rightPattern.GetUsedVariables(sqlBuilder)
        commonUsedVars = leftUsedVars & rightUsedVars # set intersection

        # determine required variables for join
        if sqlBuilder.UseOptimization(OPT_C6_PROJECT_EARLY):
            joinRequiredOnly = []              
            #Set required for left & right
            for vname in commonUsedVars:
                if not sqlBuilder.IsRequiredVariable(vname):
                    joinRequiredOnly.append(vname)
                    # temporarily set as required so left & right children inherit it as required and we ensure it is available to JOIN in this query
                    sqlBuilder.SetRequiredVariable(vname,value=True)
        
        if ((self.op == 'AND' and sqlBuilder.UseOptimization(OPT_FLAT_AND)) or 
            (self.op == 'OPTIONAL' and sqlBuilder.UseOptimization(OPT_FLAT_OPTIONAL)) or 
            sqlBuilder.UseOptimization(OPT_FLATTEN)):
            # flatten -- reuse same builder for both branches
            leftVars = self.leftPattern.BuildSql(sqlBuilder, False)
            vars=set()
            #We need to check for queries in the form P OPT (P' FILTER R) where
            #R includes a comparison operator that refers to variables in P and P'
            #these are handled with an early join below
            for op in self.rightPattern.GetDescendantOperators(RelFilter,
                                                               [],
                                                               includeSelf=True):
                    for lexComp in op.GetDecendentLexicalComparators():
                        vars.update(lexComp.GetUsedVariables(
                                         sqlBuilder,
                                         includeBNodes=False).intersection(leftVars))
            for var in vars:
                var=sqlBuilder.GetAvailableVariable(var)[0]
                sqlBuilder.AddStringJoin(var,var,addOutput=False)
            leftJoinTree = sqlBuilder.PopFromJoinTree()
            
            if self.op == 'AND':
                rightVars = self.rightPattern.BuildSql(sqlBuilder, False)
            elif self.op == 'OPTIONAL':
                # any WHERE conditions in the optional branch need to be
                # pulled out so we can use them as an ON condition
                sqlBuilder.OptionalWhereStackPush() 
                rightVars = self.rightPattern.BuildSql(sqlBuilder, False)
                onClause.extend(sqlBuilder.OptionalWhereStackPop())
            rightJoinTree = sqlBuilder.PopFromJoinTree()
                
            returnVars = []
            returnVars.extend(leftVars) 
            rightOnlyVars = []
            for v in rightVars:
                if v not in leftVars:
                    rightOnlyVars.append(v)
            returnVars.extend(rightOnlyVars)
            if  self.setRightCoalesce:
                for vname in rightOnlyVars: # vars only in the OPTIONAL clause
                    sqlBuilder.SetCoalesceVariable(vname)
            
            #BE: replaced with actual shared variables, below
            #joinVars = rightVars # potentially join any var introduced on the right hand side
        else:                        
            # left table        
            (leftTT,leftBuilder) = self.AddNestedOp(sqlBuilder, self.leftPattern, "andL")
            leftJoinTree = sqlBuilder.PopFromJoinTree()
    
            # right table
            (rightTT,rightBuilder) = self.AddNestedOp(sqlBuilder, self.rightPattern, "andR")                    
            rightJoinTree = sqlBuilder.PopFromJoinTree()
            
            if sqlBuilder.UseOptimization(OPT_C6_PROJECT_EARLY):
                # now put back the ones that don't need to be returned by this query
                for vname in joinRequiredOnly:
                    sqlBuilder.SetRequiredVariable(vname,value=False)
            
            #BE: replaced with actual shared variables, below            
            # potentially join on anything from both sides (only 2 table involved since we're nesting)
            #joinVars = sqlBuilder.GetAvailableVariables() #returnVars: #BE: this should be all joinable variables, not just the ones being returned
            
            # if this is actually an OPTIONAL, set right side variables to Nullable (need COALESCE!)
            if  self.setRightCoalesce:
                optionalOnlyVars = []
                for v in rightBuilder.GetAvailableVariables(): # vars in OPTIONAL clause
                    if not leftBuilder.IsAvailableVariable(v):
                        optionalOnlyVars.append(v) # not in REQUIRED clause
                # set coalesce for variables that are in the OPTIONAL clause ONLY
                for vname in optionalOnlyVars:
                    sqlBuilder.SetCoalesceVariable(vname)

            returnVars = sqlBuilder.GetReturnedVariables()
                                        
        # find shared variables, create projection list & join ON clause
        
        if isNested:
            sqlBuilder.AddTermAndLiteralFields(sqlBuilder.GetReturnedVariables())         
        
        joinVars = list(commonUsedVars)                
        
        for vname in joinVars: 
            availableVars = sqlBuilder.GetAvailableVariable(vname)
            if len(availableVars) > 1:    
                firstV = availableVars[0]
                firstVfn = firstV.fieldName #"%s.%s"%(firstTT,vname)
                for v in availableVars:
                    if v is firstV:
                        continue
                    fn = v.fieldName #"%s.%s"%(tt,vname)                    
                    #OPTIMIZE: don't need IS NULL checks if no OPTIONAL involved
                    if sqlBuilder.UseOptimization(OPT_C3_SIMPLIFY_JOIN) and not sqlBuilder.IsCoalesceVariable(vname):
                        onClause.append("%s = %s"%(firstVfn,fn))
                    else:
                        onClause.append("(%s = %s OR %s IS NULL OR %s IS NULL)"%(firstVfn,fn,firstVfn,fn))

        
        # add join
        if len(onClause) > 0:            
            #sqlBuilder.AddTupleJoin(rightTT, self.joinType, " AND ".join(onClause))
            #sqlBuilder.AddLastTupleJoin(self.joinType, " AND ".join(onClause))
            sqlBuilder.SetFromJoinTree(leftJoinTree, rightJoinTree, self.joinType, " AND ".join(onClause))
        else: 
            # if no ON clauses, this is really a cross product, so don't use join here
            #sqlBuilder.AddTupleJoin(rightTT, CROSS_JOIN)
            #sqlBuilder.AddLastTupleJoin(CROSS_JOIN)
            sqlBuilder.SetFromJoinTree(leftJoinTree, rightJoinTree, CROSS_JOIN, None)
            sqlBuilder.AddWarning("This query performs a cross product.  Execution may be slow!")
         
        return returnVars   
   
    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        return self.leftPattern.GetUsedVariables(sqlBuilder,includeBNodes) | self.rightPattern.GetUsedVariables(sqlBuilder,includeBNodes)


def ParseOptional(gp,prolog):
    group = ParseGroup(gp,prolog)
    if group is None:
        return None # empty optional! ignoring...
    optional = RelOptional()
    optional.optionalPattern = group
    # requiredPattern should be set up in ParseGraphPattern() & ParseGroup()
    return optional

class RelOptional(RelAnd):

    def __init__(self):
        self.requiredPattern = None
        self.optionalPattern = None
        
    def GetChildren(self):
        return [self.requiredPattern, self.optionalPattern]
        
    def __repr__(self):
        return "OPTIONAL{Req:%s,Opt:%s}"% (self.requiredPattern,self.optionalPattern)
    
    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        return self.requiredPattern.GetUsedVariables(sqlBuilder,includeBNodes) |\
               self.optionalPattern.GetUsedVariables(sqlBuilder,includeBNodes)
        
    def BuildSql(self, sqlBuilder, isNested):
        # observation - optional the same as AND with different join type!
        self.op = 'OPTIONAL'
        self.leftPattern = self.requiredPattern
        self.rightPattern = self.optionalPattern
        self.joinType = LEFT_OUTER_JOIN
        self.setRightCoalesce = True
        return RelAnd.BuildSql(self, sqlBuilder, isNested)
    
def ParseGroup(gp,prolog):
    patternList = []
    filters = []
    optionals = []
    bgp = None # combine triples from multiple BGPs
    patternQueue = deque()
    for p in gp.graphPatterns:            
        patternQueue.append(ParseGraphPattern(p, None,prolog)) 
    
    while len(patternQueue) > 0:
        (relP,relFilter) = patternQueue.popleft()
        if relFilter != None:
            if relFilter.pattern != None:
                patternQueue.append((relFilter.pattern,None))
                relFilter.pattern = None
            filters.append(relFilter)
        
        # filter rewriting
#        relPat = relP
#        if relFilter != None:
#            #relFilter.pattern = relP # may want to combine pattern with others (i.e. for BGP)
#            relPat = relFilter
#            if relP is None: # nothing but a filter returned
#                relP = relPat

        if relP is None:
            continue  # skipping empty graph patterns
        
        if isinstance(relP, RelFilter):
            filters.append(relP)
            if relP.pattern != None:
                patternQueue.append((relP.pattern,None))
                relP.pattern = None
        elif isinstance(relP, RelOptional):
            if relP.requiredPattern != None:
                # need to merge required component with rest of required parts
                patternQueue.append((relP.requiredPattern,None))
                relP.requiredPattern = None
            optionals.append(relP)
        elif isinstance(relP, RelBGP):
            if bgp == None:
                bgp = relP
                patternList.append(bgp)
            else: 
                # merge triples with previous BGP!
                bgp.triples.extend(relP.triples)
                if relP.pattern != None:
                    patternQueue.append((relP.pattern,None))
                    relP.pattern = None
        elif isinstance(relP, RelGroup):
            # merge this child group
            for p in relP.patternList:
                patternQueue.append((p,None))
        elif isinstance(relP, list):
            # merge this child group
            for p in relP:
                patternQueue.append((p,None))
        elif isinstance(relP, RelUnion):
            patternList.append(relP)
        else:
            patternList.append(relP)
            
    if len(patternList) == 0:
        group = None # nothing here? ignoring...
    elif len(patternList) == 1:
        group = patternList[0] # simplify if only one child
    else:
        # use group for remaining patterns
        group = RelGroup()
        group.patternList = patternList   
    rv = group 
    
    # do rewriting as needed now
    
    # add group as child of optional(s)
    if len(optionals) > 0:
        # this handles the case where the the BGP containing the optional has been placed in a sibling BGP within this group
        
        #Note: if multiple optionals are used in this group, this will combine them as described in the SPARQL algebra (see 12.2.2 Examples of Mapped Graph Patterns) 
        for op in optionals:            
            if op.requiredPattern is None:
                op.requiredPattern = rv
            else:
                if (isinstance(op.requiredPattern, RelBGP) and len(op.requiredPattern.triples) < 1) or isinstance(op.requiredPattern, RelEmpty):
                    op.requiredPattern = rv # ignore empty BGP
                else:
                    # there was already some triples required pattern found in the same BGP, we now we have to AND them
                    op.requiredPattern = RelAnd(rv, op.requiredPattern)
            rv = op
    
    # add group as child of filter(s)
    if len(filters) > 0:
        # in theory, we should probably combine multiple filters, but flattening will basically take care of this anyway
        for f in filters:
            f.pattern = rv
            rv = f
    
    return rv
    
class RelGroup(RelationalOperator):
    
    def __init__(self):
        self.patternList = []
        
    def __repr__(self):
        return "Grp{%s}"%repr(self.patternList)

    def GetChildren(self):
        return self.patternList
        
    def BuildSql(self, sqlBuilder, isNested):
        # convert to AND's
        pat = None
        for p in self.patternList:
            if pat is None:
                pat = p
            else:
                pat = RelAnd(pat, p)
        
        return pat.BuildSql(sqlBuilder, isNested)

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        s = set()
        for p in self.patternList:
            s = s | p.GetUsedVariables(sqlBuilder,includeBNodes)
        return s
    
def ParseBGP(gp,prolog):
    if (not gp.triples or len(gp.triples) < 1) and gp.nonTripleGraphPattern is None:
        return None # skip empty graph pattern??
    trip = []
    for triple in gp.triples:
        for s,p,o in unRollTripleItems(triple,prolog):
            trip.append(RelTriple(s,p,o))
#    trip = ParseTriples(gp.triples,prolog)
    rv = None
    if trip != None:
        bgp = RelBGP()   
        bgp.triples = trip
        rv = bgp
    
    if gp.nonTripleGraphPattern:
        # will convert BGP(...,Pat(...)) to: 
        #       1) AND(BGP(...),Pat(...)) 
        #    or 2) Pat(BGP(...),...)
        (rv,filter) = ParseGraphPattern(gp.nonTripleGraphPattern, rv,prolog)
        # filter rewrite
        if filter != None:
            filter.pattern = rv
            rv = filter
#        if not gp.triples and gp.filter is None:
#            return childGP #flatten if nothing else
        #bgp.pattern = childGP

    # not the right place to handle filter
#    if gp.filter:
#        # convert ... to FILTER(...)
#        filter = ParseFilter(gp.filter)
#        filter.pattern = rv
#        rv = filter
        
    return rv


class RelBGP(RelationalOperator):
    
    def __init__(self):
        self.triples = []
        self.pattern = None
    
    def __repr__(self):
        r = "BGP{"
        if len(self.triples) > 0:
            r += repr(self.triples)
        if self.pattern:
            r += repr(self.pattern)
        return r + "}"

    def GetChildren(self):
        list = []
        list.extend(self.triples)
        if self.pattern != None:
            list.append(self.pattern)
        return list
    
    def BuildSql(self, sqlBuilder, isNested):
                
        # convert to And's
        pat = None
        if self.triples and len(self.triples) > 0:
            # add term hashes to triples
            for t in self.triples:
                #t.SetTermHashes(sqlBuilder)
                t.ConvertTerms(sqlBuilder)
                
                #HACK: check if we need to search all partitions (i.e. Views) -- this function will mark the triple if it's a View
                sqlBuilder.TripleTable(t) # check 
            
            #OPTIMIZE: reorder triples!
            if sqlBuilder.GetQueryCostEstimator() != None:
                selections =  []
                if (sqlBuilder.UseOptimization(OPT_JOIN_GREEDY_SELECTION)):
                    # identify FILTERS that are an ancestor of this operator
                    for f in sqlBuilder.CurrentFilters():
                        # add sets of variables used and expression tree 
                        selections.append(QuerySelection(f.exp.GetUsedVariables(sqlBuilder,includeBNodes=False), f.exp))
                
                if sqlBuilder.UseOptimization(OPT_JOIN_STRAIGHT_JOIN):
                    # get an idea of the cost of the original query ordering
                    #(cost,costSum) = sqlBuilder.GetQueryCostEstimator().EstimateBGPCost(self.triples, EST_METHOD_HARTH,[])
                    #sqlBuilder.GetQueryCostEstimator().SaveExecutionStats(0,cost,costSum,self.triples)
                    pass
                if sqlBuilder.UseOptimization(OPT_JOIN_GREEDY_SMALL_STATS):
                    self.triples = sqlBuilder.GetQueryCostEstimator().GreedyOrderTriples(self.triples, EST_METHOD_SMALL, selections)
                elif sqlBuilder.UseOptimization(OPT_JOIN_GREEDY_MED_STATS):
                    self.triples = sqlBuilder.GetQueryCostEstimator().GreedyOrderTriples(self.triples, EST_METHOD_MEDIUM, selections)
                elif sqlBuilder.UseOptimization(OPT_JOIN_GREEDY_LARGE_STATS):
                    self.triples = sqlBuilder.GetQueryCostEstimator().GreedyOrderTriples(self.triples, EST_METHOD_LARGE, selections)
                elif sqlBuilder.UseOptimization(OPT_JOIN_GREEDY_ALL_PATTERNS):
                    self.triples = sqlBuilder.GetQueryCostEstimator().GreedyOrderTriples(self.triples, EST_METHOD_HARTH, selections)
                elif sqlBuilder.UseOptimization(OPT_JOIN_GREEDY_STOCKER_STATS):
                    self.triples = sqlBuilder.GetQueryCostEstimator().GreedyOrderTriples(self.triples, EST_METHOD_STOCKER, selections)                
                elif sqlBuilder.UseOptimization(OPT_JOIN_STOCKER08):
                    self.triples = sqlBuilder.GetQueryCostEstimator().StockerOrderTriples(self.triples)
                elif sqlBuilder.UseOptimization(OPT_JOIN_RANDOM):
                    self.triples = sqlBuilder.GetQueryCostEstimator().RandomOrderTriples(self.triples)
            
            # convert to a set of AND'ed triple patterns
            for t in self.triples:
                if pat is None:
                    pat = t
                else:                    
                    pat = RelAnd(pat, t)
                    
        if self.pattern:
            if pat is None:
                pat = self.pattern
            else:
                if isinstance(pat, RelEmpty):
                    pat = self.pattern # don't bother joining an empty
                elif isinstance(self.pattern, RelEmpty):
                    pass # ignore the empty one and keep the old one
                else:
                    pat = RelAnd(pat, self.pattern)
        
        if pat != None:
            return pat.BuildSql(sqlBuilder, isNested)
        else:
            # empty BGP!
            e = RelEmpty()
            return e.BuildSql(sqlBuilder, isNested)

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        s = set()
        for t in self.triples:
            s = s | t.GetUsedVariables(sqlBuilder,includeBNodes)
        if self.pattern:
            s = s | self.pattern.GetUsedVariables(sqlBuilder,includeBNodes)
        return s
        
        
class RelEmpty(RelationalOperator):
    
    def __init__(self):
        pass
    
    def __repr__(self):
        return "{Empty}"
    
    def GetChildren(self):
        return []
    
    def BuildSql(self, sqlBuilder, isNested):
        # the query "SELECT NULL LIMIT 0;" returns 0 rows
        
        if isNested:
            sqlBuilder.AddOutputAs("NULL", "EmptyColumn",genSqlAlias=False)
            sqlBuilder.SetLimit(0)
        else:
            raise NotImplementedError("What to do when Empty BGP is not nested?")
        
        return [] # no variables here

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        return set() # empty set


def ParseTriples(triples,prolog):
    list = []
    q = deque(triples)
    #q.extend(triples)
    while len(q) > 0: #for s in triples:
        #s = q.pop()  asdf
        s = q.popleft()
        for p in s.propVals:
            for o in p.objects:
                if isinstance(o, Resource):
                    # need to process BNode objects, which may contain more triples!
                    list.append(RelTriple(s.identifier, 
                                          p.property, 
                                          o.identifier))
                    q.append(o)
                else:
                    list.append(RelTriple(s.identifier, 
                                          p.property, 
                                          o))
    if len(list) < 1:
        return None
    
    return list

class RelTriple(RelationalOperator):
    
    def __init__(self,s,p,o,c=None):
        """
        Initially set up the triple with the raw parser-generated objects.  Before use, need to call ConvertTerm (at SQL build time).
        """
        self.rawS = s
        self.rawP = p
        self.rawO = o
        self.rawC = c
        self.sub = None
        self.pred = None
        self.obj = None
        self.context = None
        
        # variables set later and used for triple pattern ordering
        self.subHash = None
        self.predHash = None
        self.objHash = None
        self.contextHash = None
        
        self.cost = None     # (estimated) size of this triple pattern (# rows)
        self.cols = None     # set of columns (i.e. variables) in this triple
        self.colDist = None  # number of distinct values for a column
        
        self.allPartitions = False # indicate that this pattern must search all partitions (i.e. use a View!)
    
    def __repr__(self):
        if not self.rawC: 
            return "(%s,%s,%s)"%(self.rawS,self.rawP,self.rawO)
        else:
            return "(%s,%s,%s in %s)"%(self.rawS,self.rawP,self.rawO,self.rawC)

    
    def GetChildren(self):
        return []
    
    def ConvertTerms(self, sqlBuilder):
        if self.sub == None and self.rawS != None:
            self.sub = sqlBuilder.ConvertTerm(self.rawS)
            if not (isinstance(self.sub, Variable) or type(self.sub) is BNode):
                self.subHash = sqlBuilder.GetTermHash(self.sub)
        if self.pred == None and self.rawP != None:
            self.pred = sqlBuilder.ConvertTerm(self.rawP)
            if not (isinstance(self.pred, Variable) or type(self.pred) is BNode):
                self.predHash = sqlBuilder.GetTermHash(self.pred)
        if self.obj == None and self.rawO != None:
            self.obj = sqlBuilder.ConvertTerm(self.rawO)
            if not (isinstance(self.obj, Variable) or type(self.obj) is BNode):
                self.objHash = sqlBuilder.GetTermHash(self.obj)
        if self.context == None and self.rawC != None:
            self.context = sqlBuilder.ConvertTerm(self.rawC)
            if not (isinstance(self.context, Variable) or type(self.context) is BNode):
                self.contextHash = sqlBuilder.GetTermHash(self.context)
    
    def BuildSql(self, sqlBuilder, isNested):
        # convert terms
        self.ConvertTerms(sqlBuilder)
        
        # add table to FROM clause
        table = sqlBuilder.TripleTable(self)
        tt = sqlBuilder.AddTableTuple(table, "tp")

        variablesAdded = []
        # add variables as output
        if isinstance(self.sub,Variable) or type(self.sub) is BNode:
            (fn,fnTerm) = sqlBuilder.TripleColumn(tt, table, SUBJECT)
            if isNested:
                sqlBuilder.AddOutputAs(fn, str(self.sub)) # .sub.lower()) #BE: currently assuming variables are not case-sensitive
                sqlBuilder.AddOutputAs(fnTerm, str(self.sub) + "_term") #.lower() + "_term")  #BE: currently assuming variables are not case-sensitive
            sqlBuilder.AddPatternVariable(RdfVariable(str(self.sub), tt, fn, fnTerm, None, None, [RdfVariableSource(table, SUBJECT, False)], type(self.sub) is BNode))
            variablesAdded.append(str(self.sub)) #.lower()) #BE: currently assuming variables are not case-sensitive
        if isinstance(self.pred,Variable) or type(self.pred) is BNode:
            (fn,fnTerm) = sqlBuilder.TripleColumn(tt, table, PREDICATE) 
            if isNested:
                sqlBuilder.AddOutputAs(fn, str(self.pred)) #.lower())  #BE: currently assuming variables are not case-sensitive 
                sqlBuilder.AddOutputAs(fnTerm, str(self.pred) + "_term") #.lower() + "_term")
            sqlBuilder.AddPatternVariable(RdfVariable(str(self.pred), tt, fn, fnTerm, None, None, [RdfVariableSource(table, PREDICATE, False)], type(self.pred) is BNode))
            variablesAdded.append(str(self.pred)) #.lower()) #BE: currently assuming variables are not case-sensitive
        if isinstance(self.obj,Variable) or type(self.obj) is BNode:
            (fn,fnTerm) = sqlBuilder.TripleColumn(tt, table, OBJECT) 
            if isNested:
                sqlBuilder.AddOutputAs(fn, str(self.obj)) #.lower()) #BE: currently assuming variables are not case-sensitive
                sqlBuilder.AddOutputAs(fnTerm, str(self.obj) + "_term") #.lower() + "_term") #BE: currently assuming variables are not case-sensitive
            
            # check if this is a literal
            isLiteral = False
            for c in table.columnNames:
                if isinstance(c, tuple):
                    if c[0] == 'data_type' or c[0] == 'language':
                        isLiteral = True
                elif c == 'data_type' or c == 'language':
                    isLiteral = True                    

            if isLiteral:
                sqlBuilder.AddPatternVariable(RdfVariable(str(self.obj), tt, fn, fnTerm, '%s.data_type'%(tt), '%s.language'%(tt), [RdfVariableSource(table, OBJECT, isLiteral)], type(self.obj) is BNode))
            else:
                sqlBuilder.AddPatternVariable(RdfVariable(str(self.obj), tt, fn, fnTerm, None, None, [RdfVariableSource(table, OBJECT, isLiteral)],type(self.obj) is BNode))
            variablesAdded.append(str(self.obj)) #.lower())  #BE: currently assuming variables are not case-sensitive

            if isLiteral and isNested:
                sqlBuilder.AddOutputAs("%s.data_type"%(tt), str(self.obj) + "_data_type") #.lower() + "_data_type")  #BE: currently assuming variables are not case-sensitive
                #if "language" in table.columnNames:
                sqlBuilder.AddOutputAs("%s.language"%(tt), str(self.obj) + "_language") #.lower() + "_language") #BE: currently assuming variables are not case-sensitive
            
        if isinstance(self.context,Variable) or type(self.context) is BNode:
            (fn,fnTerm) = sqlBuilder.TripleColumn(tt, table, CONTEXT) 
            if isNested:
                sqlBuilder.AddOutputAs(fn, str(self.context)) #.lower()) #BE: currently assuming variables are not case-sensitive
                sqlBuilder.AddOutputAs(fnTerm, str(self.context) + "_term") #.lower() + "_term") #BE: currently assuming variables are not case-sensitive
            sqlBuilder.AddPatternVariable(RdfVariable(str(self.context), tt, fn, fnTerm, None, None, [RdfVariableSource(table, CONTEXT, False)],type(self.context) is BNode))
            variablesAdded.append(str(self.context)) #.lower()) #BE: currently assuming variables are not case-sensitive
            
        # add triple match conditions
        for c in sqlBuilder.MatchTripleConditions(tt, table, self):
            sqlBuilder.AddWhere(c)
            
        return variablesAdded            
         
    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        self.ConvertTerms(sqlBuilder)
        s = set()
        for pos in [SUBJECT,PREDICATE,OBJECT,CONTEXT]:
            v = self.GetPosVariable(pos, includeBNodes)
            if v != None:
                s.add(v)
        return s

    def GetPosVariable(self,pos,includeBNodes=True):
        if pos==SUBJECT and (isinstance(self.sub,Variable) or (includeBNodes and type(self.sub) is BNode)):
            return str(self.sub)
        elif pos==PREDICATE and (isinstance(self.pred,Variable) or (includeBNodes and type(self.pred) is BNode)):
            return str(self.pred)
        elif pos==OBJECT and (isinstance(self.obj,Variable) or (includeBNodes and type(self.obj) is BNode)):
            return str(self.obj)
        elif pos==CONTEXT and (isinstance(self.context,Variable) or (includeBNodes and type(self.context) is BNode)):
            return str(self.context)
        return None 
         
def ParseFilter(filter,prolog):
    f = RelFilter()
    f.exp = ParseFilterExp(filter.filter,prolog)
    # f.pattern is assigned by client code
    return f

class RelFilter(RelationalOperator):
    
    def __init__(self):
        self.exp = None
        self.pattern = None
        
    def __repr__(self):
        return "FILTER{%s,%s}"%(repr(self.exp),repr(self.pattern))

    def GetDecendentLexicalComparators(self):
        for op in self.exp.GetDecendentLexicalComparators():
            yield op        
    
    def GetChildren(self):
        return [self.pattern]
    
    def BuildSql(self, sqlBuilder, isNested):
        if sqlBuilder.UseOptimization(OPT_JOIN_GREEDY_SELECTION):
            sqlBuilder.FilterStackPush(self)
        
        if sqlBuilder.UseOptimization(OPT_C6_PROJECT_EARLY):        
            # need to set required variables before processing child pattern
            for vname in self.exp.GetUsedVariables(sqlBuilder):
                sqlBuilder.SetRequiredVariable(vname)            
        
        if sqlBuilder.UseOptimization(OPT_FLAT_FILTER) or sqlBuilder.UseOptimization(OPT_FLATTEN):
            # flatten by reusing the same builder for child pattern
            addedVars = self.pattern.BuildSql(sqlBuilder, False)            
        else:    
            # add nested query for pattern we want to filter     
            (tt,childBuilder) = self.AddNestedOp(sqlBuilder, self.pattern, "pat")
                
            addedVars = childBuilder.GetAvailableVariables()
    
        # set output
        #sqlBuilder.AddOutputField(tt, "*") # this no longer works properly with StringJoins (2 levels of filters that use the same variable)
        if isNested:
            sqlBuilder.AddTermAndLiteralFields(sqlBuilder.GetReturnedVariables())
        
        # add filter expression        
        expStr = self.exp.BuildSqlExpression(sqlBuilder)
        if expStr is not None:
            sqlBuilder.AddWhere(expStr)
        
        if sqlBuilder.UseOptimization(OPT_JOIN_GREEDY_SELECTION):
            sqlBuilder.FilterStackPop()

        return addedVars

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        s = set()        
        s = self.exp.GetUsedVariables(sqlBuilder,includeBNodes) # include variables only used in FILTER in SELECT *, but will be bound to NULL only... 
        return s | self.pattern.GetUsedVariables(sqlBuilder,includeBNodes)
        
def ParseFilterExp(filter,prolog):
    if filter is None:
        return None
    if isinstance(filter, Variable) or type(filter) is BNode:
        return RelVariableExp(filter, type(filter) is BNode)
    elif isinstance(filter, Literal): # or type(filter) is BNodeRef: # what to do with a BNodeRef in a filter??
        return RelLiteralExp(filter)
    elif isinstance(filter, BinaryOperator):
        return ParseBinaryOperator(filter,prolog)
    elif isinstance(filter, UnaryOperator):
        return ParseUnaryOperator(filter,prolog)
    elif isinstance(filter, ParsedREGEXInvocation):
        return ParseFunction(filter,prolog)
    elif isinstance(filter, FunctionCall):
        return ParseFunction(filter,prolog)
    #TODO: add other functions!
    elif isinstance(filter, ListRedirect):
        filterList = []
        for f in filter:
            filterList.append(ParseFilterExp(f,prolog))
        if isinstance(filter, ParsedConditionalAndExpressionList):
            # OR-list (NOTE: this OR!)
            r = None
            for f in filterList:
                if r is None:
                    r = f
                else:
                    r = RelBinaryExp(r, 'OR', f)
            return r
        elif isinstance(filter, ParsedRelationalExpressionList):
            # AND-list
            r = None
            for f in filterList:
                if r is None:
                    r = f
                else:
                    r = RelBinaryExp(r, 'AND', f)
            return r        
        elif isinstance(filter, ParsedPrefixedMultiplicativeExpressionList):
            # multiplicative
            raise NotImplementedError()
        else:
            raise Exception('Unknown filter list operator: %s' % filter)        
    elif isinstance(filter, ParsedDatatypedLiteral):
        return RelTypeCastExp(filter.dataType, RelLiteralExp(filter.value))
    elif isinstance(filter, QName):
        return RelUriExp(filter)
    else:
        raise Exception('Unknown filter operator: %s' % filter)
    
class RelVariableExp(RelationalTerminalExpOperator):
    def __init__(self, var, isBNode=False):
        self.variable = var
        self.isBNode = isBNode
    
    def __repr__(self):
        return str(self.variable)
    
    def BuildTerminalExpression(self, sqlBuilder):        
        # string value will require adding join with literals/identifiers table
        # add join with appropriate tables!
        
        varName = str(self.variable)
        
        #OPTIMIZE: keep track of which variables are required
        if sqlBuilder.UseOptimization(OPT_C6_PROJECT_EARLY):
            sqlBuilder.SetRequiredVariable(varName)
        
        if sqlBuilder.GetAvailableVariable(varName) != None:            
            var = sqlBuilder.GetAvailableVariable(varName)[0] #all copies of variable should be joined together, so just use the first one
            fn = sqlBuilder.AddStringJoin(var, var.name + "_val", addOutput=False) # code will be using the tuple expression, not the alias anyway, and setting this as query output can mess up SELECT DISTINCT for a flattened query
        else:
            sqlBuilder.AddWarning("Undefined variable '%s' in filter: treating as NULL."%(varName))            
            fn = "NULL" # not found
                
        return fn
    
    def BuildHash(self, sqlBuilder):
        # directly comparing with a literal hash, so we can leave alone
        return sqlBuilder.CombineSources(self.variable, VALUE_FIELD_NAME)
#        varName = str(self.variable)
#        var = sqlBuilder.GetAvailableVariable(varName)[0] #all copies of variable should be joined together, so just use the first one        
#        return var.fieldName
    
    def BuildSqlExpression(self,sqlBuilder):
        raise NotImplementedError()

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        s = set()
        s.add(str(self.variable)) #.lower()) #BE: currently assuming variables are not case-sensitive
        return s

    def GetDataTypeExp(self,sqlBuilder):
        return (sqlBuilder.CombineSources(self.variable, DATATYPE_FIELD_NAME), False)       
#        varName = str(self.variable)
#        var = sqlBuilder.GetAvailableVariable(varName)[0] #all copies of variable should be joined together, so just use the first one        
#        return (var.dataTypeFieldName, False) # None if not literal
    
    def GetLanguageExp(self,sqlBuilder):
        return sqlBuilder.CombineSources(self.variable, LANGUAGE_FIELD_NAME)       
#        varName = str(self.variable)
#        var = sqlBuilder.GetAvailableVariable(varName)[0] #all copies of variable should be joined together, so just use the first one        
#        return var.languageFieldName
    
    def GetTermExpr(self,sqlBuilder):
        return sqlBuilder.CombineSources(self.variable, TERM_FIELD_NAME)       
    
    def AdjustCostEstimate(self,cost,colDist):
        s = set()
        s.add(str(self.variable))
        return (cost, colDist, s)
    
class RelConstantExp(RelationalTerminalExpOperator):
    """
    Shared base class for Literal and Uri
    """
    pass 
    
class RelLiteralExp(RelConstantExp):
    def __init__(self, lit):
        self.literal = lit
    
    def __repr__(self):
        return repr(self.literal)
    
    def BuildTerminalExpression(self,sqlBuilder):
        #TODO: insert this as a param to avoid SQL injects                
        return "'" + str(self.literal) + "'"
    
    def BuildHash(self, sqlBuilder):
        return "'" + str(sqlBuilder.GetLiteralHash(self.literal)) + "' /*" + self.literal + "*/ "

    def BuildSqlExpression(self,sqlBuilder):
        raise NotImplementedError()

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        return set() # no variables here
    
    def GetDataTypeExp(self,sqlBuilder):
        if not self.literal.datatype:
            return (None, True)
        return (str(self.literal.datatype), True)
    
    def GetLanguageExp(self,sqlBuilder):
        if not self.literal.language:
            return None
        return "'" + str(self.literal.language) + "'"

    def GetTermExpr(self,sqlBuilder):
        return "'L'"
    
    def AdjustCostEstimate(self,cost,colDist):
        return (cost, colDist, set())    
            
            
class RelUriExp(RelConstantExp):
    def __init__(self, qname):
        self.qname = qname
        self.uri = None
    
    def __repr__(self):
        return str(self.qname)
    
    def BuildTerminalExpression(self,sqlBuilder):
        #TODO: insert this as a param to avoid SQL injects  
        if self.uri == None:
            self.uri = sqlBuilder.ConvertTerm(self.qname)
        return "'" + str(self.uri) + "'"
    
    def BuildHash(self, sqlBuilder):
        if self.uri == None:
            self.uri = sqlBuilder.ConvertTerm(self.qname)        
        return "'" + str(sqlBuilder.GetUriHash(self.uri)) + "' /*" + self.uri + "*/"

    def BuildSqlExpression(self,sqlBuilder):
        raise NotImplementedError()

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        return set() # no variables here
    
    def GetDataTypeExp(self,sqlBuilder):
        return (None, False) # no data type, not a literal
    
    def GetLanguageExp(self,sqlBuilder):
        return None

    def GetTermExpr(self,sqlBuilder):
        return "'U'"
    
    def AdjustCostEstimate(self,cost,colDist):
        return (cost, colDist, set())                   

            
def ParseBinaryOperator(filter,prolog):
    op = RelBinaryExp()    
    #TODO: do we need to do any post-processing for any of the operators?
    op.op = filter.NAME
    op.leftExp = ParseFilterExp(filter.left,prolog)
    op.rightExp = ParseFilterExp(filter.right,prolog)
    
    return op  
 
LEXICAL_COMPARISON_BINARY_OPS=[
   "<",
   "<=",
   ">",
   ">=",
] 
 
class RelBinaryExp(RelationalExpOperator):
    def __init__(self, leftExp = None, op = None, rightExp = None):
        self.op = op
        self.leftExp = leftExp
        self.rightExp = rightExp
            
    def __repr__(self):
        return "(%s %s %s)"%(self.leftExp,self.op, self.rightExp)
    
    def GetDecendentLexicalComparators(self):
        if self.op in ['AND','OR']:
            for operand in [self.leftExp,self.rightExp]:
                for lexComp in self.leftExp.GetDecendentLexicalComparators():
                    yield lexComp
        elif self.op in LEXICAL_COMPARISON_BINARY_OPS:
            yield self
    
    def BuildSqlExpression(self,sqlBuilder):
        
        # terminal expressions are expected here
        if ((self.op == "=" or self.op == "!=") and 
            ((isinstance(self.leftExp,RelConstantExp) and isinstance(self.rightExp,RelVariableExp)) or  
            (isinstance(self.leftExp,RelVariableExp) and isinstance(self.rightExp,RelConstantExp)) or
            (isinstance(self.leftExp,RelVariableExp) and isinstance(self.rightExp,RelVariableExp)))):
            #OPTIMIZE: convert to hash if literal/variable combination & op is = or !=
            leftStrExp = self.leftExp.BuildHash(sqlBuilder)
            rightStrExp = self.rightExp.BuildHash(sqlBuilder)
        else:    
            # variables & literals will be treated as strings 
            if isinstance(self.leftExp,RelationalTerminalExpOperator):
                #OPTIMIZE: convert to hash if literal & op is = or !=
    #            if isinstance(self.leftExp,RelLiteralExp) and (self.op == "=" or self.op == "!="):
    #                leftStrExp = self.leftExp.BuildHash(sqlBuilder)
    #            else:
                leftStrExp = self.leftExp.BuildTerminalExpression(sqlBuilder)
            else:
                leftStrExp = self.leftExp.BuildSqlExpression(sqlBuilder)
            
            if isinstance(self.rightExp,RelationalTerminalExpOperator):
                #OPTIMIZE: convert to hash if literal & op is = or !=
    #            if isinstance(self.rightExp,RelLiteralExp) and (self.op == "=" or self.op == "!="):
    #                rightStrExp = self.rightExp.BuildHash(sqlBuilder)
    #            else:
                rightStrExp = self.rightExp.BuildTerminalExpression(sqlBuilder)
            else:
                rightStrExp = self.rightExp.BuildSqlExpression(sqlBuilder)
        
        cond = ""
        if self.op == "=" or self.op == "!=" or self.op == "<" or self.op == ">" or self.op == "<=" or self.op == ">=":
            # basic comparison operators -- need to compare data_type & langauge!
            #TODO: add conditions for testing data_type and language
            #TODO: handle datatype of non-terminal expressions
            if (isinstance(self.leftExp,RelationalTerminalExpOperator) and
                isinstance(self.rightExp,RelationalTerminalExpOperator)):
                (leftDataType,leftLit) = self.leftExp.GetDataTypeExp(sqlBuilder)
                (rightDataType,rightLit) = self.rightExp.GetDataTypeExp(sqlBuilder)
                dataTypeCond = sqlBuilder.CompareLiteralCondition(leftDataType,leftLit,rightDataType,rightLit,'data_type', sqlBuilder.UseEvalOption(EVAL_OPTION_STRICT_DATATYPE))
                if len(dataTypeCond) > 0:
                    cond += " AND " + dataTypeCond
                    
                leftLang = self.leftExp.GetLanguageExp(sqlBuilder)
                rightLang = self.rightExp.GetLanguageExp(sqlBuilder)
                langCond = sqlBuilder.CompareLiteralCondition(leftLang,leftLit,rightLang,rightLit,'language', True)
                if len(langCond) > 0:
                    cond += " AND " + langCond
            else:
                if self.op == '=' and leftStrExp == rightStrExp:
                    #Tautology: don't return WHERE condition
                    return "1"
        return "(%s %s %s%s)"%(leftStrExp, self.op, rightStrExp,cond)    

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        return self.leftExp.GetUsedVariables(sqlBuilder,includeBNodes) | self.rightExp.GetUsedVariables(sqlBuilder,includeBNodes) 

    def GetDataTypeExp(self,sqlBuilder):
        if self.op == "=" or self.op == "!=" or self.op == "<" or self.op == ">" or self.op == "<=" or self.op == ">=":            
            return ('xsd:boolean', True)
        elif self.op == "AND" or self.op == "OR":
            return ('xsd:boolean', True)        
        elif (self.op == "*" or self.op == "/" or self.op == "+" or self.op == "-"):
            return ('numeric', True)
        else:
            raise NotImlementedException('DataType unknown for result of operator %s'%self.op)
    
    def GetLanguageExp(self,sqlBuilder):
        return None

    def GetTermExpr(self,sqlBuilder):
        return "'L'"
    
    # output type depends on operator (comparison => xsd:boolean, etc.)
    
    def AdjustCostEstimate(self,cost,colDist):
        (costL, colDistL, varsL) = self.leftExp.AdjustCostEstimate(cost,colDist)
        (costR, colDistR, varsR) = self.rightExp.AdjustCostEstimate(cost,colDist)
        
        # for now, assume no change if both sides are constant; in practice we should set it to cost=0 if the condition is always FALSE
        if len(varsL) < 1 and len(varsR) < 1:
            return (cost, colDist, varsL)
         
        if len(varsL) < 1: 
            # swap so that the variable is on the left (only for the purposes of estimation!)
            (costL, colDistL, varsL, costR, colDistR, varsR) = (costR, colDistR, varsR, costL, colDistL, varsL)
        
        if self.op == "=": 
            if len(varsL) > 0 and len(varsR) > 0: # two variables
                # Cost(S)=Cost(R)/max(V(R,a),V(R,b)); V(S,a), V(R,b)= min(V(R,a),V(R,b)
                maxDistL = -1
                for v in varsL:
                    if maxDistL < 0 or colDistL[v] > maxDistL:
                        maxDistL = colDistL[v]
                maxDistR = -1
                for v in varsR:
                    if maxDistR < 0 or colDistR[v] > maxDistR:
                        maxDistR = colDistR[v]
                cost2 = cost/float(max(maxDistL,maxDistR))
#                prod = 1.0
#                for v in varsL & varsR:
#                    prod *= double(max(colDistL[v],colDistR[v]))
#                cost2 = cost/prod
                
                minColDist = -1
                vars2 = varsL | varsR
                for v in vars2:
                    if v in varsL and v in varsR:
                        colDist = min(colDistL[v],colDistR[v])
                    elif v in varsL:
                        colDist = colDistL[v]
                    else:
                        colDist = colDistR[v]
                    if minColDist < 0 or colDist < minColDist:
                        minColDist = colDist           
                colDist2 = colDist.copy()
                for v in vars2:
                    colDist2[v] = minColDist
                return (cost2, ColDistMax(colDist2,cost2), vars2)
            else: # a variable and a constant
                # Size(S)=Size(R)/V(R,a); V(S,a)=1
                minColDist = -1
                colDist2 = colDist.copy()
                for v in varsL:
                    colDist2[v] = 1
                    if minColDist < 0 or colDistL[v] < minColDist:
                        minColDist = colDistL[v]
                cost2 = cost / float(minColDist)
                return (cost2, ColDistMax(colDist2,cost2), varsL)                    
        elif self.op == "!=":
            if len(varsL) > 0 and len(varsR) > 0: # two variables
                # Cost(S)=Cost(R)-Cost(R)/max(V(R,a),V(R,b)); V(S,a)=V(R,a)                
                #prod = 1.0                
                #for v in varsL & varsR:
                #    prod *= float(max(colDistL[v],colDistR[v]))
                maxDistL = -1
                for v in varsL:
                    if maxDistL < 0 or colDistL[v] > maxDistL:
                        maxDistL = colDistL[v]
                maxDistR = -1
                for v in varsR:
                    if maxDistR < 0 or colDistR[v] > maxDistR:
                        maxDistR = colDistR[v]
                cost2 = cost - cost/float(max(maxDistL,maxDistR))
                
                colDist2 = colDist.copy()
                vars2 = varsL | varsR
                for v in vars2:
                    if v in varsL and v in varsR:
                        colDist2[v] = min(colDistL[v],colDistR[v])
                    elif v in varsL:
                        colDist2[v] = colDistL[v]
                    else:
                        colDist2[v] = colDistR[v]                        
                return (cost2, ColDistMax(colDist2,cost2), vars2)
            else: # a variable and a constant
                # Size(S)=Size(R)(V(R,a)-1)/V(R,a); V(S,a) = V(R,a)-1
                minColDist = -1
                colDist2 = colDist.copy()
                for v in varsL:
                    colDist2[v] = colDistL[v] - 1
                    if minColDist < 0 or colDistL[v] < minColDist:
                        minColDist = colDistL[v]
                cost2 = cost * ((minColDist - 1)/ float(minColDist))
                return (cost2, ColDistMax(colDist2,cost2), varsL)                    
                
        elif self.op == self.op == "<" or self.op == ">" or self.op == "<=" or self.op == ">=":
            # treating the same for 2 variable and variable/literal cases
            # Size(S)=Size(R)/3; V(S,a)=Ceil(V(R,a)/3) 
            cost2 = cost / 3.0
            colDist2 = colDist.copy()
            vars2 = varsL | varsR
            for v in vars2:
                if v in varsL and v in varsR:
                    colDist2[v] = math.ceil(min(colDistL[v],colDistR[v]) / 3.0)
                elif v in varsL:
                    colDist2[v] = math.ceil(colDistL[v] / 3.0)
                else:
                    colDist2[v] = math.ceil(colDistR[v] / 3.0)                        
            return (cost2, ColDistMax(colDist2,cost2), vars2)
        elif self.op == "AND": # AND
            # treat as consecutive selections
            return self.rightExp.AdjustCostEstimate(costL,colDistL)
        elif self.op == "OR": # OR
            cost2 = cost*float(1-((1-(costL/cost))*(1-(costR/cost))))
            # Size(S)=Size(R)(1-(1-Size(Q)/Size(R))(1-Size(U)/Size(R))); V(S,a)=max(V(T,a),V(U,a))
            colDist2 = colDist.copy() 
            vars2 = varsL | varsR
            for v in vars2:
                if v in varsL and v in varsR:
                    colDist2[v] = max(colDistL[v],colDistR[v])
                elif v in varsL:
                    colDist2[v] = colDistL[v]
                else:
                    colDist2[v] = colDistR[v]
            return (cost2, ColDistMax(colDist2,cost2), vars2)
        elif self.op == "*" or self.op == "/" or self.op == "+" or self.op == "-":
            # treating arithmetic as no change in selectivity/distinct values
            colDist2 = colDist.copy()
            vars2 = varsL | varsR
            for v in vars2:
                if v in varsL and v in varsR:
                    colDist2[v] = min(colDistL[v],colDistR[v])
                elif v in varsL:
                    colDist2[v] = colDistL[v]
                else:
                    colDist2[v] = colDistR[v] 
            cost2 = min(costL, costR)
            return (cost2, ColDistMax(colDist2,cost2), vars2)        
        raise Exception('Cost estimate unknown for result of operator %s'%self.op)
 
def ParseUnaryOperator(filter,prolog):
    op = RelUnaryExp()
    
    #TODO: do we need to do any post-processing for any of the operators?
    op.op = filter.NAME
    op.exp = ParseFilterExp(filter.argument,prolog)
    
    return op      

class RelUnaryExp(RelationalExpOperator):
    def __init__(self):
        self.exp = None
        self.op = None
            
    def __repr__(self):
        return "(%s %s)"%(self.op, self.exp)
    
    def GetDecendentLexicalComparators(self):
        for lexComp in self.exp.GetDecendentLexicalComparators():
            yield lexComp    
    
    def BuildSqlExpression(self,sqlBuilder):
        # terminal expressions are expected here
        if isinstance(self.exp,RelationalTerminalExpOperator):
            strExp = self.exp.BuildTerminalExpression(sqlBuilder)
        else:
            strExp = self.exp.BuildSqlExpression(sqlBuilder)
        
        if self.op == "!":
            opText = "NOT "
        else:
            opText = self.op 

        
        return "%s%s"%(opText, strExp)

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        return self.exp.GetUsedVariables(sqlBuilder,includeBNodes)
        
    def GetDataTypeExp(self,sqlBuilder):
        if self.op == "!":
            return ('xsd:boolean', True)
        elif (self.op == "+" or self.op == "-"):
            return ('numeric', True)
        else:
            raise NotImlementedException('DataType unknown for result of operator %s'%self.op)
            
    def GetLanguageExp(self,sqlBuilder):
        return None

    def GetTermExpr(self,sqlBuilder):
        return "'L'"
            
    def AdjustCostEstimate(self,cost,colDist):
        (costC, colDistC, varsC) = self.exp.AdjustCostEstimate(cost,colDist)
        
        # for now, assume no change if both sides are constant; in practice we should set it to cost=0 if the condition is always FALSE
        if len(varsC) > 0:
            return (costC, colDistC, varsC) 
        
        if self.op == "!": # NOT
            # Size(S)=Size(R)-Size(Q); V(S,a) = V(R,a)-V(Q,a)
            cost2 = cost - costC
            colDist2 = colDist.copy()
            for v in varsC:
                colDist2[v] = colDist[v] - colDistC[v]
            return (cost2, ColDistMax(colDist2,cost2), varsC)
        elif self.op == "+" or self.op == "-":
            # no change
            return (costC, ColDistMax(colDistC,costC), varsC)
        else:
            raise NotImlementedException('DataType unknown for result of operator %s'%self.op)
        
        
def ParseFunction(filter,prolog):
    func = RelFunctionExp()
    
    #TODO: implement, add more function types
    if isinstance(filter, ParsedREGEXInvocation):
        func.op = "REGEXP"
        func.args.append(ParseFilterExp(filter.arg1,prolog))
        func.args.append(ParseFilterExp(filter.arg2,prolog))
        if filter.arg3 != None:
            raise Exception("REGEX flags not supported.")
    elif isinstance(filter, FunctionCall):
        if FUNCTION_NAMES.has_key(filter.name):
            func.op = FUNCTION_NAMES[filter.name]
        else:
            func.op = str(filter.name)        
        for a in filter.arguments:
            func.args.append(ParseFilterExp(a,prolog))
        expectedArgs = -1
        if func.op == 'xsd:integer' or func.op == 'xsd:decimal' or func.op == 'xsd:float' or func.op == 'xsd:double':
            expectedArgs = 1
        elif func.op == 'xsd:string' or func.op == 'xsd:boolean' or func.op == 'xsd:dateTime' or func.op == 'xsd:date':
            expectedArgs = 1
        elif func.op == "STR" or func.op == "LANG" or func.op == "DATATYPE":
            expectedArgs = 1
        elif func.op == "BOUND":
            expectedArgs = 1
        elif func.op == "isIRI" or func.op == "isURI" or func.op == "isBLANK" or func.op == "isLITERAL":
            expectedArgs = 1
        elif func.op == "sameTERM" or func.op == "LANGMATCHES":
            expectedArgs = 2
        else:
            raise Exception("Unsupported function call: %s (%s)"%(func.op, repr(func)))        
        if expectedArgs != len(func.args):
            raise Exception("Unexpected number of arguments for function '%s': expected %s, but was given %s."%(func.op,expectedArgs, len(func.args)))         
    else:
        raise Exception("Unsupported function: %s"%(repr(filter)))

    return func

class RelFunctionExp(RelationalExpOperator):
    def __init__(self):
        self.op = None
        self.args = []
        
    def __repr__(self):
        rList = []
        for a in self.args:
            rList.append(repr(a))
        return "%s(%s)"%(self.op, ",".join(rList))
    
    def BuildSqlExpression(self,sqlBuilder):
        argList = []
        for a in self.args:
            # terminal expressions are expected here
            if isinstance(a,RelationalTerminalExpOperator):
                argList.append(a.BuildTerminalExpression(sqlBuilder))
            else:
                argList.append(a.BuildSqlExpression(sqlBuilder))
        
        #TODO: debug this -- especially use of args vs. already built argList!
        
        # handle special function formats        
        
        #WARNING: 'should be ok' indicates code has been reviewed, but may not have been tested!  (i.e. may be broken!)
        if self.op == "BOUND": 
            # tested
            if isinstance(self.args[0],RelVariableExp):
                varExpr = sqlBuilder.CombineSources(self.args[0].variable, VALUE_FIELD_NAME)
                if varExpr != "NULL":
                    return "%s IS NOT NULL"%(varExpr)
            return "FALSE" #Note: won't work in MySQL?
        elif self.op == "isIRI" or self.op == "isURI": 
            # should be ok
            if not isinstance(self.args[0],RelVariableExp):
                return str(isinstance(self.args[0], RelUriExp)).upper()
            varExpr = sqlBuilder.CombineSources(self.args[0].variable, TERM_FIELD_NAME)
            if varExpr != "NULL":
                return "%s = 'U'"%(varExpr)
            else:
                return "FALSE" # unbound            
        elif self.op == "isBLANK": 
            # should be ok for variable; constant version requires creating RelBNodeExp class for use of BNodes in FILTER expressions
            if not isinstance(self.args[0],RelVariableExp):
                raise NotImplementedException("isBLANK currently only supported for variables.")
                #return str(isinstance(self.args[0], BNode) or isinstance(argList[0], BNodeRef)).upper() #TODO: BNode in filter?
            if isinstance(self.args[0], RelVariableExp):
                varExpr = sqlBuilder.CombineSources(self.args[0].variable, TERM_FIELD_NAME)
                if varExpr != "NULL":
                    return "%s = 'B'"%(varExpr)
                else:
                    return "FALSE" # unbound         
            raise Exception("TODO: handle other types")
        elif self.op == "isLITERAL": 
            # tested
            if not isinstance(self.args[0],RelVariableExp):
                return str(isinstance(self.args[0], RelLiteralExp)).upper()
            if isinstance(self.args[0], RelVariableExp):
                varExpr = sqlBuilder.CombineSources(self.args[0].variable, TERM_FIELD_NAME)
                if varExpr != "NULL":
                    return "%s = 'L'"%(varExpr)
                else:
                    return "FALSE" # unbound   
            raise Exception("TODO: handle other types")
        elif self.op == "STR":
            # should be ok, except for BNode
            if not isinstance(self.args[0],RelVariableExp): #TODO: BNode in filter? #and not isinstance(argList[0], BNode):
                return "'%s'"%(self.args[0])            
            if isinstance(self.args[0], RelVariableExp):
                return sqlBuilder.CombineSources(self.args[0].variable, VALUE_FIELD_NAME)
            raise Exception("TODO: handle other types")
        elif self.op == "LANG":
            # should be ok
            if isinstance(self.args[0], RelLiteralExp):
                return "'%s'"%self.args[0].language
            if not isinstance(self.args[0], RelVariableExp):
                return '' # non-literal constant -- no language!
            if isinstance(self.args[0], RelVariableExp):
                varExpr = sqlBuilder.CombineSources(self.args[0].variable, LANGUAGE_FIELD_NAME)
                if varExpr != "NULL" and varExpr != None:
                    return "COALESCE(%s,'')"%(varExpr)
                else:
                    return "''" # unbound
            raise Exception("TODO: handle other types")
        elif self.op == "DATATYPE":
            # should be ok
            xsdString = (sqlBuilder.ConvertTerm(QName("xsd:string")))
            if isinstance(self.args[0], RelLiteralExp):
                if self.args[0].datatype == None:
                    return "'%s'"%str(xsdString)
                return self.args[0].datatype
            if isinstance(self.args[0], RelUriExp):
                return "'%s'"%str(xsdString)
            if isinstance(self.args[0], RelVariableExp):
                varExpr = sqlBuilder.CombineSources(self.args[0].variable, DATATYPE_FIELD_NAME)
                if varExpr != "NULL" and varExpr != None:
                    return "COALESCE(%s,'%s')"%(varExpr,str(xsdString))
                else:
                    return "NULL" # unbound
            elif isinstance(self.args[0],RelFunctionExp):
                dType,valid=self.args[0].GetDataTypeExp(sqlBuilder)
                if valid:
                    return "'%s'"%sqlBuilder.ConvertTerm(QName(dType))
                else:
                    raise
            # something else (function, etc.)
            return self.args[0].GetDataTypeExp(sqlBuilder)
        elif self.op == "sameTERM":
            #TODO: test
            term1 = argList[0]
            term2 = argList[1]
            if term1 == None or term2 == None:
                return "FALSE"
            if not isinstance(term1,Variable) and not isinstance(term1,BNode) and not isinstance(term2,Variable) and not isinstance(term2,BNode):
                # all literal
                return str(term1 == term2).upper()
            # get term 1 props
            valExpr1 = term1
            (dataTypeExpr1, isLit1) = term1.GetDataTypeExp(sqlBuilder)
            langExpr1 = term1.GetLanguageExp(sqlBuilder)
            termExpr1 = term1.GetTermExpr(sqlBuilder)
            # get term 2 props
            valExpr2 = term2
            (dataTypeExpr2, isLit2) = term2.GetDataTypeExp(sqlBuilder)
            langExpr2 = term2.GetLanguageExp(sqlBuilder)
            termExpr2 = term2.GetTermExpr(sqlBuilder)            
            # see if they are literal/non literal compatible
            if isLit1 != isLit2:
                return False            
            # add conditions
            conds = []
            if (isinstance(term1, Variable) or isinstance(term1, BNode)) and (isinstance(term2, Variable) or isinstance(term2, BNode)):
                # both variables
                conds.append("%s = %s"%(termExpr1, termExpr2))
                conds.append("%s = %s"%(valExpr1, valExpr2))
                if isLit1 == True:
                    conds.append("(%s = %s OR (%s IS NULL AND %s IS NULL))"%(dataTypeExpr1, dataTypeExpr2, dataTypeExpr1, dataTypeExpr2))
                    conds.append("(%s = %s OR (%s IS NULL AND %s IS NULL))"%(langExpr1, langExpr2, langExpr1, langExpr2))                    
            else:
                # one variable and one literal
                if isinstance(term2, Variable) or isinstance(term2, BNode):
                    # swap so term1 is the variable
                    (dataTypeExpr1, isLit1, langExpr1, termExpr1, dataTypeExpr2, isLit2, langExpr2, termExpr2) = (dataTypeExpr2, isLit2, langExpr2, termExpr2, dataTypeExpr1, isLit1, langExpr1, termExpr1)
                conds.append("%s = %s"%(termExpr1, termExpr2))
                conds.append("%s = %s"%(valExpr1, valExpr2))
                if isLit1 == True:
                    if datatypeExpr2 != NULL and datatypeExpr2 != None:
                        conds.append("%s = %s"%(dataTypeExpr1, dataTypeExpr2))
                    else:
                        conds.append("%s IS NULL"%(dataTypeExpr1))
                    if langExpr2 != NULL and langExpr2 != None:
                        conds.append("%s = %s"%(langExpr1, langExpr2))
                    else:
                        conds.append("%s IS NULL"%(langExpr1))                    
            return "(%s)"%(" AND ".join(conds))
        elif self.op == "LANGMATCHES":
            #TODO: test
            langTag = argList[0]
            langRange = argList[1]
            if isinstance(argList[0], URIRef):
                return "FALSE"
            if isinstance(langTag, Literal):
                if langRange == "*":
                    return str(langTag.language != None).upper()
                else:
                    return str(langTag.language == langRange).upper()
            varExpr = sqlBuilder.CombineSources(langTag, LANGUAGE_FIELD_NAME)
            if varExpr == "NULL" or varExpr == None:
                return "FALSE"
            if langRange == "*":
                return "LENGTH(COALESCE(%s,'')) > 0"%(varExpr)
            else:
                #TODO: preprocess langRange value to avoid chance of SQL injection attack 
                return "%s = '%s'"%(varExpr,langRange)
        elif self.op == "REGEXP":
            # tested
            return "(%s %s BINARY %s)"%(argList[0],self.op, argList[1]) # case senstive (SPARQL default)
            #return "(%s %s %s)"%(argList[0],self.op, argList[1]) # case insenstive (the "i" flag present)   
        #NOTE: these are also handled in RelFunctionExp
        elif self.op == "xsd:string":
            return "CAST(%s AS CHAR)"%(argList[0])
        elif self.op == 'xsd:integer':
            return "CAST(%s AS SIGNED)"%(argList[0])
        elif self.op == 'xsd:decimal':
            return "CAST(%s AS DECIMAL)"%(argList[0])
        elif self.op == 'xsd:float':
            return "CAST(%s AS DECIMAL)"%(argList[0]) # better type?
        elif self.op == 'xsd:double':
            return "CAST(%s AS DECIMAL)"%(argList[0]) # better type?
        elif self.op == 'xsd:boolean':
            return "CAST(%s AS SIGNED)"%(argList[0]) #TODO: what to do for CAST to boolean (xx == TRUE?; BIT?)??
        elif self.op == 'xsd:dateTime':
            return "CAST(%s AS DATETIME)"%(argList[0])
        elif self.op == 'xsd:date':
            return "CAST(%s AS DATE)"%(argList[0])
                      
        return "%s(%s)"%(self.op, ",".join(argList))   

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        s = set()
        for a in self.args:
            s = s | a.GetUsedVariables(sqlBuilder,includeBNodes)
        return s
        
    def GetDataTypeExp(self,sqlBuilder):
        if self.op == "BOUND" or self.op == "isIRI" or self.op == "isURI" or self.op == "isBLANK" or self.op == "isLITERAL":
            return ('xsd:boolean', True)
        elif self.op == "STR" or self.op == "LANG":
            return (None, True) # converted to simple literal string, no type
        elif self.op == "DATATYPE":
            return (None, True) # converted to IRI, which has no type
        elif self.op == "sameTERM" or self.op == "LANGMATCHES":
            return ('xsd:boolean', True)        
        elif self.op == "REGEXP":
            return ('xsd:boolean', True)  
        elif self.op == 'xsd:integer' or self.op == 'xsd:decimal' or self.op == 'xsd:float' or self.op == 'xsd:double':
            # cast to numeric
            return (self.op, True)     
        elif self.op == 'xsd:string' or self.op == 'xsd:boolean' or self.op == 'xsd:dateTime' or self.op == 'xsd:date':
            # casting functions
            return (self.op, True)     
        else:
            raise NotImplementedError()
    
    def GetLanguageExp(self,sqlBuilder):
        return None # is this correct?        
        
    def GetTermExpr(self,sqlBuilder):
        if self.op == "DATATYPE": # converted to URI
            return "'U'"
        return "'L'"        
        
    def AdjustCostEstimate(self,cost,colDist):
        (cost1, colDist1, vars1) = self.args[0].AdjustCostEstimate(cost,colDist)
#        varsMerge = vars1
#        colDistMerge = {}
#        for v in colDist1:
#            colDistMerge[v] = colDist1[v]
#        if len(self.args) > 1:
#            (cost2, colDist2, vars2) = self.args[1].AdjustCostEstimate(cost,colDist)
#            varsMerge = varsMerge | vars2
#            for v in colDist2:
#                if colDistMerge.has_key(v):
#                    colDistMerge[v] = min(colDistMerge[v], colDist2[v])
#                else:
#                    colDistMerge[v] = colDist2[v]
#        if len(self.args) > 2:
#            (cost3, colDist3, vars3) = self.args[2].AdjustCostEstimate(cost,colDist)
#            varsMerge = varsMerge | vars3
#            for v in colDist3:
#                if colDistMerge.has_key(v):
#                    colDistMerge[v] = min(colDistMerge[v], colDist3[v])
#                else:
#                    colDistMerge[v] = colDist3[v]
            
        if self.op == 'xsd:integer' or self.op == 'xsd:decimal' or self.op == 'xsd:float' or self.op == 'xsd:double' or self.op == 'xsd:string' or self.op == 'xsd:boolean' or self.op == 'xsd:dateTime' or self.op == 'xsd:date':
            # constructor functions (1 param) -- treat as no effect
            return (cost1, colDist1, vars1)
        elif self.op == "STR" or self.op == "LANG" or self.op == "DATATYPE":
            # treat as no effect (1 param)
            return (cost1, colDist1, vars1)
        elif self.op == "BOUND":
            #TODO: if variables can be NULL, then reduce estimate!
            # for now, treat as no effect (1 param)
            return (cost1, colDist1, vars1)            
        elif self.op == "isIRI" or self.op == "isURI" or self.op == "isBLANK" or self.op == "isLITERAL":
            # 1 param
            # Cost(S)=Cost(R)/x; V(S,a)=ceil(V(R,a)/x)
            #TODO: adjust estimate, based on which column/table for variable
            #      For subject, x=1/2 for isURI and isBlank and x=0 for isLiteral; for predicate, x=1 for isURI and x=0 for isBlank and isLiteral; for object, x=1/3 for all three
            
            # for now, assume 1/2 for all
            x = 2.0
            costF = cost1 / x
            colDistF = colDist.copy()
            for v in vars1:
                colDistF[v] = math.ceil(colDist1[v] / x)
            return (costF, ColDistMax(colDistF,costF), vars1)
        #elif func.op == "sameTerm":
        #    (cost2, colDist2, vars2) = self.args[1].AdjustCostEstimate(cost,colDist)
            #TODO: treat like equals
            
        elif self.op == "LANGMATCHES":
            # only first param can be a variable
            if self.args[2] == "*":
                # no change
                return (cost1, colDist1, vars1)
            # assuming 1/2 reduction (i.e. two languages)
            x = 2.0
            costF = cost1 / x
            colDistF = colDist.copy()
            for v in vars1:
                colDistF[v] = math.ceil(colDist1[v] / x)
            return (costF, ColDistMax(colDistF,costF), vars1)            
        elif self.op == "REGEXP":
            # only first param can be a variable
            #TODO: should treat exact string like EQUALS and 'match all' as unchanged
            
            # otherwise, assuming 1/3 reduction
            x = 3.0
            costF = cost1 / x
            colDistF = colDist.copy()
            for v in vars1:
                colDistF[v] = math.ceil(colDist1[v] / x)
            return (costF, ColDistMax(colDistF,costF), vars1)        
                
        raise NotImplementedError()
        
class RelTypeCastExp(RelationalExpOperator):
    def __init__(self, dataType, exp):
        self.dataType = dataType
        self.exp = exp
        
    def __repr__(self):
        return "CAST(%s,%s)"%(repr(self.exp),repr(self.dataType))
    
    def BuildSqlExpression(self,sqlBuilder):
        outputType = None

        # MySQL Casting Types:
        # CHAR
        # BINARY
        # DATE
        # DATETIME
        # DECIMAL[(M[,D])]
        # SIGNED [INTEGER]
        # TIME
        # UNSIGNED [INTEGER]
        
        # note that these are also handled in RelFunctionExp
        if str(self.dataType) == "xsd:string":
            outputType = "CHAR"            
        elif str(self.dataType) == 'xsd:integer':
            outputType = "SIGNED"            
        elif str(self.dataType) == 'xsd:decimal':
            outputType = "DECIMAL"            
        elif str(self.dataType) == 'xsd:float':
            outputType = "DECIMAL" # better type?
        elif str(self.dataType) == 'xsd:double':
            outputType = "DECIMAL" # better type?            
        elif str(self.dataType) == 'xsd:boolean':
            outputType = "SIGNED" #TODO: what to do for CAST to boolean (xx == TRUE?; BIT?)??
        elif str(self.dataType) == 'xsd:dateTime':        
            outputType = "DATETIME"            
        elif str(self.dataType) == 'xsd:date':        
            outputType = "DATE"            
        else:
            sqlBuilder.AddWarning("Unknown cast type: %s.  Expression used without SQL CAST.")
            #raise Exception("Unexpected cast type: %s"%(self.dataType))
            outputType = None
        
        childExp = None
        if isinstance(self.exp,RelationalTerminalExpOperator):
            childExp = self.exp.BuildTerminalExpression(sqlBuilder)
        else:
            childExp = self.exp.BuildSqlExpression(sqlBuilder)
            
        if outputType != None: 
            return "CAST(%s AS %s)"%(childExp, outputType)
        else:
            return childExp

    def GetUsedVariables(self,sqlBuilder,includeBNodes=True):
        return self.exp.GetUsedVariables(sqlBuilder,includeBNodes)
    
    def GetDataTypeExp(self,sqlBuilder):
        return (str(self.dataType), True)
    
    def GetLanguageExp(self,sqlBuilder):
        return None

    def GetTermExpr(self,sqlBuilder):
        return "'L'" 
    
    def AdjustCostEstimate(self,cost,colDist):
        # no effect
        return self.exp.AdjustCostEstimate(cost,colDist)
