
class NoResultsException(Exception):
    def __init__(self):
        Exception("No Results.")

class RelationalOperator(object):
    
    def __init__(self, parent):
        self.parent = parent
    
    def GenSql(self, sqlBuilder):
        """
        Main external interface for SQL generation.
        The client code should construct and pass an RdfSqlBuilder instance.
        """
        self.BuildSql(sqlBuilder, True) # treat outermost query as 'nested' since it must return variables
    
    def BuildSql(sqlBuilder, isNested):
        """
        Main (internal) interface for SQL generation.  The logic required to
        implement the operator should be implemented
        using the provided SqlBuilder class.
        
        If isNested=True, then output (SELECT clause)
        variables must be set. 
        """
        raise Exception("BuildSql must be overridden in child classes.")
    
    def AddNestedOp(self, sqlBuilder, relOp, tuplePrefix):
        childBuilder = sqlBuilder.GetNestedSQLBuilder()
        #childBuilder.SetComment(repr(relOp)) # useful for SQL debugging
        relOp.BuildSql(childBuilder, True)
        #sqlBuilder.SetVariablesFromChild(childBuilder)
        tt = sqlBuilder.AddNestedTableTuple(childBuilder.Sql(),tuplePrefix)
        
        sqlBuilder.AddChildVariables(childBuilder, tt)
        return (tt, childBuilder)
    
    def GetUsedVariables(self, sqlBuilder, includeBNodes=True):
        """
        The operator should return a set of 
        variable name strings
        of the variables used in this operator and 
        all child operators. 
        """
        raise Exception("GetUsedVariables must be overridden in child classes.")
        
    def GetChildren(self):
        """
        Returns all child operators.
        """
        raise Exception("GetChildren must be overridden in child classes.")
        
    def GetDescendantOperators(self, returnType, excludeSubtreeTypes, includeSelf=False):
        """
        Returns all child operators of a given type, recursively 
        (including the operator itself is specified).
        If an operator belonging to one of the excludeSubtreeTypes is found,
        do not returning and ignore its children as well. 
        """
        results = []
        queue = []
        queue.extend(self.GetChildren())
        if includeSelf:
            queue.append(self)
        while len(queue) > 0:
            q = queue.pop()
            if isinstance(q,returnType):
                results.append(q)
                
            exclude = False
            for e in excludeSubtreeTypes:
                if isinstance(q,e):
                    exclude = True
                    break
            if exclude:
                continue
            
            queue.extend(q.GetChildren())
            
        return results 
        
class RelationalExpOperator(object):
        
    def GetDecendentLexicalComparators(self):
        pass
        
    def BuildSqlExpression(self,sqlBuilder,tupleTable):
        raise Exception("BuildSqlExpression must be overridden in child classes.")
    
    def AdjustCostEstimate(self,cost,colDist):
        # Returns (cost, colDist, varSet)
        raise Exception("AdjustCostEstimate must be overridden in child classes.")

class RelationalTerminalExpOperator(object):

    def BuildTerminalExpression(self,sqlBuilder, tupleTable):
        raise Exception("BuildTerminalExpression must be overridden in child classes.")
    
    def BuildHash(self, sqlBuilder):
        raise Exception("BuildHash must be overridden in child classes.")
        
    def BuildSqlExpression(sqlBuilder,tupleTable):
        raise Exception("BuildSqlExpression must be overridden in child classes.")
   
    def GetDataTypeExp(self,sqlBuilder):
        raise Exception("GetDataTypeExp must be overridden in child classes.")
    
    def GetLanguageExp(self,sqlBuilder):
        raise Exception("GetLanguageExp must be overridden in child classes.")

    def GetTermExp(self,sqlBuilder):
        raise Exception("GetTermExp must be overridden in child classes.")
   