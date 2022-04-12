import unittest

from rdflib import Literal
from rdflib.namespace import XSD


class NormalizedStringTest(unittest.TestCase):
    def test1(self):
        lit2 = Literal("\two\nw", datatype=XSD.normalizedString)
        lit = Literal("\two\nw", datatype=XSD.string)
        self.assertFalse(str(lit) == str(lit2))

    def test2(self):
        lit = Literal(
            "\tBeing a Doctor Is\n\ta Full-Time Job\r", datatype=XSD.normalizedString
        )
        st = Literal(" Being a Doctor Is  a Full-Time Job ", datatype=XSD.string)
        self.assertFalse(Literal.eq(st, lit))
        self.assertEqual(str(lit), str(st))

    def test3(self):
        lit = Literal("hey\nthere", datatype=XSD.normalizedString).n3()
        self.assertTrue(
            lit == '"hey there"^^<http://www.w3.org/2001/XMLSchema#normalizedString>'
        )

    def test4(self):
        lit = Literal(
            "hey\nthere\ta tab\rcarriage return", datatype=XSD.normalizedString
        )
        expected = Literal("""hey there a tab carriage return""", datatype=XSD.string)
        self.assertEqual(str(lit), str(expected))


if __name__ == "__main__":
    unittest.main()
