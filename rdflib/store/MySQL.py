from __future__ import generators
from rdflib import BNode
from rdflib.store import Store
from rdflib import RDF
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from pprint import pprint
from rdflib.Variable import Variable
import MySQLdb,sha,sys,re
from rdflib.term_utils import *
from rdflib.Graph import QuotedGraph
from rdflib.store.REGEXMatching import REGEXTerm
Any = None

COUNT_SELECT   = 0
CONTEXT_SELECT = 1
TRIPLE_SELECT  = 2

ASSERTED_NON_TYPE_PARTITION = 3
ASSERTED_TYPE_PARTITION     = 4
QUOTED_PARTITION            = 5
ASSERTED_LITERAL_PARTITION  = 6

FULL_TRIPLE_PARTITIONS = [QUOTED_PARTITION,ASSERTED_LITERAL_PARTITION]

#FIXME:  This *may* prove to be a performance bottleneck and should perhaps be implemented in C (as it was in 4Suite RDF)
def EscapeQuotes(qstr):
    """
    Ported from Ft.Lib.DbUtil
    """
    if qstr is None:
        return u''
    tmp = qstr.replace("\\","\\\\")
    tmp = tmp.replace("'", "\\'")
    return tmp
#Terms: u - uri refs  v - variables  b - bnodes l - literal f - formula

#Normalize a MySQL command before executing it.  Commence unicode black magic
def _normalizeMySQLCmd(cmd):
    return cmd.encode('utf-8')


#Helper function for building union all select statement
#Takes a list of:
# - table name
# - table alias
# - table type (literal, type, asserted, quoted)
# - where clause string
def unionSELECT(selectComponents,distinct=False,selectType=TRIPLE_SELECT):
    selects = []
    for tableName,tableAlias,whereClause,tableType in selectComponents:
        assert isinstance(whereClause,unicode)

        if selectType == COUNT_SELECT:
            selectString = "select count(*)"
            tableSource = u" from %s "%tableName
        elif selectType == CONTEXT_SELECT:
            selectString = "select %s.context"%tableAlias
            tableSource = u" from %s as %s "%(tableName,tableAlias)
        elif tableType in FULL_TRIPLE_PARTITIONS:
            selectString = "select *"#%(tableAlias)
            tableSource = u" from %s as %s "%(tableName,tableAlias)
        elif tableType == ASSERTED_TYPE_PARTITION:
            selectString =\
            u"""select %s.member as subject, '%s' as predicate, %s.klass as object, %s.context as context, %s.termComb as termComb, NULL as objLanguage, NULL as objDatatype"""%(tableAlias,RDF.type,tableAlias,tableAlias,tableAlias)
            tableSource = u" from %s as %s "%(tableName,tableAlias)
        elif tableType == ASSERTED_NON_TYPE_PARTITION:
            selectString =\
            u"""select *,NULL as objLanguage, NULL as objDatatype"""
            tableSource = u" from %s as %s "%(tableName,tableAlias)
        
        selects.append('('+selectString + tableSource + whereClause+')')

    orderStmt = ''
    if selectType == TRIPLE_SELECT:
        orderStmt = ' order by subject,predicate,object'
    if distinct:
        return u' union '.join(selects) + orderStmt
    else:
        return u' union all '.join(selects) + orderStmt

#Builds WHERE clauses for the supplied terms and, context
def buildClause(tableName,subject,predicate, obj,context=None,typeTable=False):
    if typeTable:
        rdf_type_memberClause   = buildTypeMemberClause(subject,tableName)
        rdf_type_klassClause    = buildTypeClassClause(obj,tableName)
        rdf_type_contextClause  = buildContextClause(context,tableName)
        typeClauses = [rdf_type_memberClause,rdf_type_klassClause,rdf_type_contextClause]
        clauseString = u' and '.join([clause for clause in typeClauses if clause])
        clauseString = clauseString and u'where %s'%clauseString or u''
    else:
       subjClause        = buildSubjClause(subject,tableName)
       predClause        = buildPredClause(predicate,tableName)
       objClause         = buildObjClause(obj,tableName)
       contextClause           = buildContextClause(context,tableName)
       litDTypeClause    = buildLitDTypeClause(obj,tableName)
       litLanguageClause = buildLitLanguageClause(obj,tableName)

       clauses=[subjClause,predClause,objClause,contextClause,litDTypeClause,litLanguageClause]
       clauseString = u' and '.join([clause for clause in clauses if clause])
       clauseString = clauseString and u'where %s'%clauseString or u''
    return clauseString

#Builds an insert command for a type table
def buildTypeSQLCommand(member,klass,context,storeId):
    #columns: member,klass,context
    rt= u"INSERT INTO %s_type_statements VALUES ('%s', '%s', '%s',%s)"%(
        storeId,
        normalizeTerm(member),
        normalizeTerm(klass),
        context.identifier,
        type2TermCombination(member,klass,context))
    return rt

