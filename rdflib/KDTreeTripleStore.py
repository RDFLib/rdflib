from __future__ import generators

from rdflib.store.AbstractTripleStore import AbstractTripleStore
from rdflib.store.KDTreeStore import KDTreeStore
from rdflib.store.Concurrent import Concurrent
from rdflib.store.TypeCheck import TypeCheck
from rdflib.model.schema import Schema
from rdflib.syntax.loadsave import LoadSave
from rdflib.store.BackwardCompatibility import BackwardCompatibility


class KDTreeTripleStore(BackwardCompatibility,
                          LoadSave, Schema,
                          TypeCheck, Concurrent,
                          KDTreeStore, AbstractTripleStore):
    pass
