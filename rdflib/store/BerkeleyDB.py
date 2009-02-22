import warnings, thread
from bsddb import db
from os import makedirs
from os.path import exists, join
from time import sleep
import logging

from rdflib.store import NO_STORE
from rdflib.store.Sleepycat import Sleepycat

if db.version() < (4,3,29):
    warnings.warn("Your BDB library may not be supported.")
    
SUPPORT_MULTIPLE_STORE_ENVIRON = False

_logger = logging.getLogger(__name__)

class TransactionExpired(Exception): pass

# A transaction decorator for BDB
def transaction(f, name=None, **kwds):
    def wrapped(*args, **kwargs):
        bdb = args[0]
        retries = 10
        delay = 1
        e = None
        
        #t = kwargs['env'].txn_begin()
        while retries > 0:
            kwargs['txn'] = bdb.begin_txn()
    
            try:
                result = f(*args, **kwargs)
                bdb.commit()
                # returns here when the transaction was successful
                return result
            except MemoryError, e:
                # Locks are leaking in this code or in BDB
                # print "out of locks: ", e, sys.exc_info()[0], self.db_env.lock_stat()['nlocks']
                bdb.rollback()
                retries = 0
            except db.DBLockDeadlockError, e:
                # print "Deadlock when adding data: ", e
                bdb.rollback()
                sleep(0.1*delay)
                #delay = delay << 1
                retries -= 1
            except Exception, e:
                # print "Got exception in add:", sys.exc_info()[0], e, bdb.dbTxn[thread.get_ident()], bdb.db_env.lock_stat()['nlocks'], retries
                bdb.rollback()
                #print "After rollback", e, add_txn, self.__dbTxn[thread.get_ident()], thread.get_ident()
                retries -= 1
                
        #print "Retries failed!", bdb.db_env.lock_stat()['nlocks']
        raise TransactionExpired("Add failed after exception:" % str(e))

#        except Exception, e:
#            print "Got exception: ", e            
#            bdb.rollback()
            
            #t.abort()

    wrapped.__doc__ = f.__doc__
    return wrapped


