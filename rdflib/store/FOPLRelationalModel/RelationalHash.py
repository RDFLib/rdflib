"""
This module implements two hash tables for identifiers and values that 
facilitate maximal index lookups and minimal redundancy (since identifiers and values are stored once
only and referred to by integer half-md5-hashes).  The identifier hash uses
the half-md5-hash (converted by base conversion to an integer) to key on the identifier's full
lexical form (for partial matching by REGEX) and their term types.
The use of a half-hash introduces a collision risk that is currently not accounted for.  The volume at which
the risk becomes significant is calculable, though through the 'birthday paradox'.

The value hash is keyed off the half-md5-hash (as an integer also) and stores the identifier's full lexical
representation (for partial matching by REGEX)

These classes are meant to automate the creation, management, linking, insertion of these hashes (by SQL)
automatically
    
see: http://en.wikipedia.org/wiki/Birthday_Paradox
"""

from rdflib import BNode
from rdflib import RDF
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef
from rdflib.term_utils import *
from rdflib.Graph import QuotedGraph
from rdflib.store.REGEXMatching import REGEXTerm
from QuadSlot import POSITION_LIST, normalizeValue
Any = None

COLLISION_DETECTION = False

CREATE_HASH_TABLE = """
CREATE TABLE %s (    
    %s
) ENGINE=InnoDB;"""

IDENTIFIER_GARBAGE_COLLECTION_SQL="CREATE TEMPORARY TABLE danglingIds SELECT %s.%s FROM %s %s where %s and %s.%s <> %s;"
VALUE_GARBAGE_COLLECTION_SQL="CREATE TEMPORARY TABLE danglingIds SELECT %s.%s FROM %s %s where %s"
PURGE_KEY_SQL="DELETE %s FROM %s INNER JOIN danglingIds on danglingIds.%s = %s.%s;"

def GarbageCollectionQUERY(idHash,valueHash,aBoxPart,binRelPart,litPart):
    """
    Performs garbage collection on interned identifiers and their references.  Joins 
    the given KB parititions against the identifiers and values and removes the 'danglers'.  This
    must be performed after every removal of an assertion and so becomes a primary bottleneck
    """
    purgeQueries = ["drop temporary table if exists danglingIds"]
    rdfTypeInt = normalizeValue(RDF.type,'U')
    idHashKeyName = idHash.columns[0][0]
    valueHashKeyName = valueHash.columns[0][0]
    idHashJoinees    = [aBoxPart,binRelPart,litPart]
    idJoinClauses = []
    idJoinColumnCandidates = []
    explicitJoins = []
    for part in idHashJoinees:
        partJoinClauses = []
        for colName in part.columnNames:
            if part.columnNames.index(colName) >= 4:
                colName,sqlType,index = colName
                if sqlType.lower()[:6]=='bigint':
                    partJoinClauses.append("%s.%s = %s.%s"%(part,colName,idHash,idHashKeyName))
                    idJoinColumnCandidates.append("%s.%s"%(part,colName))
            elif colName:
                partJoinClauses.append("%s.%s = %s.%s"%(part,colName,idHash,idHashKeyName))
                idJoinColumnCandidates.append("%s.%s"%(part,colName))
        explicitJoins.append("left join %s on (%s)"%(part,' or '.join(partJoinClauses)))
        idJoinClauses.extend(partJoinClauses)
                
    intersectionClause = " and ".join([col + " is NULL" for col in idJoinColumnCandidates])
    idGCQuery = IDENTIFIER_GARBAGE_COLLECTION_SQL%(
        idHash,
        idHashKeyName,
        idHash,
        ' '.join(explicitJoins),
        intersectionClause,
        idHash,
        idHashKeyName,
        rdfTypeInt
    )
    
    idPurgeQuery = PURGE_KEY_SQL%(idHash,idHash,idHashKeyName,idHash,idHashKeyName)    
    purgeQueries.append(idGCQuery)
    purgeQueries.append(idPurgeQuery)    

    partJoinClauses = []
    idJoinColumnCandidates = []
    explicitJoins = []
    partJoinClauses.append("%s.%s = %s.%s"%(litPart,litPart.columnNames[OBJECT],valueHash,valueHashKeyName))
    idJoinColumnCandidates.append("%s.%s"%(litPart,litPart.columnNames[OBJECT]))

    intersectionClause = " and ".join([col + " is NULL" for col in idJoinColumnCandidates])
    valueGCQuery = VALUE_GARBAGE_COLLECTION_SQL%(
        valueHash,
        valueHashKeyName,
        valueHash,
        "left join %s on (%s)"%(litPart,' or '.join(partJoinClauses)),
        intersectionClause
    )
    
    valuePurgeQuery = PURGE_KEY_SQL%(valueHash,valueHash,valueHashKeyName,valueHash,valueHashKeyName)    
    purgeQueries.append("drop temporary table if exists danglingIds")
    purgeQueries.append(valueGCQuery)
    purgeQueries.append(valuePurgeQuery)
    return purgeQueries

