# -*- coding: utf-8 -*-

import rdflib
from rdflib.graph import ConjunctiveGraph
from rdflib.store.FOPLRelationalModel.QuadSlot import *
from rdflib.term import Literal, URIRef, Variable, BNode
from rdflib.namespace import Namespace
from rdflib.sparql.bison.QName import *
from rdflib.sparql.bison.Expression import *

from SqlBuilder import *
from QueryCostEstimator import *

# Optimization enumeration constants
#====================================
# Newly proposed simplifications
OPT_PUSH_DISTINCT = "PushDistinct"      # push down DISTINCT to nested queries
OPT_PAD_UNION = "PadUnion"              # replace outer join with "'NULL' as missingColumn" for making shemas agree for UNION
OPT_FLATTEN = "Flat"            # unnest SQL queries as much as possible:
#OPT_FLAT_BGP = "FlatBGP"        # flatten BGP/Triples (effectively done via AND)
OPT_FLAT_OPTIONAL = "FlatOpt"   # flatten optional graph patterns
OPT_FLAT_SELECT = "FlatSelect"  # flatten select queries (except for string value joins)
OPT_FLAT_FILTER = "FlatFilter"  # flatten filter expressions
OPT_FLAT_AND = "FlatAnd"        # flatten AND graph patterns
OPT_FLAT_UNION = "FlatUnion" # flatten UNION graph patterns

# Previously proposed simplifications (see Chebotko et al., 2007 Tech Report)
OPT_C2_SKIP_COALESCE = "C2SkipCoalesce"     # [done] if no outer joins used (Chebotko 2007TR: Simp. 2)
OPT_C3_SIMPLIFY_JOIN = "C3SimplifyJoin"     # [done] if URI or literal, or not outer joins (Chebotko 2007TR: Simp. 3)
OPT_C5_SKIP_UNION_JOIN = "C5SkipUnionJoin"  # skip left outer join in UNION if schemas are the same (Chebotko 2007TR: Simp. 5)
OPT_C6_PROJECT_EARLY = "C6ProjectEarly"       # [done] only keep columns in output or used in FILTERs, etc. (Chebotko 2007TR: Simp. 6)
    #NOTE: we always do Chebotko, 2007TR Simplifications: 
    #     Simp. 1 (skip projection on non-variables)
    #     Simp. 4 (remove 'TRUE AND...')

# Triple pattern ordering
OPT_JOIN_STRAIGHT_JOIN = "StraightJoin"  # force evaluation in same order
OPT_JOIN_GREEDY_SMALL_STATS = "JoinGreedySmall"     # greedy ordering algorithm (Garcia-Molina et al. 2000) with stats that use small space
OPT_JOIN_GREEDY_MED_STATS = "JoinGreedyMedium"      # greedy algorithm with stats that use medium space 
OPT_JOIN_GREEDY_LARGE_STATS = "JoinGreedyLarge"     # greedy algorithm with stats that use larger space
OPT_JOIN_GREEDY_ALL_PATTERNS = "JoinGreedyHarth"   # greedy algorithm using triple patterns storing all triple patterns (Harth et al. 2005)
OPT_JOIN_GREEDY_STOCKER_STATS = "JoinGreedyStocker" # greedy algorithm using triple patterns estimated by Stocker et al. 2008  
OPT_JOIN_GREEDY_SELECTION = "JoinGreedySelection" # greedy algorithm uses selections as part of estimate
OPT_JOIN_STOCKER08 = "JoinStocker" 
OPT_JOIN_RANDOM = "JoinRandom"  
#====================================

DEFAULT_OPT_FLAGS = {
    OPT_PAD_UNION:True,
    OPT_FLATTEN:True,
    OPT_C2_SKIP_COALESCE:True,
    OPT_C3_SIMPLIFY_JOIN:True,
    OPT_C6_PROJECT_EARLY:True,
    OPT_JOIN_GREEDY_STOCKER_STATS:True, #NOTE: may want to use a different set of statistics with greedy ordering algorithm
    OPT_JOIN_GREEDY_SELECTION:True #NOTE: initial experiments were unclear if this was helping in all cases; may want to disable?
                     }

# Query evaluation options
#====================================
EVAL_OPTION_STRICT_DATATYPE = "StrictDataType"   # enforce strict data type matching for literals in triple patterns and filter expressions:
                                                 # -if enabled, literal matching behaves as http://www.w3.org/TR/rdf-concepts/#section-Literal-Equality 
                                                 # -if disabled, untyped literals can be matched with typed literals
EVAL_OPTION_ALLOW_BNODE_REF = "BNodeRef"         # enables support for using "_:x" to reference a named BNode in the graph instead of being treated as an undistinguished variable (as per the SPARQL spec)

# default evaluation options if not overridden at runtime
DEFAULT_EVAL_OPTIONS = {
   EVAL_OPTION_STRICT_DATATYPE: True,
   EVAL_OPTION_ALLOW_BNODE_REF: True}

#ACTIVE_EVAL_OPTIONS = {}
#
#def UseEvalOption(name):
#    """
#    Returns True if the named evaluation option has been enabled,
#    False otherwise.  Evaluation options changed the behavior
#    of query execution.
#    """
#    if ACTIVE_EVAL_OPTIONS.has_key(name):
#        return ACTIVE_EVAL_OPTIONS[name]
#    if DEFAULT_EVAL_OPTIONS.has_key(name):
#        return DEFAULT_EVAL_OPTIONS[name]
#    return False
#
#def SetEvalOption(name, value):
#    """
#    Enables/Disables a named evaluation option.  
#    'value' should be True or False.
#    """    
#    DEFAULT_EVAL_OPTIONS[name] = value
#    
#def ResetEvalOptions():
#    ACTIVE_EVAL_OPTIONS = {}        
#====================================


class ViewTable(object):    
    """
    Used to provide the same interface for view as available
    to the partition tables.
    """
    
    def __init__(self):
        self.columnNames = []
        self.table = None  
              
    def __repr__(self):
        return self.table
    
