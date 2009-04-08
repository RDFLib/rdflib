"""
The set of classes used to model the 3 'partitions' for N3 assertions.
There is a top level class which implements operations common to all partitions as
well as a class for each partition.  These classes are meant to allow the underlying
SQL schema to be completely configurable as well as to automate the generation
of SQL queries for adding,updating,removing,resolving triples from the partitions.
These classes work in tandem with the RelationHashes to automate all (or most) of
the SQL processing associated with this FOPL Relational Model

NOTE: The use of foreign keys (which - unfortunately - bumps the minimum MySQL version to 5.0) allows for
the efficient removal of all statements about a particular resource using cascade on delete (currently not used)

see: http://dev.mysql.com/doc/refman/5.0/en/ansi-diff-foreign-keys.html
"""
from rdflib.term import BNode, URIRef, Literal
from rdflib.namespace import RDF
from pprint import pprint
from rdflib.term_utils import *
from rdflib.store.REGEXMatching import REGEXTerm
from QuadSlot import *
from RelationalHash import Table
Any = None

EXPLAIN_INFO = False

CONTEXT_COLUMN = 'context'
ANY_TERM = ['U','B','F','V','L']
CONTEXT_TERMS   = ['U','B','F']
IDENTIFIER_TERMS   = ['U','B']
GROUND_IDENTIFIERS = ['U']
NON_LITERALS = ['U','B','F','V']
CLASS_TERMS = ['U','B','V']
PREDICATE_NAMES = ['U','V']

NAMED_BINARY_RELATION_PREDICATES = GROUND_IDENTIFIERS
NAMED_BINARY_RELATION_OBJECTS    = ['U','B','L']

NAMED_LITERAL_PREDICATES = GROUND_IDENTIFIERS
NAMED_LITERAL_OBJECTS    = ['L']

ASSOCIATIVE_BOX_CLASSES    = GROUND_IDENTIFIERS

CREATE_BRP_TABLE = """
CREATE TABLE %s (
    %s
) %s"""

LOOKUP_INTERSECTION_SQL = "INNER JOIN %s %s ON (%s)"
LOOKUP_UNION_SQL        = "LEFT JOIN %s %s ON (%s)"

