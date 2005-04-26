import unittest

from rdflib import Graph
from rdflib import URIRef, BNode, Literal, RDFS
from rdflib.StringInputSource import StringInputSource


class ParserTestCase(unittest.TestCase):        

    def testNoPathWithHash(self):
        g = Graph()
        g.parse(StringInputSource("""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
>

<rdf:Description rdf:about="http://example.org#">
  <rdfs:label>testing</rdfs:label>
</rdf:Description>
  
</rdf:RDF>
        """))
        label = g.value(URIRef("http://example.org#"), RDFS.label)        
        self.assertEquals(label, Literal("testing"))


if __name__ == "__main__":
    unittest.main()   