class TriplesTable(ViewTable):
    """
    Used to provide the same interface for the all triples view as available
    to the partition tables.
    """
    
    def __init__(self, graph):
        self.columnNames = ['subject', 'predicate', 'object', 'context', 'data_type', 'language']
        self.table = graph.store._internedId + '_all'
        self.hardCodedResultTermsTypes = None
        

class AllObjectsTable(ViewTable):
    """
    Used to provide the same interface for the all all objects view as available
    to the identifier/literal tables.
    """
    
    def __init__(self, graph):
        self.columnNames = ['id', 'term_type', 'lexical']
        self.table = graph.store._internedId + '_all_objects'
        
# Field Types
VALUE_FIELD_NAME = 0
TERM_FIELD_NAME = 1
DATATYPE_FIELD_NAME = 2
LANGUAGE_FIELD_NAME= 3

class RdfVariable(object):
    """
    Helper class that stores info about an available variable instance in a (sub-)query. 
    """
    
    def __init__(self, name, tableTuple, fieldName, termFieldName, dataTypeFieldName, languageFieldName, sources, isBNode):
        self.name = name
        self.tableTuple = tableTuple
        self.fieldName = fieldName
        self.termFieldName = termFieldName
        self.dataTypeFieldName = dataTypeFieldName
        self.languageFieldName = languageFieldName
        self.sources = sources
        self.isBNode = isBNode
    
    def GetField(self, fieldType): 
        if fieldType == VALUE_FIELD_NAME:
            return self.fieldName
        elif fieldType == TERM_FIELD_NAME:
            return self.termFieldName
        elif fieldType == DATATYPE_FIELD_NAME:
            return self.dataTypeFieldName
        elif fieldType == LANGUAGE_FIELD_NAME:
            return self.languageFieldName
    
    def __repr__(self):
        #TODO: possibly rewrite name to ensure it is SQL-friendly!
        return self.name

    def AddSources(self, sources):
        #for s in sources:
        #    self.sources.append(s)
        self.sources.extend(sources)

    def IsLiteralField(self):
        for s in self.sources:
            if s.literalField:
                return True
        return False

    def Clone(self, tableTuple, fieldName, termFieldName, dataTypeFieldName, languageFieldName):
        return RdfVariable(self.name, tableTuple, fieldName, termFieldName, dataTypeFieldName, languageFieldName, self.sources, self.isBNode)

def EmptyVar(vname):
    return RdfVariable(vname, None, None, None, None, None, [],False)

class RdfVariableSource(object):
    """
    Helper class that stores info about where variables came from (partition table, column)
    """
    
    def __init__(self, table, pos, literalField):
        self.table = table
        self.pos = pos
        self.literalField = literalField
        self.forcedNonLiteral = False # set later if we can reason that this variable must not be literal (i.e. for 'all' table)

class BNodeRef(BNode):
    """
    An explicit reference to a persistent BNode in the data set.
    This use of the syntax "_:x" to reference a named BNode is
    technically in violation of the SPARQL spec, but is also
    very useful.  If an undistinguished variable is desired,
    then an actual variable can be used as a trivial workaround.
    
    Support for these can be disabled by disabling the 
    'EVAL_OPTION_ALLOW_BNODE_REF' evaulation option.
    
    Also known as special 'session' BNodes.  I.e., BNodes at the query side which refer to 
    BNodes in persistence
    """
    pass  
 

try:
    from Ft.Lib.Uri import UriResolverBase as Resolver
except:
    class Resolver:
        supportedSchemas=[None]
        def normalize(self, uriRef, baseUri):
            return baseUri+uriRef
    
class RdfSqlBuilder(SqlBuilder):
    """
    Provides methods and state specific to the construction of SQL from SPARQL.
    
    Used by the RelationalAlgebra parsing functions and RelationalOperator-derived classes in
    their BuildSql() method implementations. 
    """
    
    def __init__(self, graph, parentBuilder = None, rootBuilder = None, optimizations = {}):
        self.Reset(rootBuilder)
        self.isAsk = False
        self.graph = graph
        self.parentBuilder = parentBuilder
        
        if self.rootBuilder is self:
            self.tables = dict(type = graph.store.aboxAssertions,
                      lit = graph.store.literalProperties,
                      rel = graph.store.binaryRelations,
                      all = TriplesTable(graph),
                      idObj = graph.store.idHash,
                      litObj = graph.store.valueHash,
                      #litObj = graph.store.hashes[1], #TODO: better way to reference this table?
                      allObj =  AllObjectsTable(graph))
