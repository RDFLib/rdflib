import unittest, time
from context import ContextTestCase
from graph import GraphTestCase
from rdflib import URIRef, Literal, ConjunctiveGraph
from threading import Thread, currentThread
from random import random
from tempfile import mkdtemp

def random_uri():
    return URIRef(str(random()))

def worker_add(performed_ops, graph, num_ops, input=[]):
    t1 = time.time()
    #print "thread: %s started" % currentThread().getName()
    for i in range(0, num_ops):
        #print "id: %s, thread: %s" % (i, currentThread().getName())
        try:
            s = random_uri()
            p = random_uri()
            o = random_uri()
            graph.add((s,p,o))
            performed_ops.append((s,p,o))
        except Exception, e:
            print "could not perform op", e
            raise e
            
    print "%s triples, add time: %.4f, thread: %s" % (num_ops, (time.time() - t1), currentThread().getName())

def worker_remove(performed_ops, graph, num_ops, input=[]):
    t1 = time.time()
    #print "thread: %s started" % currentThread().getName()
    for i in range(0, num_ops):
        #print "id: %s, thread: %s" % (i, currentThread().getName())
        try:
            try:
                s,p,o = input.pop()
            except:
                s = random_uri()
                p = random_uri()
                o = random_uri()
                
            graph.remove((s,p,o))
            performed_ops.append((s,p,o))
        except Exception, e:
            raise e
            #print "could not perform op", e
            
    print "remove time: %.4f, thread: %s" % ((time.time() - t1), currentThread().getName())

class TestBDBGraph(GraphTestCase):
    store_name = "BerkeleyDB"

class TestBDBContext(ContextTestCase):
    store = "BerkeleyDB"

class TestBDBTransactions(unittest.TestCase):

    slowtest = True

    def setUp(self):
        self.graph = ConjunctiveGraph(store="BerkeleyDB")
        self.path = mkdtemp()
        self.graph.open(self.path, create=True)
                    
    def tearDown(self):
        self.graph.close()

    def get_context(self, identifier):
        assert isinstance(identifier, URIRef) or \
               isinstance(identifier, BNode), type(identifier)
        return Graph(store=self.graph.store, identifier=identifier,
                         namespace_manager=self)

    def __manyOpsManyThreads(self, worker, workers=10, triples=1000, input=[]):
        all_ops = []
        
        pool = []
        for i in range(0, workers):
            t = Thread(target=worker, args=(all_ops, self.graph, triples), kwargs={'input':input})
            pool.append(t)
            t.start()

        for t in pool:
            t.join()

        return all_ops
    
    def testAddManyManyThreads(self):
        # TODO: sometimes this test leads to TypeError exceptions?
        w = 4
        t = 1000
        self.__manyOpsManyThreads(worker_add, workers=w, triples=t)
        #print "graph size after finish: ", len(self.graph)
        self.failUnless(len(self.graph) == w*t)
    
    def testRemove(self):
        ops = self.__manyOpsManyThreads(worker_add, workers=1, triples=10)
        self.__manyOpsManyThreads(worker_remove, workers=1, triples=7, input=ops)
        #print "graph size after finish: ", len(self.graph)
        self.failUnless(len(self.graph) == 3)

    def testRemoveAll(self):
        ops = self.__manyOpsManyThreads(worker_add, workers=1, triples=10)
        
        try:
            self.graph.remove((None, None, None))
        except Exception, e:
            #print "Could not remove all: ", e
            raise e
            
        #print "graph size after finish: ", len(self.graph)
        self.failUnless(len(self.graph) == 0)

    def testReadWrite(self):
        triples = 1000
        
        def _worker_transaction():
#            self.graph.store.begin_txn()
            try:
                worker_add([], self.graph, triples)
#                self.graph.store.commit()
            except Exception, e:
                print "got exc: ", e
