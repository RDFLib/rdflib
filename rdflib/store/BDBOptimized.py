from bsddb import db
from urllib import pathname2url
from os import mkdir
from os.path import exists, abspath

from rdflib import URIRef
from rdflib.store import Store, VALID_STORE, CORRUPTED_STORE, NO_STORE, UNKNOWN

SUPPORT_MULTIPLE_STORE_ENVIRON = False

warnings.warn("The BDBOptimized store is experimental and not yet recommended for production.")

if db.version() < (4,3,29):
    warnings.warn("Your BDB library may not be supported.")
    
import logging
_logger = logging.getLogger(__name__)

# TODO: performance testing?

class IDMap:
    def __init__(self, db_env, node_pickler):
        self.__db_env = db_env
        self.__dbp = db.DB(db_env)
        self.__dbp.open("IDMap_hash.db", None, db.DB_HASH, db.DB_CREATE | db.DB_AUTO_COMMIT)

        self.__dbs = db.DB(db_env)
        self.__dbs.open("IDMap_recno.db", None, db.DB_RECNO, db.DB_CREATE | db.DB_AUTO_COMMIT)

        # pickling and un-pickling the data
        self.__node_pickler = node_pickler
        
        self.__loads = self.__node_pickler.loads
        self.__dumps = self.__node_pickler.dumps

    def insert(self, key):
        # this inserts a new key if the key was not available
        t = self.__db_env.txn_begin()
        try:
            k = self.__dumps(key)
            val = self.__dbp.get(k, txn=t)
            # the key is not found, register a new value for it
            if val is None:
                val = "%s" % self.__dbs.append(k, t)
                #dbp.put("counter", counter, txn=t)
                self.__dbp.put(k, val, txn=t)
            t.commit(0)
            return val
        except Exception, e:
            t.abort()
        
    #    t2.commit(0)
    
    def get_id(self, key):
        k = self.__dumps(key)
        t = self.__db_env.txn_begin()
        try:
            val = self.__dbp.get(k, txn=t)
            t.commit(0)
            if val == None:
                return None
            
            return val
        except Exception, e:
            t.abort()
    
    def get_var(self, num):
        t = self.__db_env.txn_begin()
        try:
            val = self.__dbs.get(num, txn=t)
            t.commit(0)
            return self.__loads(val)
        except Exception, e:
            t.abort()

    def close(self):
        self.__dbp.close()
        self.__dbs.close()

    def all(self):
        l = []
        
        cursor = self.__dbs.cursor()
        current = cursor.first()
        while current:
            try:
                key, value = current
                l.append((key, value))            
                current = cursor.next()
            except Exception, e:
                cursor.close()
                
        cursor.close()
        return l

def secondaryIndexKey(key, data):
    # returns the first part of a tuple of ints joined by : in a str.
    return (data.split("^")[0])
    
