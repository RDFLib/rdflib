
# Join types -- add more if needed
NONE_JOIN = 0
INNER_JOIN = 1
LEFT_OUTER_JOIN = 2
RIGHT_OUTER_JOIN = 3
FULL_OUTER_JOIN = 4
CROSS_JOIN = 10

JoinTypeMap = {NONE_JOIN: "",
               INNER_JOIN: "INNER JOIN",
               LEFT_OUTER_JOIN: "LEFT OUTER JOIN",
               RIGHT_OUTER_JOIN: "RIGHT OUTER JOIN",
               FULL_OUTER_JOIN: "FULL OUTER JOIN",
               CROSS_JOIN: "CROSS JOIN"}
            
# Option Flags
FLAG_STRAIGHT_JOIN = "STRAIGHT_JOIN"
FLAG_NO_CACHE = "SQL_NO_CACHE"

class FromJoinNode(object):
    """
    Helper class to represent more complex parenthesized join structures.    
    """
    def __init__(self, left, right, joinType=CROSS_JOIN, onClause=None):
        self.left = left
        self.right = right
        self.joinType = joinType
        self.onClause = onClause

    def __repr__(self):
        if self.onClause != None:
            on = " ON (.)"
        else:
            on = ""
        return "(%s) %s (%s)%s"%(repr(self.left),JoinTypeMap[self.joinType], repr(self.right), on)

    def MakeFromClause(self, fromTables):
        if isinstance(self.left, FromJoinNode):
            l = self.left.MakeFromClause(fromTables)
        else:
            l = fromTables[self.left]
        if isinstance(self.right, FromJoinNode):
            r = self.right.MakeFromClause(fromTables)
        else:
            r = fromTables[self.right]
        
        if self.onClause == None:
            f = "(%s %s %s)"%(l,JoinTypeMap[self.joinType],r)
        else:
            f = "(%s %s %s ON %s)"%(l,JoinTypeMap[self.joinType],r, self.onClause)
        return f
            

class SqlBuilder(object):
    """
    Generic class for programatically building SELECT SQL queries. 
    
    Basic SQL features supported: 
    -Output field projection with aliases
    -Distinct
    -Specifying Join type (inner, left outer, cross product, etc.)
    -Nested queries in FROM clause with aliases (and WHERE-clause)
    -Conjunctive where clause (OR/NOT can be used within a where condition)
    -Limit, offset
    -Group by, Having
    -Order by (with support for DESC)
    
    Supports generating nested sub-queries with common state stored in the 
    initially constructed 'root' instance of the SqlBuilder.
    
    Based on C# code ported from RisuPicWeb.
    """
    def __init__(self, rootBuilder = None):
        self.Reset(rootBuilder)
        self.isAsk = False
        
    def Reset(self,rootBuilder):
        if rootBuilder == None: # only the root builder (non-nested query) maintains next tuple counter, etc.  
            self.rootBuilder = self
            self.nextTupleNum = 1
            self.nextParamNum = 1
            self.paramValues = {}
        else:
            self.rootBuilder = rootBuilder
            self.nextTupleNum = None
            self.nextParamNum = None
            self.paramValues = None
        self.comment = None
        self.selectClause = []
        self.selectAlias = []
        #self.fromTupleNames = []
        self.fromJoinTree = None        
        self.fromTables = {}
        #self.fromJoins = {}
        #self.lastTupleJoin = None        
        self.whereClause = []
        self.havingClause = []
        self.groupByClause = []
        self.orderByClause = []
        self.unionBuilder = None
        
        self.selectDistinct = False
        self.limit = -1
        self.offset = -1
        
        self.flags = {}
        
        self.outputFields = set()
        #self.outputMap = {}
        
        
    def SetComment(self, comment):
        self.comment = comment
    
    def AddOutputAs(self, expr, alias, genSqlAlias=True):
        if genSqlAlias:
            sqlAlias = self.MakeSqlVarAlias(alias)
        else:
            sqlAlias = alias
        self.selectClause.append("%s AS '%s'"%(expr,sqlAlias))
        self.selectAlias.append(sqlAlias)
        self.outputFields.add(sqlAlias)
        return sqlAlias
        
    def AddOutputField(self, tupleName, field, alias=None, genSqlAlias=True):
        if alias != None:
            if genSqlAlias:
                sqlAlias = self.MakeSqlVarAlias(alias)
            else:
                sqlAlias = alias
            self.selectClause.append("%s.%s AS '%s'"%(tupleName, field, sqlAlias))
            self.selectAlias.append(sqlAlias)
            self.outputFields.add(sqlAlias)
            return sqlAlias
        else:
            self.selectClause.append("%s.%s"%(tupleName,field))
            self.selectAlias.append("%s.%s"%(tupleName,field))
            return "%s.%s"%(tupleName,field)

    def SortOutputFieldsByAlias(self):
        items = []
        
        for n in range(len(self.selectClause)):
            items.append((self.selectAlias[n],self.selectClause[n]))
        
        sortedItems = sorted(items)
        self.selectClause = []
        self.selectAlias = []
        for (alias,clause) in sortedItems:
            self.selectClause.append(clause)
            self.selectAlias.append(alias)    

