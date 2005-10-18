from __future__ import generators
from rdflib import BNode
from rdflib.backends import Backend
from rdflib import RDF
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from pprint import pprint
from rdflib.Variable import Variable
import MySQLdb,sha,sys,re
from term_utils import *
from rdflib.Graph import QuotedGraph
Any = None


#REGEXTerm can be used in any term slot and is interpreted as
#a request to perform a REGEX match (not a string comparison) using the value
#(pre-compiled) for checkin rdf:type matches
class REGEXTerm(unicode):
    def __init__(self,expr):
        self.compiledExpr = re.compile(expr)
    
#Terms: u - uri refs  v - variables  b - bnodes l - literal f - formula

#FIXME:  This may prove to be a performance bottleneck and should perhaps be implemented in C
def EscapeQuotes(qstr):
    """
    Ported from Ft.Lib.DbUtil
    """
    if qstr is None:
        return ''
    tmp = qstr.replace("\\","\\\\")
    tmp = tmp.replace("'", "\\'")
    return tmp


#Builds WHERE clauses for the supplied terms, context, and whether or not this is for a typeTable
def buildClause(tableName,subject,obj,context=None,typeTable=True,predicate=None):
    if typeTable:
        rdf_type_memberClause   = buildTypeMemberClause(subject,tableName)
        rdf_type_klassClause    = buildTypeClassClause(obj,tableName)
        rdf_type_contextClause  = buildContextClause(context,tableName)
        typeClauses = [rdf_type_memberClause,rdf_type_klassClause,rdf_type_contextClause]
        clauseString = ' and '.join([clause for clause in typeClauses if clause])
        clauseString = clauseString and 'where %s'%clauseString or ''
    else:
       subjClause        = buildSubjClause(subject,tableName)
       predClause        = buildPredClause(predicate,tableName)
       objClause         = buildObjClause(obj,tableName)
       contextClause           = buildContextClause(context,tableName)
       litDTypeClause    = buildLitDTypeClause(obj,tableName)
       litLanguageClause = buildLitLanguageClause(obj,tableName)

       clauses=[subjClause,predClause,objClause,contextClause,litDTypeClause,litLanguageClause]
       clauseString = ' and '.join([clause for clause in clauses if clause])
       clauseString = clauseString and 'where %s'%clauseString or ''
    return clauseString

#Builds an insert command for a type table
def buildTypeSQLCommand(member,klass,context,storeId):
    #columns: member,klass,context
    rt= "INSERT INTO %s_type_statements VALUES ('%s', '%s', '%s',%s)"%(
        storeId,
        normalizeTerm(member),
        normalizeTerm(klass),
        context,
        type2TermCombination(member,klass))
    return rt

#Builds an insert command for regular triple table
def buildTripleSQLCommand(subject,predicate,obj,context,storeId,quoted):
    stmt_table = quoted and "%s_quoted_statements"%storeId or "%s_asserted_statements"%storeId
    triplePattern = statement2TermCombination(subject,predicate,obj)
    command="INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', %s,%s,%s)"%(
            stmt_table,
            normalizeTerm(subject),
            predicate,
            normalizeTerm(obj),
            context,
            str(triplePattern),
            type(obj)== Literal and  "'%s'"%obj.language or 'NULL',
            type(obj)== Literal and "'%s'"%obj.datatype or 'NULL')
    return command

#Takes a dictionary which represents an entry in a result set and
#converts it to a tuple of terms using the termComb integer
#to interpret how to instanciate each term
def extractTriple(rtDict,backend,hardCodedContext=None):
    #If context is None, should extract quads??!
    context = rtDict['context'] and rtDict['context'] or hardCodedContext
    termCombString=REVERSE_TERM_COMBINATIONS[rtDict['termComb']]
    if 'member' in rtDict and rtDict['member']:
        s=createTerm(rtDict['member'],termCombString[SUBJECT],backend)
        p=RDF.type
        o=createTerm(rtDict['klass'],termCombString[OBJECT],backend)
    elif 'subject' in rtDict and rtDict['subject']:
        #regular statement
        s=createTerm(rtDict['subject'],termCombString[SUBJECT],backend)
        p=createTerm(rtDict['predicate'],termCombString[PREDICATE],backend)
        if termCombString[OBJECT] == 'L':
            o=Literal(rtDict['object'],rtDict['objLanguage'],rtDict['objDatatype'])
        else:
            o=createTerm(rtDict['object'],termCombString[OBJECT],backend)
            
    if backend.yieldConjunctiveQuads:
        return s,p,o,context
    else:
        return s,p,o

