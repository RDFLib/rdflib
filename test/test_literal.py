import unittest

import rdflib # needed for eval(repr(...)) below


# these are actually meant for test_term.py, which is not yet merged into trunk

class TestMd5(unittest.TestCase):
    def testMd5(self):
        self.assertEqual(rdflib.URIRef("http://example.com/").md5_term_hash(),
                         "40f2c9c20cc0c7716fb576031cceafa4")
        self.assertEqual(rdflib.Literal("foo").md5_term_hash(),
                         "da9954ca5f673f8ab9ebd6faf23d1046")
    

class TestLiteral(unittest.TestCase):
    def setUp(self):
        pass

    def test_repr_apostrophe(self):        
        a = rdflib.Literal("'")
        b = eval(repr(a))
        self.assertEquals(a, b)

    def test_repr_quote(self):        
        a = rdflib.Literal('"')
        b = eval(repr(a))
        self.assertEquals(a, b)

    def test_literal_from_bool(self):
        l = rdflib.Literal(True)
        XSD_NS = rdflib.Namespace(u'http://www.w3.org/2001/XMLSchema#')
        self.assertEquals(l.datatype, XSD_NS["boolean"])

if __name__ == "__main__":
    unittest.main()

