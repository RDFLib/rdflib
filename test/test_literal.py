import unittest

import rdflib # needed for eval(repr(...)) below
from rdflib.term import Literal

# these are actually meant for test_term.py, which is not yet merged into trunk
from rdflib.term import URIRef
class TestMd5(unittest.TestCase):
    def testMd5(self):
        self.assertEqual(URIRef("http://example.com/").md5_term_hash(),
                         "40f2c9c20cc0c7716fb576031cceafa4")
        self.assertEqual(Literal("foo").md5_term_hash(),
                         "da9954ca5f673f8ab9ebd6faf23d1046")
    

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

