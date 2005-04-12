# Alias for backward compat.
from rdflib import Graph

from rdflib.backends import Memory

class TripleStore(Graph):

    def __init__(self, location=None, backend=None):
        if backend==None:
            backend = Memory()
        super(TripleStore, self).__init__(backend=backend)
        if location:
            self.load(location)
    
    def prefix_mapping(self, prefix, namespace):
        self.bind(prefix, namespace)