class BinaryRelationPartition(Table):
    """
    The common ancestor of the three partitions for assertions.
    Implements behavior common to all 3.  Each subclass is expected to define the following:

    nameSuffix - The suffix appended to the name of the table
    termEnumerations - a 4 item list (for each quad 'slot') of lists (or None) which enumerate the allowable term types
                       for each quad slot (one of 'U' - URIs,'V' - Variable,'L' - Literals,'B' - BNodes,'F' - Formulae)
    columnNames - a list of column names for each quad slot (can be of additional length where each item is a 3-item tuple of:
                  column name, column type, index)
    columnIntersectionList - a list of 2 item tuples (the quad index and a boolean indicating whether or not the associated term is an identifier)
                             this list (the order of which is very important) is used for generating intersections between the partition and the identifier / value hash
    hardCodedResultFields - a dictionary mapping quad slot indices to their hardcoded value (for partitions - such as ABOX - which have a hardcoded value for a particular quad slot)
    hardCodedResultTermsTypes - a dictionary mapping quad slot indices to their hardcoded term type (for partitions - such as Literal properties - which have hardcoded values for a particular quad slot's term type)
    """
    assertedColumnName = 'asserted'
    indexSuffix = 'Index'
    literalTable = False
    objectPropertyTable = False
    def __init__(self, identifier, idHash, valueHash,
                 useSignedInts=False, hashFieldType='BIGINT unsigned',
                 engine='ENGINE=InnoDB', declareEnums=False):
        self.identifier = identifier
        self.idHash    = idHash
        self.valueHash = valueHash
        self.useSignedInts = useSignedInts
        self._hashFieldType = hashFieldType
        self.declareEnums = declareEnums
        self._engine = engine
        self._repr = self.identifier+'_'+self.nameSuffix
        self.singularInsertionSQLCmd = self.insertRelationsSQLCMD()
        self._resetPendingInsertions()
        self._intersectionSQL = self.generateHashIntersections()
        self._selectFieldsLeading    = self._selectFields(True)  + ['NULL as '+SlotPrefixes[DATATYPE_INDEX],'NULL as '+SlotPrefixes[LANGUAGE_INDEX]]
        self._selectFieldsNonLeading = self._selectFields(False) + ['NULL','NULL']

        self._cacheStatements()

        self.delimited_file = None

    def __repr__(self):
        return self._repr

    def get_name(self):
        return self._repr

    def foreignKeySQL(self, slot):
        """
        Generates foreign key expressions for relating a particular quad
        term with the identifier hash.
        """
        self._foreign.append(
            ("""ALTER TABLE %s ADD CONSTRAINT %s_%s_lookup
                FOREIGN KEY (%s) REFERENCES %s (%s)""" %
                  (self, self,
                   self.columnNames[slot],
                   self.columnNames[slot],
                   self.idHash,
                   self.idHash.columns[0][0]),
             "ALTER TABLE %s DROP FOREIGN KEY %s_%s_lookup" %
                  (self, self,
                   self.columnNames[slot])))

    def indexingStatements(self):
        return [pair[0] for pair in self._indexing]

    def removeIndexingStatements(self):
        return [pair[1] for pair in self._indexing]

    def foreignKeyStatements(self):
        return [pair[0] for pair in self._foreign]

    def removeForeignKeyStatements(self):
        return [pair[1] for pair in self._foreign]

    def order_column_names(self, positions):
        return [self.columnNames[position] for
          position in positions if self.columnNames[position] is not None]

    def _cacheStatements(self):
        self._indexing = []
        self._foreign = []
        for slot in POSITION_LIST:
            if self.columnNames[slot]:
                self._indexing.append(
                    ("CREATE INDEX %s_%s%s ON %s (%s)" %
                       (self.get_name(), self.columnNames[slot],
                        self.indexSuffix, self.get_name(),
                        self.columnNames[slot]),
                     "DROP INDEX %s_%s%s ON %s" %
                       (self.get_name(), self.columnNames[slot],
                        self.indexSuffix, self.get_name())))

                if self.termEnumerations[slot]:
                    self._indexing.append(
                        ("CREATE INDEX %s_%s_term%s ON %s (%s_term)" %
                           (self.get_name(), self.columnNames[slot],
                            self.indexSuffix, self.get_name(),
                            self.columnNames[slot]),
                         "DROP INDEX %s_%s_term%s ON %s" %
                           (self.get_name(), self.columnNames[slot],
                            self.indexSuffix, self.get_name())))

                self.foreignKeySQL(slot)

        if len(self.columnNames) > 4:
            for otherSlot in range(4, len(self.columnNames)):
                colMD = self.columnNames[otherSlot]
                if isinstance(colMD, tuple):
                    colName, colType, indexStr = colMD
                    self._indexing.append(
                        ("CREATE INDEX %s_%s%s ON %s (%s)" %
                           (self.get_name(), colName, self.indexSuffix,
                            self.get_name(), indexStr % colName),
                         "DROP INDEX %s_%s%s ON %s" %
                           (self.get_name(), colName, self.indexSuffix,
                            self.get_name())))
                else:
                    self._indexing.append(
                        ("CREATE INDEX %s_%s%s ON %s (%s)" %
                           (self.get_name(), colMD, self.indexSuffix,
                            self.get_name(), colMD),
                         "DROP INDEX %s_%s%s ON %s" %
                           (self.get_name(), colMD, self.indexSuffix,
                            self.get_name())))
                    self.foreignKeySQL(otherSlot)

        self._indexing.append(
          ('CREATE UNIQUE INDEX %s_posc%s ON %s (%s)' %
             (self.get_name(), self.indexSuffix, self.get_name(),
              ', '.join(self.order_column_names(
                (PREDICATE, OBJECT, SUBJECT, CONTEXT)))),
           'DROP INDEX %s_posc%s ON %s' %
             (self.get_name(), self.indexSuffix, self.get_name())))

    def createStatements(self):
        """
        Generates a CREATE TABLE statement which creates a SQL table used for
        persisting assertions associated with this partition.
        """
        statements = []
        columnSQLStmts = []
        for slot in POSITION_LIST:
            if self.columnNames[slot]:
                columnSQLStmts.append("\t%s\t%s not NULL" %
                  (self.columnNames[slot], self._hashFieldType))
                if self.termEnumerations[slot]:
                    if self.declareEnums:
                        # This is disabled until PostgreSQL grows enums (8.3)
                        if False:
                          enumName = '%s_enum' % (self.columnNames[slot],)
                          statements.append(
                            'CREATE TYPE %s AS ENUM (%s)' %
                            (enumName,
                             ','.join(["'%s'" % tType for tType in
                                        self.termEnumerations[slot]])))
                        enumName = 'char'
                        columnSQLStmts.append("\t%s_term %s not NULL" %
                          (self.columnNames[slot], enumName))
                    else:
                        columnSQLStmts.append("\t%s_term enum(%s) not NULL" %
                          (self.columnNames[slot],
                           ','.join(["'%s'" % tType for tType in
                                              self.termEnumerations[slot]])))

        if len(self.columnNames) > 4:
            for otherSlot in range(4, len(self.columnNames)):
                colMD = self.columnNames[otherSlot]
                if isinstance(colMD, tuple):
                    colName, colType, indexStr = colMD
                    columnSQLStmts.append("\t%s %s" % (colName, colType))
                else:
                    columnSQLStmts.append("\t%s %s unsigned not NULL" %
                                          (self._hashFieldType, colMD))

        statements.append(CREATE_BRP_TABLE % (
            self,
            ',\n'.join(columnSQLStmts),
            self._engine))
        return statements

    def _resetPendingInsertions(self):
        """
        Resets the cache for pending insertions
        """
        self.pendingInsertions = []

    def insertRelationsSQLCMD(self):
        """
        Generates a SQL command with parameter references (%s) in order to facilitate
        efficient batch insertion of multiple assertions by Python DB implementations (such as MySQLdb)
        """
        vals = 0
        insertColNames = []
        for colName in self.columnNames:
            colIdx = self.columnNames.index(colName)
            if colName:
                insertColNames.append(colName)
                vals += 1
            if colIdx < len(self.termEnumerations) and self.termEnumerations[colIdx]:
                insertColNames.append(colName+'_term')
                vals += 1
        insertColsExpr = "(%s)"%(','.join([isinstance(i,tuple) and i[0] or i for i in insertColNames]))
        return "INSERT INTO %s %s VALUES "%(self,insertColsExpr)+"(%s)"%(','.join(['%s' for i in range(vals)]))

    def insertRelations(self,quadSlots):
        """
        Takes a list of QuadSlot objects and queues the new identifiers / values to insert and
        the assertions as well (so they can be added in a batch for maximum efficiency)
        """
        for quadSlot in quadSlots:
            self.extractIdentifiers(quadSlot)
            self.pendingInsertions.append(self.compileQuadToParams(quadSlot))

    def flushInsertions(self,db):
        """
        Adds the pending identifiers / values and assertions (using executemany for
        maximum efficiency), and resets the queue.
        """
        self.idHash.insertIdentifiers(db)
        self.valueHash.insertIdentifiers(db)
        cursor = db.cursor()
        cursor.executemany(self.singularInsertionSQLCmd,self.pendingInsertions)
        cursor.close()
        self._resetPendingInsertions()
        
    def viewUnionSelectExpression(self,relations_only=False):
        """
        Return a SQL statement which creates a view of all the RDF statements
        from all the contributing partitions
        """
        rt=[]
        if relations_only and self.objectPropertyTable:
            return "select * from %s"%repr(self)
        for idx in range(len(POSITION_LIST)):
            rdfTermLabel=SlotPrefixes[idx]
            if idx < len(self.columnNames) and self.columnNames[idx]:
                #there is a matching column
                rt.append(self.columnNames[idx]+' as %s'%rdfTermLabel)
                if self.termEnumerations[idx]:
                    #there is a corresponding term enumeration
                    rt.append(self.columnNames[idx]+'_term as %s_term'%rdfTermLabel)
                else:
                    #no corresponding term enumeration (hardcoded)
                    rt.append("'%s' as %s_term"%(self.hardCodedResultTermsTypes[idx],
                                                 rdfTermLabel))
            else:
                assert self.hardCodedResultFields[idx] == RDF.type
                rt.append("'%s' as %s" % (normalizeValue(
                # reverted Brendan's fix: b4e8646d61a2 (Fixed bug in View 
                #creation for MySQL store that was causing the View to have 
                #the predicate column as VARCHAR(20) instead of BIGINT)
                #rt.append("CONVERT('%s',UNSIGNED INTEGER) as %s" % (normalizeValue(
                  self.hardCodedResultFields[idx], 'U', self.useSignedInts),
                                          rdfTermLabel))
                if self.hardCodedResultTermsTypes[idx]:
                    rt.append("'%s' as %s_term"%(self.hardCodedResultTermsTypes[idx],
                                                 rdfTermLabel))
        if not relations_only:
            if self.literalTable:
                for i in self.columnNames[-2:]:
                    rt.append(i[0])
            else:
                rt.append('NULL as data_type')
                rt.append('NULL as language')
        return "select %s from %s"%(', '.join(rt),repr(self))        

    def selectContextFields(self,first):
        """
        Generates a list of column aliases for the SELECT SQL command used in order
        to fetch contexts from each partition
        """
        rt = []
        idHashLexicalCol = self.idHash.columns[-1][0]
        idHashTermTypeCol = self.idHash.columns[-2][0]
        termNameAlias = first and ' as %s'%SlotPrefixes[CONTEXT] or ''
        rt.append('rt_'+SlotPrefixes[CONTEXT]+'.'+idHashLexicalCol + termNameAlias)
        termTypeAlias = first and ' as %sTermType'%SlotPrefixes[CONTEXT] or ''
        if self.termEnumerations[CONTEXT]:
            rt.append('rt_'+SlotPrefixes[CONTEXT]+'.'+idHashTermTypeCol+termTypeAlias)
        else:
            rt.append("'%s'"%self.hardCodedResultTermsTypes[CONTEXT]+termTypeAlias)
        return rt

    def _selectFields(self,first):
        rt = []
        idHashLexicalCol = self.idHash.columns[-1][0]
        idHashTermTypeCol = self.idHash.columns[-2][0]
        for idx in range(len(POSITION_LIST)):
            termNameAlias = first and ' as %s'%SlotPrefixes[idx] or ''
            if idx < len(self.columnNames) and self.columnNames[idx]:
                rt.append('rt_'+SlotPrefixes[idx]+'.'+idHashLexicalCol + termNameAlias)
                termTypeAlias = first and ' as %sTermType'%SlotPrefixes[idx] or ''
                if self.termEnumerations[idx]:
                    rt.append('rt_'+SlotPrefixes[idx]+'.'+idHashTermTypeCol+termTypeAlias)
                else:
                    rt.append("'%s'"%self.hardCodedResultTermsTypes[idx]+termTypeAlias)
            else:
                rt.append("'%s'"%self.hardCodedResultFields[idx]+termNameAlias)
                if self.hardCodedResultTermsTypes[idx]:
                    rt.append("'%s'"%self.hardCodedResultTermsTypes[idx]+termNameAlias)
        return rt

    def selectFields(self,first=False):
        """
        Returns a list of column aliases for the SELECT SQL command used to fetch quads from
        a partition
        """
        return first and self._selectFieldsLeading or self._selectFieldsNonLeading

    def generateHashIntersections(self):
        """
        Generates the SQL JOINS (INNER and LEFT) used to intersect the identifier and value hashes
        with this partition.  This relies on each parition setting up an ordered list of
        intersections (ordered with optimization in mind).  For instance the ABOX partition
        would want to intersect on classes first (since this will have a lower cardinality than any other field)
        wherease the Literal Properties partition would want to intersect on datatypes first.
        The paritions and hashes are joined on the integer half-MD5-hash of the URI (or literal) as well
        as the 'Term Type'
        """
        intersections = []
        for idx,isId in self.columnIntersectionList:
            lookup = isId and self.idHash or self.valueHash
            lookupAlias = idx < len(POSITION_LIST) and 'rt_'+SlotPrefixes[idx] or 'rt_'+self.columnNames[idx][0]
            lookupKeyCol = lookup.columns[0][0]
            if idx < len(POSITION_LIST) or len(self.columnNames) > len(POSITION_LIST):
                colName = idx < len(POSITION_LIST) and self.columnNames[idx] or self.columnNames[idx][0]
                intersectionClauses = ["%s.%s = %s.%s"%(self,colName,lookupAlias,lookupKeyCol)]
                if idx < len(POSITION_LIST) and self.termEnumerations[idx]:
                    intersectionClauses.append("%s.%s_term = %s.%s"%(self,colName,lookupAlias,lookup.columns[1][0]))
                if isId and idx < len(POSITION_LIST) and idx in self.hardCodedResultTermsTypes:
                    intersectionClauses.append("%s.%s = '%s'"%(lookupAlias,lookup.columns[1][0],self.hardCodedResultTermsTypes[idx]))
            if idx == DATATYPE_INDEX and len(self.columnNames) > len(POSITION_LIST):
                intersections.append(LOOKUP_UNION_SQL%(lookup,lookupAlias,' AND '.join(intersectionClauses)))
            else:
                intersections.append(LOOKUP_INTERSECTION_SQL%(lookup,lookupAlias,' AND '.join(intersectionClauses)))
        return ' '.join(intersections)

    def generateWhereClause(self,queryPattern):
        """
        Takes a query pattern (a list of quad terms - subject,predicate,object,context)
        and generates a SQL WHERE clauses which works in conjunction to the intersections
        to filter the result set by partial matching (by REGEX), full matching (by integer half-hash),
        and term types.  For maximally efficient SELECT queries
        """
        whereClauses = []
        whereParameters = []
        asserted = dereferenceQuad(CONTEXT,queryPattern) is None
        for idx in SlotPrefixes.keys():
            queryTerm = dereferenceQuad(idx,queryPattern)
            lookupAlias = 'rt_'+SlotPrefixes[idx]
            if idx == CONTEXT and asserted:
                whereClauses.append("%s.%s_term != 'F'"%(self,self.columnNames[idx]))

            if idx < len(POSITION_LIST) and isinstance(queryTerm,REGEXTerm):
                whereClauses.append("%s.lexical REGEXP "%lookupAlias+"%s")
                whereParameters.append(queryTerm)
            elif idx == CONTEXT and isinstance(queryTerm,Graph) and isinstance(queryTerm.identifier,REGEXTerm):
                whereClauses.append("%s.lexical REGEXP "%lookupAlias+"%s")
                whereParameters.append(queryTerm.identifier)
            elif idx < len(POSITION_LIST) and queryTerm is not Any:
                if self.columnNames[idx]:

                    if isinstance(queryTerm,list):
                        whereClauses.append("%s.%s"%(self,self.columnNames[idx])+" in (%s)"%','.join(['%s' for item in range(len(queryTerm))]))
                        whereParameters.extend(
                          [normalizeValue(item, term2Letter(item),
                                          self.useSignedInts)
                           for item in queryTerm])
                    else:
                        whereClauses.append("%s.%s"%(self,self.columnNames[idx])+" = %s")
                        whereParameters.append(normalizeValue(
                          queryTerm, term2Letter(queryTerm),
                          self.useSignedInts))

                if not idx in self.hardCodedResultTermsTypes and self.termEnumerations[idx] and not isinstance(queryTerm,list):
                    whereClauses.append("%s.%s_term"%(self,self.columnNames[idx])+" = %s")
                    whereParameters.append(term2Letter(queryTerm))
            elif idx >= len(POSITION_LIST) and len(self.columnNames) > len(POSITION_LIST) and queryTerm is not None:
                compVal = idx == DATATYPE_INDEX and normalizeValue(
                  queryTerm, term2Letter(queryTerm),
                  self.useSignedInts) or queryTerm
                whereClauses.append("%s.%s"%(self,self.columnNames[idx][0])+" = %s")
                whereParameters.append(compVal)

        return ' AND '.join(whereClauses),whereParameters# + "#{%s}\n"%(str(queryPattern)),whereParameters

    def listIdentifiers(self, quadSlots):
        return []

    def listLiterals(self, quadSlots):
        return []

