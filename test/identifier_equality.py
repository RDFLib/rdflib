import unittest

from rdflib.TripleStore import TripleStore
from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from rdflib.BNode import BNode

from rdflib.constants import CORE_SYNTAX_TERMS
class TypeCheckCase(unittest.TestCase):

    def testA(self):
        uriref = URIRef("http://example.org/")
        bnode = BNode()
        literal = Literal("http://example.org/")
        python_literal = u"http://example.org/"
        python_literal_2 = u"foo"

        print uriref==literal
        print literal==uriref
        
        print uriref==python_literal
        print python_literal==uriref
        
        print literal==python_literal
        print python_literal==literal

        print "---"
        print "foo" in CORE_SYNTAX_TERMS
        print "http://www.w3.org/1999/02/22-rdf-syntax-ns#RDF" in CORE_SYNTAX_TERMS
        print "??"


if __name__ == "__main__":
    unittest.main()   