#Builds an insert command for literal triples (statements where the object is a Literal)
def buildLiteralTripleSQLCommand(subject,predicate,obj,context,storeId):
    triplePattern = statement2TermCombination(subject,predicate,obj,context)
    literal_table = "%s_literal_statements"%storeId
    command=u"INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', %s,%s,%s)"%(
        literal_table,
        normalizeTerm(subject),
        normalizeTerm(predicate),
        normalizeTerm(obj),
        context.identifier,
        str(triplePattern),
        isinstance(obj,Literal) and  "'%s'"%obj.language or 'NULL',
        isinstance(obj,Literal) and "'%s'"%obj.datatype or 'NULL')
    return command

#Builds an insert command for regular triple table
def buildTripleSQLCommand(subject,predicate,obj,context,storeId,quoted):
    stmt_table = quoted and "%s_quoted_statements"%storeId or "%s_asserted_statements"%storeId
    triplePattern = statement2TermCombination(subject,predicate,obj,context)
    if quoted:
        command=u"INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', %s,%s,%s)"%(
            stmt_table,
            normalizeTerm(subject),
            normalizeTerm(predicate),
            normalizeTerm(obj),
            context.identifier,
            str(triplePattern),
            isinstance(obj,Literal) and  "'%s'"%obj.language or 'NULL',
            isinstance(obj,Literal) and "'%s'"%obj.datatype or 'NULL')
    else:
        command=u"INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', %s)"%(
            stmt_table,
            normalizeTerm(subject),
            normalizeTerm(predicate),
            normalizeTerm(obj),
            context.identifier,
            str(triplePattern))
    return command

#Takes a dictionary which represents an entry in a result set and
#converts it to a tuple of terms using the termComb integer
#to interpret how to instanciate each term
def extractTriple(tupleRt,store,hardCodedContext=None):
    subject,predicate,obj,rtContext,termComb,objLanguage,objDatatype = tupleRt    
    context = rtContext is not None and rtContext or hardCodedContext.identifier
    termCombString=REVERSE_TERM_COMBINATIONS[termComb]
    subjTerm,predTerm,objTerm,ctxTerm = termCombString
    s=createTerm(subject,subjTerm,store)
    p=predicate == RDF.type and RDF.type or createTerm(predicate,predTerm,store)            
    o=createTerm(obj,objTerm,store,objLanguage,objDatatype)
    
    graphKlass, idKlass = constructGraph(ctxTerm)
    return s,p,o,(graphKlass,idKlass,context)

#Takes a term and 'normalizes' it.
#Literals are escaped, Quoted graphs are replaced with just their identifiers
def normalizeTerm(term):
    if isinstance(term,(QuotedGraph,Graph)):
        return term.identifier
    else:
        return EscapeQuotes(term)

#Takes a term value, term type, and store intance
#and Creates a term object.  QuotedGraphs are instanciated differently
def createTerm(termString,termType,store,objLanguage=None,objDatatype=None):    
    if termType == 'L':
        cache = store.termCache.get((termType,termString,objLanguage,objDatatype))
        if cache is not None:
            return cache
        else:
            rt = Literal(termString,objLanguage,objDatatype)
            store.termCache[((termType,termString,objLanguage,objDatatype))] = rt
            return rt
    elif termType=='F':
        cache = store.termCache.get((termType,termString))
        if cache is not None:
            return cache
        else:
            rt = QuotedGraph(store,termString)
            store.termCache[(termType,termString)] = rt
            return rt
    else:
        cache = store.termCache.get((termType,termString))
        if cache is not None:
            return cache
        else:
            rt = TERM_INSTANCIATION_DICT[termType](termString)
            store.termCache[(termType,termString)] = rt
            return rt

#Where Clause  utility Functions
#The predicate and object clause builders are modified in order to optimize
#subjects and objects utility functions which can take lists as their last argument (object,predicate - respectively)
def buildSubjClause(subject,tableName):
    if isinstance(subject,REGEXTerm):
        return u"%s REGEXP '%s'"%(tableName and u'%s.subject'%tableName or u'subject',EscapeQuotes(subject))
    elif isinstance(subject,list):
        clauseStrings=[]
        for s in subject:
            if isinstance(s,REGEXTerm):
                clauseStrings.append(u"%s REGEXP '%s'"%(tableName and u'%s.subject'%tableName or u'subject',EscapeQuotes(s)))
            elif isinstance(s,(QuotedGraph,Graph)):
                clauseStrings.append(u"%s='%s'"%(tableName and u'%s.subject'%tableName or u'subject',s.identifier))                
            else:
                clauseStrings.append(s and u"%s='%s'"%(tableName and u'%s.subject'%tableName or u'subject',s) or None)
        return u'(%s)'%u' or '.join([clauseString for clauseString in clauseStrings])
    elif isinstance(subject,(QuotedGraph,Graph)):
        return u"%s='%s'"%(tableName and u'%s.subject'%tableName or u'subject',subject.identifier)    
    else:
        return subject and u"%s='%s'"%(tableName and u'%s.subject'%tableName or u'subject',subject) or None