#            self.identifierTable = graph.store.idHash
#            self.literalTable = graph.store.hashes[1] #TODO: better way to reference this table?
            # cache into about rdfs:type property
            self.typeUri = self.tables['type'].hardCodedResultFields[PREDICATE]
            self.typeHash = self.GetUriHash(self.typeUri)
            # convert property type lists to hashtables for speed
            self.literal_properties = {}
            for prop in self.graph.store.literal_properties:
                self.literal_properties[str(prop)] = True            
            self.resource_properties = {}
            for prop in self.graph.store.resource_properties:
                self.resource_properties[str(prop)] = True   
            # bindings
            self.variableBindings = {}
            self.prefixBindings   = {}
                    
            self.baseDeclaration = None
            # optimizations
            self.optimizations = optimizations
            # eval options
            self.evalOptions = {}
            for o in DEFAULT_EVAL_OPTIONS:
                self.evalOptions[o] = DEFAULT_EVAL_OPTIONS[o]
                
            # query cost estimation
            if graph.store.stats:
                self.costEstimator = QueryCostEstimator(self,graph.stats) #TODO: get stats here!
            else:
                self.costEstimator = None
            self.joinOrdering = 0
            self.joinOrderTime = 0
            self.joinOrders = []
            self.joinEstimatedCost = 0
            self.joinEstimatedCostSum = 0
            self.filterStack = []
            
            self.fromList = []
            self.fromNamedList = []

            self.nextAlias = 0
            self.aliasMap = {}
            self.columnMap = {}
                
    def Reset(self, rootBuilder):
        SqlBuilder.Reset(self,rootBuilder)
        self.variables = {}
        self.requiredVariables = {}
        self.coalesceVars = {}
        self.stringVariables = {}
        self.optionalWhereStack = [] # list of lists of strings
        
        if self.rootBuilder is self:
            self.nestedQueries = 0
            self.errors = []
            self.warnings = []
            #self.variableSources = {}

    def Sql(self):
        # set additional flags
        
        if (self.UseOptimization(OPT_JOIN_STRAIGHT_JOIN) or
            self.UseOptimization(OPT_JOIN_GREEDY_SMALL_STATS) or
            self.UseOptimization(OPT_JOIN_GREEDY_MED_STATS) or
            self.UseOptimization(OPT_JOIN_GREEDY_LARGE_STATS) or
            self.UseOptimization(OPT_JOIN_GREEDY_ALL_PATTERNS) or
            self.UseOptimization(OPT_JOIN_GREEDY_STOCKER_STATS) or
            self.UseOptimization(OPT_JOIN_STOCKER08) or
            self.UseOptimization(OPT_JOIN_RANDOM)):
            # force join order
            if self.graph.store.select_modifier:
                self.SetFlag(FLAG_STRAIGHT_JOIN, True)
        
        return SqlBuilder.Sql(self)        

    def UseOptimization(self, name):
        """
        Returns True if the named optimization has been enabled,
        False otherwise.
        """
        if not self.rootBuilder.optimizations.has_key(name):
            return False
        return self.rootBuilder.optimizations[name]
        
    def SetOptimization(self, name, value):
        """
        Enables/Disables a named optimization.  
        'value' should be True or False.
        """
        self.rootBuilder.optimizations[name] = value
        
    def GetQueryCostEstimator(self):
        return self.rootBuilder.costEstimator

    def UseEvalOption(self, name):
        """
        Returns True if the named evaluation option has been enabled,
        False otherwise.  Evaluation options changed the behavior
        of query execution.
        """
        if not self.rootBuilder.evalOptions.has_key(name):
            return False
        return self.rootBuilder.evalOptions[name]
        
    def SetEvalOption(self, name, value):
        """
        Enables/Disables a named evaluation option.  
        'value' should be True or False.
        """
        self.rootBuilder.evalOptions[name] = value

    def SetBaseDeclaration(self, base):
        self.rootBuilder.baseDeclaration = base

    def AddVariableBinding(self, var, val):
        self.rootBuilder.variableBindings[var] = val          

    def SetParamValue(self,name,value):
        # Need to convert URI and literals to their Hash values in most cases
        #   (except possibly within filters!)

        #vterm = self.GetTermHash(value)
            
        SqlBuilder.SetParamValue(self, name, value)
            
    def GetNestedSQLBuilder(self):
        """
        Creates a child RdfSqlBuilder to be used to
        create a child sub-query for the current query.
        
        However, typically, the client code uses RelationalOperator.AddNestedOp() 
        instead of call this function directly unless special 
        handling is needed (used in RelationalSelect.BuildSql()).
        
        Each call to this function should be followed by
        a call to AddChildVariables() _after_ child
        sub-queries have been built (using BuildSql())!
        """
        child = RdfSqlBuilder(self.graph, self, self.rootBuilder)
        
        #TODO: figure out if other properties should be pushed to child queries!
        
        #OPTIMZE: push distinct down to sub-queries
        if self.UseOptimization(OPT_PUSH_DISTINCT):
            child.selectDistinct = self.selectDistinct
            
        #OPTIMIZE: keep track of required variables needed at each level of (sub-)query
        if self.UseOptimization(OPT_C6_PROJECT_EARLY):
            for reqVar in self.requiredVariables:
                child.SetRequiredVariable(reqVar)                
            
        # increment count of nested queries
        self.rootBuilder.nestedQueries += 1
            
        return child

    def MakeSqlVarAlias(self, var):
        """
        SQL column aliases are NOT case sensitive,
        so we need to map each unique alias case
        to a different SQL alias.  We do this by
        appending a number at the end.  Note that
        these renamed alias must be global across
        all nested queries to enable correct implementation
        of SPARQL UNION. 
        """
        vname = str(var)
        if self.rootBuilder.aliasMap.has_key(vname):
            return self.rootBuilder.aliasMap[vname]
        # this alias has not been seen before
        sqlAlias = "%s_a%s"%(vname.lower(), self.rootBuilder.nextAlias)
        self.rootBuilder.nextAlias += 1
        self.rootBuilder.aliasMap[vname] = sqlAlias
        self.rootBuilder.columnMap[sqlAlias] = vname
        return sqlAlias

    def GetSqlVarAlias(self, var):
        vname = str(var)
        if self.rootBuilder.aliasMap.has_key(vname):
            return self.rootBuilder.aliasMap[vname]
        return None
    
    def GetAliasForColumn(self,col):
        if self.rootBuilder.columnMap.has_key(col):
            return self.rootBuilder.columnMap[col]
        return None
        

