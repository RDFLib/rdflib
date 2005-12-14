from rdflib.store import Store
from pprint import pprint
import threading

destructiveOpLocks = {
    'add':None,
    'remove':None,
}
        
class RemoveQuad:
    def __init__(self,(s,p,o,c)):
        self.subject   = s
        self.predicate = p
        self.obj       = o
        self.context   = c
        
    def __repr__(self):
        return "<RemoveQuad: subject=%s, predicate=%s, object=%s,context=%s>"%(self.subject,self.predicate,self.obj,self.context)
        
class AddQuad:
    def __init__(self,(s,p,o,c)):
        self.subject   = s
        self.predicate = p
        self.obj       = o
        self.context   = c
        
    def __repr__(self):
        return "<AddQuad: subject=%s, predicate=%s, object=%s,context=%s>"%(self.subject,self.predicate,self.obj,self.context)

class AuditableStorage(Store):
    def __init__(self, storage):
        self.storage = storage
        self.context_aware = storage.context_aware
        #NOTE: this store can't be formula_aware as it doesn't have enough info to reverse
        #The removal of a quoted statement
        self.formula_aware = False#storage.formula_aware
        self.transaction_aware = True #This is only half true
        self.reverseOps = []
        self.rollbackLock = threading.RLock()
        
    def open(self, configuration, create=True):
        return self.storage.open(configuration,create)
    
    def close(self, commit_pending_transaction=False):
        self.storage.close()
    
    def destroy(self, configuration):
        self.storage.destroy(configuration)
    
    def add(self, (subject, predicate, object_), context, quoted=False):
        #print "add((%s, %s, %s), %s)"%(subject,predicate,object_,context)
        lock = destructiveOpLocks['add']
        lock = lock and lock or threading.RLock()
        lock.acquire()
        self.reverseOps.append(RemoveQuad((subject,predicate,object_,context)))
        self.storage.add((subject, predicate, object_), context, quoted)
        lock.release()
    
    def remove(self, (subject, predicate, object_), context=None):
        #print "remove((%s, %s, %s), %s)"%(subject,predicate,object_,context)
        lock = destructiveOpLocks['remove']
        lock = lock and lock or threading.RLock()
        lock.acquire()
        #Need to determine which quads will be removed if any term is a wildcard
        if None in [subject,predicate,object_,context]:
            for (s,p,o),cg in self.storage.triples((subject,predicate,object_),context):
                for ctx in cg:
                    self.reverseOps.append(AddQuad((s,p,o,ctx)))
        else:
            self.reverseOps.append(AddQuad((subject,predicate,object_,context)))
        self.storage.remove((subject,predicate,object_),context)
        lock.release()
    
    def triples(self, (subject, predicate, object_), context=None):
        return self.storage.triples((subject, predicate, object_), context)
    
    def __len__(self, context=None):
        return self.storage.__len__(context)
    
    def contexts(self, triple=None):
        return self.storage.contexts(triple)
    
    def remove_context(self, identifier):
        self.storage.remove_context(identifier)
    
    def bind(self, prefix, namespace):
        self.storage.bind(prefix, namespace)
    
    def prefix(self, namespace):
        return self.prefix(namespace)
    
    def namespace(self, prefix):
        return self.storage.namespace(prefix)
    
    def namespaces(self):
        return self.storage.namespaces()
    
    def commit(self):
        self.storage.commit()
    
    def rollback(self):
        #Aquire Rollback lock and apply reverse operations in the forward order
        self.rollbackLock.acquire()
        #print "Before: "
        #for triple in self.storage.triples((None,None,None),None):
        #    print triple
        #print "Rollbacks: "
        #pprint(self.reverseOps)
        for revOp in self.reverseOps:
            if isinstance(revOp,AddQuad):
                #print "Adding "
                #print (revOp.subject,revOp.predicate,revOp.obj,revOp.context)
                self.storage.add((revOp.subject,revOp.predicate,revOp.obj),revOp.context)
            else:
                #print "Removing "
                #print (revOp.subject,revOp.predicate,revOp.obj,revOp.context)
                self.storage.remove((revOp.subject,revOp.predicate,revOp.obj),revOp.context)
                
        self.reverseOps = []
        #print "After: "
        #for triple in self.storage.triples((None,None,None),None):
        #    print triple
        self.rollbackLock.release()