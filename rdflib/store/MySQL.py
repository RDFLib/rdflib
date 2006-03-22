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

class MySQL(AbstractSQLStore):
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

    def executeSQL(self,cursor,qStr,params=None):
        """
        Overridded in order to pass params seperate from query for MySQLdb
        to optimize
        """
        #print qStr
        if params:
            #print qStr,params
            #print [(type(p),p) for p in params]
            cursor.execute(qStr,tuple(params))
        else:            
            cursor.execute(qStr)
            
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
                                      host=configDict['host'],
                                      #use_unicode=True,
                                      #read_default_file='/etc/my-client.cnf'
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
                                 host=configDict['host'],
                                 #use_unicode=True,
                                 #read_default_file='/etc/my-client.cnf'
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
                                   host=configDict['host'],
                                   #use_unicode=True,
                                   read_default_file='/etc/my.cnf'
                                  )
        c=self._db.cursor()
        c.execute("""SHOW DATABASES""")        
        #FIXME This is a character set hack.  See: http://sourceforge.net/forum/forum.php?thread_id=1448424&forum_id=70461
        self._db.charset = 'utf8'
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
            except Exception, e:
                print "unable to drop table: %s"%(tblsuffix%(self._internedId))
                print e
            
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
            return "%s REGEXP "%(tableName and '%s.subject'%tableName or 'subject') + " %s",[subject]
        elif isinstance(subject,list):
            clauseStrings=[]
            paramStrings = []
            for s in subject:
                if isinstance(s,REGEXTerm):
                    clauseStrings.append("%s REGEXP"%(tableName and '%s.subject'%tableName or 'subject') + " %s")
                    paramStrings.append(self.normalizeTerm(s))
                elif isinstance(s,(QuotedGraph,Graph)):
                    clauseStrings.append("%s="%(tableName and '%s.subject'%tableName or 'subject')+"%s")
                    paramStrings.append(self.normalizeTerm(s.identifier))
                else:
                    clauseStrings.append("%s="%(tableName and '%s.subject'%tableName or 'subject')+"%s")
                    paramStrings.append(self.normalizeTerm(s))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        elif isinstance(subject,(QuotedGraph,Graph)):
            return "%s="%(tableName and '%s.subject'%tableName or 'subject')+"%s",[self.normalizeTerm(subject.identifier)]
        else:
            return subject is not None and "%s="%(tableName and '%s.subject'%tableName or 'subject')+"%s",[subject] or None
    
    #Capable off taking a list of predicates as well (in which case sub clauses are joined with 'OR')
    def buildPredClause(self,predicate,tableName):
        if isinstance(predicate,REGEXTerm):
            return "%s REGEXP "%(tableName and '%s.predicate'%tableName or 'predicate')+"%s",[predicate]
        elif isinstance(predicate,list):
            clauseStrings=[]
            paramStrings = []
            for p in predicate:
                if isinstance(p,REGEXTerm):
                    clauseStrings.append("%s REGEXP "%(tableName and '%s.predicate'%tableName or 'predicate')+"%s")                    
                else:
                    clauseStrings.append("%s="%(tableName and '%s.predicate'%tableName or 'predicate')+"%s")
                paramStrings.append(self.normalizeTerm(p))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        else:
            return predicate is not None and "%s="%(tableName and '%s.predicate'%tableName or 'predicate')+"%s",[predicate] or None
    
    #Capable of taking a list of objects as well (in which case sub clauses are joined with 'OR')    
    def buildObjClause(self,obj,tableName):
        if isinstance(obj,REGEXTerm):
            return "%s REGEXP "%(tableName and '%s.object'%tableName or 'object')+"%s",[obj]
        elif isinstance(obj,list):
            clauseStrings=[]
            paramStrings = []
            for o in obj:
                if isinstance(o,REGEXTerm):
                    clauseStrings.append("%s REGEXP"%(tableName and '%s.object'%tableName or 'object')+" %s")
                    paramStrings.append(self.normalizeTerm(o))
                elif isinstance(o,(QuotedGraph,Graph)):
                    clauseStrings.append("%s="%(tableName and '%s.object'%tableName or 'object')+"%s")
                    paramStrings.append(self.normalizeTerm(o.identifier))
                else:
                    clauseStrings.append("%s="%(tableName and '%s.object'%tableName or 'object')+"%s")
                    paramStrings.append(self.normalizeTerm(o))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        elif isinstance(obj,(QuotedGraph,Graph)):
            return "%s="%(tableName and '%s.object'%tableName or 'object')+"%s",[self.normalizeTerm(obj.identifier)]
        else:
            return obj is not None and "%s="%(tableName and '%s.object'%tableName or 'object')+"%s",[obj] or None
    
    def buildContextClause(self,context,tableName):
        context = context is not None and self.normalizeTerm(context.identifier) or context
        if isinstance(context,REGEXTerm):
            return "%s REGEXP"%(tableName and '%s.context'%tableName)+" %s",[context]
        else:
            return context is not None and "%s="%(tableName and '%s.context'%tableName)+"%s",[context] or None
        
    def buildTypeMemberClause(self,subject,tableName):
        if isinstance(subject,REGEXTerm):
            return "%s.member REGEXP "%(tableName)+" %s",[subject]
        elif isinstance(subject,list):
            clauseStrings=[]
            paramStrings = []
            for s in subject:                        
                clauseStrings.append("%s.member="%tableName+"%s")
                if isinstance(s,(QuotedGraph,Graph)):                                        
                    paramStrings.append(self.normalizeTerm(s.identifier))
                else:
                    paramStrings.append(self.normalizeTerm(s))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        else:
            return subject and u"%s.member = "%(tableName)+"%s",[subject]
        
    def buildTypeClassClause(self,obj,tableName):
        if isinstance(obj,REGEXTerm):
            return "%s.klass REGEXP "%(tableName)+"%s",[obj]
        elif isinstance(obj,list):
            clauseStrings=[]
            paramStrings = []
            for o in obj:
                clauseStrings.append("%s.klass="%tableName+"%s")
                if isinstance(o,(QuotedGraph,Graph)):                    
                    paramStrings.append(self.normalizeTerm(o.identifier))
                else:
                    paramStrings.append(self.normalizeTerm(o))
            return '('+ ' or '.join(clauseStrings) + ')', paramStrings
        else:
            return obj is not None and "%s.klass = "%tableName+"%s",[obj] or None