#    def MakeSqlAlias(self, alias):
#        if self.outputMap.has_key(alias):
#            raise Exception("BUG: MakeSqlAlias called more than once for output alias '%s'!"%(alias))
#        if alias.lower() in self.outputFields:
#            # duplicate need a different alias!
#            n = 0
#            while alias.lower() + "_alias" + n in self.outputFields:
#                n += 1
#            sqlAlias += "_alias" + n
#        else:
#            sqlAlias = alias
#            self.outputFields.add(alias.lower())
#        self.outputMap[alias] = sqlAlias        
#        return sqlAlias        
#
#    def GetSqlAlias(self, alias):
#        if not self.outputMap.has_key(alias):
#            return None
#        return self.outputMap[alias]

    def OptionalWhereStackPush(self):
        """
        Where conditions inside of an OPTIONAL clause must be 
        put in the SQL ON-clause of the LEFT OUTER JOIN, otherwise
        they will invalidate the LEFT OUTER JOIN (i.e. no NULL values returned).
        
        Thus, when flattening one (or more) OPTIONAL, we use 
        a stack of lists of WHERE conditions (strings) to store
        the conditions that belong in the current ON clause.
        This function must be called before adding any conditions needed
        within the OPTIONAL clause;  OptionalWhereStackPop() must be
        called when the OPTIONAL clause has been fully processed.
        
        Having at least one element on this stack causes the behavior
        of SqlBuilder.AddWhere() to write to the list on the top of
        this stack instead. 
        
        This function has no arguments since we always start with an empty list of conditions.
        """
        self.optionalWhereStack.append([])
    
    def OptionalWhereStackPop(self):
        """
        Obtain all WHERE conditions added since the last call to 
        OptionalWhereStackPush().
        """
        return self.optionalWhereStack.pop()

    def AddWhere(self, condition):
        if len(self.optionalWhereStack) < 1:
            # normal behavior
            SqlBuilder.AddWhere(self, condition)
        else:
            # write to list of OPTIONAL conditions
            self.optionalWhereStack[-1].append(condition)
            
    def FilterStackPush(self, filter):
        """
        Used to keep track of which filters are the ancestors of BGPs
        for the use of FILTERs for triple pattern ordering cost estimates.
        """
        self.rootBuilder.filterStack.append(filter)
        
    def FilterStackPop(self):
        return self.rootBuilder.filterStack.pop()
    
    def CurrentFilters(self):
        return self.rootBuilder.filterStack

    def AddFrom(self,fromItem):
        self.rootBuilder.fromList.append(fromItem)

    def GetFromList(self):
        return self.rootBuilder.fromList

    def AddFromNamed(self,fromNamedItem):
        self.rootBuilder.fromNamedList.append(fromNamedItem)

    def GetFromNamedList(self):
        return self.rootBuilder.fromNamedList

    # New var code
    
    def SetCoalesceVariable(self, varName):
        """
        Indicates that the available variable instances for 
        a given variable name must be combined using COALESCE()
        instead of picking the first one (i.e. due to OPTIONAL).
        
        Note that once this is set, we are saying that a variable
        may contain a NULL (unbound) value and we will need to use
        COALESCE with this variable in all parent queries as well.  
        """
        #varName = varName.lower() #BE: currently assuming variables are not case-sensitive
        self.coalesceVars[varName] = True
        if self.parentBuilder != None: # push to ancestors
            self.parentBuilder.SetCoalesceVariable(varName)
        
    def IsCoalesceVariable(self, varName):
        #varName = varName.lower() #BE: currently assuming variables are not case-sensitive
        return self.coalesceVars.has_key(varName)  
    
    def SetRequiredVariable(self, varName, value=True):
        """
        Indicates that the current (sub-)query must
        return the specified variable name because
        it will be used in the parent/ancestor query. 
        
        Variables are required when:
            1) specified in SELECT clause
            2) used in a FILTER clause
        """
        #varName = varName.lower() #BE: currently assuming variables are not case-sensitive
        self.requiredVariables[varName] = value
        
    def IsRequiredVariable(self, varName):
        #varName = varName.lower() #BE: currently assuming variables are not case-sensitive
        return self.requiredVariables.has_key(varName)
    
    def AddPatternVariable(self, rdfVar):
        """
        Add a new available variable to this (sub-)query,
        which comes from a triple/graph pattern.
        
        Note that variables are provided by either: 
            1) a triple pattern (using this function)
            2) from a child sub-query (using AddChildVariables())
            
        For variables from patterns, we must record _all_
        tables/columns where the variable came from and 
        have this available to decide which metadata columns we
        need (i.e. for literal columns that need data_type and language).
        
        If a variable is available from more than one place, then we must
        either COALESCE (if OPTIONAL appears) or pick one (simple JOIN) as the output.
        """
        varName = rdfVar.name #.lower() #BE: currently assuming variables are not case-sensitive
        if not self.variables.has_key(varName):
            self.variables[varName] = []
        self.variables[varName].append(rdfVar)
    
    def AddChildVariables(self, childBuilder, tableTuple):
        """
        Add the available variables returned from a sub-query
        to the set of available variables for this query. 
        
        Need to combine the table source info for each variable and 
        insert a single available variable.
        """
        for vname in childBuilder.variables:
            hasDataType = False
            hasLang = False
            for v in childBuilder.variables[vname]:
                if v.dataTypeFieldName != None:
                    hasDataType = True
                if v.languageFieldName != None:
                    hasLang = True
                    
            if hasDataType:
                #dataTypeFn = '%s.%s_data_type'%(tableTuple, vname)  
                dataTypeFn = '%s.%s'%(tableTuple, childBuilder.GetSqlVarAlias(vname + '_data_type'))  
            else:
                dataTypeFn = None          
            if hasLang:
                #langFn = '%s.%s_language'%(tableTuple, vname)
                langFn = '%s.%s'%(tableTuple, childBuilder.GetSqlVarAlias(vname + '_language'))
            else:
                langFn = None
            
            #fn = '%s.%s'%(tableTuple, vname)
            #termFn = '%s.%s_term'%(tableTuple, vname)
            fn = '%s.%s'%(tableTuple, childBuilder.GetSqlVarAlias(vname))
            termFn = '%s.%s'%(tableTuple, childBuilder.GetSqlVarAlias(vname + '_term'))
            var = childBuilder.variables[vname][0].Clone(tableTuple, fn, termFn, dataTypeFn,langFn) # field name will always become the variable name in the parent query
            if len(childBuilder.variables[vname]) > 1:
                for v in childBuilder.variables[vname][1:len(childBuilder.variables[vname])]:
                    var.AddSources(v.sources) # combine source tables from all of child's available versions of variable into one version for this one
                    
            if not self.variables.has_key(vname):
                self.variables[vname] = []            
            self.variables[vname].append(var)
            
            #union -- add other branch
            if childBuilder.unionBuilder != None:
                (unionBuilder, unionAll) = childBuilder.unionBuilder
                self.AddChildVariables(unionBuilder, tableTuple)
                
    
    def GetAvailableVariable(self, varName):
        """
        Check the current query for a definition of this variable.
        This must come from either:
            1) Triple pattern in this (sub-)query
            2) Variable from a child sub-query
            3) Variable defined in a parent/ancestor query (which is available to nested sub-queries)
        """
        #varName = varName.lower() #BE: currently assuming variables are not case-sensitive
        if not self.variables.has_key(varName):
            return None
        return self.variables[varName]
    
    def GetAvailableVariables(self):
        """
        Get the variable names immediately available to this
        (sub-)query.  These are defined in either triple
        patterns in this query or come from child sub-queries.
        """
        vars = []
        for v in self.variables:
            vars.append(v)
        return vars
    
    def IsAvailableVariable(self, vname):
        #vname = vname.lower() #BE: currently assuming variables are not case-sensitive
        return self.variables.has_key(vname)
    
    def GetReturnedVariables(self):
        """
        The variables to be returned are the parent query's 
        required variables that are available.
        
        If no variables are required by the parent query, 
        return all variables (i.e. for SELECT *).
        """
        if self.parentBuilder != None:
            reqVars = [i for i in self.parentBuilder.requiredVariables]
        else:
            reqVars = [i for i in self.requiredVariables] # root query currently set to use its own required vars.

        vars = []
        if len(reqVars) < 1 or not self.UseOptimization(OPT_C6_PROJECT_EARLY):
            # return all available
            for v in self.variables:
                vars.append(v)
        else:
            for v in reqVars:
                if self.variables.has_key(v):
                    vars.append(v) # safe to return            
                #else:
                #    self.AddWarning('Required variable not found: %s'%v)
            if len(vars) < 1 and len(self.variables) > 0:
                # nothing listed as required (disconnected graph cross product??)

                #self.AddWarning("Disconnected subgraph with no required variables (is this on purpose?).")
                                
                #NOTE: one way to fix this problem is to remove the OPT_C6_PROJECT_EARLY optimization flag!
                
                #TODO: if we want to support disconnected subgraphs that are not returned:
                #       need to return all these variables to be returned here and all nested child queries 
                #       need all their variables set as 'required' _BEFORE_ they are converted to strings (i.e. right here is too late);
                #        In addition; these variables must be set as required for all ancestor operators.
                #NOTE: this is only an issue for NESTED queries (i.e. when flattening is used, UNION with one side of the union never being used)
                raise Exception("Disconnected subgraph with no required variables (i.e. contributing nothing to the final query except adding a cross product).")

                # return all available
                #for v in self.variables:
                #    vars.append(v)
        return vars
    
    def GetVariableSources(self, varName):
        """
        Return all tables/columns that have been 
        combined to form the returns for this variable.
        This determines which additional metadata columns
        need to be returned (i.e. for literals). 
        """
        sources = []
        #varName = varName.lower() #BE: currently assuming variables are not case-sensitive
        if not self.variables.has_key(varName):
            return []
        for v in self.variables[varName]:
            sources.extend(v.sources)
        return sources
        
    def ConvertTerm(self, term):
        """
        Utility function  for converting parsed Triple components into Unbound 
        
        Note: Ported from SPARQLEvaluate.py: convertTerm()
        """        
        from rdflib.sparql.bison.SPARQLEvaluate import convertTerm
        return convertTerm(term, self.rootBuilder)

    def GetTermHash(self, value):
        if value == None:
            return None
        
        #vterm = self.ConvertTerm(value)

        #TODO: handle BNode hashing for get 'told' (named) BNodes

        if isinstance(value, URIRef):
            vterm = self.GetUriHash(value)
        elif isinstance(value, Literal):
            vterm = self.GetLiteralHash(value)
        elif isinstance(value, BNodeRef): # treating BNode in query as the reference to a named BNode in the graph
            vterm = self.GetBNodeHash(value)
        else:
            #print repr(value), type(value)
            raise Exception("BUG: Raw parser term not converted to RDFLib object: type=%s (value=%s)"%(type(value),repr(value)))
        
        return vterm
        
    def GetUriHash(self, uri):
        return normalizeValue(uri, 'U', self.graph.store.useSignedInts)
    
    def GetLiteralHash(self, lit):
        return normalizeValue(lit, 'L', self.graph.store.useSignedInts)
    
    def GetBNodeHash(self, bnode):
        return normalizeValue(bnode, 'B', self.graph.store.useSignedInts)
    
    def AddWarning(self, message):
        #TODO: display warning on console as well
        import warnings
        warnings.warn(message)
        self.rootBuilder.warnings.append(message)
        print "WARNING: " + message
    
    def AddError(self, message):
        self.rootBuilder.errors.append(message)
        
    def GetTable(self,name):
        return self.rootBuilder.tables[name]
    
    def IsLiteralProperty(self,prop):
        return self.rootBuilder.literal_properties.has_key(str(prop))
    
    def IsResourceProperty(self,prop):
        return self.rootBuilder.resource_properties.has_key(str(prop))
    
    def TripleTable(self, tp):
        """
        This is the 'alpha' function from Chebotko 2007(TR):
        'For a triple pattern tp, alpha(tp) is a relation in which all the triples
        that may match tp are stored.'
        """
        pred = tp.pred # self.ConvertTerm(tp.pred)
        if pred == self.rootBuilder.typeUri:
            return self.GetTable('type')
        if isinstance(tp.obj,Literal) or  self.IsLiteralProperty(pred):
            return self.GetTable('lit')
        if ((not isinstance(tp.obj,Literal) and not isinstance(tp.obj,Variable)) 
                or self.IsResourceProperty(pred)):
            return self.GetTable('rel')
        
        if tp.allPartitions == False: # only warn once
            self.AddWarning("Could not determine partition table for triple pattern '%s'. Must search all!"%(tp))
            tp.allPartitions = True
        return self.rootBuilder.tables['all']
        
    def TripleColumn(self, tableTuple, table, pos):
        """ 
        This is the 'beta' function from Chebotko 2007(TR):
        'For a triple pattern tp and a position pos (i.e. SUBJECT, PREDICATE, OBJECT, [CONTEXT]),
        beta(tp,pos) is a relational attribute whose value may match tp at position pos.'
        """
        if table.columnNames[pos] is None:            
            #add missing column for type table 'hash(rdfs:type)' AS pred
            # table.hardCodedResultFields[pos]
            
            #TODO: rewrite generically if additional hardCodedResultFields are added!
            return ("CONVERT('%s',UNSIGNED INTEGER)"%self.rootBuilder.typeHash, "'U'")
        if pos > CONTEXT:
            valueTuple = "%s.%s"%(tableTuple, table.columnNames[pos][0])
        else:
            valueTuple = "%s.%s"%(tableTuple, table.columnNames[pos])
        if table.hardCodedResultTermsTypes and table.hardCodedResultTermsTypes.has_key(pos):
            return (valueTuple, "'"+ table.hardCodedResultTermsTypes[pos] + "'")
        return (valueTuple, valueTuple + '_term')


    def MatchTripleConditions(self, tableTuple, table, tp):
        """
        This is the 'genCond-SQL' function from Chebotko 2007(TR):
        'Given a triple pattern tp, generates an SQL boolean expression which is
        evaluated to True if and only if tp matches a tuple represented by relational attributes
        beta(tp, SUBJECT), beta(tp, PREDICATE), and beta(tp, OBJECT).'
        """
        cond = []
        
        tp.ConvertTerms(self)
        
        # match non-variables
        if not (isinstance(tp.sub, Variable) or type(tp.sub) is BNode):
            cond.append("%s = '%s' /*%s*/"%(self.TripleColumn(tableTuple, table, SUBJECT)[0], self.AddLiteralParam(tp.subHash), 
                                            tp.sub.find('%')==-1 and tp.sub or ''))
        if not (isinstance(tp.pred, Variable) or type(tp.pred) is BNode):
            if table is self.GetTable('type'):
                pass # condition is redundant as it will evaluate to true (if type table is chosen because predicate is type, then this field is hardcoded to be rdf:type
            else:
                cond.append("%s = '%s' /*%s*/"%(self.TripleColumn(tableTuple, table, PREDICATE)[0], self.AddLiteralParam(tp.predHash), 
                                                tp.pred.find('%')==-1 and tp.pred or '' ))
        if not (isinstance(tp.obj, Variable) or type(tp.obj) is BNode):
            cond.append("%s = '%s' /*%s*/"%(self.TripleColumn(tableTuple, table, OBJECT)[0], self.AddLiteralParam(tp.objHash), 
                                            tp.obj.find('%')==-1 and tp.obj or '' ))

            #TODO: match data_type & language of literals here
            if self.UseEvalOption(EVAL_OPTION_STRICT_DATATYPE) and \
               isinstance(tp.obj,Literal) and tp.obj.datatype:
                cond.append("%s = '%s' /*%s*/"%(self.TripleColumn(tableTuple, table,DATATYPE_INDEX)[0], 
                                                self.AddLiteralParam(normalizeValue(tp.obj.datatype, 'U', self.graph.store.useSignedInts)), 
                                                tp.obj.datatype))
            else:
                pass
        if tp.context != None:
            if not (isinstance(tp.context, Variable) or type(tp.context) is BNode):
                cond.append("%s = '%s' /*%s*/"%(self.TripleColumn(tableTuple, table, CONTEXT)[0], self.AddLiteralParam(tp.contextHash), 
                                                tp.context.find('%')==-1 and tp.context or ''))
            else:
                #TODO: if a variable is given for context in GRAPH, we shouldn't match the default graph (with a NULL context)???
                #TODO: how to get the default graph URI???
                #defaultGraphHash = '7349213765459492968'
                #cond.append("%s != '%s'"%(self.TripleColumn(tableTuple, table, CONTEXT)[0],defaultGraphHash))
                pass
        elif tp.context == None:
            # process from/from named
            if len(self.rootBuilder.fromList) > 0:
                orConds = []
                for c in self.rootBuilder.fromList:
                    orConds.append("%s = '%s'"%(self.TripleColumn(tableTuple, table, CONTEXT)[0], self.AddLiteralParam(self.GetUriHash(c))))
                cond.append("(%s) "%("OR ".join(orConds)))
            elif len(self.rootBuilder.fromNamedList) > 0:
                # FROM NAMED without FROM and not in a GRAPH... add impossible condition
                cond.append("%s IS NULL"%(self.TripleColumn(tableTuple, table, CONTEXT)[0])) 
        
        # variable repeated
        if tp.sub == tp.pred and type(tp.sub) == type(tp.pred):
            cond.append("%s = %s"%(self.TripleColumn(tableTuple, table, SUBJECT)[0], self.TripleColumn(tableTuple, table, PREDICATE)[0]))
        if tp.sub == tp.obj and type(tp.sub) == type(tp.obj):
            cond.append("%s = %s"%(self.TripleColumn(tableTuple, table, SUBJECT)[0], self.TripleColumn(tableTuple, table, OBJECT)[0]))
        if tp.obj == tp.pred and type(tp.obj) == type(tp.pred):
            cond.append("%s = %s"%(self.TripleColumn(tableTuple, table, OBJECT)[0], self.TripleColumn(tableTuple, table, PREDICATE)[0]))

        if tp.context != None:
            # context var is repeated
            if tp.context == tp.sub and type(tp.context) == type(tp.sub):
                cond.append("%s = %s"%(self.TripleColumn(tableTuple, table, CONTEXT)[0], self.TripleColumn(tableTuple, table, SUBJECT)[0]))
            if tp.context == tp.pred and type(tp.context) == type(tp.pred):
                cond.append("%s = %s"%(self.TripleColumn(tableTuple, table, CONTEXT)[0], self.TripleColumn(tableTuple, table, PREDICATE)[0]))
            if tp.context == tp.obj and type(tp.context) == type(tp.obj):
                cond.append("%s = %s"%(self.TripleColumn(tableTuple, table, CONTEXT)[0], self.TripleColumn(tableTuple, table, OBJECT)[0]))
         
        return cond

    def ProjectTriples(self, tp):
        """
        This is the 'genPR-SQL' function from Chebotko 2007(TR):
        'Given a triple pattern tp, generates an SQL expression which can be used
        to project only those relational attributes that correspond to distinct 
        tp.sp, tp.pp, and tp.op and rename the projected attributes as 
        beta(tp,SUBJECT) -> name(tp.sp), beta(tp,PREDICATE) -> name(tp.pp), and
        beta(tp,OBJECT) -> name(tp.op)'.
        
        In practice, we only project the columns that are variables!
        """
        raise NotImplementedError()
        #TODO: think about this one some more!  Only want to actually
        #     project variables that are used!
    
    def CombineSources(self, var, fieldType):
        """
        If the variable var is in available(f), then CombineSources will  
        generate an expression for var that and we can simply check 
        if that is not "NULL".
        
        fieldType is VALUE_FIELD_NAME, TERM_FIELD_NAME, DATATYPE_FIELD_NAME, or LANGUAGE_FIELD_NAME
        """
        vname = str(var)
        availableVars = self.GetAvailableVariable(vname)
        if availableVars == None or len(availableVars)<1:
            return "NULL" #return None

        if (len(availableVars) == 1 or 
                (self.UseOptimization(OPT_C2_SKIP_COALESCE) and 
                 not self.IsCoalesceVariable(vname))):
            v = availableVars[0]
            return v.GetField(fieldType)
        else:
            combineCols = []            
            for v in availableVars:
                combineCols.append(v.GetField(fieldType))
            return "COALESCE(%s)"%(",".join(combineCols))
    
        
    def AddTermAndLiteralFields(self, varList, outputVar=True):
        """
        Given a list of variables that should be returned by a this (sub-)query,
        generate appropriate code for coalescing alternatives available variables
        and add corresponding _term, _data_type, and _language columns to the SELECT.
        
        The default is to add the variables to the SELECT query (outputVar=True); 
        however, in the main query, we want to replace these columns with their
        string versions, so this function has the option to add the metadata columns
        without adding the actual columns to the SELECT clause.
        """
        for vname in varList:
            availableVars = self.GetAvailableVariable(vname)
            
            if availableVars == None or len(availableVars)<1:
                # this is probably a case where the variable in the SELECT, but not in the rest of the query
                self.AddWarning("Undefined variable '%s': treating as NULL."%(vname))
                if outputVar:
                    self.AddOutputAs("NULL", vname)
                self.AddOutputAs("NULL", vname + "_term")
                self.SetCoalesceVariable(vname) # just in case, mark that this variable can be NULL                
                continue

            # determine if join of literal/non-literal
            literalFields = False
            nonLiteralFields = False
            for v in availableVars:                
                for s in v.sources:
                    if s.literalField:
                        literalFields = True
                    else:
                        nonLiteralFields = True
                        
            #NOTE: joining a literal & a non-literal column produces a non-literal column!
            if literalFields and nonLiteralFields:
                # let's now update the variable to reflect this knowledge
                for v in availableVars:
                    if v.IsLiteralField():
                        for s in v.sources:
                            s.literalField = False
                            s.forcedNonLiteral = True 
                        v.dataTypeFieldName = None
                        v.languageFieldName = None
                literalFields = False
                #TODO: we also now know that we may be using the wrong partition table, but we're now too late in the query generation process (need to do this earlier?)
            
            #OPTIMIZE: if no outer joins used, there can't be any NULLs and thus we don't need COALESCE
            if (len(availableVars) == 1 or 
                    (self.UseOptimization(OPT_C2_SKIP_COALESCE) and 
                     not self.IsCoalesceVariable(vname))):
                # this var not shared
                if len(availableVars) > 1:
                    availableVars.sort(key=lambda x:x.tableTuple)
                v = availableVars[0]
                if outputVar:
                    #self.AddOutputAs("%s.%s"%(v.tableTuple,vname), vname)
                    self.AddOutputAs(v.fieldName, vname)
                #self.AddOutputAs("%s.%s_term"%(v.tableTuple,vname), vname + "_term")                
                self.AddOutputAs(v.termFieldName, vname + "_term")
                if literalFields and not nonLiteralFields:
                    #self.AddOutputAs("%s.%s_data_type"%(v.tableTuple,vname), vname + "_data_type")
                    #self.AddOutputAs("%s.%s_language"%(v.tableTuple,vname), vname + "_language")
                    if v.dataTypeFieldName != None:
                        self.AddOutputAs(v.dataTypeFieldName, vname + "_data_type")
                    if v.languageFieldName != None:
                        self.AddOutputAs(v.languageFieldName, vname + "_language")                    
            else:
                # this var is shared and at least one of them might be NULL!
                combineCols = []
                combineTermCols = []
                
                for v in availableVars:
                    #combineCols.append("%s.%s"%(v.tableTuple,vname))
                    #combineTermCols.append("%s.%s_term"%(v.tableTuple,vname))
                    combineCols.append(v.fieldName)
                    combineTermCols.append(v.termFieldName)

    
                if not outputVar: # this is only OK if the other code is adding the COALESCE or simply passing values through (in which case the var should only appear once!)
                    raise Exception("AddTermAndLiteralFields should never be called with outputVar disable when COALESCE is required!")
                if outputVar:
                    self.AddOutputAs("COALESCE(%s)"%(",".join(combineCols)), vname)
                self.AddOutputAs("COALESCE(%s)"%(",".join(combineTermCols)), vname + "_term")
                                
                # need to add literal fields
                if literalFields and not nonLiteralFields:
                    combineDataTypeCols = []
                    combineLangCols = []
                    for v in availableVars:
                        if v.IsLiteralField():
                            #combineDataTypeCols.append("%s.%s_data_type"%(v.tableTuple,vname))
                            #combineLangCols.append("%s.%s_language"%(v.tableTuple,vname))
                            if v.dataTypeFieldName != None:
                                combineDataTypeCols.append(v.dataTypeFieldName)
                            if v.languageFieldName != None:
                                combineLangCols.append(v.languageFieldName)
                    self.AddOutputAs("COALESCE(%s)"%(",".join(combineDataTypeCols)), vname + "_data_type")
                    self.AddOutputAs("COALESCE(%s)"%(",".join(combineDataTypeCols)), vname + "_language")                  
    
    def AddStringJoin(self, var, outputName, addOutput=True):
        """
        Give a table tuple (tt), a variable name and an output name (alias), 
        join tt.vname with the appropriate literals/identifiers tables (or both) so 
        that we can obtain the actual string value for the column.
         
        Returns the tuple+field/COALESCE/etc. or alias generated.
        """        
        if self.stringVariables.has_key(var.name): # .lower()): #BE: currently assuming variables are not case-sensitive
            # the string version of this variable is already available (used more than once in FILTER, etc.)
            return self.stringVariables[var.name] #.lower()] #BE: currently assuming variables are not case-sensitive
        
        varSources = var.sources #self.GetVariableSources(vname)
        # determine which table we need to do the join with (i.e. identifier or literal)
        needIdentifier = False
        needLiteral = False
        constValue = None
        for v in varSources:
            if v.pos == SUBJECT:
                needIdentifier = True
            
            if v.pos == PREDICATE:
                if v.table is self.GetTable('type'):
                    # special case for rdf:type
                    constValue = "'" + self.rootBuilder.typeUri + "'"
                else:
                    needIdentifier = True
            if v.pos == OBJECT:
                if v.table is self.GetTable('lit'):
                    needLiteral = True
                elif v.table is self.GetTable('all'):
                    needLiteral = True
                    needIdentifier = True
                else:
                    needIdentifier = True
            if v.pos == CONTEXT:
                needIdentifier = True
        if len(varSources) < 1:
            # variable not found!!!
            self.AddWarning("Variable '%s' not found in query, treating as 'NULL'!"%(var.name))
            constValue = "NULL"
        if constValue != None:
            if addOutput:
                outputFn = outputName
                self.AddOutputAs("%s" % (constValue), outputName) # we probably don't need to cast this (NULL or constant string)
            else:
                outputFn = "%s" % (constValue) #no alias available, use value directly
                
        # figure out which table we need to join with
        else:
            objTable = None
            idField = "id"
            lexField = "lexical"
            if not needIdentifier and not needLiteral:
                raise Exception("Table not identified for strings for variable: " + vname)
                
            # replacing view with two LEFT OUTER JOINS & a COALESCE() --> much faster!
            outputFn = None
            if needIdentifier:
                objTable = self.GetTable("idObj")
                # join with table
                objTT1 = self.AddTableTuple(objTable, "valId")
                #self.AddTupleJoinFields(objTT1, idField, LEFT_OUTER_JOIN, tt, vname)
                self.AddTupleJoin(objTT1, LEFT_OUTER_JOIN, "%s.%s = %s"%(objTT1, idField, var.fieldName))
                outputFn = "%s.%s"%(objTT1, lexField)
            if needLiteral:
                objTable = self.GetTable("litObj")
                # join with table
                objTT2 = self.AddTableTuple(objTable, "valLit")
                #self.AddTupleJoinFields(objTT2, idField, LEFT_OUTER_JOIN, tt, vname)
                self.AddTupleJoin(objTT2, LEFT_OUTER_JOIN, "%s.%s = %s"%(objTT2, idField, var.fieldName))
                if outputFn is None:
                    outputFn = "%s.%s"%(objTT2, lexField)
                else:
                    outputFn = "COALESCE(%s,%s.%s)"%(outputFn,objTT2, lexField)
                
            # add to output
            #self.AddOutputField(objTT, lexField, outputName)
            if addOutput:
                self.AddOutputAs(outputFn, outputName)

        self.stringVariables[var.name] = outputFn #.lower()] = outputFn  #BE: currently assuming variables are not case-sensitive
        return outputFn    
    
    def CompareLiteralCondition(self,leftExp,leftLit,rightExp,rightLit,type,strictMatch):
        """
        Generate the appropriate WHERE conditions for comparing literals/variables
        based on data type/language.  
        
        Input: SQL strings for the two data_type/language expressions (i.e. constant string or None for literal
        and table.fieldname or None for variable) along with whether or not each side is a literal
          Type: must be 'data_type' or 'language'
          strictMatch: True for strict adherence to RDF/SPARQL spec for match
          
        Literal expressions should be strings that will be processed here into appropriate hashes.
        
        Output: SQL WHERE condition string if needed, or empty string if no conditions are required. 
        """
        cond = ""
        # data type condition(s)
        if leftExp != rightExp:
            # expressions are different, need to compare (if the same, do nothing as the condition would be redundant)
            if leftLit and rightLit:
                # comparing two literals
                raise Exception('Attempting to comparing two non-equal literals (always False)!')
            if ((leftLit and not rightExp) or
                (rightLit and not leftExp)):
                raise Exception('Literal with type being compared to a variable with no data type (URI)!')
            if not leftLit and not rightLit:
                # comparing two variables
                if leftExp == None or rightExp == None:
                    #raise Exception('Comparing a variable with no %s to a variable with a %s!'%(type,type))
                    self.AddWarning("Comparing a variable with no %s to a variable with a %s!"%(type,type))
                    cond = "FALSE"                    
                elif strictMatch:
                    cond = "(%s = %s OR (%s IS NULL AND %s IS NULL))"%(leftExp,rightExp,leftExp,rightExp)
                else:
                    # weaken data_type condition for NULLs
                    cond = "(%s = %s OR %s IS NULL OR %s IS NULL)"%(leftExp,rightExp,leftExp,rightExp)
            else:
                # one var and one lit being compared
                if leftLit:
                    varExp = rightExp
                    litExp = leftExp
                else:
                    varExp = leftExp
                    litExp = rightExp
                
                # post-process literal strings
                if litExp == 'numeric':
                    #TODO: special treatment of numeric: expand to OR of appropriate types
                    pass
                
                # get string hash (if not None)
                if litExp != None:
                    if type == 'language':
                        # treat as literal
                        litExp = "'" + str(litExp) + "' "
                    elif type == 'data_type':
                        litExp = "'" + str(self.GetUriHash(litExp)) + "' /*U:" + litExp + "*/ "
                    else:
                        raise Exception("Unsupport type for CompareLiteralCondition: %s"%(type))
                
                if strictMatch:
                    if litExp != None:
                        cond = "%s = %s"%(varExp,litExp)
                    else:
                        cond = "%s IS NULL"%(varExp)
                else:
                    # weaken data_type conditions
                    if lit != None:
                        cond = "(%s = %s OR %s IS NULL)"%(varExp,litExp,varExp)
        return cond
    