class AssociativeBox(BinaryRelationPartition):
    """
    The partition associated with assertions of class membership (formally known - in Description Logics - as an Associative Box)
    This partition is for all assertions where the property is rdf:type
    see: http://en.wikipedia.org/wiki/Description_Logic#Modelling_in_Description_Logics
    """
    nameSuffix = 'associativeBox'
    termEnumerations=[NON_LITERALS,None,CLASS_TERMS,CONTEXT_TERMS]
    columnNames = ['member',None,'class',CONTEXT_COLUMN]
    columnIntersectionList = [
                               (OBJECT,True),
                               (CONTEXT,True),
                               (SUBJECT,True)]

    hardCodedResultFields = {
        PREDICATE      : RDF.type,
    }
    hardCodedResultTermsTypes = {
        PREDICATE : 'U',
    }

    def compileQuadToParams(self,quadSlots):
        subjSlot,predSlot,objSlot,conSlot = quadSlots
        return (subjSlot.md5Int,
                term2Letter(subjSlot.term),
                objSlot.md5Int,
                term2Letter(objSlot.term),
                conSlot.md5Int,
                term2Letter(conSlot.term))

    def makeRowComponents(self, quadSlots):
        subjSlot, predSlot, objSlot, conSlot = quadSlots
        return (subjSlot.md5Int, subjSlot.termType,
                objSlot.md5Int, objSlot.termType,
                conSlot.md5Int, conSlot.termType)

    def listIdentifiers(self, quadSlots):
        subjSlot, predSlot, objSlot, conSlot = quadSlots

        return [(subjSlot.md5Int, subjSlot.termType, subjSlot.term),
                (objSlot.md5Int, objSlot.termType, objSlot.term),
                (conSlot.md5Int, conSlot.termType, conSlot.term)]

    def extractIdentifiers(self,quadSlots):
        subjSlot,predSlot,objSlot,conSlot = quadSlots
        self.idHash.updateIdentifierQueue([
                                           (subjSlot.term,subjSlot.termType),
                                           (objSlot.term,objSlot.termType),
                                           (conSlot.term,conSlot.termType)
                                           ])