#Takes a term and 'normalizes' it.
#Literals are escaped, Quoted graphs are replaced with just their identifiers
def normalizeTerm(term):
    if type(term)==QuotedGraph:
        return term.identifier
    elif type(term)==Literal:
        return EscapeQuotes(term)
    else:
        return term

#Takes a term value, term type, and backend intance
#and Creates a term object
def createTerm(termString,termType,backend):
    if termType=='B':
        return BNode(termString)
    elif termType=='U':
        return URIRef(termString)
    elif termType == 'V':
        return Variable(termString)
    elif termType=='F':
        return QuotedGraph(backend,termString)
    else:
        print termString,termType
        raise Exception('Unknown term string returned from store: %s'%(termString))

#Where Clause  utility Functions
#The predicate and object clause builders are modified in order to optimize
#subjects and objects utility functions which can take lists as their last argument (object,predicate - respectively)
def buildSubjClause(subject,tableName):
    if isinstance(subject,REGEXTerm):
        return "%s REGEXP '%s'"%(tableName and '%s.subject'%tableName or 'subject',EscapeQuotes(subject))
    elif isinstance(subject,list):
        clauseStrings=[]
        for s in subject:
            if isinstance(s,REGEXTerm):
                clauseStrings.append("%s REGEXP '%s'"%(tableName and '%s.subject'%tableName or 'subject',EscapeQuotes(s)))
            else:
                clauseStrings.append(s and "%s='%s'"%(tableName and '%s.subject'%tableName or 'subject',s) or None)
        return '(%s)'%' or '.join([clauseString for clauseString in clauseStrings])        
    else:
        return subject and "%s='%s'"%(tableName and '%s.subject'%tableName or 'subject',subject) or None

#Capable off taking a list of predicates as well (in which case sub clauses are joined with 'OR')
def buildPredClause(predicate,tableName):
    if isinstance(predicate,REGEXTerm):
        return "%s REGEXP '%s'"%(tableName and '%s.predicate'%tableName or 'predicate',EscapeQuotes(predicate))
    elif isinstance(predicate,list):
        clauseStrings=[]
        for p in predicate:
            if isinstance(p,REGEXTerm):
                clauseStrings.append("%s REGEXP '%s'"%(tableName and '%s.predicate'%tableName or 'predicate',EscapeQuotes(p)))
            else:
                clauseStrings.append(predicate and "%s='%s'"%(tableName and '%s.predicate'%tableName or 'predicate',p) or None)
        return '(%s)'%' or '.join([clauseString for clauseString in clauseStrings])
    else:
        return predicate and "%s='%s'"%(tableName and '%s.predicate'%tableName or 'predicate',predicate) or None

#Capable off taking a list of objects as well (in which case sub clauses are joined with 'OR')    
def buildObjClause(obj,tableName):
    if isinstance(obj,REGEXTerm):
        return "%s REGEXP '%s'"%(tableName and '%s.object'%tableName or 'object',EscapeQuotes(obj))
    elif isinstance(obj,list):
        clauseStrings=[]
        for o in obj:
            if isinstance(o,REGEXTerm):
                clauseStrings.append("%s REGEXP '%s'"%(tableName and '%s.object'%tableName or 'object',EscapeQuotes(o)))
            elif isinstance(o,QuotedGraph):
                clauseStrings.append("%s='%s'"%(tableName and '%s.object'%tableName or 'object',o.identifier))
            else:
                clauseStrings.append(o and "%s='%s'"%(tableName and '%s.object'%tableName or 'object',isinstance(o,Literal) and EscapeQuotes(o) or o) or None)
        return '(%s)'%' or '.join([clauseString for clauseString in clauseStrings])
    else:
        return obj and "%s='%s'"%(tableName and '%s.object'%tableName or 'object',isinstance(obj,Literal) and EscapeQuotes(obj) or obj) or None     

