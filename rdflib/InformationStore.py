"""Deprecated; use Graph."""

from rdflib import Graph
from rdflib.Namespace import Namespace

from rdflib.util import check_subject, check_predicate, check_object, check_context

INFORMATION_STORE = Namespace("http://rdflib.net/2002/InformationStore#")
CONTEXT = INFORMATION_STORE["Context"]
SOURCE = INFORMATION_STORE["source"]


class InformationStore(Graph):
    """
    Depcrecated. Use Graph instead.
    """
    
    def __init__(self, path=None, backend=None):
        if backend==None:
            backend = SleepyCatBackend()
        super(InformationStore, self).__init__(backend=backend)
        if path:
            self.open(path)
        
    def load(self, location, format="xml", publicID=None):
        location = self.absolutize(location)
        for id in self.subjects(SOURCE, location):
            context = self.get_context(id)
            self.remove_context(id)
        id = BNode()
        context = self.get_context(id)
        context.add((id, TYPE, CONTEXT))
        context.add((id, SOURCE, location))
        context.load(location, format, publicID)
        return context

            
