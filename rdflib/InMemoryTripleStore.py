from rdflib.store.InMemoryStore import InMemoryStore
from rdflib.model.schema import Schema
from rdflib.syntax.loadsave import LoadSave
from rdflib.store.BackwardCompatibility import BackwardCompatibility


class InMemoryTripleStore(BackwardCompatibility,
                          LoadSave, Schema,
                          InMemoryStore):
    pass
