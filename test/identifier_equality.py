import unittest

from rdflib import URIRef, BNode, Literal

from rdflib.syntax.parsers.RDFXMLHandler import CORE_SYNTAX_TERMS

class TypeCheckCase(unittest.TestCase):

    def testA(self):
        uriref = URIRef("http://example.org/")
        bnode = BNode()
        literal = Literal("http://example.org/")
        python_literal = u"http://example.org/"
        python_literal_2 = u"foo"

        self.assertEquals(uriref==literal, False)
        self.assertEquals(literal==uriref, False)
        
        self.assertEquals(uriref==python_literal, True)
        self.assertEquals(python_literal==uriref, True)
        
        self.assertEquals(literal==python_literal, True)
        self.assertEquals(python_literal==literal, True)

        self.assertEquals("foo" in CORE_SYNTAX_TERMS, False)
        self.assertEquals("http://www.w3.org/1999/02/22-rdf-syntax-ns#RDF" in CORE_SYNTAX_TERMS, True) 


if __name__ == "__main__":
    unittest.main()   