#    def MakeSqlVarAlias(self, var):
#        return var
#
#    def GetSqlVarAlias(self, var):
#        return var
    
    def HasOutputField(self, alias):
        return (alias in self.outputFields)
    
    def GetOutputFields(self):
        return self.outputFields

    def NewTupleName(self, tableName, tuplePrefix):
        """
        Generates a new table tuple name from the given tuple prefix
        and the next value of the tuple number counter to ensure
        it is globally unique across the query.
        """
#        if self.nextTupleNum == None:
#             return self.rootBuilder.NewTupleName(tableName, tuplePrefix)
        tupleName = tuplePrefix + str(self.rootBuilder.nextTupleNum)
        self.rootBuilder.nextTupleNum = self.rootBuilder.nextTupleNum + 1
        return tupleName
        
    def AddTableTuple(self, tableName, tuplePrefix):
        tupleName = self.NewTupleName(tableName, tuplePrefix)
        #self.fromTupleNames.append(tupleName)
        self.fromTables[tupleName] = "%s %s"%(tableName, tupleName)
        #self.lastTupleJoin = tupleName 
        if self.fromJoinTree == None:
            self.fromJoinTree = tupleName       
        return tupleName
    
    def AddNestedTableTuple(self, subquery, tuplePrefix):
        return self.AddTableTuple("(%s) AS"%(subquery), tuplePrefix)
    
    def GetNestedSQLBuilder(self):
        return SqlBuilder(self)
    
    def SetUnionSQLBuilder(self, sqlBuilder, unionAll): 
        """
        Union is supported by attaching a 2nd (sibling) builder as
        the 'union builder' for a SqlBuilder.  When generating the SQL
        for this builder, the union builder is then rendered as well
        after a UNION/UNION ALL. This allows a single call to Sql() to
        generate both.
        
        It's sufficient to have only 1 here, as we can chain them.
        """
        self.unionBuilder = (sqlBuilder, unionAll)
    
    def AddTupleJoin(self, tupleName, joinType, onClause=None):
        """
        Used to construct left-deep linear joins.  
        To create more complex join structures, use PopFromJoinTree() and SetFromJoinTree()
        """
        #self.fromJoins[tupleName] = (joinType, onClause)
        if self.fromJoinTree == None:
            self.fromJoinTree = tupleName
        else:
            self.fromJoinTree = FromJoinNode(self.fromJoinTree, tupleName, joinType, onClause)
      
    def AddLastTupleJoin(self, joinType, onClause=None):
        #self.fromJoins[self.lastTupleJoin] = (joinType, onClause)
        if isinstance(self.fromJoinTree, FromJoinNode):
            self.fromJoinTree.joinType = joinType
            self.fromJoinTree.onClause = onClause
        else:
            raise Exception("Error: Can't use AddLastTupleJoin when no joins are present!")
        
    def AddTupleJoinField(self, tupleName, joinType, joinTupleName, joinField):
        self.AddTupleJoin(tupleName, joinType, "%s.%s = %s.%s"%(tupleName,joinField,joinTupleName,joinField))

    def AddTupleJoinFields(self, tupleName, tupleField, joinType, joinTupleName, joinField):
        self.AddTupleJoin(tupleName, joinType, "%s.%s = %s.%s"%(tupleName,tupleField,joinTupleName,joinField))
      
    def PopFromJoinTree(self):
        """
        Return the current from join tree and then set it to None.
        This is used in JOIN/OPTIONAL for the left and right branches.
        """
        tree = self.fromJoinTree
        self.fromJoinTree = None
        return tree
    
    def SetFromJoinTree(self, leftTree, rightTree, joinType, onClause):
        self.fromJoinTree = FromJoinNode(leftTree, rightTree, joinType, onClause)
        
    def AddWhere(self, condition):
        self.whereClause.append(condition)
                
    def AddWhereComparison(self, tupleName, tupleField, op, value):
        paramName = self.AddLiteralParam(value)
        self.AddWhere("%s.%s %s %%(%s)s"%(tupleName,tupleField,op,paramName))

    def AddParam(self):
