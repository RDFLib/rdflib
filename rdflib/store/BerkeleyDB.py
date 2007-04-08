import warnings, thread, sys

from rdflib.store import Store, VALID_STORE, CORRUPTED_STORE, NO_STORE, UNKNOWN
from rdflib.store.Sleepycat import Sleepycat
from rdflib.URIRef import URIRef
from bsddb import db
from os import mkdir, rmdir, makedirs
from os.path import exists, abspath, join
from urllib import pathname2url
from threading import Thread
from time import sleep, time
import logging

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
                #print "After rollback", e, add_txn, self.dbTxn[thread.get_ident()], thread.get_ident()
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
        self.locks = 5000

        # Each thread is responsible for a single transaction, indexed by the 
        # thread id
        self.dbTxn = {}

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

    def _init_db_environment(self, homeDir):
        #NOTE: The identifeir is appended to the path as the location for the db
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
        # can be added/removed with a single operation
        db_env.set_lk_max_locks(self.locks)
        db_env.set_lk_max_lockers(self.locks)
        db_env.set_lk_max_objects(self.locks)
        
        #db_env.set_lg_max(1024*1024)
        #db_env.set_flags(envsetflags, 1)
        db_env.open(fullDir, envflags | db.DB_CREATE,0)
        return db_env

    #Transactional interfaces
    def begin_txn(self, nested=False):
        """
        Start a bsddb transaction. 
        """
        # A user should be able to wrap several operations in a transaction.
        # For example, two or more adds when adding a graph.
        # Each internal operation should be a transaction, e.g. an add
        # must be atomic and isolated. However, since add should handle
        # BDB exceptions (like deadlock), an internal transaction should
        # not fail the user transaction. Here, nested transactions are used
        # which have this property.
        
        if not thread.get_ident() in self.dbTxn:
            self.dbTxn[thread.get_ident()] = []
            # add the new transaction to the list of transactions
            txn = self.db_env.txn_begin()
            self.dbTxn[thread.get_ident()].append(txn)
        else:
            # add a nested transaction with the top one as parent
            txn = self.db_env.txn_begin(self.dbTxn[thread.get_ident()][0])
            self.dbTxn[thread.get_ident()].append(txn)

        # return the transaction handle
        return txn
        
    def commit(self):
        """
        Bsddb tx objects cannot be reused after commit 
        """
        if thread.get_ident() in self.dbTxn:
            try:
                txn = self.dbTxn[thread.get_ident()].pop()
                _logger.debug("committing")
                before = self.db_env.lock_stat()['nlocks']
                txn.commit(0)
                #print "committing a transaction", self.dbTxn[thread.get_ident()], txn, before, self.db_env.lock_stat()['nlocks']
                if len(self.dbTxn[thread.get_ident()]) == 0:
                    del self.dbTxn[thread.get_ident()]
            except IndexError, e:
                #The dbTxn for the current thread is removed to indicate that 
                #there are no active transactions for the current thread.
                del self.dbTxn[thread.get_ident()]
            except Exception, e:
                # print "Got exception in commit", e
                raise e
        else:
            _logger.warning("No transaction to commit")

    def rollback(self):
        """
        Bsddb tx objects cannot be reused after commit
        """
        
        if thread.get_ident() in self.dbTxn:
            _logger.debug("rollingback")
            try:
                txn = self.dbTxn[thread.get_ident()].pop()
                before = self.db_env.lock_stat()['nlocks']
                # print "rolling back a transaction", self.dbTxn[thread.get_ident()], txn, before, self.db_env.lock_stat()['nlocks']
                txn.abort()
                
                if len(self.dbTxn[thread.get_ident()]) == 0:
                    del self.dbTxn[thread.get_ident()]
            except IndexError, e:
                #The dbTxn for the current thread is removed to indicate that 
                #there are no active transactions for the current thread.
                del self.dbTxn[thread.get_ident()]
            except Exception, e:
                # print "Got exception in rollback", e
                raise e
        else:
            _logger.warning("No transaction to rollback")
    
#    def close(self, commit_pending_transaction=True):
#        """
#        Properly handles transactions explicitely (with parameter) or by default
#        """
#        if not self.__open:
#            return
        # this should close all existing transactions, not only by this thread
#        if self.dbTxn:
#            if not commit_pending_transaction:
#                for t in self.dbTxn.keys():
#                    self.rollback()
#            else:
#                for t in self.dbTxn.keys():
#                    for ti in self.dbTxn[t]:
#                        self.commit() 
#        self.__open = False
#        self.__sync_thread.join()
#        for i in self.__indicies:
#            i.close()
#        self.__contexts.close()
#        self.__namespace.close()
#        self.__prefix.close()
#        self.__i2k.close()
        #self.__k2i.close()      
#        self.db_env.close()

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