#Capable off taking a list of predicates as well (in which case sub clauses are joined with 'OR')
def buildPredClause(predicate,tableName):
    if isinstance(predicate,REGEXTerm):
        return u"%s REGEXP '%s'"%(tableName and u'%s.predicate'%tableName or u'predicate',EscapeQuotes(predicate))
    elif isinstance(predicate,list):
        clauseStrings=[]
        for p in predicate:
            if isinstance(p,REGEXTerm):
                clauseStrings.append(u"%s REGEXP '%s'"%(tableName and u'%s.predicate'%tableName or u'predicate',EscapeQuotes(p)))
            else:
                clauseStrings.append(predicate and u"%s='%s'"%(tableName and u'%s.predicate'%tableName or u'predicate',p) or None)
        return u'(%s)'%u' or '.join([clauseString for clauseString in clauseStrings])
    else:
        return predicate and u"%s='%s'"%(tableName and u'%s.predicate'%tableName or u'predicate',predicate) or None

#Capable of taking a list of objects as well (in which case sub clauses are joined with 'OR')    
def buildObjClause(obj,tableName):
    if isinstance(obj,REGEXTerm):
        return u"%s REGEXP '%s'"%(tableName and u'%s.object'%tableName or u'object',EscapeQuotes(obj))
    elif isinstance(obj,list):
        clauseStrings=[]
        for o in obj:
            if isinstance(o,REGEXTerm):
                clauseStrings.append(u"%s REGEXP '%s'"%(tableName and u'%s.object'%tableName or u'object',EscapeQuotes(o)))
            elif isinstance(o,(QuotedGraph,Graph)):
                clauseStrings.append(u"%s='%s'"%(tableName and u'%s.object'%tableName or u'object',o.identifier))
            else:
                clauseStrings.append(o and u"%s='%s'"%(tableName and u'%s.object'%tableName or u'object',isinstance(o,Literal) and EscapeQuotes(o) or o) or None)
        return u'(%s)'%u' or '.join([clauseString for clauseString in clauseStrings])
    elif isinstance(obj,(QuotedGraph,Graph)):
        return u"%s='%s'"%(tableName and u'%s.object'%tableName or u'object',obj.identifier)
    else:
        return obj and u"%s='%s'"%(tableName and u'%s.object'%tableName or u'object',EscapeQuotes(obj)) or None

def buildContextClause(context,tableName):
    context = context is not None and context.identifier or context
    if isinstance(context,REGEXTerm):
        return u"%s REGEXP '%s'"%(tableName and u'%s.context'%tableName,EscapeQuotes(context))
    else:
        return context and u"%s='%s'"%(tableName and u'%s.context'%tableName,context) or None
    
def buildLitDTypeClause(obj,tableName):
    return (isinstance(obj,Literal) and obj.datatype and u"%s.objDatatype='%s'"%(tableName,obj.datatype)) or None 

def buildLitLanguageClause(obj,tableName):
    return (isinstance(obj,Literal) and obj.datatype and "%s.objLanguage='%s'"%(tableName,obj.language)) or None

def buildTypeMemberClause(subject,tableName):
    if isinstance(subject,REGEXTerm):
        return u"%s.member REGEXP '%s'"%(tableName,EscapeQuotes(subject))
    elif isinstance(subject,list):
        subjs = [isinstance(s,(QuotedGraph,Graph)) and s.identifier or s for s in subject]        
        return u' or '.join([s and u"%s.member = '%s'"%(tableName,s) for s in subjs])    
    else:
        return subject and u"%s.member = '%s'"%(tableName,subject)
    
def buildTypeClassClause(obj,tableName):
    if isinstance(obj,REGEXTerm):
        return u"%s.klass REGEXP '%s'"%(tableName,EscapeQuotes(obj))
    elif isinstance(obj,list):
        obj = [isinstance(o,(QuotedGraph,Graph)) and o.identifier or o for o in obj]        
        return u' or '.join([o and not isinstance(o,Literal) and u"%s.klass = '%s'"%(tableName,o) for o in obj])
    else:
        return obj and not isinstance(obj,Literal) and u"%s.klass = '%s'"%(tableName,obj)
    
def ParseConfigurationString(config_string):
    """
    Parses a configuration string in the form:
    key1=val1,key2=val2,key3=val3,...
    The following configuration keys are expected (not all are required):
    user
    password
    db
    host
    port (optional - defaults to 3306)
    """
    kvDict = dict([(part.split('=')[0],part.split('=')[-1]) for part in config_string.split(',')])
    for requiredKey in ['user','db','host']:
        assert requiredKey in kvDict
    if 'port' not in kvDict:
        kvDict['port']=3306
    if 'password' not in kvDict:
        kvDict['password']=''
    return kvDict

