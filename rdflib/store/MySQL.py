from __future__ import generators
from rdflib import BNode
from rdflib.store import Store,VALID_STORE, CORRUPTED_STORE, NO_STORE, UNKNOWN
from rdflib.Literal import Literal
from pprint import pprint
import MySQLdb,sys
from rdflib.term_utils import *
from rdflib.Graph import QuotedGraph
from rdflib.store.REGEXMatching import REGEXTerm, NATIVE_REGEX, PYTHON_REGEX
from rdflib.store.AbstractSQLStore import *
from FOPLRelationalModel.RelationalHash import IdentifierHash, LiteralHash, RelationalHash, GarbageCollectionQUERY
from FOPLRelationalModel.BinaryRelationPartition import *
from FOPLRelationalModel.QuadSlot import *

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

def createTerm(termString,termType,store,objLanguage=None,objDatatype=None):
    if termType == 'L':
        cache = store.literalCache.get((termString,objLanguage,objDatatype))
        if cache is not None:
            #store.cacheHits += 1
            return cache
        else:
            #store.cacheMisses += 1
            rt = Literal(termString,objLanguage,objDatatype)
            store.literalCache[((termString,objLanguage,objDatatype))] = rt
            return rt
    elif termType=='F':
        cache = store.otherCache.get((termType,termString))
        if cache is not None:
            #store.cacheHits += 1
            return cache
        else:
            #store.cacheMisses += 1
            rt = QuotedGraph(store,URIRef(termString))
            store.otherCache[(termType,termString)] = rt
            return rt
    elif termType == 'B':
        cache = store.bnodeCache.get((termString))
        if cache is not None:
            #store.cacheHits += 1
            return cache
        else:
            #store.cacheMisses += 1
            rt = TERM_INSTANCIATION_DICT[termType](termString)
            store.bnodeCache[(termString)] = rt
            return rt
    elif termType =='U':
        cache = store.uriCache.get((termString))
        if cache is not None:
            #store.cacheHits += 1
            return cache
        else:
            #store.cacheMisses += 1
            rt = URIRef(termString)
            store.uriCache[(termString)] = rt
            return rt
    else:
        cache = store.otherCache.get((termType,termString))
        if cache is not None:
            #store.cacheHits += 1
            return cache
        else:
            #store.cacheMisses += 1
            rt = TERM_INSTANCIATION_DICT[termType](termString)
            store.otherCache[(termType,termString)] = rt
            return rt

def extractTriple(tupleRt,store,hardCodedContext=None):
    subject,sTerm,predicate,pTerm,obj,oTerm,rtContext,cTerm,objDatatype,objLanguage = tupleRt
    context = rtContext is not None and rtContext or hardCodedContext.identifier

    s=createTerm(subject,sTerm,store)
    p=createTerm(predicate,pTerm,store)
    o=createTerm(obj,oTerm,store,objLanguage,objDatatype)

    graphKlass, idKlass = constructGraph(cTerm)
    return s,p,o,(graphKlass,idKlass,context)