class QuadIndex:

    def __init__(self, db_env, idmapper):
        self.__db_env = db_env
        self.__map = idmapper
        
        self.__splitter = '^'
        
        self.__index_list = ['spoc', 'pocs', 'ocsp', 'ospc', 'cspo', 'cpso']        
        self.__indices = self.__init_indices()
        self.__use_index = self.__init_use_index()
        self.__re_order = self.__init_re_order()
        self.__open = True

    def __init_indices(self):
        indices = {}
        for index in self.__index_list:
            indices[index] = db.DB(self.__db_env)
            indices[index].open("index_%s.db" % index, None, db.DB_BTREE, db.DB_CREATE | db.DB_AUTO_COMMIT)
        
        return indices
        
    def __init_re_order(self):
        # create functions that changes the variable order back
        # to s,p,o,c
        re_order = {}

        re_order['spoc'] = lambda (s,p,o,c): (s,p,o,c)
        re_order['pocs'] = lambda (p,o,c,s): (s,p,o,c)
        re_order['ocsp'] = lambda (o,c,s,p): (s,p,o,c)
        re_order['ospc'] = lambda (o,s,p,c): (s,p,o,c)
        re_order['cspo'] = lambda (c,s,p,o): (s,p,o,c)
        re_order['cpso'] = lambda (c,p,s,o): (s,p,o,c)
        
        return re_order
    
    def __init_use_index(self):
        # a hashmap deciding which index to use depending on bound variables
        # there are 16 combinations and 6 indices
        use_index = {}
        
        # spoc
        use_index[(False, False, False, False)] = 'spoc'
        use_index[(True, False, False, False)] = 'spoc'
        use_index[(True, True, False, False)] = 'spoc'
        use_index[(True, True, True, False)] = 'spoc'
        use_index[(True, True, True, True)] = 'spoc'

        # pocs
        use_index[(False, True, False, False)] = 'pocs'
        use_index[(False, True, True, False)] = 'pocs'
        use_index[(False, True, True, True)] = 'pocs'

        # ocsp
        use_index[(False, False, True, False)] = 'ocsp'
        use_index[(False, False, True, True)] = 'ocsp'
        use_index[(True, False, True, True)] = 'ocsp'
        
        # cspo
        use_index[(False, False, False, True)] = 'cspo'
        use_index[(True, False, False, True)] = 'cspo'
        use_index[(True, True, False, True)] = 'cspo'
        
        # cpso
        use_index[(False, True, False, True)] = 'cpso'
        
        # ospc
        use_index[(True, False, True, False)] = 'ospc'  
                
        return use_index
    
    def insert(self, (s,p,o,c)):
        # check if the key is available,
        
        # make sure there is a mapping for all the values
        s_id = self.__map.insert(s)
        p_id = self.__map.insert(p)
        o_id = self.__map.insert(o)
        c_id = self.__map.insert(c)
        
        index_map = self.__init_index_map((s_id, p_id, o_id, c_id))
        
        t = self.__db_env.txn_begin()
        try:
            for index in self.__indices:
                self.__indices[index].put(index_map[index], '', txn=t)
                
            t.commit(0)        
        except Exception, e:
            t.abort()

    def delete(self, (s,p,o,c), txn=None):
        (s_id, p_id, o_id, c_id) = self.__map_id((s,p,o,c))
        
        # setup the indices
        index_map = self.__init_index_map((s_id, p_id, o_id, c_id))

        # since an index is in used within a transaction to traverse
        # the keys to delete, the delete deadlocks when acting on that index
        # close the cursor in __all_prefix before yielding?
        if txn == None:
            t = self.__db_env.txn_begin()
        else:
            t = self.__db_env.txn_begin(txn)
            
        try:
            for index in self.__indices:
                self.__indices[index].delete(index_map[index], txn=t, flags=0)
            t.commit(0)        
        except Exception, e:
            t.abort()
        
    #    t2.commit(0)
    
    # returns a mapping from index configuration to a
    # string in the format v1^v2^v3^v4, which is used
    # as a key in the index
    def __init_index_map(self, (s_id,p_id,o_id,c_id)):
        indices = {}

        indices['spoc'] = self.__splitter.join([str(k) for k in (s_id, p_id, o_id, c_id)])
        indices['pocs'] = self.__splitter.join([str(k) for k in (p_id, o_id, c_id, s_id)])
        indices['ocsp'] = self.__splitter.join([str(k) for k in (o_id, c_id, s_id, p_id)])
        indices['ospc'] = self.__splitter.join([str(k) for k in (o_id, s_id, p_id, c_id)])        
        indices['cspo'] = self.__splitter.join([str(k) for k in (c_id, s_id, p_id, o_id)])
        indices['cpso'] = self.__splitter.join([str(k) for k in (c_id, p_id, s_id, o_id)])

        return indices

    # a 0 (or '0') in a BDB range query is first in the range    
    # returns the list of ints representing the bound
    # variables in the index
     
    def __map_id(self, (s,p,o,c)):
        def map_id(val): 
            m = self.__map.get_id(val)
            if m == None:
                return 0
            return int(m)

        return [map_id(v) for v in (s,p,o,c)]

    def __map_var(self, (s_id, p_id, o_id, c_id)):
        def map_var(val):
            v = self.__map.get_var(int(val))
            if v == None:
                return ''
            return v
        
        return tuple([map_var(v) for v in (s_id, p_id, o_id, c_id)])
    
    def triples(self, (s,p,o,c), twopass=False):
        # TODO: implement a twopass version where all IDs are collected before
        # being mapped to their real values. Does this improve performance?
        # 
        # iterates over the triples depending on the values of s,p,o,c
        indices = {}
        
        (s_id, p_id, o_id, c_id) = self.__map_id((s,p,o,c))
        
        # setup the indices
        indices = self.__init_index_map((s_id, p_id, o_id, c_id))
                
        # get the bool map for the current configuration
        (s_bool, p_bool, o_bool, c_bool) = [v != 0 for v in (s_id, p_id, o_id, c_id)]

        current_index = self.__use_index[(s_bool, p_bool, o_bool, c_bool)]
        prefix = indices[current_index]
        # strip of all ^0
        # no bound variables
        if not (True in (s_bool, p_bool, o_bool, c_bool)):
            prefix = ''
        # bound  variables found, strip of trailing ^0 for the prefix
        elif self.__splitter + '0' in prefix:
            prefix = prefix[0:prefix.find(self.__splitter + '0')]
        # otherwise use the given prefix
            
        re_order_f = self.__re_order[current_index]
        
        # convert the key back into the corresponding values        
        for k,v in self.__all_prefix(prefix, current_index):
            (s,p,o,c) = self.__map_var(re_order_f(k.split(self.__splitter)))