class MySQL(Store):
    """
    MySQL store formula-aware implementation.  It stores it's triples in the following partitions:

    - Asserted non rdf:type statements
    - Asserted rdf:type statements (in a table which models Class membership)
    The motivation for this partition is primarily query speed and scalability as most graphs will always have more rdf:type statements than others
    - All Quoted statements

    In addition it persists namespace mappings in a seperate table
    """
    context_aware = True
    formula_aware = True
    transaction_aware = True
    regex_matching = True
    def __init__(self, identifier=None, configuration=None):
        """ 
        identifier: URIRef of the Store. Defaults to CWD
        configuration: string containing infomation open can use to
        connect to datastore.
        """
        self.identifier = identifier and identifier or 'hardcoded'
        #Use only the first 10 bytes of the digest
        self._internedId = sha.new(self.identifier).hexdigest()[:10]

        #This parameter controls how exlusively the literal table is searched
        #If true, the Literal partition is searched *exclusively* if the object term
        #in a triple pattern is a Literal or a REGEXTerm.  Note, the latter case
        #prevents the matching of URIRef nodes as the objects of a triple in the store.
        #If the object term is a wildcard (None)
        #Then the Literal paritition is searched in addition to the others
        #If this parameter is false, the literal partition is searched regardless of what the object
        #of the triple pattern is
        self.STRONGLY_TYPED_TERMS = False
        
        if configuration is not None:
            self.open(configuration)
            
        self.termCache = {}
            
    #Database Management Methods
    def open(self, configuration, create=True):
        """ 
        Opens the store specified by the configuration string. If
        create is True a store will be created if it does not already
        exist. If create is False and a store does not already exist
        an exception is raised. An exception is also raised if a store
        exists, but there is insufficient permissions to open the
        store."""
        configDict = ParseConfigurationString(configuration)
        if create:
            test_db = MySQLdb.connect(user=configDict['user'],
                                      passwd=configDict['password'],
                                      db='test',
                                      port=configDict['port'],
                                      host=configDict['host']
                                      )        
            c=test_db.cursor()
            c.execute("""SET AUTOCOMMIT=0""")
            c.execute("""SHOW DATABASES""")
            if not (configDict['db'].encode('utf-8'),) in c.fetchall():
                print "creating %s (doesn't exist)"%(configDict['db'])
                c.execute("""CREATE DATABASE %s"""%(configDict['db'],))
                test_db.commit()                            
                c.close()
                test_db.close()    
                
            db = MySQLdb.connect(user = configDict['user'],
                                 passwd = configDict['password'],
                                 db=configDict['db'],
                                 port=configDict['port'],
                                 host=configDict['host']
                                 )
            c=db.cursor()
            c.execute("""SET AUTOCOMMIT=0""")   
            c.execute(CREATE_ASSERTED_STATEMENTS_TABLE%(self._internedId))
            c.execute(CREATE_ASSERTED_TYPE_STATEMENTS_TABLE%(self._internedId))
            c.execute(CREATE_QUOTED_STATEMENTS_TABLE%(self._internedId))
            c.execute(CREATE_NS_BINDS_TABLE%(self._internedId))
            c.execute(CREATE_LITERAL_STATEMENTS_TABLE%(self._internedId))                                
            db.commit()
            c.close()
            db.close()            

        self._db = MySQLdb.connect(user = configDict['user'],
                                   passwd = configDict['password'],
                                   db=configDict['db'],
                                   port=configDict['port'],
                                   host=configDict['host']
                                  )
        c=self._db.cursor()
        c.execute("""SHOW DATABASES""")
        rt = c.fetchall()

        if (configDict['db'].encode('utf-8'),) in rt:
            for tn in [tbl%(self._internedId) for tbl in table_name_prefixes]:
                c.execute("""show tables like '%s'"""%(tn,))
                rt=c.fetchall()
                if not rt:
                    sys.stderr.write("table %s Doesn't exist\n" % (tn));
                    #The database exists, but one of the partitions doesn't exist
                    return 0
            #Everything is there (the database and the partitions)
            return 1
        #The database doesn't exist - nothing is there
        return -1

    def close(self, commit_pending_transaction=False):
        """ 
        FIXME:  Add documentation!!
        """
        if commit_pending_transaction:
            self._db.commit()
        self._db.close()

    def destroy(self, configuration):
        """
        FIXME: Add documentation
        """        
        configDict = ParseConfigurationString(configuration)
        msql_db = MySQLdb.connect(user=configDict['user'],
                                passwd=configDict['password'],
                                db=configDict['db'],
                                port=configDict['port'],
                                host=configDict['host']
                                )
        c=msql_db.cursor()
        c.execute("""SET AUTOCOMMIT=0""")
        for tblsuffix in table_name_prefixes:
            try:
                c.execute('DROP table %s'%tblsuffix%(self._internedId))
                #print "dropped table: %s"%(tblsuffix%(self._internedId))
            except:
                print "unable to drop table: %s"%(tblsuffix%(self._internedId))
            
            
        #Note, this only removes the associated tables for the closed world universe given by the identifier
        print "Destroyed Close World Universe %s ( in MySQL database %s)"%(self.identifier,configDict['db'])
        msql_db.commit()
        msql_db.close()
        
    #Triple Methods    
        
    def add(self, (subject, predicate, obj), context=None, quoted=False):        
        """ Add a triple to the store of triples. """
        c=self._db.cursor()
        c.execute("""SET AUTOCOMMIT=0""")
        if quoted or predicate != RDF.type:
            #quoted statement or non rdf:type predicate
            #check if object is a literal
            if isinstance(obj,Literal):
                addCmd=buildLiteralTripleSQLCommand(subject,predicate,obj,context,self._internedId)
            else:
                addCmd=buildTripleSQLCommand(subject,predicate,obj,context,self._internedId,quoted)
        elif predicate == RDF.type:
            #asserted rdf:type statement
            addCmd=buildTypeSQLCommand(subject,obj,context,self._internedId)
        c.execute(_normalizeMySQLCmd(addCmd))

    def remove(self, (subject, predicate, obj), context):
        """ Remove a triple from the store """
        if context is not None:
            if subject is None and predicate is None and object is None:
                self._remove_context(context)
                return
        c=self._db.cursor()
        c.execute("""SET AUTOCOMMIT=0""")        
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId
        if not predicate or predicate != RDF.type:            
            #Need to remove predicates other than rdf:type

            if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal):
                #remove literal triple
                clauseString = buildClause(literal_table,subject,predicate, obj,context)
                cmd=clauseString and u"DELETE FROM %s %s"%(literal_table,clauseString) or u'DELETE FROM %s;'%literal_table
                c.execute(_normalizeMySQLCmd(cmd))

            for table in [quoted_table,asserted_table]:
                #If asserted non rdf:type table and obj is Literal, don't do anything (already taken care of)
                if table == asserted_table and isinstance(obj,Literal):
                    continue
                else:
                    clauseString = buildClause(table,subject,predicate,obj,context)
                    cmd=clauseString and u"DELETE FROM %s %s"%(table,clauseString) or u'DELETE FROM %s;'%table
                    c.execute(_normalizeMySQLCmd(cmd))

        if predicate == RDF.type or not predicate:
            #Need to check rdf:type and quoted partitions (in addition perhaps)
            clauseString = buildClause(asserted_type_table,subject,RDF.type,obj,context,True)
            cmd=clauseString and u"DELETE FROM %s %s"%(asserted_type_table,clauseString) or u'DELETE FROM %s;'%asserted_type_table
            c.execute(_normalizeMySQLCmd(cmd))

            clauseString = buildClause(quoted_table,subject,predicate, obj,context)
            cmd=clauseString and u"DELETE FROM %s %s"%(quoted_table,clauseString) or 'DELETE FROM %s;'%quoted_table
            c.execute(cmd)
            
    def triples(self, (subject, predicate, obj), context=None):
        """ 
        A generator over all the triples matching pattern. Pattern can
        be any objects for comparing against nodes in the store, for
        example, RegExLiteral, Date? DateRange?
        
        quoted table:                <id>_quoted_statements
        asserted rdf:type table:     <id>_type_statements
        asserted non rdf:type table: <id>_asserted_statements
        
        triple columns: subject,predicate,object,context,termComb,objLanguage,objDatatype
        class membership columns: member,klass,context termComb

        FIXME:  These union all selects *may* be further optimized by joins 
        
        """
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId
        c=self._db.cursor()

        if predicate == RDF.type:
            #select from asserted rdf:type partition and quoted table (if a context is specified)
            selects = [
                (
                  asserted_type_table,
                  'typeTable',
                  buildClause('typeTable',subject,RDF.type, obj,context,True),
                  ASSERTED_TYPE_PARTITION
                ),
            ]

        elif isinstance(predicate,REGEXTerm) and predicate.compiledExpr.match(RDF.type) or not predicate:
            #Select from quoted partition (if context is specified), literal partition if (obj is Literal or None) and asserted non rdf:type partition (if obj is URIRef or None)
            selects = []
            if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal) or not obj or (self.STRONGLY_TYPED_TERMS and isinstance(obj,REGEXTerm)):
                selects.append((
                  literal_table,
                  'literal',
                  buildClause('literal',subject,predicate,obj,context),
                  ASSERTED_LITERAL_PARTITION
                ))                    
            if not isinstance(obj,Literal) and not (isinstance(obj,REGEXTerm) and self.STRONGLY_TYPED_TERMS) or not obj:
                selects.append((
                  asserted_table,
                  'asserted',
                  buildClause('asserted',subject,predicate,obj,context),
                  ASSERTED_NON_TYPE_PARTITION
                ))
                
            selects.append(
                (
                  asserted_type_table,
                  'typeTable',
                  buildClause('typeTable',subject,RDF.type,obj,context,True),
                  ASSERTED_TYPE_PARTITION                    
                )
            )
                

        elif predicate:
            #select from asserted non rdf:type partition (optionally), quoted partition (if context is speciied), and literal partition (optionally)
            selects = []
            if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal) or not obj or (self.STRONGLY_TYPED_TERMS and isinstance(obj,REGEXTerm)):
                selects.append((
                  literal_table,
                  'literal',
                  buildClause('literal',subject,predicate,obj,context),
                  ASSERTED_LITERAL_PARTITION
                ))
            if not isinstance(obj,Literal) and not (isinstance(obj,REGEXTerm) and self.STRONGLY_TYPED_TERMS) or not obj:                
                selects.append((
                  asserted_table,
                  'asserted',
                  buildClause('asserted',subject,predicate,obj,context),
                  ASSERTED_NON_TYPE_PARTITION
                ))                    

        if context is not None:
            selects.append(
                (
                  quoted_table,
                  'quoted',
                  buildClause('quoted',subject,predicate, obj,context),
                  QUOTED_PARTITION
                )
            )

        q=unionSELECT(selects)
        c.execute(_normalizeMySQLCmd(q))
        rt = c.fetchone()
        while rt:
            s,p,o,(graphKlass,idKlass,graphId) = extractTriple(rt,self,context)
            currentContext=graphKlass(self,idKlass(graphId))
            contexts = [currentContext]
            rt = next = c.fetchone()
            sameTriple = next and extractTriple(next,self,context)[:3] == (s,p,o)
            while sameTriple:
                s2,p2,o2,(graphKlass,idKlass,graphId) = extractTriple(next,self,context)
                c2 = graphKlass(self,idKlass(graphId))
                contexts.append(c2)
                rt = next = c.fetchone()
                sameTriple = next and extractTriple(next,self,context)[:3] == (s,p,o)
                    
            yield (s,p,o),(c for c in contexts)
            
    def __repr__(self):
        c=self._db.cursor()
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId
        
        selects = [
            (
              asserted_type_table,
              'typeTable',
              u'',
              ASSERTED_TYPE_PARTITION          
            ),
            (
              quoted_table,
              'quoted',
              u'',
              QUOTED_PARTITION     
            ),
            (
              asserted_table,
              'asserted',
              u'',
              ASSERTED_NON_TYPE_PARTITION                   
            ),
            (
              literal_table,
              'literal',
              u'',
              ASSERTED_LITERAL_PARTITION  
            ),                
        ]
        q=unionSELECT(selects,distinct=False,selectType=COUNT_SELECT)
        c.execute(_normalizeMySQLCmd(q))
        rt=c.fetchall()
        typeLen,quotedLen,assertedLen,literalLen = [rtTuple[0] for rtTuple in rt]
        return "<Parititioned MySQL N3 Store: %s contexts, %s classification assertions, %s quoted statements, %s property/value assertions, and %s other assertions>"%(len([c for c in self.contexts()]),typeLen,quotedLen,literalLen,assertedLen)

    def __len__(self, context=None):
        """ Number of statements in the store. """
        c=self._db.cursor()
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId

        quotedContext   = buildContextClause(context,quoted_table)
        assertedContext = buildContextClause(context,asserted_table)
        typeContext     = buildContextClause(context,asserted_type_table)
        literalContext  = buildContextClause(context,literal_table)
        
        if context is not None:
            selects = [
                (
                  asserted_type_table,
                  'typeTable',
                  typeContext and u'where ' + typeContext or u'',
                  ASSERTED_TYPE_PARTITION          
                ),
                (
                  quoted_table,
                  'quoted',
                  quotedContext and u'where ' + quotedContext or u'',
                  QUOTED_PARTITION     
                ),
                (
                  asserted_table,
                  'asserted',
                  assertedContext and u'where ' + assertedContext or u'',
                  ASSERTED_NON_TYPE_PARTITION                   
                ),
                (
                  literal_table,
                  'literal',
                  literalContext and u'where ' + literalContext or u'',
                  ASSERTED_LITERAL_PARTITION  
                ),                
            ]
            q=unionSELECT(selects,distinct=True,selectType=COUNT_SELECT)
        else:
            selects = [
                (
                  asserted_type_table,
                  'typeTable',
                  typeContext and u'where ' + typeContext or u'',
                  ASSERTED_TYPE_PARTITION
                ),
                (
                  asserted_table,
                  'asserted',
                  assertedContext and u'where ' + assertedContext or u'',
                  ASSERTED_NON_TYPE_PARTITION                   
                ),
                (
                  literal_table,
                  'literal',
                  literalContext and u'where ' + literalContext or u'',
                  ASSERTED_LITERAL_PARTITION
                ),                
            ]
            q=unionSELECT(selects,distinct=False,selectType=COUNT_SELECT)
        c.execute(_normalizeMySQLCmd(q))
        rt=c.fetchall()
        return reduce(lambda x,y: x+y,  [rtTuple[0] for rtTuple in rt])

    def contexts(self, triple=None):
        c=self._db.cursor()
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId
        if triple is not None:
            subject,predicate,obj=triple
            if predicate == RDF.type:
                #select from asserted rdf:type partition and quoted table (if a context is specified)
                selects = [
                    (
                      asserted_type_table,
                      'typeTable',
                      buildClause('typeTable',subject,RDF.type, obj,Any,True),
                      ASSERTED_TYPE_PARTITION
                    ),
                ]

            elif isinstance(predicate,REGEXTerm) and predicate.compiledExpr.match(RDF.type) or not predicate:
                #Select from quoted partition (if context is specified), literal partition if (obj is Literal or None) and asserted non rdf:type partition (if obj is URIRef or None)
                selects = [
                    (
                      asserted_type_table,
                      'typeTable',
                      buildClause('typeTable',subject,RDF.type,obj,Any,True),
                      ASSERTED_TYPE_PARTITION                   
                    ),
                ]

                if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal) or not obj or (self.STRONGLY_TYPED_TERMS and isinstance(obj,REGEXTerm)):
                    selects.append((
                      literal_table,
                      'literal',
                      buildClause('literal',subject,predicate,obj),
                      ASSERTED_LITERAL_PARTITION
                    ))
                if not isinstance(obj,Literal) and not (isinstance(obj,REGEXTerm) and self.STRONGLY_TYPED_TERMS) or not obj:                
                    selects.append((
                      asserted_table,
                      'asserted',
                      buildClause('asserted',subject,predicate,obj),
                      ASSERTED_NON_TYPE_PARTITION
                    ))                    

            elif predicate:
                #select from asserted non rdf:type partition (optionally), quoted partition (if context is speciied), and literal partition (optionally)
                selects = []
                if not self.STRONGLY_TYPED_TERMS or isinstance(obj,Literal) or not obj or (self.STRONGLY_TYPED_TERMS and isinstance(obj,REGEXTerm)):
                    selects.append((
                      literal_table,
                      'literal',
                      buildClause('literal',subject,predicate,obj),
                      ASSERTED_LITERAL_PARTITION
                    ))
                if not isinstance(obj,Literal) and not (isinstance(obj,REGEXTerm) and self.STRONGLY_TYPED_TERMS) or not obj:                
                    selects.append((
                      asserted_table,
                      'asserted',
                      buildClause('asserted',subject,predicate,obj),
                      ASSERTED_NON_TYPE_PARTITION
                ))

            selects.append(
                (
                  quoted_table,
                  'quoted',
                  buildClause('quoted',subject,predicate, obj),
                  QUOTED_PARTITION
                )
            )
            q=unionSELECT(selects,distinct=True,selectType=CONTEXT_SELECT)
        else:
            selects = [
                (
                  asserted_type_table,
                  'typeTable',
                  u'',
                  ASSERTED_TYPE_PARTITION                   
                ),
                (
                  quoted_table,
                  'quoted',
                  u'',
                  QUOTED_PARTITION     
                ),
                (
                  asserted_table,
                  'asserted',
                  u'',
                  ASSERTED_NON_TYPE_PARTITION                    
                ),
                (
                  literal_table,
                  'literal',
                  u'',
                  ASSERTED_LITERAL_PARTITION  
                ),                
            ]
            q=unionSELECT(selects,distinct=True,selectType=CONTEXT_SELECT)

        c.execute(_normalizeMySQLCmd(q))
        rt=c.fetchall()
        for context in [rtTuple[0] for rtTuple in rt]:
            yield context
    
    def _remove_context(self, identifier):
        """ """
        c=self._db.cursor()
        c.execute("""SET AUTOCOMMIT=0""")        
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        literal_table = "%s_literal_statements"%self._internedId
        for table in [quoted_table,asserted_table,asserted_type_table,literal_table]:
            c.execute(_normalizeMySQLCmd("DELETE from %s where %s"%(table,buildContextClause(identifier,table))))

    # Optional Namespace methods

    #quantifier utility methods
    def variables(context):
        raise Exception("Not implemented")                
    def existentials(context):
        raise Exception("Not implemented")                

    #optimized interfaces (those needed in order to port Versa)
    def subjects(self, predicate=None, obj=None):
        """
        A generator of subjects with the given predicate and object.
        """
        raise Exception("Not implemented")

    #capable of taking a list of predicate terms instead of a single term
    def objects(self, subject=None, predicate=None):
        """
        A generator of objects with the given subject and predicate.
        """
        raise Exception("Not implemented")        

    #optimized interfaces (others)
    def predicate_objects(self, subject=None):
        """
        A generator of (predicate, object) tuples for the given subject
        """
        raise Exception("Not implemented")

    def subject_objects(self, predicate=None):
        """
        A generator of (subject, object) tuples for the given predicate
        """
        raise Exception("Not implemented")

    def subject_predicates(self, object=None):
        """
        A generator of (subject, predicate) tuples for the given object
        """
        raise Exception("Not implemented")

    def value(self, subject, predicate=u'http://www.w3.org/1999/02/22-rdf-syntax-ns#value', object=None, default=None, any=False):
        """
        Get a value for a subject/predicate, predicate/object, or
        subject/object pair -- exactly one of subject, predicate,
        object must be None. Useful if one knows that there may only
        be one value.
        
        It is one of those situations that occur a lot, hence this
        'macro' like utility

        Parameters:
        -----------
        subject, predicate, object  -- exactly one must be None
        default -- value to be returned if no values found
        any -- if True:
                 return any value in the case there is more than one
               else:
                 raise UniquenessError"""
        raise Exception("Not implemented")



    #Namespace persistence interface implementation
    def bind(self, prefix, namespace):
        """ """
        c=self._db.cursor()
        try:
            c.execute("INSERT INTO %s_namespace_binds VALUES ('%s', '%s')"%(
                self._internedId,
                prefix,
                namespace)
            )
        except:
            pass

    def prefix(self, namespace):
        """ """
        c=self._db.cursor()
        c.execute("select prefix from %s_namespace_binds where uri = '%s'"%(
            self._internedId,
            namespace)
        )
        rt = [rtTuple[0] for rtTuple in c.fetchall()]
        return rt and rt[0] or None

    def namespace(self, prefix):
        """ """
        c=self._db.cursor()
        c.execute("select uri from %s_namespace_binds where prefix = '%s'"%(
            self._internedId,
            prefix)
        )
        rt = [rtTuple[0] for rtTuple in c.fetchall()]
        return rt and rt[0] or None

    def namespaces(self):
        """ """
        c=self._db.cursor()
        c.execute("select prefix, uri from %s_namespace_binds where 1;"%(
            self._internedId
            )
        )        
        for prefix,uri in c.fetchall():
            yield prefix,uri
        

    #Transactional interfaces
    def commit(self):
        """ """
        self._db.commit()
    
    def rollback(self):
        """ """
        self._db.rollback()
        