class BerkeleyDB(Sleepycat):
    """
    A transaction-capable BerkeleyDB implementation
    The major difference are:
      - a dbTxn attribute which is the transaction object used for all bsddb databases
      - All operations (put,delete,get) take the dbTxn instance
      - The actual directory used for the bsddb persistence is the name of the identifier as a subdirectory of the 'path'
      
    """
    context_aware = True
    formula_aware = True
    transaction_aware = True

    def __init__(self, configuration=None, identifier=None):
        super(BerkeleyDB, self).__init__(configuration, identifier)

        # number of locks, lockers and objects
        self.__locks = 5000

        # when closing is True, no new transactions are allowed
        self.__closing = False
        
        # Each thread is responsible for a single transaction (included nested
        # ones) indexed by the thread id
        self.__dbTxn = {}

    def destroy(self, configuration):
        """
        Destroy the underlying bsddb persistence for this store
        """
        if SUPPORT_MULTIPLE_STORE_ENVIRON:
            fullDir = join(configuration,self.identifier)
        else:
            fullDir = configuration
        if exists(configuration):
            #From bsddb docs:
            #A DB_ENV handle that has already been used to open an environment 
            #should not be used to call the DB_ENV->remove function; a new DB_ENV handle should be created for that purpose.
            self.close()
            db.DBEnv().remove(fullDir,db.DB_FORCE)

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

    #Transactional interfaces
    def begin_txn(self):
        """
        Start a bsddb transaction. If the current thread already has a running
        transaction, a nested transaction with the first transaction for this
        thread as parent is started. See:
        http://pybsddb.sourceforge.net/ref/transapp/nested.html for more on
        nested transactions in BDB.
        """
        # A user should be able to wrap several operations in a transaction.
        # For example, two or more adds when adding a graph.
        # Each internal operation should be a transaction, e.g. an add
        # must be atomic and isolated. However, since add should handle
        # BDB exceptions (like deadlock), an internal transaction should
        # not fail the user transaction. Here, nested transactions are used
        # which have this property.
        
        txn = None

        try:
            if not thread.get_ident() in self.__dbTxn and self.is_open() and not self.__closing:
                self.__dbTxn[thread.get_ident()] = []
                # add the new transaction to the list of transactions
                txn = self.db_env.txn_begin()
                self.__dbTxn[thread.get_ident()].append(txn)
            else:
                # add a nested transaction with the top one as parent
                txn = self.db_env.txn_begin(self.__dbTxn[thread.get_ident()][0])
                self.__dbTxn[thread.get_ident()].append(txn)
        except Exception, e:
            print "begin_txn: ", e
            if txn != None:
                txn.abort()
                
        # return the transaction handle
        return txn
        
    def commit(self, commit_root=False):
        """
        Bsddb tx objects cannot be reused after commit. Set rollback_root to 
        true to commit all active transactions for the current thread.
        """
        if thread.get_ident() in self.__dbTxn and self.is_open():
            try:
                # when the root commits, all childs commit as well
                if commit_root == True:
                    self.__dbTxn[thread.get_ident()][0].commit(0)
                    # no more transactions, clean up
                    del self.__dbTxn[thread.get_ident()]
                else:
                    txn = self.__dbTxn[thread.get_ident()].pop()
                    _logger.debug("committing")
                    #before = self.db_env.lock_stat()['nlocks']
                    txn.commit(0)
                    #print "committing a transaction", self.__dbTxn[thread.get_ident()], txn, before, self.db_env.lock_stat()['nlocks']
                    if len(self.__dbTxn[thread.get_ident()]) == 0:
                        del self.__dbTxn[thread.get_ident()]
            except IndexError, e:
                #The dbTxn for the current thread is removed to indicate that 
                #there are no active transactions for the current thread.
                del self.__dbTxn[thread.get_ident()]
            except Exception, e:
                # print "Got exception in commit", e
                raise e
        else:
            _logger.warning("No transaction to commit")

    def rollback(self, rollback_root=False):
        """
        Bsddb tx objects cannot be reused after commit. Set rollback_root to 
        true to abort all active transactions for the current thread.
        """
        
        if thread.get_ident() in self.__dbTxn and self.is_open():
            _logger.debug("rollingback")
            try:
                if rollback_root == True:
                    # same as commit, when root aborts, all childs abort
                    self.__dbTxn[thread.get_ident()][0].abort()
                    del self.__dbTxn[thread.get_ident()]
                else:
                    txn = self.__dbTxn[thread.get_ident()].pop()
                    #before = self.db_env.lock_stat()['nlocks']
                    # print "rolling back a transaction", self.__dbTxn[thread.get_ident()], txn, before, self.db_env.lock_stat()['nlocks']
                    txn.abort()
                    
                    if len(self.__dbTxn[thread.get_ident()]) == 0:
                        del self.__dbTxn[thread.get_ident()]
            except IndexError, e:
                #The dbTxn for the current thread is removed to indicate that 
                #there are no active transactions for the current thread.
                del self.__dbTxn[thread.get_ident()]
            except Exception, e:
                # print "Got exception in rollback", e
                raise e
        else:
            _logger.warning("No transaction to rollback")
    
    def close(self, commit_pending_transaction=True):
        """
        Properly handles transactions explicitely (with parameter) or by default
        """
        # when closing, no new transactions are allowed
        # problem is that a thread can already have passed the test and is
        # half-way through begin_txn when close is called...
        self.__closing = True
        
        if not self.is_open():
            return
        # this should close all existing transactions, not only by this thread, 
        # uses the number of active transactions to sync on.
        if self.__dbTxn:
            # this will block for a while, depending on how long it takes 
            # before the active transactions are committed/aborted
            while self.db_env.txn_stat()['nactive'] > 0:
                active_threads = self.__dbTxn.keys()
                for t in active_threads:                    
                    if not commit_pending_transaction:    
                        self.rollback(rollback_root=True)
                    else:
                        self.commit(commit_root=True)
                
                sleep(0.1)

        # there may still be open transactions
        super(BerkeleyDB, self).close()
        
    def add(self, (subject, predicate, object_), context, quoted=False):

        @transaction
        def _add(self, (subject, predicate, object_), context, quoted, txn=None):
            Sleepycat.add(self, (subject, predicate, object_), context, quoted, txn)

        try:
            _add(self, (subject, predicate, object_), context, quoted)
        except Exception, e:
            # print "Got exception in _add: ", e
            raise e

    def remove(self, (subject, predicate, object_), context):

        @transaction
        def _remove(self, (subject, predicate, object_), context, txn=None):
            Sleepycat.remove(self, (subject, predicate, object_), context, txn=txn)

        try:
            _remove(self, (subject, predicate, object_), context)
        except Exception, e:
            # print "Got exception in _remove: ", e
            raise e
