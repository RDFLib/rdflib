from rdflib.Store import Store
from rdflib.Store import check_subject, check_predicate, check_object

from rdflib.backends.InMemoryBackend import InMemoryBackend
from rdflib.backends.Concurrent import Concurrent


class TripleStore(Store):

    def __init__(self, location=None, backend=None):
        if backend==None:
            #backend = Concurrent(InMemoryBackend())
            backend = InMemoryBackend()
        super(TripleStore, self).__init__(backend)
        if location:
            self.load(location)

    def add(self, (subject, predicate, object)):
        check_subject(subject)
        check_predicate(predicate)
        check_object(object)
        self.backend.add((subject, predicate, object))

    def remove(self, (subject, predicate, object)):
        if subject:
            check_subject(subject)
        if predicate:
            check_predicate(predicate)
        if object:
            check_object(object)
        self.backend.remove((subject, predicate, object))        
        
    def triples(self, (subject, predicate, object)):
        if subject:
            check_subject(subject)
        if predicate:
            check_predicate(predicate)
        if object:
            check_object(object)
        for triple in self.backend.triples((subject, predicate, object)):
            yield triple

        