class NamedLiteralProperties(BinaryRelationPartition):
    """
    The partition associated with assertions where the object is a Literal.
    """
    nameSuffix = 'literalProperties'
    termEnumerations=[NON_LITERALS,PREDICATE_NAMES,None,CONTEXT_TERMS]
    columnIntersectionList = [
                               (DATATYPE_INDEX,True),
                               (PREDICATE,True),
                               (CONTEXT,True),
                               (OBJECT,False),
                               (SUBJECT,True)]

    hardCodedResultFields = {}
    hardCodedResultTermsTypes = {
        OBJECT    : 'L'
    }
    literalTable = True
    def foreignKeySQL(self,slot):
        hash = slot == OBJECT and self.valueHash or self.idHash
        rt = ["\tCONSTRAINT %s_%s_lookup FOREIGN KEY  (%s) REFERENCES %s (%s)"%(
                    self,
                    self.columnNames[slot],
                    self.columnNames[slot],
                    hash,
                    hash.columns[0][0])]
        return rt

    def __init__(self, identifier, idHash, valueHash,
                 useSignedInts=False, hashFieldType='BIGINT unsigned',
                 engine='ENGINE=InnoDB', declareEnums=False):
        self.columnNames = ['subject', 'predicate', 'object', CONTEXT_COLUMN,
                            ('data_type', hashFieldType, '%s'),
                            ('language', 'varchar(3)', '%s')]
        super(NamedLiteralProperties, self).__init__(
          identifier, idHash, valueHash, useSignedInts, hashFieldType,
          engine, declareEnums)
        self.insertSQLCmds = {
           (False,False): self.insertRelationsSQLCMD(),
           (False,True) : self.insertRelationsSQLCMD(language=True),
           (True,False) : self.insertRelationsSQLCMD(dataType=True),
           (True,True)  : self.insertRelationsSQLCMD(dataType=True,language=True)
        }
        idHashLexicalCol = self.idHash.columns[-1][0]
        self._selectFieldsLeading = self._selectFields(True) + \
          [
            'rt_%s.%s'%(self.columnNames[DATATYPE_INDEX][0],idHashLexicalCol) + ' as %s'%SlotPrefixes[DATATYPE_INDEX],
            str(self)+'.'+self.columnNames[LANGUAGE_INDEX][0]+' as %s'%SlotPrefixes[LANGUAGE_INDEX],
          ]
        self._selectFields        = self._selectFields(False) + \
          [
            'rt_%s.%s'%(self.columnNames[DATATYPE_INDEX][0],idHashLexicalCol),
            str(self)+'.'+self.columnNames[LANGUAGE_INDEX][0],
          ]

    def _resetPendingInsertions(self):
        self.pendingInsertions = {
           (False,False): [],
           (False,True) : [],
           (True,False) : [],
           (True,True)  : [],
        }

    def insertRelationsSQLCMD(self,dataType=None,language=None):
        vals = 0
        insertColNames = []
        for colName in self.columnNames:
            colIdx = self.columnNames.index(colName)
            if colName:
                if isinstance(colName,tuple):
                    colName = colName[0]
                    for argColName,arg in [(self.columnNames[DATATYPE_INDEX][0],dataType),(self.columnNames[LANGUAGE_INDEX][0],language)]:
                        if colName == argColName and arg:
                            insertColNames.append(colName)
                            vals += 1
                else:
                    insertColNames.append(colName)
                    vals += 1
            if colIdx < len(self.termEnumerations) and self.termEnumerations[colIdx]:
                insertColNames.append(colName+'_term')
                vals += 1

        insertColsExpr = "(%s)"%(','.join([i for i in insertColNames]))
        return "INSERT INTO %s %s VALUES "%(self,insertColsExpr)+"(%s)"%(','.join(['%s' for i in range(vals)]))

    def insertRelations(self,quadSlots):
        for quadSlot in quadSlots:
            self.extractIdentifiers(quadSlot)
            literal = quadSlot[OBJECT].term
            insertionCMDKey = (bool(literal.datatype),bool(literal.language))
            self.pendingInsertions[insertionCMDKey].append(self.compileQuadToParams(quadSlot))

    def flushInsertions(self,db):
        self.idHash.insertIdentifiers(db)
        self.valueHash.insertIdentifiers(db)
        cursor = db.cursor()
        for key,paramList in self.pendingInsertions.items():
            if paramList:
                cursor.executemany(self.insertSQLCmds[key],paramList)
        cursor.close()
        self._resetPendingInsertions()

    def compileQuadToParams(self,quadSlots):
        subjSlot,predSlot,objSlot,conSlot = quadSlots
        dTypeParam = objSlot.term.datatype and normalizeValue(
          objSlot.term.datatype, 'U', self.useSignedInts) or None
        langParam  = objSlot.term.language and objSlot.term.language or None
        rtList = [
                    subjSlot.md5Int,
                    term2Letter(subjSlot.term),
                    predSlot.md5Int,
                    term2Letter(predSlot.term),
                    objSlot.md5Int,
                    conSlot.md5Int,
                    term2Letter(conSlot.term)]
        for item in [dTypeParam,langParam]:
            if item:
                rtList.append(item)
        return tuple(rtList)

    def makeRowComponents(self, quadSlots):
        subjSlot, predSlot, objSlot, conSlot = quadSlots
        dTypeParam = objSlot.term.datatype and normalizeValue(
          objSlot.term.datatype, 'U', self.useSignedInts) or None
        langParam  = objSlot.term.language and objSlot.term.language or None
        return (subjSlot.md5Int, subjSlot.termType,
                predSlot.md5Int, predSlot.termType,
                objSlot.md5Int,
                conSlot.md5Int, conSlot.termType,
                dTypeParam, langParam)

    def extractIdentifiers(self,quadSlots):
        """
        Test literal data type extraction
        >>> from rdflib import RDF
        >>> class DummyClass:
        ...   def __init__(self,test=False):
        ...     self.test = test
        ...   def updateIdentifierQueue(self,stuff): 
        ...     if self.test: 
        ...       term,termType = stuff[-1]
        ...       assert termType == 'U',"Datatype's are URIs!" 
        >>> class Tester(NamedLiteralProperties):
        ...   def __init__(self): 
        ...     self.idHash    = DummyClass(True)
        ...     self.valueHash = DummyClass()
        >>> c = Tester()
        >>> slots = genQuadSlots([BNode(),RDF.first,Literal(1),BNode()])
        >>> c.extractIdentifiers(slots)
        """
        subjSlot,predSlot,objSlot,conSlot = quadSlots
        idTerms = [
                    (subjSlot.term,subjSlot.termType),
                    (predSlot.term,predSlot.termType),
                    (conSlot.term,conSlot.termType)]
        if objSlot.term.datatype:
            idTerms.append((objSlot.term.datatype,term2Letter(objSlot.term.datatype)))
        self.idHash.updateIdentifierQueue(idTerms)
        self.valueHash.updateIdentifierQueue([(objSlot.term,objSlot.termType)])

    def listIdentifiers(self, quadSlots):
        subjSlot, predSlot, objSlot, conSlot = quadSlots

        idTerms = [(subjSlot.md5Int, subjSlot.termType, subjSlot.term),
                   (predSlot.md5Int, predSlot.termType, predSlot.term),
                   (conSlot.md5Int, conSlot.termType, conSlot.term)]
        if objSlot.term.datatype:
            dt = objSlot.getDatatypeQuadSlot()
            idTerms.append((dt.md5Int, dt.termType, dt.term))
        return idTerms

    def listLiterals(self, quadSlots):
        subjSlot, predSlot, objSlot, conSlot = quadSlots

        return [(objSlot.md5Int, objSlot.term)]

    def selectFields(self,first=False):
        return first and self._selectFieldsLeading or self._selectFieldsNonLeading

