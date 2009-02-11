import unittest

from rdflib import URIRef, Literal


class TestRelativeBase(unittest.TestCase):
    def setUp(self):
        self.x = Literal("2008-12-01T18:02:00Z",
                         datatype=URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))

    def test_equality(self):        
        self.assertEquals(self.x == self.x, True)


if __name__ == "__main__":
    unittest.main()