def buildContextClause(context,tableName):
    if isinstance(context,REGEXTerm):
        return "%s REGEXP '%s'"%(tableName and '%s.context'%tableName,EscapeQuotes(context))
    else:
        return context and "%s='%s'"%(tableName and '%s.context'%tableName,context) or None
    
def buildLitDTypeClause(obj,tableName):
    return (isinstance(obj,Literal) and obj.datatype and "%s.objDatatype='%s'"%(tableName,obj.datatype)) or None 

def buildLitLanguageClause(obj,tableName):
    return (isinstance(obj,Literal) and obj.datatype and "%s.objLanguage='%s'"%(tableName,obj.language)) or None

def buildTypeMemberClause(subject,tableName):
    if isinstance(subject,REGEXTerm):
        return "%s.member REGEXP '%s'"%(tableName,EscapeQuotes(subject))
    elif isinstance(subject,list):
        subjs = [isinstance(s,QuotedGraph) and s.identifier or s for s in subject]        
        return ' or '.join([s and "%s.member = '%s'"%(tableName,s) for s in subjs])    
    else:
        return subject and "%s.member = '%s'"%(tableName,subject)
    
def buildTypeClassClause(obj,tableName):
    if isinstance(obj,REGEXTerm):
        return "%s.klass REGEXP '%s'"%(tableName,EscapeQuotes(obj))
    elif isinstance(obj,list):
        obj = [isinstance(o,QuotedGraph) and o.identifier or o for o in obj]        
        return ' or '.join([o and not isinstance(o,Literal) and "%s.klass = '%s'"%(tableName,o) for o in obj])
    else:
        return obj and not isinstance(obj,Literal) and "%s.klass = '%s'"%(tableName,obj)
    
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
    for requiredKey in ['user','password','db','host']:
        assert requiredKey in kvDict
    if 'port' not in kvDict:
        kvDict['port']=3306
    return kvDict