class NamedBinaryRelations(BinaryRelationPartition):
    """
    Partition associated with assertions where the predicate isn't rdf:type and the object isn't a literal
    """
    nameSuffix = 'relations'
    termEnumerations=[NON_LITERALS,PREDICATE_NAMES,NON_LITERALS,CONTEXT_TERMS]
    columnNames = ['subject','predicate','object',CONTEXT_COLUMN]
    columnIntersectionList = [
                               (PREDICATE,True),
                               (CONTEXT,True),
                               (OBJECT,True),
                               (SUBJECT,True)]

    hardCodedResultFields = {}
    hardCodedResultTermsTypes = {}
    objectPropertyTable = True
    def compileQuadToParams(self,quadSlots):
        subjSlot,predSlot,objSlot,conSlot = quadSlots
        return (subjSlot.md5Int,
                term2Letter(subjSlot.term),
                predSlot.md5Int,
                term2Letter(predSlot.term),
                objSlot.md5Int,
                term2Letter(objSlot.term),
                conSlot.md5Int,
                term2Letter(conSlot.term))

    def makeRowComponents(self, quadSlots):
        subjSlot, predSlot, objSlot, conSlot = quadSlots
        return (subjSlot.md5Int, subjSlot.termType,
                predSlot.md5Int, predSlot.termType,
                objSlot.md5Int, objSlot.termType,
                conSlot.md5Int, conSlot.termType)

    def listIdentifiers(self, quadSlots):
        subjSlot, predSlot, objSlot, conSlot = quadSlots

        return [(subjSlot.md5Int, subjSlot.termType, subjSlot.term),
                (predSlot.md5Int, predSlot.termType, predSlot.term),
                (objSlot.md5Int, objSlot.termType, objSlot.term),
                (conSlot.md5Int, conSlot.termType, conSlot.term)]

    def extractIdentifiers(self,quadSlots):
        subjSlot,predSlot,objSlot,conSlot = quadSlots
        self.idHash.updateIdentifierQueue([
                                           (subjSlot.term,subjSlot.termType),
                                           (predSlot.term,predSlot.termType),
                                           (objSlot.term,objSlot.termType),
                                           (conSlot.term,conSlot.termType)])

