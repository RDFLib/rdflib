#from rdflib.TripleStore import TripleStore
from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode
from rdflib.Namespace import Namespace
from rdflib.const import LABEL, TYPE

FOAF = Namespace("http://xmlns.com/foaf/0.1/")
foo = URIRef("foo")


from ZODB import DB
from ZODB.FileStorage import FileStorage

from rdflib.store.BTreeStore import BTreeStore
from rdflib.store.concurrent import Concurrent
from rdflib.store.type_check import TypeCheck
from rdflib.model.schema import Schema
from rdflib.syntax.loadsave import LoadSave
from rdflib.store.Resources import Resources
class TripleStore(Resources, LoadSave, Schema, TypeCheck, Concurrent, BTreeStore):
    def open(self, file):
        # setup the database
        storage = FileStorage(file)
        db = DB(storage)
        try:
            db.pack()
        except:
            pass
        self.connection = connection = db.open()
        self.set_indices(connection.root())

    def close(self):
        indices = self.connection.root()
        indices["spo"] = indices["spo"]
        indices["pos"] = indices["pos"]
        get_transaction().commit()        
        self.connection.close()
    
store = TripleStore()
store.open("store.fs")

#store.load("http://redfoot.net/2002/10/red")
#store.load("http://eikeon.com/eikeon.rdf")
store.load("http://www.w3.org/1999/02/22-rdf-syntax-ns")

#store.add(foo, foo, foo)
#store.remove(foo, foo, foo)

for s, p, o in store:
    print s==foo, s, foo
    #print s, p, o
#store.remove_triples(None, None, None)

#store.remove_triples(foo, foo, foo)
store.close()


