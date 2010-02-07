import unittest

from rdflib import Graph, Literal, URIRef


class NTTestCase(unittest.TestCase):

    def testIssue78(self):
        g = Graph()
        g.add((URIRef("foo"), URIRef("foo"), Literal(u"R\u00E4ksm\u00F6rg\u00E5s")))
        s=g.serialize(format='nt')
        self.assertEquals(type(s), str)
        self.assertTrue(r"R\u00E4ksm\u00F6rg\u00E5s" in s)


if __name__ == "__main__":
    unittest.main()