def BinaryRelationPartitionCoverage((subject,predicate,object_,context),BRPs):
    """
    This function takes a quad pattern (where any term is one of: URIRef,BNode,Literal,None,or REGEXTerm)
    ,a list of 3 live partitions and returns a list of only those partitions that need to be searched
    in order to resolve the pattern.  This function relies on the BRPQueryDecisionMap dictionary
    to determine which partitions to use.  Note that the dictionary as it is currently constituted
    requres that REGEXTerms in the object slot require that *both* the binary relation partition and
    the literal properties partitions are searched when this search could be limited to the literal
    properties only (for more efficient REGEX evaluation of literal values).  Given the nature of the
    REGEX function in SPARQL and the way Versa matches by REGEX, this seperation couldn't be done
    """
    if isinstance(predicate,list) and len(predicate) == 1:
        predicate = predicate[0]
    if isinstance(predicate,REGEXTerm):
        pId = predicate.compiledExpr.match(RDF.type) and 'RT' or 'U_RNT'
    elif isinstance(predicate,(URIRef,BNode)):
        pId = predicate == RDF.type and 'T' or 'U_RNT'
    elif predicate is None or predicate is []:
        pId = 'W'
    elif isinstance(predicate,list):
        if [p for p in predicate if p == RDF.type or isinstance(p,REGEXTerm) and p.compiledExpr.match(RDF.type)]:
            #One of the predicates is (or matches) rdf:type, so can be treated as a REGEX term that matches rdf:type
            pId = 'RT'
        else:
            #Otherwise, can be treated as a REGEXTerm that *doesn't* match rdf:type
            pId = 'U_RNT'
    elif isinstance(predicate,Variable):
        #Predicates as variables would only exist in literal property assertions and 'other' Relations partition
        #(same as URIs or REGEX Terms that don't match rdf:type)
        pId = 'U_RNT'
    else:
        raise Exception("Unable to determine a parition to cover with the given predicate %s (a %s)"%(predicate,type(predicate).__name__))

    if isinstance(object_,list) and len(object_) == 1:
        object_ = object_[0]
    if isinstance(object_,REGEXTerm):
        oId = 'R'
    elif isinstance(object_,Literal):
        oId = 'L'
    elif isinstance(object_,(URIRef,BNode,Graph)):
        oId = 'U'
    elif object_ is None:
        oId = 'W'
    elif isinstance(object_,list):
        if [o for o in object_ if isinstance(o,REGEXTerm)]:
            #If there are any REGEXTerms in the list then the list behaves as a REGEX / Wildcard
            oId = 'R'
        elif not [o for o in object_ if isinstance(o,REGEXTerm) or isinstance(o,Literal)]:
            #There are no Literals or REGEXTerms, the list behaves as a URI (i.e., it never checks literal partition)
            oId = 'U'
        elif len([o for o in object_ if isinstance(o,Literal)]) == len(object_):
            #They are all literals
            oId = 'L'
        else:
            #Treat as a wildcard
            oId = 'R'
    elif isinstance(object_,Variable):
        #Variables would only exist in the ABOX and 'other' Relations partition (same as URIs)
        oId = 'U'
    else:
        raise Exception("Unable to determine a parition to cover with the given object %s (a %s)"%(object_,type(object_).__name__))

    targetBRPs = [brp for brp in BRPs if isinstance(brp,BRPQueryDecisionMap[pId+oId])]
    return targetBRPs

