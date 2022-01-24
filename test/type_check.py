import unittest

from rdflib.exceptions import ObjectTypeError, PredicateTypeError, SubjectTypeError
from rdflib.graph import Graph
from rdflib.term import URIRef

foo = URIRef("foo")


class TypeCheckCase(unittest.TestCase):
    unstable = (
        True  # TODO: until we decide if we want to add type checking back to rdflib
    )
    backend = "default"
    path = "store"

    def setUp(self):
        self.store = Graph(backend=self.backend)
        self.store.open(self.path)

    def tearDown(self):
        self.store.close()

    def testSubjectTypeCheck(self):
        self.assertRaises(SubjectTypeError, self.store.add, (None, foo, foo))

    def testPredicateTypeCheck(self):
        self.assertRaises(PredicateTypeError, self.store.add, (foo, None, foo))

    def testObjectTypeCheck(self):
        self.assertRaises(ObjectTypeError, self.store.add, (foo, foo, None))
