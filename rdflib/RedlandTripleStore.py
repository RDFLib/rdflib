from __future__ import generators

from rdflib.store.AbstractTripleStore import AbstractTripleStore
from rdflib.store.RedlandStore import RedlandStore
from rdflib.store.Concurrent import Concurrent
from rdflib.store.TypeCheck import TypeCheck
from rdflib.model.schema import Schema
from rdflib.syntax.loadsave import LoadSave
from rdflib.store.BackwardCompatibility import BackwardCompatibility


class RedlandTripleStore(BackwardCompatibility,
                          LoadSave, Schema,
                          TypeCheck, Concurrent,
                          RedlandStore, AbstractTripleStore):
    def __init__(self, **args):
        """Create a wrapper over a Redland Model.  Use the keyword
        arguments to initialize the redland storage backing the model.
        """
        super(RedlandTripleStore, self).__init__()
        apply(self.open, [], args)

