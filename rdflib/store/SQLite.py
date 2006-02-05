from __future__ import generators
from rdflib import BNode
from rdflib.store import Store
from rdflib.Literal import Literal
from pprint import pprint
from pysqlite2 import dbapi2
import sha,sys,re,os
from rdflib.term_utils import *
from rdflib.Graph import QuotedGraph
from rdflib.store.REGEXMatching import REGEXTerm, NATIVE_REGEX, PYTHON_REGEX
from rdflib.store.AbstractSQLStore import *
Any = None

#User-defined REGEXP operator
def regexp(expr, item):
    r = re.compile(expr)
    return r.match(item) is not None
    
class SQLite(AbstractSQLStore,Store):
    """
    SQLite store formula-aware implementation.  It stores it's triples in the following partitions:

    - Asserted non rdf:type statements
    - Asserted rdf:type statements (in a table which models Class membership)
    The motivation for this partition is primarily query speed and scalability as most graphs will always have more rdf:type statements than others
    - All Quoted statements

    In addition it persists namespace mappings in a seperate table
    """
    context_aware = True
    formula_aware = True
    transaction_aware = True
    regex_matching = PYTHON_REGEX
    autocommit_default = False    

    def EscapeQuotes(self,qstr):
        """
        Ported from Ft.Lib.DbUtil
        """
        if qstr is None:
            return u''
        tmp = qstr.replace("\\","\\\\")
        tmp = tmp.replace('"', '""')
        tmp = tmp.replace("'", "''")        
        return tmp
    
    def open(self, home, create=True):
        """ 
        Opens the store specified by the configuration string. If
        create is True a store will be created if it does not already
        exist. If create is False and a store does not already exist
        an exception is raised. An exception is also raised if a store
        exists, but there is insufficient permissions to open the
        store."""
        if create:
            db = dbapi2.connect(os.path.join(home,self.identifier))
            c=db.cursor()
            c.execute(CREATE_ASSERTED_STATEMENTS_TABLE%(self._internedId))
            c.execute(CREATE_ASSERTED_TYPE_STATEMENTS_TABLE%(self._internedId))
            c.execute(CREATE_QUOTED_STATEMENTS_TABLE%(self._internedId))
            c.execute(CREATE_NS_BINDS_TABLE%(self._internedId))
            c.execute(CREATE_LITERAL_STATEMENTS_TABLE%(self._internedId))
            for tblName,indices in [
                (
                    "%s_asserted_statements",
                    [
                        ("%s_A_termComb_index",('termComb',)),
                        ("%s_A_spoc_index",('subject','predicate','object','context')),
                        ("%s_A_poc_index",('predicate','object','context')),
                        ("%s_A_csp_index",('context','subject','predicate')),
                        ("%s_A_cp_index",('context','predicate')),
                    ],
                ),
                (
                    "%s_type_statements",
                    [
                        ("%s_T_termComb_index",('termComb',)),
                        ("%s_memberC_index",('member','klass','context')),
                        ("%s_klassC_index",('klass','context')),
                        ("%s_c_index",('context',)),
                    ],
                ),
                (
                    "%s_literal_statements",
                    [
                        ("%s_L_termComb_index",('termComb',)),
                        ("%s_L_spoc_index",('subject','predicate','object','context')),
                        ("%s_L_poc_index",('predicate','object','context')),
                        ("%s_L_csp_index",('context','subject','predicate')),
                        ("%s_L_cp_index",('context','predicate')),
                    ],
                ),    
                (
                    "%s_quoted_statements",
                    [
                        ("%s_Q_termComb_index",('termComb',)),
                        ("%s_Q_spoc_index",('subject','predicate','object','context')),
                        ("%s_Q_poc_index",('predicate','object','context')),
                        ("%s_Q_csp_index",('context','subject','predicate')),
                        ("%s_Q_cp_index",('context','predicate')),
                    ],
                ),
                (
                    "%s_namespace_binds",
                    [
                        ("%s_uri_index",('uri',)),
                    ],
                )]:
                for indexName,columns in indices:
                    c.execute("CREATE INDEX %s on %s (%s)"%(indexName%self._internedId,tblName%(self._internedId),','.join(columns)))
            c.close()
            db.commit()
            db.close()            

        self._db = dbapi2.connect(os.path.join(home,self.identifier))
        self._db.create_function("regexp", 2, regexp)

        if os.path.exists(os.path.join(home,self.identifier)):
            c = self._db.cursor()
            c.execute("SELECT * FROM sqlite_master WHERE type='table'")
            tbls = [rt[1] for rt in c.fetchall()]
            c.close()
            for tn in [tbl%(self._internedId) for tbl in table_name_prefixes]:                
                if tn not in tbls:
                    sys.stderr.write("table %s Doesn't exist\n" % (tn));
                    #The database exists, but one of the partitions doesn't exist
                    return 0
            #Everything is there (the database and the partitions)
            return 1
        #The database doesn't exist - nothing is there
        #return -1        

    def destroy(self, home):
        """
        FIXME: Add documentation
        """
        db = dbapi2.connect(os.path.join(home,self.identifier))
        c=db.cursor()
        for tblsuffix in table_name_prefixes:
            try:
                c.execute('DROP table %s'%tblsuffix%(self._internedId))
            except:
                print "unable to drop table: %s"%(tblsuffix%(self._internedId))
            
            
        #Note, this only removes the associated tables for the closed world universe given by the identifier
        print "Destroyed Close World Universe %s ( in SQLite database %s)"%(self.identifier,home)
        db.commit()
        c.close()
        db.close()
        os.remove(os.path.join(home,self.identifier))


    #Builds WHERE clauses for the supplied terms and, context
    def buildClause(self,tableName,subject,predicate, obj,context=None,typeTable=False):
        if typeTable:
            rdf_type_memberClause   = self.buildTypeMemberClause(subject,tableName)
            rdf_type_klassClause    = self.buildTypeClassClause(obj,tableName)
            rdf_type_contextClause  = self.buildContextClause(context,tableName)
            typeClauses = [rdf_type_memberClause,rdf_type_klassClause,rdf_type_contextClause]
            clauseString = u' and '.join([clause for clause in typeClauses if clause])
            clauseString = clauseString and u'where %s'%clauseString or u''
        else:
           subjClause        = self.buildSubjClause(subject,tableName)
           predClause        = self.buildPredClause(predicate,tableName)
           objClause         = self.buildObjClause(obj,tableName)
           contextClause     = self.buildContextClause(context,tableName)
           litDTypeClause    = self.buildLitDTypeClause(obj,tableName)
           litLanguageClause = self.buildLitLanguageClause(obj,tableName)
    
           clauses=[subjClause,predClause,objClause,contextClause,litDTypeClause,litLanguageClause]
           clauseString = u' and '.join([clause for clause in clauses if clause])
           clauseString = clauseString and u'where %s'%clauseString or u''
        return clauseString
    
    #Where Clause  utility Functions
    #The predicate and object clause builders are modified in order to optimize
    #subjects and objects utility functions which can take lists as their last argument (object,predicate - respectively)
    def buildSubjClause(self,subject,tableName):
        if isinstance(subject,REGEXTerm):
            return u" REGEXP ('%s',%s)"%(self.EscapeQuotes(subject),tableName and u'%s.subject'%tableName or u'subject')
        elif isinstance(subject,list):
            clauseStrings=[]
            for s in subject:
                if isinstance(s,REGEXTerm):
                    clauseStrings.append(u"REGEXP ('%s',%s)"%(self.EscapeQuotes(s),tableName and u'%s.subject'%tableName or u'subject'))
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
    def buildPredClause(self,predicate,tableName):
        if isinstance(predicate,REGEXTerm):
            return u"REGEXP ('%s',%s)"%(self.EscapeQuotes(predicate),tableName and u'%s.predicate'%tableName or u'predicate')
        elif isinstance(predicate,list):
            clauseStrings=[]
            for p in predicate:
                if isinstance(p,REGEXTerm):
                    clauseStrings.append(u"REGEXP ('%s',%s)"%(self.EscapeQuotes(p),tableName and u'%s.predicate'%tableName or u'predicate'))
                else:
                    clauseStrings.append(predicate and u"%s='%s'"%(tableName and u'%s.predicate'%tableName or u'predicate',p) or None)
            return u'(%s)'%u' or '.join([clauseString for clauseString in clauseStrings])
        else:
            return predicate and u"%s='%s'"%(tableName and u'%s.predicate'%tableName or u'predicate',predicate) or None
    
    #Capable of taking a list of objects as well (in which case sub clauses are joined with 'OR')    
    def buildObjClause(self,obj,tableName):
        if isinstance(obj,REGEXTerm):
            return u"REGEXP ('%s',%s)"%(self.EscapeQuotes(obj),tableName and u'%s.object'%tableName or u'object')
        elif isinstance(obj,list):
            clauseStrings=[]
            for o in obj:
                if isinstance(o,REGEXTerm):
                    clauseStrings.append(u"REGEXP ('%s',%s)"%(self.EscapeQuotes(o),tableName and u'%s.object'%tableName or u'object'))
                elif isinstance(o,(QuotedGraph,Graph)):
                    clauseStrings.append(u"%s='%s'"%(tableName and u'%s.object'%tableName or u'object',o.identifier))
                else:
                    clauseStrings.append(o and u"%s='%s'"%(tableName and u'%s.object'%tableName or u'object',isinstance(o,Literal) and self.EscapeQuotes(o) or o) or None)
            return u'(%s)'%u' or '.join([clauseString for clauseString in clauseStrings])
        elif isinstance(obj,(QuotedGraph,Graph)):
            return u"%s='%s'"%(tableName and u'%s.object'%tableName or u'object',obj.identifier)
        else:
            return obj and u"%s='%s'"%(tableName and u'%s.object'%tableName or u'object',self.EscapeQuotes(obj)) or None
    
    def buildContextClause(self,context,tableName):
        context = context is not None and context.identifier or context
        if isinstance(context,REGEXTerm):
            return u"REGEXP ('%s',%s)"%(self.EscapeQuotes(context),tableName and u'%s.context'%tableName)
        else:
            return context and u"%s='%s'"%(tableName and u'%s.context'%tableName,context) or None
        
    def buildTypeMemberClause(self,subject,tableName):
        if isinstance(subject,REGEXTerm):
            return u"REGEXP ('%s',%s.member)"%(self.EscapeQuotes(subject),tableName)
        elif isinstance(subject,list):
            subjs = [isinstance(s,(QuotedGraph,Graph)) and s.identifier or s for s in subject]        
            return u' or '.join([s and u"%s.member = '%s'"%(tableName,s) for s in subjs])    
        else:
            return subject and u"%s.member = '%s'"%(tableName,subject)
        
    def buildTypeClassClause(self,obj,tableName):
        if isinstance(obj,REGEXTerm):
            return u"REGEXP ('%s',%s.klass)"%(self.EscapeQuotes(obj),tableName)
        elif isinstance(obj,list):
            obj = [isinstance(o,(QuotedGraph,Graph)) and o.identifier or o for o in obj]        
            return u' or '.join([o and not isinstance(o,Literal) and u"%s.klass = '%s'"%(tableName,o) for o in obj])
        else:
            return obj and not isinstance(obj,Literal) and u"%s.klass = '%s'"%(tableName,obj)

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
                  self.buildClause('typeTable',subject,RDF.type, obj,context,True),
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
                  self.buildClause('literal',subject,predicate,obj,context),
                  ASSERTED_LITERAL_PARTITION
                ))                    
            if not isinstance(obj,Literal) and not (isinstance(obj,REGEXTerm) and self.STRONGLY_TYPED_TERMS) or not obj:
                selects.append((
                  asserted_table,
                  'asserted',
                  self.buildClause('asserted',subject,predicate,obj,context),
                  ASSERTED_NON_TYPE_PARTITION
                ))
                
            selects.append(
                (
                  asserted_type_table,
                  'typeTable',
                  self.buildClause('typeTable',subject,RDF.type,obj,context,True),
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
                  self.buildClause('literal',subject,predicate,obj,context),
                  ASSERTED_LITERAL_PARTITION
                ))
            if not isinstance(obj,Literal) and not (isinstance(obj,REGEXTerm) and self.STRONGLY_TYPED_TERMS) or not obj:                
                selects.append((
                  asserted_table,
                  'asserted',
                  self.buildClause('asserted',subject,predicate,obj,context),
                  ASSERTED_NON_TYPE_PARTITION
                ))                    

        if context is not None:
            selects.append(
                (
                  quoted_table,
                  'quoted',
                  self.buildClause('quoted',subject,predicate, obj,context),
                  QUOTED_PARTITION
                )
            )

        q=unionSELECT(selects,selectType=TRIPLE_SELECT_NO_ORDER)
        c.execute(self._normalizeSQLCmd(q))
        #NOTE: SQLite does not support ORDER BY terms that aren't integers, so the entire result set must be iterated
        #in order to be able to return a generator of contexts
        tripleCoverage = {}
        result = c.fetchall()
        c.close()
        for rt in result:                
            s,p,o,(graphKlass,idKlass,graphId) = extractTriple(rt,self,context)
            contexts = tripleCoverage.get((s,p,o),[])
            contexts.append(graphKlass(self,idKlass(graphId)))            
            tripleCoverage[(s,p,o)] = contexts
                  
        for (s,p,o),contexts in tripleCoverage.items(): 
            yield (s,p,o),(c for c in contexts)        
        
CREATE_ASSERTED_STATEMENTS_TABLE = """
CREATE TABLE %s_asserted_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text not NULL,
    context       text not NULL,
    termComb      tinyint unsigned not NULL)"""
    
CREATE_ASSERTED_TYPE_STATEMENTS_TABLE = """
CREATE TABLE %s_type_statements (
    member        text not NULL,
    klass         text not NULL,
    context       text not NULL,
    termComb      tinyint unsigned not NULL)"""

CREATE_LITERAL_STATEMENTS_TABLE = """
CREATE TABLE %s_literal_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text,
    context       text not NULL,
    termComb      tinyint unsigned not NULL,    
    objLanguage   varchar(3),
    objDatatype   text)"""
    
CREATE_QUOTED_STATEMENTS_TABLE = """
CREATE TABLE %s_quoted_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text,
    context       text not NULL,
    termComb      tinyint unsigned not NULL,
    objLanguage   varchar(3),
    objDatatype   text)"""
    
CREATE_NS_BINDS_TABLE = """
CREATE TABLE %s_namespace_binds (
    prefix        varchar(20) UNIQUE not NULL,
    uri           text,
    PRIMARY KEY (prefix))"""