table_name_prefixes = [
    '%s_asserted_statements',
    '%s_type_statements',
    '%s_quoted_statements',
    '%s_namespace_binds',
    '%s_literal_statements'
]        


CREATE_ASSERTED_STATEMENTS_TABLE = """
CREATE TABLE %s_asserted_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text not NULL,
    context       text not NULL,
    termComb      tinyint unsigned not NULL,    
    INDEX termComb_index (termComb),    
    INDEX spoc_index (subject(100),predicate(100),object(50),context(50)),
    INDEX poc_index (predicate(100),object(50),context(50)),
    INDEX csp_index (context(50),subject(100),predicate(100)),
    INDEX cp_index (context(50),predicate(100))) TYPE=InnoDB"""
    
CREATE_ASSERTED_TYPE_STATEMENTS_TABLE = """
CREATE TABLE %s_type_statements (
    member        text not NULL,
    klass         text not NULL,
    context       text not NULL,
    termComb      tinyint unsigned not NULL,
    INDEX termComb_index (termComb),
    INDEX memberC_index (member(100),klass(100),context(50)),
    INDEX klassC_index (klass(100),context(50)),
    INDEX c_index (context(10))) TYPE=InnoDB"""

CREATE_LITERAL_STATEMENTS_TABLE = """
CREATE TABLE %s_literal_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text,
    context       text not NULL,
    termComb      tinyint unsigned not NULL,    
    objLanguage   varchar(3),
    objDatatype   text,
    INDEX termComb_index (termComb),    
    INDEX spoc_index (subject(100),predicate(100),object(50),context(50)),
    INDEX poc_index (predicate(100),object(50),context(50)),
    INDEX csp_index (context(50),subject(100),predicate(100)),
    INDEX cp_index (context(50),predicate(100))) TYPE=InnoDB"""
    
CREATE_QUOTED_STATEMENTS_TABLE = """
CREATE TABLE %s_quoted_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text,
    context       text not NULL,
    termComb      tinyint unsigned not NULL,
    objLanguage   varchar(3),
    objDatatype   text,
    INDEX termComb_index (termComb),
    INDEX spoc_index (subject(100),predicate(100),object(50),context(50)),
    INDEX poc_index (predicate(100),object(50),context(50)),
    INDEX csp_index (context(50),subject(100),predicate(100)),
    INDEX cp_index (context(50),predicate(100))) TYPE=InnoDB"""
    
CREATE_NS_BINDS_TABLE = """
CREATE TABLE %s_namespace_binds (
    prefix        varchar(20) UNIQUE not NULL,
    uri           text,
    PRIMARY KEY (prefix),
    INDEX uri_index (uri(100))) TYPE=InnoDB"""
