import unittest

import rdflib
from rdflib import URIRef, Literal


class TestRelativeBase(unittest.TestCase):
    def setUp(self):
        pass

    def test_repr_apostrophe(self):        
        a = Literal("'")
        b = eval(repr(a))
        self.assertEquals(a, b)

    def test_repr_quote(self):        
        a = Literal('"')
        b = eval(repr(a))
        self.assertEquals(a, b)


if __name__ == "__main__":
    unittest.main()

