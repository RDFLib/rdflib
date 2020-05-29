from rdflib import *
import unittest

class test_normalisedString(unittest.TestCase):
    def test1(self):
        lit2 = Literal("\two\nw", datatype=XSD.normalizedString)
        lit = Literal("\two\nw", datatype=XSD.string)
        self.assertEqual(lit == lit2, False)

    def test2(self):
        lit = Literal("\tBeing a Doctor Is\n\ta Full-Time Job\r", datatype=XSD.normalizedString)
        st = Literal(" Being a Doctor Is  a Full-Time Job ", datatype=XSD.string)
        self.assertFalse(Literal.eq(st,lit))

    def test3(self):
        lit=Literal("hey\nthere", datatype=XSD.normalizedString).n3()
        print(lit)
        self.assertTrue(lit=="\"hey there\"^^<http://www.w3.org/2001/XMLSchema#normalizedString>")



if __name__ == "__main__":
    unittest.main()