class MySQL(Store):
    """
    MySQL implementation of FOPL Relational Model as an rdflib Store
    """
    context_aware = True
    formula_aware = True
    transaction_aware = True
    regex_matching = NATIVE_REGEX

    def __init__(self, identifier=None, configuration=None):
        self.identifier = identifier and identifier or 'hardcoded'
        #Use only the first 10 bytes of the digest
        self._internedId = INTERNED_PREFIX + sha.new(self.identifier).hexdigest()[:10]

        #Setup FOPL RelationalModel objects
        self.idHash = IdentifierHash(self._internedId)
        self.valueHash = LiteralHash(self._internedId)
        self.binaryRelations = NamedBinaryRelations(self._internedId,self.idHash,self.valueHash)
        self.literalProperties = NamedLiteralProperties(self._internedId,self.idHash,self.valueHash)
        self.aboxAssertions = AssociativeBox(self._internedId,self.idHash,self.valueHash)
        self.tables = [
                       self.binaryRelations,
                       self.literalProperties,
                       self.aboxAssertions,
                       self.idHash,
                       self.valueHash
                       ]
        self.createTables = [
                       self.idHash,
                       self.valueHash,
                       self.binaryRelations,
                       self.literalProperties,
                       self.aboxAssertions
                       ]
        self.hashes = [self.idHash,self.valueHash]
        self.partitions = [self.literalProperties,self.binaryRelations,self.aboxAssertions,]

        #This parameter controls how exlusively the literal table is searched
        #If true, the Literal partition is searched *exclusively* if the object term
        #in a triple pattern is a Literal or a REGEXTerm.  Note, the latter case
        #prevents the matching of URIRef nodes as the objects of a triple in the store.
        #If the object term is a wildcard (None)
        #Then the Literal paritition is searched in addition to the others
        #If this parameter is false, the literal partition is searched regardless of what the object
        #of the triple pattern is
        self.STRONGLY_TYPED_TERMS = False
        self._db = None
        if configuration is not None:
            self.open(configuration)

        self.cacheHits = 0
        self.cacheMisses = 0

        self.literalCache = {}
        self.uriCache = {}
        self.bnodeCache = {}
        self.otherCache = {}

    def executeSQL(self,cursor,qStr,params=None,paramList=False):
        """
        Overridded in order to pass params seperate from query for MySQLdb
        to optimize
        """
        #self._db.autocommit(False)
        if params is None:
            cursor.execute(qStr)
        elif paramList:
            cursor.executemany(qStr,[tuple(item) for item in params])
        else:
            cursor.execute(qStr,tuple(params))

    #Database Management Methods
    def open(self, configuration, create=False):
        """
        Opens the store specified by the configuration string. If
        create is True a store will be created if it does not already
        exist. If create is False and a store does not already exist
        an exception is raised. An exception is also raised if a store
        exists, but there is insufficient permissions to open the
        store.
        """
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
            c.execute(CREATE_NS_BINDS_TABLE%(self._internedId))
            for kb in self.createTables:
                c.execute(kb.createSQL())
                if isinstance(kb,RelationalHash) and kb.defaultSQL():
                    c.execute(kb.defaultSQL())

            db.commit()
            c.close()
            db.close()

        self._db = MySQLdb.connect(user = configDict['user'],
                                   passwd = configDict['password'],
                                   db=configDict['db'],
                                   port=configDict['port'],
                                   host=configDict['host'],
                                   #use_unicode=True,
                                   #read_default_file='/etc/my.cnf'
                                  )
        self._db.autocommit(False)
        c=self._db.cursor()
        c.execute("""SHOW DATABASES""")
        #FIXME This is a character set hack.  See: http://sourceforge.net/forum/forum.php?thread_id=1448424&forum_id=70461
        #self._db.charset = 'utf8'
        rt = c.fetchall()
        if (configDict['db'].encode('utf-8'),) in rt:
            for tn in self.tables:
                c.execute("""show tables like '%s'"""%(tn,))
                rt=c.fetchall()
                if not rt:
                    sys.stderr.write("table %s Doesn't exist\n" % (tn));
                    #The database exists, but one of the partitions doesn't exist
                    return CORRUPTED_STORE
            #Everything is there (the database and the partitions)
            return VALID_STORE
        #The database doesn't exist - nothing is there
        return NO_STORE

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
        msql_db.autocommit(False)
        c=msql_db.cursor()
        for tbl in self.tables + ["%s_namespace_binds"%self._internedId]:
            try:
                c.execute('DROP table %s'%tbl)
                #print "dropped table: %s"%(tblsuffix%(self._internedId))
            except Exception, e:
                print "unable to drop table: %s"%(tbl)
                print e

        #Note, this only removes the associated tables for the closed world universe given by the identifier
        print "Destroyed Close World Universe %s ( in MySQL database %s)"%(self.identifier,configDict['db'])
        msql_db.commit()
        msql_db.close()

    #Transactional interfaces
    def commit(self):
        """ """
        self._db.commit()

    def rollback(self):
        """ """
        self._db.rollback()

    def gc(self):
        """
        Purges unreferenced identifiers / values - expensive
        """
        c=self._db.cursor()
        purgeQueries = GarbageCollectionQUERY(
                                               self.idHash,
                                               self.valueHash,
                                               self.binaryRelations,
                                               self.aboxAssertions,
                                               self.literalProperties)

        for q in purgeQueries:
            self.executeSQL(c,q)

    def add(self, (subject, predicate, obj), context=None, quoted=False):
        """ Add a triple to the store of triples. """
        qSlots = genQuadSlots([subject,predicate,obj,context])
        if predicate == RDF.type:
            kb = self.aboxAssertions
        elif isinstance(obj,Literal):
            kb = self.literalProperties
        else:
            kb = self.binaryRelations
        kb.insertRelations([qSlots])
        kb.flushInsertions(self._db)

    def addN(self, quads):
        """
        Adds each item in the list of statements to a specific context. The quoted argument
        is interpreted by formula-aware stores to indicate this statement is quoted/hypothetical.
        Note that the default implementation is a redirect to add
        """
        for s,p,o,c in quads:
            assert c is not None, "Context associated with %s %s %s is None!"%(s,p,o)
            qSlots = genQuadSlots([s,p,o,c])
            if p == RDF.type:
                kb = self.aboxAssertions
            elif isinstance(o,Literal):
                kb = self.literalProperties
            else:
                kb = self.binaryRelations

            kb.insertRelations([qSlots])

        for kb in self.partitions:
            if kb.pendingInsertions:
                kb.flushInsertions(self._db)

    def remove(self, (subject, predicate, obj), context):
        """ Remove a triple from the store """
        targetBRPs = BinaryRelationPartitionCoverage((subject,predicate,obj,context),self.partitions)
        c=self._db.cursor()
        for brp in targetBRPs:
            query = "DELETE %s from %s %s WHERE "%(
                                          brp,
                                          brp,
                                          brp.generateHashIntersections()
                                        )
            whereClause,whereParameters = brp.generateWhereClause((subject,predicate,obj,context))
            self.executeSQL(c,query+whereClause,params=whereParameters)

        c.close()

    def triples(self, (subject, predicate, obj), context=None):
        c=self._db.cursor()
        if context is None or isinstance(context.identifier,REGEXTerm):
            rt=PatternResolution((subject,predicate,obj,context),c,self.partitions,fetchall=False)
        else:
            #No need to order by triple (expensive), all result sets will be in the same context
            rt=PatternResolution((subject,predicate,obj,context),c,self.partitions,orderByTriple=False,fetchall=False)
        while rt:
            s,p,o,(graphKlass,idKlass,graphId) = extractTriple(rt,self,context)
            currentContext=(context is None or isinstance(context.identifier,REGEXTerm)) and graphKlass(self,idKlass(graphId)) or context
            contexts = [currentContext]
            rt = next = c.fetchone()
            if context is None or isinstance(context.identifier,REGEXTerm):
                sameTriple = next and extractTriple(next,self,context)[:3] == (s,p,o)
                while sameTriple:
                    s2,p2,o2,(graphKlass,idKlass,graphId) = extractTriple(next,self,context)
                    c2 = graphKlass(self,idKlass(graphId))
                    contexts.append(c2)
                    rt = next = c.fetchone()
                    sameTriple = next and extractTriple(next,self,context)[:3] == (s,p,o)

            yield (s,p,o),(c for c in contexts)

    def triples_choices(self, (subject, predicate, object_),context=None):
        """
        A variant of triples that can take a list of terms instead of a single
        term in any slot.  Stores can implement this to optimize the response time
        from the import default 'fallback' implementation, which will iterate
        over each term in the list and dispatch to tripless
        """
        if isinstance(object_,list):
            assert not isinstance(subject,list), "object_ / subject are both lists"
            assert not isinstance(predicate,list), "object_ / predicate are both lists"
            if not object_:
                object_ = None
            for (s1, p1, o1), cg in self.triples((subject,predicate,object_),context):
                yield (s1, p1, o1), cg

        elif isinstance(subject,list):
            assert not isinstance(predicate,list), "subject / predicate are both lists"
            if not subject:
                subject = None
            for (s1, p1, o1), cg in self.triples((subject,predicate,object_),context):
                yield (s1, p1, o1), cg

        elif isinstance(predicate,list):
            assert not isinstance(subject,list), "predicate / subject are both lists"
            if not predicate:
                predicate = None
            for (s1, p1, o1), cg in self.triples((subject,predicate,object_),context):
                yield (s1, p1, o1), cg

    def __repr__(self):
        c=self._db.cursor()

        rtDict = {}
        countRows = "select count(*) from %s"
        countContexts = "select DISTINCT %s from %s"
        unionSelect = ' union '.join([countContexts%(part.columnNames[CONTEXT],str(part)) for part in self.partitions])
        self.executeSQL(c,unionSelect)
        ctxCount = len(c.fetchall())
        for part in self.partitions:
            self.executeSQL(c,countRows%part)
            rowCount = c.fetchone()[0]
            rtDict[str(part)]=rowCount
        return "<Parititioned MySQL N3 Store: %s context(s), %s classification(s), %s property/value assertion(s), and %s other relation(s)>"%(
            ctxCount,
            rtDict[str(self.aboxAssertions)],
            rtDict[str(self.literalProperties)],
            rtDict[str(self.binaryRelations)],
        )

    def __len__(self, context=None):
        rows = []
        countRows = "select count(*) from %s"
        c=self._db.cursor()
        for part in self.partitions:
            self.executeSQL(c,countRows%part)
            rowCount = c.fetchone()[0]
            rows.append(rowCount)
        return reduce(lambda x,y: x+y,rows)

    def contexts(self, triple=None):
        c=self._db.cursor()
        if triple:
            subject,predicate,obj = triple
        else:
            subject = predicate = obj = None
        rt=PatternResolution((subject,predicate,obj,None),
                              c,
                              self.partitions,
                              fetchall=False,
                              fetchContexts=True)
        while rt:
            contextId,cTerm = rt
            graphKlass, idKlass = constructGraph(cTerm)
            yield graphKlass(self,idKlass(contextId))
            rt = c.fetchone()

    #Namespace persistence interface implementation
    def bind(self, prefix, namespace):
        """ """
        c=self._db.cursor()
        try:
            self.executeSQL(
                c,
                "INSERT INTO %s_namespace_binds VALUES ('%s', '%s')"%(
                self._internedId,
                prefix,
                namespace)
            )
        except:
            pass
        c.close()

    def prefix(self, namespace):
        """ """
        c=self._db.cursor()
        self.executeSQL(c,"select prefix from %s_namespace_binds where uri = '%s'"%(
            self._internedId,
            namespace)
        )
        rt = [rtTuple[0] for rtTuple in c.fetchall()]
        c.close()
        return rt and rt[0] or None

    def namespace(self, prefix):
        """ """
        c=self._db.cursor()
        try:
            self.executeSQL(c,"select uri from %s_namespace_binds where prefix = '%s'"%(
                self._internedId,
                prefix)
                      )
        except:
            return None
        rt = [rtTuple[0] for rtTuple in c.fetchall()]
        c.close()
        return rt and rt[0] or None

    def namespaces(self):
        """ """
        c=self._db.cursor()
        self.executeSQL(c,"select prefix, uri from %s_namespace_binds where 1;"%(
            self._internedId
            )
        )
        rt=c.fetchall()
        c.close()
        for prefix,uri in rt:
            yield prefix,uri


CREATE_NS_BINDS_TABLE = """
CREATE TABLE %s_namespace_binds (
    prefix        varchar(20) UNIQUE not NULL,
    uri           text,
    PRIMARY KEY (prefix),
    INDEX uri_index (uri(100))) ENGINE=InnoDB"""        