CREATE_ASSERTED_STATEMENTS_TABLE = """
CREATE TABLE %s_asserted_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text not NULL ,
    context       text not NULL ,
    termComb      tinyint unsigned not NULL,    
    INDEX s_index (subject(100)),
    INDEX p_index (predicate(100)),
    INDEX o_index (object(100)),
    INDEX c_index (context(50))) TYPE=InnoDB CHARACTER SET utf8"""
    
CREATE_ASSERTED_TYPE_STATEMENTS_TABLE = """
CREATE TABLE %s_type_statements (
    member        text not NULL,
    klass         text not NULL,
    context       text not NULL,
    termComb      tinyint unsigned not NULL,    
    INDEX member_index (member(100)),
    INDEX klass_index (klass(100)),
    INDEX c_index (context(50))) TYPE=InnoDB CHARACTER SET utf8"""

CREATE_LITERAL_STATEMENTS_TABLE = """
CREATE TABLE %s_literal_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text,
    context       text not NULL,
    termComb      tinyint unsigned not NULL,    
    objLanguage   varchar(3),
    objDatatype   text,
    INDEX s_index (subject(100)),
    INDEX p_index (predicate(100)),
    INDEX c_index (context(50))) TYPE=InnoDB CHARACTER SET utf8"""
    
CREATE_QUOTED_STATEMENTS_TABLE = """
CREATE TABLE %s_quoted_statements (
    subject       text not NULL,
    predicate     text not NULL,
    object        text,
    context       text not NULL,
    termComb      tinyint unsigned not NULL,
    objLanguage   varchar(3),
    objDatatype   text,
    INDEX s_index (subject(100)),
    INDEX p_index (predicate(100)),
    INDEX o_index (object(100)),
    INDEX c_index (context(50))) TYPE=InnoDB CHARACTER SET utf8"""
    
CREATE_NS_BINDS_TABLE = """
CREATE TABLE %s_namespace_binds (
    prefix        varchar(20) UNIQUE not NULL,
    uri           text,
    PRIMARY KEY (prefix),
    INDEX uri_index (uri(100))) TYPE=InnoDB CHARACTER SET utf8"""