def PatternResolution(quad,cursor,BRPs,orderByTriple=True,fetchall=True,fetchContexts=False):
    """
    This function implements query pattern resolution against a list of partition objects and
    3 parameters specifying whether to sort the result set (in order to group identical triples
    by the contexts in which they appear), whether to fetch the entire result set or one at a time,
    and whether to fetch the matching contexts only or the assertions.
    This function uses BinaryRelationPartitionCoverage to whittle out the partitions that don't need
    to be searched, generateHashIntersections / generateWhereClause to generate the SQL query
    and the parameter fill-ins and creates a single UNION query against the relevant partitions.

    Note the use of UNION syntax requires that the literal properties partition is first (since it
    uses the first select to determine the column types for the resulting rows from the subsequent
    SELECT queries)

    see: http://dev.mysql.com/doc/refman/5.0/en/union.html
    """
    subject,predicate,object_,context = quad
    targetBRPs = BinaryRelationPartitionCoverage((subject,predicate,object_,context),BRPs)
    unionQueries = []
    unionQueriesParams = []
    for brp in targetBRPs:
        first = targetBRPs.index(brp) == 0
        if fetchContexts:
            query = "SELECT DISTINCT %s FROM %s %s WHERE "%(
                                          ','.join(brp.selectContextFields(first)),
                                          brp,
                                          brp._intersectionSQL
                                        )
        else:
            query = CROSS_BRP_QUERY_SQL%(
                                          ','.join(brp.selectFields(first)),
                                          brp,
                                          brp._intersectionSQL
                                        )
        whereClause,whereParameters = brp.generateWhereClause((subject,predicate,object_,context))
        unionQueries.append(query+whereClause)
        unionQueriesParams.extend(whereParameters)

    if fetchContexts:
        orderBySuffix = ''
    else:
        orderBySuffix = orderByTriple and ' ORDER BY %s,%s,%s'%(SlotPrefixes[SUBJECT],SlotPrefixes[PREDICATE],SlotPrefixes[OBJECT]) or ''
    if len(unionQueries) == 1:
        query = unionQueries[0] + orderBySuffix
    else:
        query = ' union all '.join(['('+q+')' for q in unionQueries]) + orderBySuffix
    try:
        if EXPLAIN_INFO:
            cursor.execute("EXPLAIN "+query,tuple(unionQueriesParams))
            print query
            from pprint import pprint;pprint(cursor.fetchall())
        cursor.execute(query,tuple(unionQueriesParams))
    except ValueError,e:
        print "## Query ##\n",query
        print "## Parameters ##\n",unionQueriesParams
        raise e
    if fetchall:
        qRT = cursor.fetchall()
    else:
        qRT = cursor.fetchone()
    return qRT