#                self.graph.store.rollback()
            
        def _read():
            self.graph.store.begin_txn()
            try:
                res = [r for r in self.graph.triples((None, None, None))]
                self.graph.store.commit()
            except Exception, e:
                print "got exc: ", e
                self.graph.store.rollback()
            
        add_t = Thread(target=_worker_transaction)
        read_t = Thread(target=_read)
        
        add_t.start()
        time.sleep(0.1)
        
        read_t.start()
        
        add_t.join()
        read_t.join()

    def testAddUserTransaction(self):
        workers = 2
        triples = 2000
        
        def _worker():
            t1 = time.time()
            success = False
            delay = 1
            
            while not success:
                txn = self.graph.store.begin_txn()                
                try:
                    #print "thread: %s started, txn: %s" % (currentThread().getName(), txn)
                    retry = False
                    for i in range(0, triples):
                        s = random_uri()
                        p = random_uri() 
                        o = random_uri()
                            
                        self.graph.add((s,p,o))
                        #print "triple: %s, thread: %s" % (i, currentThread().getName())
                except Exception, e:
                    #print "could not complete transaction: ", e, delay                   
                    self.graph.store.rollback()
                    time.sleep(0.1*delay)
                    delay = delay << 1
                else:
                    self.graph.store.commit()
                    success = True
                
            print "%s triples add time: %.4f, thread: %s" % (triples, (time.time() - t1), currentThread().getName())

        pool = []
        for i in range(0, workers):
            t = Thread(target=_worker)
            pool.append(t)
            t.start()

        for t in pool:
            t.join()

#        print "graph size after finish: ", len(self.graph)
        self.failUnless(len(self.graph) == workers*triples)

    def testCloseCommit(self):
        triples = 1000
        
        def _worker_transaction():
            self.graph.store.begin_txn()
            try:
                worker_add([], self.graph, triples)
                self.graph.store.commit()
            except Exception, e:
                print "got exc: ", e
                self.graph.store.rollback()
            
        def _close():
            self.graph.store.close(commit_pending_transaction=True)
            
        add_t = Thread(target=_worker_transaction)
        close_t = Thread(target=_close)
        
        add_t.start()
        time.sleep(0.5)
        
        close_t.start()
        
        add_t.join()
        print "add finished"
        close_t.join()
        print "close finished"
        #self.graph.open(self.path, create=False)
        #print "store length: ", len(self.graph)
        
        #self.failUnless()
        
    def testCloseOpen(self):
        # setUp opened
        self.graph.store.close()
        self.graph.store.open(self.path, create=False)
        
if __name__ == "__main__":
    bdb_suite = unittest.TestSuite()
    bdb_suite.addTest(TestBDBTransactions('testAddManyManyThreads'))
    bdb_suite.addTest(TestBDBTransactions('testAddUserTransaction'))
    bdb_suite.addTest(TestBDBTransactions('testRemove'))
    bdb_suite.addTest(TestBDBTransactions('testRemoveAll'))
    bdb_suite.addTest(TestBDBTransactions('testCloseCommit'))
    bdb_suite.addTest(TestBDBTransactions('testCloseOpen'))
    bdb_suite.addTest(TestBDBTransactions('testReadWrite'))

    context_suite = unittest.TestSuite()    
    context_suite.addTest(TestBDBContext('testAdd'))
    context_suite.addTest(TestBDBContext('testRemove'))
    context_suite.addTest(TestBDBContext('testLenInOneContext'))
    context_suite.addTest(TestBDBContext('testLenInMultipleContexts'))
    context_suite.addTest(TestBDBContext('testConjunction'))
    context_suite.addTest(TestBDBContext('testRemoveInMultipleContexts'))
    context_suite.addTest(TestBDBContext('testContexts'))
    context_suite.addTest(TestBDBContext('testRemoveContext'))
    context_suite.addTest(TestBDBContext('testRemoveAny'))
    context_suite.addTest(TestBDBContext('testTriples'))
    context_suite.addTest(TestBDBContext('testContexts'))        

    graph_suite = unittest.TestSuite()
    graph_suite.addTest(TestBDBGraph('testAdd'))
    graph_suite.addTest(TestBDBGraph('testRemove'))
    graph_suite.addTest(TestBDBGraph('testTriples'))
    graph_suite.addTest(TestBDBGraph('testStatementNode'))
    graph_suite.addTest(TestBDBGraph('testGraphValue'))
    graph_suite.addTest(TestBDBGraph('testConnected'))
       
    unittest.TextTestRunner(verbosity=2).run(graph_suite)
    unittest.TextTestRunner(verbosity=2).run(context_suite)
    unittest.TextTestRunner(verbosity=2).run(bdb_suite)
    
#    unittest.main()    
