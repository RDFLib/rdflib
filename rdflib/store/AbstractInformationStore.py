from __future__ import generators

from rdflib.store.AbstractTripleStore import AbstractTripleStore
from rdflib.model.schema import Schema
from rdflib.syntax.loadsave import LoadSave
from rdflib.BNode import BNode


class InformationStoreBacked(object):
    def add(self, (s, p, o)):
        self.information_store.add((s, p, o), self.identifier)
    def remove(self, (s, p, o)):        
        self.information_store.remove((s, p, o), self.identifier)
    def triples(self, triple):
        for triple in self.information_store.triples(triple, self.identifier):
            yield triple
    

class ContextStore(LoadSave, Schema,
                   InformationStoreBacked, AbstractTripleStore):

    def __init__(self, information_store, identifier):
        super(ContextStore, self).__init__()
        self.information_store = information_store
        self.identifier = identifier


class AbstractInformationStore(AbstractTripleStore):

    def __init__(self):
        super(AbstractInformationStore, self).__init__()
        self.__context = None
        
    def __get_context(self):
        if self.__context==None:            
            self.__context = BNode()
        return self.__context

    def __set_context(self, context):
        self.__context = context

    # Declare context as a property of AbstractInformationStore
    context = property(__get_context, __set_context)

    def get_context(self, identifier):
        return ContextStore(self, identifier)
    
    def load(self, source, context=None):
        context = context or self.context
        store = ContextStore(self, context)
        store.load(source)
        return store

