from __future__ import generators
from rdflib import BNode
from rdflib.store import Store
from rdflib.Literal import Literal
from pprint import pprint
import MySQLdb,sys
from rdflib.term_utils import *
from rdflib.Graph import QuotedGraph
from rdflib.store.REGEXMatching import REGEXTerm, NATIVE_REGEX, PYTHON_REGEX
from rdflib.store.AbstractSQLStore import *
Any = None
    
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

class MySQL(AbstractSQLStore,Store):
    """
    MySQL store formula-aware implementation.  It stores it's triples in the following partitions:

    - Asserted non rdf:type statements
    - - Asserted literal statements
    - Asserted rdf:type statements (in a table which models Class membership)
    The motivation for this partition is primarily query speed and scalability as most graphs will always have more rdf:type statements than others
    - All Quoted statements

    In addition it persists namespace mappings in a seperate table
    """
    context_aware = True
    formula_aware = True
    transaction_aware = True
    regex_matching = NATIVE_REGEX
    autocommit_default = False            
            
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

    #Where Clause  utility Functions
    #The predicate and object clause builders are modified in order to optimize
    #subjects and objects utility functions which can take lists as their last argument (object,predicate - respectively)
    def buildSubjClause(self,subject,tableName):
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
    def buildPredClause(self,predicate,tableName):
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
    def buildObjClause(self,obj,tableName):
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
    
    def buildContextClause(self,context,tableName):
        context = context is not None and context.identifier or context
        if isinstance(context,REGEXTerm):
            return u"%s REGEXP '%s'"%(tableName and u'%s.context'%tableName,EscapeQuotes(context))
        else:
            return context and u"%s='%s'"%(tableName and u'%s.context'%tableName,context) or None
        
    def buildTypeMemberClause(self,subject,tableName):
        if isinstance(subject,REGEXTerm):
            return u"%s.member REGEXP '%s'"%(tableName,EscapeQuotes(subject))
        elif isinstance(subject,list):
            subjs = [isinstance(s,(QuotedGraph,Graph)) and s.identifier or s for s in subject]        
            return u' or '.join([s and u"%s.member = '%s'"%(tableName,s) for s in subjs])    
        else:
            return subject and u"%s.member = '%s'"%(tableName,subject)
        
    def buildTypeClassClause(self,obj,tableName):
        if isinstance(obj,REGEXTerm):
            return u"%s.klass REGEXP '%s'"%(tableName,EscapeQuotes(obj))
        elif isinstance(obj,list):
            obj = [isinstance(o,(QuotedGraph,Graph)) and o.identifier or o for o in obj]        
            return u' or '.join([o and not isinstance(o,Literal) and u"%s.klass = '%s'"%(tableName,o) for o in obj])
        else:
            return obj and not isinstance(obj,Literal) and u"%s.klass = '%s'"%(tableName,obj)



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
