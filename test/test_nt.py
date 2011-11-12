import unittest

from rdflib import Graph, Literal, URIRef
from rdflib.py3compat import bytestype, b

class NTTestCase(unittest.TestCase):

    def testIssue78(self):
        g = Graph()
        g.add((URIRef("foo"), URIRef("foo"), Literal(u"R\u00E4ksm\u00F6rg\u00E5s")))
        s = g.serialize(format='nt')
        self.assertEquals(type(s), bytestype)
        self.assertTrue(b(r"R\u00E4ksm\u00F6rg\u00E5s") in s)

    def testIssue146(self):
        g = Graph()
        g.add((URIRef("foo"), URIRef("foo"), Literal("test\n", lang="en")))
        s = g.serialize(format="nt").strip()
        self.assertEqual(s, b('<foo> <foo> "test\\n"@en .'))


if __name__ == "__main__":
    unittest.main()
