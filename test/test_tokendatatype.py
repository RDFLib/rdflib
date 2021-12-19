import unittest

from rdflib import Literal, XSD


class TokenDatatypeTest(unittest.TestCase):
    def test1(self):
        lit2 = Literal("\two\nw", datatype=XSD.normalizedString)
        lit = Literal("\two\nw", datatype=XSD.string)
        self.assertFalse(str(lit) == str(lit2))

    def test2(self):
        lit = Literal("\tBeing a Doctor    Is\n\ta Full-Time Job\r", datatype=XSD.token)
        st = Literal("Being a Doctor Is a Full-Time Job", datatype=XSD.string)
        self.assertFalse(Literal.eq(st, lit))
        self.assertEqual(str(lit), str(st))

    def test3(self):
        lit = Literal("       hey\nthere      ", datatype=XSD.token).n3()
        self.assertTrue(lit == '"hey there"^^<http://www.w3.org/2001/XMLSchema#token>')

    def test4(self):
        lit = Literal("hey\nthere\ta tab\rcarriage return", datatype=XSD.token)
        expected = Literal("""hey there a tab carriage return""", datatype=XSD.string)
        self.assertEqual(str(lit), str(expected))

    def test_whitespace_is_collapsed_and_trailing_whitespace_is_stripped(self):
        lit = Literal(
            "\n  hey -  white  space is collapsed for xsd:token       and preceding and trailing whitespace is stripped     ",
            datatype=XSD.token,
        )
        expected = Literal(
            "hey - white space is collapsed for xsd:token and preceding and trailing whitespace is stripped",
            datatype=XSD.string,
        )
        self.assertEqual(str(lit), str(expected))


if __name__ == "__main__":
    unittest.main()