#            print (k,v, prefix, indices[current_index], s, p, o, c)
            yield ((s,p,o), c)

        return

    def contexts(self, triple=None):
        for k,v in self.__all_prefix('', index='cspo'):
            (c,s,p,o) = self.__map_var(k.split(self.__splitter))
            yield c
    
    def remove(self, (s,p,o,c)):
        [self.delete((s_t,p_t,o_t,c_t)) for ((s_t,p_t,o_t),c_t) in self.triples((s,p,o,c))]
        

    def __len__(self, context=None):
        return len([x for x in self.triples((None, None, None, context))])
    
    def __all_prefix(self, prefix, index='spoc'):
        next = True
        next_key = prefix
        
        while next:
            c = self.__indices[index].cursor()
            try:
                current = c.set_range(next_key)
                next = c.next()
                if next:
                    next_key, data = next
            except db.DBNotFoundError, e:
                next = None
            # what happens when the cursor is closed and re-opened between
            # each access, does this mean that the lookup will be done again 
            # or is the location preserved somehow?
            # in the first case it is better to collect a list of results and
            # then yield over this list
            c.close()
            
            if current:
                key, data = current
                if key and key.startswith(prefix):
                    yield key, data
        
            if next_key and not next_key.startswith(prefix):
                next = None
            
    def close(self):
        self.__open = False
        
        for index in self.__indices:
            self.__indices[index].close()

class BDBOptimized(Store):
    """ An alternative BDB store implementing the index-structure proposed in:
     http://sw.deri.org/2005/02/dexa/yars.pdf
    
     Index structures
     key -> int, int -> key for variable to id and id -> variable
     Triple indices: spoc, pocs, ocsp, cspo, cpso, ospc
     
     This store is both transaction and context-aware.
    """
    
    context_aware = True
    formula_aware = False

    # TODO: transaction support
    transaction_aware = True
    
    def __init__(self, configuration=None, identifier=None):
        self.__open = False
        self.__identifier = identifier
        super(BDBOptimized, self).__init__(configuration)
        self.configuration = configuration
        self.__db_env = None
        self.__id_mapper = None
        self.__quad_index = None
        self.__locks = 5000
        
    def __get_identifier(self):
        return self.__identifier
    identifier = property(__get_identifier)

    def _init_db_environment(self, homeDir, create=True):
        #NOTE: The identifier is appended to the path as the location for the db
        #This provides proper isolation for stores which have the same path but different identifiers
        
        if SUPPORT_MULTIPLE_STORE_ENVIRON:
            fullDir = join(homeDir,self.identifier)
        else:
            fullDir = homeDir
        envsetflags  = db.DB_CDB_ALLDB
        envflags = db.DB_INIT_MPOOL | db.DB_INIT_LOCK | db.DB_THREAD | db.DB_INIT_TXN | db.DB_RECOVER
        if not exists(fullDir):
            if create==True:
                makedirs(fullDir)
                self.create(path)
            else:                
                return NO_STORE

        db_env = db.DBEnv()
        db_env.set_cachesize(0, 1024*1024*50) # TODO
        
        # enable deadlock-detection
        db_env.set_lk_detect(db.DB_LOCK_MAXLOCKS)
        
        # increase the number of locks, this is correlated to the size (num triples) that 
        # can be added/removed with a single transaction
        db_env.set_lk_max_locks(self.__locks)
        db_env.set_lk_max_lockers(self.__locks)
        db_env.set_lk_max_objects(self.__locks)
        
        #db_env.set_lg_max(1024*1024)
        #db_env.set_flags(envsetflags, 1)
        db_env.open(fullDir, envflags | db.DB_CREATE,0)
        return db_env

    def is_open(self):
        return self.__open

    def open(self, path, create=True):
        homeDir = path

        if self.__identifier is None:
            self.__identifier = URIRef(pathname2url(abspath(homeDir)))

        self.__db_env  = self._init_db_environment(homeDir, create)        
        self.__open = True

        self.__id_mapper = IDMap(self.__db_env, self.node_pickler)
        self.__quad_index = QuadIndex(self.__db_env, self.__id_mapper)

    def triples(self, (subject, predicate, object), context=None):
        for result in self.__quad_index.triples((subject, predicate, object, context)):
            yield result

    def contexts(self, triple=None):
        return self.__quad_index.contexts(triple=triple)
 
    def add(self, (subject, predicate, object), context, quoted=False, txn=None):
        """\
        Add a triple to the store of triples.
        """
        assert self.__open, "The Store must be open."
        Store.add(self, (subject, predicate, object), context, quoted)

        self.__quad_index.insert((subject, predicate, object, context))

    def remove(self, (subject, predicate, object), context, txn=None):
        """
        Remove the matching triples and/or context from the store. Variables
        can be unbound by using None.
        """
        
        assert self.__open, "The Store must be open."
        Store.remove(self, (subject, predicate, object), context)
        
        self.__quad_index.remove((subject, predicate, object, context))

    def __len__(self, context=None):
        return self.__quad_index.__len__(context)
    
    def close(self, commit_pending_transaction=True):
        self.__open = False
        self.__id_mapper.close()
        self.__quad_index.close()