#        if self.nextParamNum == None:
#            return self.rootBuilder.AddParam()
        paramName = "param" + str(self.rootBuilder.nextParamNum)
        self.rootBuilder.nextParamNum = self.rootBuilder.nextParamNum + 1
        self.rootBuilder.paramValues[paramName] = None
        return paramName

    def SetParamValue(self, name, value):
#        if self.nextParamNum == None:
#            return self.rootBuilder.SetParamValue(name, value)
        self.rootBuilder.paramValues[name] = value

    def AddLiteralParam(self, value):
        paramName = self.AddParam()
        self.SetParamValue(paramName, value)
        return "%(" + paramName + ")s"
        
    def AddHavingAndClause(self, condition):
        self.havingClause.append(condition) 
        
    def AddOrderBy(self, tupleName, descending=False):
        if descending:
            self.orderByClause.append(tupleName + " DESC ")
        else:
            self.orderByClause.append(tupleName)
            
    def AddGroupBy(self, tupleName):
        self.groupByClause.append(tupleName)
        
    def SetDistinct(self, value):
        self.selectDistinct = value
        
    def SetLimit(self, limit):
        self.limit = str(limit)
        
    def SetOffset(self, offset):
        self.offset = str(offset)
        
    def SetFlag(self, name, value):
        self.flags[name] = value
        
    def SetFlags(self, flags):
        self.flags = flags
        
    def GetFlag(self, name):
        if not self.flags.has_key(name):
            return False
        return self.flags[name]
        
    def Sql(self):
        
        sql = ""
        
        if self.comment != None:
            sql += "\n/* " + self.comment + " */\n  " 
        
        sql += "SELECT "
        if self.selectDistinct:
            sql += "DISTINCT "
        # for other SQL implementations (i.e. MS SQLServer)
#        if self.limit > 0:
#            sql += "TOP " + self.limit + " "

        # MySQL specific query options
        if self.GetFlag(FLAG_STRAIGHT_JOIN):
            sql += " STRAIGHT_JOIN"
        if self.GetFlag(FLAG_NO_CACHE):
            sql += " SQL_NO_CACHE"
            
        # projections
        if len(self.selectClause) > 0:
            sql += " " + ", ".join(self.selectClause)
        else:
            #raise Exception("No columns specified in SELECT clause!")
            # treat no columns as 'SELECT *'
            sql += " *"
            
            
        # from clause
        sql += " FROM"
        if isinstance(self.fromJoinTree, FromJoinNode):
            fromClause = self.fromJoinTree.MakeFromClause(self.fromTables) # more complex join structure
        elif self.fromJoinTree is None:            
            fromClause = " "
        else:            
            fromClause = self.fromTables[self.fromJoinTree] # single table name
        sql += " " + fromClause + " "
        
        # where clause  
        if len(self.whereClause) > 0:
            sql += "WHERE " + " AND ".join(self.whereClause) + " "

        # grouping
        if len(self.groupByClause) > 0:
            sql += "GROUP BY " + ",".join(self.groupByClause) + " "        
        if len(self.havingClause) > 0:
            sql += "HAVING " + " AND ".join(self.havingClause) + " "
        
        # modifiers
        if len(self.orderByClause) > 0:
            sql += "ORDER BY " + ",".join(self.orderByClause) + " "
            
        if self.limit > -1:
            sql += "LIMIT " + self.limit + " "
        if self.offset > -1:
            if self.limit <= -1:
                raise NotImplementedError("OFFSET without LIMIT not supported by MySQL!")

            sql += "OFFSET " + self.offset + " "
        
        if self.comment != None:
            sql += "\n"
            

        # union
        if self.unionBuilder != None:  
            sql = "(" + sql + " "
            (unionBuilder, unionAll) = self.unionBuilder  
            sql += ") UNION ("
            if unionAll:
                sql += "ALL "
            sql += unionBuilder.Sql() + ") "

        if self.isAsk:
            sql="SELECT EXISTS (%s)"%sql
        return sql
            
    def Params(self):
        return self.paramValues
    
    def __repr__(self):
        return self.Sql()