class MySQL(Backend):
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
    def __init__(self, identifier=None, configuration=None):
        """ 
        identifier: URIRef of the Store. Defaults to CWD
        configuration: string containing infomation open can use to
        connect to datastore.
        """
        self.identifier = identifier and identifier or 'hardcoded'
        self._internedId = sha.new(self.identifier).hexdigest()

        #determines whether or not to yield conjunctive quads
        self.yieldConjunctiveQuads = False
        if configuration:
            self.open(configuration)
            
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
                for tblsuffix in table_name_prefixes:
                    print "creating table: %s"%(tblsuffix%(self._internedId))
                c.execute(CREATE_ASSERTED_STATEMENTS_TABLE%(self._internedId))
                c.execute(CREATE_ASSERTED_TYPE_STATEMENTS_TABLE%(self._internedId))
                c.execute(CREATE_QUOTED_STATEMENTS_TABLE%(self._internedId))
                c.execute(CREATE_NS_BINDS_TABLE%(self._internedId))                    
                db.commit()
                c.close()
                db.close()            
            else:
                print "database %s already exists"%configDict['db']
                #Already exists, do nothing
                c.close()
                test_db.close()

        self._db = MySQLdb.connect(user = configDict['user'],
                                   passwd = configDict['password'],
                                   db=configDict['db'],
                                   port=configDict['port'],
                                   host=configDict['host']
                                  )
        self._db.cursorclass = MySQLdb.cursors.DictCursor
        c=self._db.cursor()
        c.execute("""SET AUTOCOMMIT=0""")   
        c.close()
            
    def close(self, commit_pending_transaction=False):
        """ 
        FIXME:  Add documentation!!
        """
        if commit_pending_transaction:
            self._db.commit()
        self._db.close()
        self._db = None

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
        c.execute('DROP database %s'%configDict['db'])
        print "Destroyed database (%s)"%configDict['db']
        msql_db.commit()
        msql_db.close()
        
    #Triple Methods    
        
    def add(self, (subject, predicate, obj), context=None, quoted=False):        
        """ Add a triple to the store of triples. """
        assert context
        c=self._db.cursor()
        if quoted or predicate != RDF.type:
            #quoted statement or non rdf:type predicate
            c.execute(
                buildTripleSQLCommand(
                    subject,
                    predicate,
                    obj,
                    context,
                    self._internedId,
                    quoted)
            )
        elif predicate == RDF.type:
            #asserted rdf:type statement
            c.execute(
                buildTypeSQLCommand(
                    subject,
                    obj,
                    context,
                    self._internedId)
            )
        c.close()

    def remove(self, (subject, predicate, obj), context):
        """ Remove a triple from the store """
        c=self._db.cursor()
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        if not predicate or predicate != RDF.type:            
            #Need to remove predicates other than rdf:type

            for table in [quoted_table,asserted_table]:
                clauseString = buildClause(table,subject,obj,context,False,predicate)
                c.execute(clauseString and "DELETE FROM %s %s"%(table,clauseString) or 'DELETE FROM %s;'%table)

        if predicate == RDF.type or not predicate:
            #Need to check rdf:type and quoted partitions
            clauseString = buildClause(asserted_type_table,subject,obj,context)
            c.execute(clauseString and "DELETE FROM %s %s"%(asserted_type_table,clauseString) or 'DELETE FROM %s;'%asserted_type_table)
            clauseString = buildClause(quoted_table,subject,obj,context,False,predicate)
            c.execute(clauseString and "DELETE FROM %s %s"%(quoted_table,clauseString) or 'DELETE FROM %s;'%quoted_table)
            
        c.close()

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
        contextClause  = context and "context = '%s'"%context or None        
        c=self._db.cursor()
        if context:
            #Normal context constraint against asserted/quoted tables
            if predicate == RDF.type:
                #select from asserted rdf:type partition and quoted table only
                quotedClauseString = buildClause('quoted',subject,obj,context,False,predicate)
                typeClauseString = buildClause('typeTable',subject,obj,context)
                
                q="""(select                     
                        quoted.*
                     from
                        %s as quoted
                     %s)

                     union all

                     (select
                        typeTable.member as subject,
                        '%s' as predicate,
                        typeTable.klass as object,
                        NULL as objLanguage,
                        NULL as objDatatype,
                        typeTable.context as context,
                        typeTable.termComb as termComb
                     from                         
                        %s as typeTable
                     %s)"""%(
                    quoted_table,
                    quotedClauseString,
                    RDF.type,
                    asserted_type_table,
                    typeClauseString)
                
            elif isinstance(predicate,REGEXTerm) and predicate.compiledExpr.match(RDF.type):
                #select from asserted non rdf:type partition, asserted rdf:type (matches rdf:type) and quoted table
                clauseStrings=[]
                quotedClauseString = buildClause('quoted',subject,obj,context,False,predicate)
                typeClauseString = buildClause('typeTable',subject,obj,context)
                
                for tableAlias in ['quoted','asserted']:
                    clauseStrings.append(buildClause(tableAlias,subject,obj,context,False,predicate))
                    
                q="""select                     
                        quoted.*
                      from                         
                        %s as quoted
                      %s

                      union all

                      select
                        asserted.*
                      from
                        %s as asserted
                      %s

                      union all

                      select
                        typeTable.member as subject,
                        '%s' as predicate,
                        typeTable.klass as object,
                        typeTable.termComb as termComb,
                        NULL as objLanguage,
                        NULL as objDatatype,
                        typeTable.context as context
                     from
                        %s as typeTable
                     %s"""%(quoted_table,clauseStrings[0],asserted_table,clauseStrings[1],RDF.type,asserted_type_table,typeClauseString)                
            elif predicate:
                #select from asserted non rdf:type partition and quoted table only
                clauseStrings=[]
                quotedClauseString = buildClause('quoted',subject,obj,context,False,predicate)
                typeClauseString = buildClause('typeTable',subject,obj,context)
                
                for tableAlias in ['quoted','asserted']:
                    clauseStrings.append(buildClause(tableAlias,subject,obj,context,False,predicate))
                    
                q="""select                     
                        quoted.*
                      from                         
                        %s as quoted
                      %s

                      union all

                      select
                        asserted.*
                      from
                        %s as asserted
                      %s"""%(quoted_table,clauseStrings[0],asserted_table,clauseStrings[1])
 
            else:
                #select from asserted rdf:type, asserted non rdf:type and quoted table
                clauseStringList=[]
                for tableAlias in ['quoted','asserted']:                    
                    clauseStringList.append(buildClause(tableAlias,subject,obj,context,False,predicate))                    

                typeClauseString = buildClause('typeTable',subject,obj,context)
                
                q="""
                     (select
                        quoted.*
                     from
                        %s as quoted
                     %s)

                     union all

                     (select
                        asserted.*
                      from     
                        %s as asserted
                      %s)

                     union all

                     (select
                        typeTable.member as subject,
                        '%s' as predicate,
                        typeTable.klass as object,
                        typeTable.termComb,
                        NULL as objLanguage,
                        NULL as objDatatype,
                        typeTable.context as context
                     from
                        %s as typeTable
                     %s)"""%(quoted_table,clauseStringList[0],asserted_table,clauseStringList[1],RDF.type,asserted_type_table,typeClauseString)
        else:
            if predicate == RDF.type:
                #select from asserted rdf:type partition only
                clauseString = buildClause('type',subject,obj)
                q="""select                    
                        type.*
                      from     
                        %s as type
                      %s"""%(asserted_type_table,clauseString)
                
            elif isinstance(predicate,REGEXTerm) and predicate.compiledExpr.match(RDF.type):
                #Predicate matched rdf:type (might also match other predicates)
                assertedClauseString = buildClause('asserted',subject,obj,context,False,predicate)
                typeClauseString = buildClause('typeTable',subject,obj,context)
                    
                q="""(select                     
                        asserted.*
                      from                         
                        %s as asserted
                     %s)

                     union all

                     (select
                       typeTable.member as subject,
                       '%s' as predicate,
                       typeTable.klass as object,
                       NULL as objLanguage,
                       NULL as objDatatype,
                       typeTable.context as context,
                       typeTable.termComb as termComb
                      from                         
                        %s as typeTable
                      %s)"""%(asserted_table,assertedClauseString,RDF.type,asserted_type_table,typeClauseString)

            elif predicate:
                #select from asserted non rdf:type partition only
                
                clauseString = buildClause('asserted',subject,obj,context,False,predicate)
                q="""select                                             
                        asserted.*
                      from                         
                        %s as asserted
                      %s"""%(asserted_table,clauseString)
            else:
                #select from asserted rdf:type, asserted non rdf:type
                clauseString = buildClause('asserted',subject,obj,context,False,predicate)
                typeClauseString = buildClause('typeTable',subject,obj)
                q="""select                     
                        asserted.*
                     from %s as asserted
                     %s

                     union all

                     select
                        typeTable.member as subject,
                        '%s' as predicate,
                        typeTable.klass as object,
                        typeTable.termComb as termComb,
                        NULL as objLanguage,
                        NULL as objDatatype,
                        typeTable.context as context
                      from                         
                        %s as typeTable
                      %s"""%(asserted_table,clauseString,RDF.type,asserted_type_table,typeClauseString)

        c.execute(q)
        c.close()
        for rtDict in c.fetchall():
            yield extractTriple(rtDict,self,context)

    def __len__(self, context=None):
        """ Number of statements in the store. """
        c=self._db.cursor()
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        if context:
            q="""select
                   count(*)
                 from
                   %s,
                   %s,
                   %s
                 where %s and %s and %s;"""%(
                   quoted_table,
                   asserted_table,
                   asserted_type_table,
                   buildContextClause(context,quoted_table),
                   buildContextClause(context,asserted_table),
                   buildContextClause(context,asserted_type_table),
                   )
        else:
            q="""select count(*)
                 from %s

                 union all

                 select count(*)
                 from %s"""%(asserted_table,asserted_type_table)
        c.execute(q)
        rt=c.fetchall()
        c.close()
        return len(rt)>1 and reduce(lambda x,y: x['count(*)']+y['count(*)'],rt) or int([rtDict['count(*)'] for rtDict in rt][0])

    def contexts(self, triple=None):
        """
        FIXME:  Add support for triple argument
        """
        c=self._db.cursor()
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        if triple:
            s,p,o=triple
            if p == RDF.type:
                clauseString = buildClause('quoted',s,o,None,False,p)
                typeClauseString = buildClause('typeTable',s,o)
                q="""
                     select
                       quoted.context
                     from
                       %s as quoted
                     %s
                     
                     union 
            
                     select
                       typeTable.context
                     from
                       %s as typeTable
                     %s"""%(quoted_table,clauseString,asserted_type_table,typeClauseString)
            elif not p or isinstance(p,REGEXTerm) and p.compiledExpr.match(RDF.type):
                clauseStringList=[]
                for tableAlias in ['quoted','asserted']:                    
                    clauseStringList.append(buildClause(tableAlias,s,o,None,False,p))                    

                typeClauseString = buildClause('typeTable',s,o,None)                
                q="""
                     select
                        quoted.context
                     from
                        %s as quoted
                     %s

                     union 

                     select
                        asserted.context
                      from     
                        %s as asserted
                      %s

                     union 

                     select
                        typeTable.context as context
                     from
                        %s as typeTable
                     %s

                     union 


                      """%(quoted_table,clauseStringList[0],asserted_table,clauseStringList[1],asserted_type_table,typeClauseString)                                
            else:
                clauseStringList=[]
                for tableAlias in ['quoted','asserted']:                    
                    clauseStringList.append(buildClause(tableAlias,s,o,None,False,p))                    
                
                q="""select
                        quoted.context
                     from
                        %s as quoted
                     %s

                     union 

                     select
                        asserted.context
                      from     
                        %s as asserted
                      %s"""%(quoted_table,clauseStringList[0],asserted_table,clauseStringList[1])                                

        else:
            q="""select
                   quoted.context
                 from
                   %s as quoted

                 union

                 select
                   asserted.context
                 from
                   %s as asserted

                 union

                 select
                   assertedType.context
                 from
                   %s as assertedType"""%(quoted_table,asserted_table,asserted_type_table)
        c.execute(q)
        rt=c.fetchall()
        c.close()
        for context in [rtDict['context'] for rtDict in rt]:
            yield context
    
    def remove_context(self, identifier):
        """ """
        c=self._db.cursor()
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        q= "DELETE %s,%s,%s from %s,%s,%s where %s and %s and %s;"%(
            quoted_table,
            asserted_table,
            asserted_type_table,
            quoted_table,
            asserted_table,
            asserted_type_table,
            buildContextClause(identifier,quoted_table),
            buildContextClause(identifier,asserted_table),
            buildContextClause(identifier,asserted_type_table)
            )
        c.execute(q)
        c.close()

    # Optional Namespace methods

    #quantifier utility methods
    def variables(context):
        raise Exception("Not implemented")                
    def existentials(context):
        raise Exception("Not implemented")                

    #optimized interfaces (those needed in order to port Versa)
    #capable of taking a list of object/predicate terms instead of a single term
    def subjects(self, predicate=None, obj=None):
        """
        A generator of subjects with the given predicate and object.
        """
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        c=self._db.cursor()
        if predicate == RDF.type:
            typeClauseString = buildClause('typeTable',None,obj)
            q="""
                 select
                   typeTable.member as subject,
                   typeTable.termComb
                 from
                 %s as typeTable
                 %s"""%(asserted_type_table,typeClauseString)            
        elif isinstance(predicate,REGEXTerm) and predicate.compiledExpr.match(RDF.type) or\
                 isinstance(predicate,list) and RDF.type in predicate or\
                 isinstance(predicate,list) and [p for p in predicate if isinstance(p,REGEXTerm) and p.compiledExpr.match(RDF.type)]:
            clauseString = buildClause('asserted',None,obj,None,False,predicate)
            typeClauseString = buildClause('typeTable',None,obj)
            q="""
                 select
                   typeTable.member as subject,
                   typeTable.termComb
                 from
                   %s as typeTable
                 %s

                union
                 
                select
                  asserted.subject,
                  asserted.termComb
                from
                  %s as asserted
                  %s"""%(asserted_type_table,typeClauseString,asserted_table,clauseString)            
        elif predicate and predicate != RDF.type:
            clauseString=buildClause('asserted',None,obj,None,False,predicate)

            q="""select
                   asserted.subject,
                   asserted.termComb
                 from     
                   %s as asserted
                   %s"""%(asserted_table,clauseString)                                            
        else:
            clauseString=buildClause('asserted',None,obj,None,False,predicate)
            typeClauseString = buildClause('typeTable',None,obj,None)                
            q="""select
                   typeTable.member as subject,
                   typeTable.termComb
                 from
                   %s as typeTable
                 %s

                 union 

                 select
                   asserted.subject,
                   asserted.termComb
                 from     
                   %s as asserted
                   %s"""%(asserted_type_table,typeClauseString,asserted_table,clauseString)
        c.execute(q)
        rt=c.fetchall()
        c.close()
        for subject,termComb in [(rtDict['subject'],rtDict['termComb']) for rtDict in rt]:
            termComb=REVERSE_TERM_COMBINATIONS[termComb][SUBJECT]
            yield createTerm(subject,termComb,self)


    #capable of taking a list of predicate terms instead of a single term
    def objects(self, subject=None, predicate=None):
        """
        A generator of objects with the given subject and predicate.
        """
        quoted_table="%s_quoted_statements"%self._internedId
        asserted_table="%s_asserted_statements"%self._internedId
        asserted_type_table="%s_type_statements"%self._internedId
        c=self._db.cursor()
        if RDF.type == predicate:
            typeClauseString = buildClause('typeTable',subject,None)
            q="""
                 select
                   typeTable.klass as object,
                   typeTable.termComb
                 from
                   %s as typeTable
                  %s"""%(asserted_type_table,typeClauseString)

        elif predicate and predicate != RDF.type or isinstance(predicate,list) and RDF.type not in predicate:
            clauseString = buildClause('asserted',subject,None,None,False,predicate)
            q="""
                select
                  asserted.object,
                  asserted.termComb
                from
                  %s as asserted
                  %s"""%(asserted_table,clauseString)                                    
            
        else:
            clauseString = buildClause('asserted',subject,None,None,False,predicate)
            typeClauseString = buildClause('typeTable',subject,None)
            q="""
                 select
                   typeTable.klass as object,
                   typeTable.termComb
                 from
                   %s as typeTable
                 %s

                union
                 
                select
                  asserted.object,
                  asserted.termComb
                from
                  %s as asserted
                  %s"""%(asserted_type_table,typeClauseString,asserted_table,clauseString)                                    

        c.execute(q)
        rt=c.fetchall()
        c.close()
        for obj,termComb in [(rtDict['object'],rtDict['termComb']) for rtDict in rt]:
            termComb=REVERSE_TERM_COMBINATIONS[termComb][OBJECT]
            yield createTerm(obj,termComb,self)


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
        c.execute("INSERT INTO %s_namespace_binds VALUES ('%s', '%s')"%(
            self._internedId,
            prefix,
            namespace)
        )
        c.close()

    def prefix(self, namespace):
        """ """
        c=self._db.cursor()
        c.execute("select prefix from %s_namespace_binds where uri = '%s'"%(
            self._internedId,
            namespace)
        )
        rt = [rtDict['prefix'] for rtDict in c.fetchall()]
        c.close()
        return rt and rt or None

    def namespace(self, prefix):
        """ """
        c=self._db.cursor()
        c.execute("select uri from %s_namespace_binds where prefix = '%s'"%(
            self._internedId,
            prefix)
        )
        rt = [rtDict['uri'] for rtDict in c.fetchall()]
        c.close()
        return rt and rt or None

    def namespaces(self):
        """ """
        c=self._db.cursor()
        c.execute("select prefix, uri from %s_namespace_binds where 1;"%(
            self._internedId
            )
        )
        rt = [(rtDict['prefix'],rtDict['uri']) for rtDict in c.fetchall()]
        c.close()
        for prefix,uri in rt:
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
    '%s_namespace_binds'
]        


CREATE_ASSERTED_STATEMENTS_TABLE = """
CREATE TABLE %s_asserted_statements (
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
    
CREATE_ASSERTED_TYPE_STATEMENTS_TABLE = """
CREATE TABLE %s_type_statements (
    member        text not NULL,
    klass         text,
    context       text not NULL,
    termComb      tinyint unsigned not NULL,
    INDEX termComb (termComb),
    INDEX memberC_index (member(100),klass(100),context(50)),
    INDEX klassC_index (klass(100),context(50)),
    INDEX c_index (context(10))) TYPE=InnoDB"""
    
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