CREATE_RESULT_TABLE = \
"""
CREATE TEMPORARY TABLE result (
    subject text NOT NULL,
    subjectTerm enum('F','V','U','B','L') NOT NULL,
    predicate text NOT NULL,
    predicateTerm enum('F','V','U','B','L') NOT NULL,
    object text NOT NULL,
    objectTerm enum('F','V','U','B','L') NOT NULL,
    context text not NULL,
    contextTerm enum('F','V','U','B','L') NOT NULL,
    dataType text,
    language char(3),
    INDEX USING BTREE (context(50))
)
"""
CROSS_BRP_QUERY_SQL="SELECT STRAIGHT_JOIN %s FROM %s %s WHERE "
CROSS_BRP_RESULT_QUERY_SQL="SELECT * FROM result ORDER BY context"
DROP_RESULT_TABLE_SQL = "DROP result"

BRPQueryDecisionMap = {
    'WL':(NamedLiteralProperties),
    'WU':(AssociativeBox,NamedBinaryRelations),
    'WW':(NamedLiteralProperties,AssociativeBox,NamedBinaryRelations),
    'WR':(NamedLiteralProperties,AssociativeBox,NamedBinaryRelations),  #Could be optimized to not include NamedBinaryRelations
    'RTL':(NamedLiteralProperties),
    'RTU':(NamedBinaryRelations,AssociativeBox),
    'RTR':(NamedLiteralProperties,AssociativeBox,NamedBinaryRelations), #Could be optimized to not include NamedBinaryRelations
    'TU':(AssociativeBox),
    'TW':(AssociativeBox),
    'TR':(AssociativeBox),
    'U_RNTL':(NamedLiteralProperties),
    'U_RNTU':(NamedBinaryRelations),
    'U_RNTW':(NamedLiteralProperties,NamedBinaryRelations),
    'U_RNTR':(NamedLiteralProperties,NamedBinaryRelations), #Could be optimized to not include NamedBinaryRelations
}

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