class RelationalHash:    
    def __init__(self,identifier):
        self.identifier = identifier
        self.hashUpdateQueue = {}

    def defaultSQL(self):
        return ''

    def EscapeQuotes(self,qstr):
        if qstr is None:
            return ''
        tmp = qstr.replace("\\","\\\\")
        tmp = tmp.replace("'", "\\'")
        return tmp

    def normalizeTerm(self,term):
        if isinstance(term,(QuotedGraph,Graph)):
            return term.identifier.encode('utf-8')
        elif isinstance(term,Literal):
            return self.EscapeQuotes(term).encode('utf-8')
        elif term is None or isinstance(term,(list,REGEXTerm)):
            return term
        else:
            return term.encode('utf-8')
        
    def __repr__(self):
        return "%s_%s"%(self.identifier,self.tableNameSuffix)
        
    def createSQL(self):
        columnSQLStmts = []
        for colName,colType,indexMD in self.columns:                        
            assert indexMD
            indexName,indexCol = indexMD
            if indexName:
                if self.columns.index((colName,colType,indexMD)) > POSITION_LIST:
                    columnSQLStmts.append("\t%s\t%s"%(colName,colType))
                else:
                    columnSQLStmts.append("\t%s\t%s not NULL"%(colName,colType))
                columnSQLStmts.append("\tINDEX %s (%s)"%(indexName,indexCol))
            else:
                columnSQLStmts.append("\t%s\t%s not NULL PRIMARY KEY"%(colName,colType))
        
        return CREATE_HASH_TABLE%(
            self,
            ',\n'.join(columnSQLStmts)            
        )
    def dropSQL(self):
        pass
    
class IdentifierHash(RelationalHash):
    columns = [
                ('id','BIGINT unsigned',[None,'id']),
                ('term_type',"enum('U','B','F','V','L')",['termTypeIndex','term_type']),
                ('lexical','text',['lexical_index','lexical(100)'])
    ]

    tableNameSuffix = 'identifiers'    

    def defaultSQL(self):
        """
        Since rdf:type is modeled explicitely (in the ABOX partition) it must be inserted as a 'default'
        identifier
        """
        return 'INSERT into %s values (%s,"U","%s");'%(self,normalizeValue(RDF.type,'U'),RDF.type)

    def generateDict(self,db):
        c=db.cursor()
        c.execute("select * from %s"%self)
        rtDict = {}
        for rt in c.fetchall():
            rtDict[rt[0]] = (rt[1],rt[2])
        c.close()
        return rtDict

    def updateIdentifierQueue(self,termList):
        for term,termType in termList:
            md5Int = normalizeValue(term,termType)
            self.hashUpdateQueue[md5Int]=(termType,self.normalizeTerm(term))
        
    def insertIdentifiers(self,db):
        c=db.cursor()
        keyCol = self.columns[0][0]
        if self.hashUpdateQueue:
            params = [(md5Int,termType,lexical) for md5Int,(termType,lexical) in self.hashUpdateQueue.items()]
            c.executemany("INSERT IGNORE INTO %s"%(self)+" VALUES (%s,%s,%s)",params)
            if COLLISION_DETECTION:
                insertedIds = self.hashUpdateQueue.keys()
                if len(insertedIds) > 1:
                    c.execute("SELECT * FROM %s"%(self)+" WHERE %s"%keyCol+" in %s",(tuple(insertedIds),))
                else:
                    c.execute("SELECT * FROM %s"%(self)+" WHERE %s"%keyCol+" = %s",tuple(insertedIds))
                for key,termType,lexical in c.fetchall():
                    if self.hashUpdateQueue[key] != (termType,lexical):
                        #Collision!!! Raise an exception (allow the app to rollback the transaction if it wants to)
                        raise Exception("Hash Collision (in %s) on %s,%s vs %s,%s!"%(self,termType,lexical,self.hashUpdateQueue[key][0],self.hashUpdateQueue[key][1]))
                    
            self.hashUpdateQueue = {}
        c.close()

class LiteralHash(RelationalHash):
    columns = [
                ('id','BIGINT unsigned',[None,'id']),
                ('lexical','text',['lexicalIndex','lexical(100)']),
                ]
    tableNameSuffix = 'literals'    

    def generateDict(self,db):
        c=db.cursor()
        c.execute("select * from %s"%self)
        rtDict = {}
        for rt in c.fetchall():
            rtDict[rt[0]] = rt[1]
        c.close()
        return rtDict

    def updateIdentifierQueue(self,termList):
        for term,termType in termList:
            md5Int = normalizeValue(term,termType)
            self.hashUpdateQueue[md5Int]=self.normalizeTerm(term)
        
    def insertIdentifiers(self,db):
        c=db.cursor()
        keyCol = self.columns[0][0]
        if self.hashUpdateQueue:
            params = [(md5Int,lexical) for md5Int,lexical in self.hashUpdateQueue.items()]
            c.executemany("INSERT IGNORE INTO %s"%(self)+" VALUES (%s,%s)",params)
            if COLLISION_DETECTION:
                insertedIds = self.hashUpdateQueue.keys()
                if len(insertedIds) > 1:
                    c.execute("SELECT * FROM %s"%(self)+" WHERE %s"%keyCol+" in %s",(tuple(insertedIds),))
                else:
                    c.execute("SELECT * FROM %s"%(self)+" WHERE %s"%keyCol+" = %s",tuple(insertedIds))
                for key,lexical in c.fetchall():
                    if self.hashUpdateQueue[key] != lexical:
                        #Collision!!! Raise an exception (allow the app to rollback the transaction if it wants to)
                        raise Exception("Hash Collision (in %s) on %s vs %s!"%(self,lexical,self.hashUpdateQueue[key][0]))
            self.hashUpdateQueue = {}
        c.close()