from __future__ import generators


from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.constants import TYPE
from rdflib.util import first

UNAMBIGUOUSPROPERTY = URIRef("http://www.daml.org/2001/03/daml+oil#UnambiguousProperty")


class Resource(object):

    def __init__(self, subject, store=None):
        super(Resource, self).__init__(subject)
        self.id = subject
        self.subjects = [subject, ]
        self.store = store
        self._update()
        
    def _update(self):
        for p in self.store.subjects(TYPE, UNAMBIGUOUSPROPERTY):
            for o in self.store.objects(self.subjects[0], p):
                for s in self.store.subjects(p, o):
                    if not s in self.subjects:
                        self.subjects.append(s)
        
    def __getitem__(self, predicate):
        for subject in self.subjects:
            for object in self.store.objects(subject, predicate):
                return object
        return None

    def get(self, predicate, default=None):
        value = self.__getitem__(predicate)
        if value==None:
            return default
        else:
            return value

    def __setitem__(self, predicate, object):
        for subject in self.subjects:
            self.store.remove_triples((subject, predicate, None))
        self.store.add((self.subjects[0], predicate, object))

    def objects(self, predicate):
        for subject in self.subjects:
            for object in self.store.objects(subject, predicate):
                yield object

    def add(self, predicate, value):
        self.store.add((self.subjects[0], self.predicate, value))

    def remove(self, predicate, value):
        for subject in self.subjects:
            self.store.remove((subject, self.predicate, value))

    
