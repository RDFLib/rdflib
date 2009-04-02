import unittest

from rdflib.term import BNode
from rdflib.term import Literal
from rdflib.namespace import Namespace
from rdflib.graph import Graph
from rdflib.namespace import RDF

FOAF = Namespace("http://xmlns.com/foaf/0.1/")


rdfxml = """\
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:xml='http://www.w3.org/XML/1998/namespace'
  xmlns:foaf='http://xmlns.com/foaf/0.1/'
  xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  xmlns:dc='http://http://purl.org/dc/elements/1.1/'
  xmlns:rdfs='http://www.w3.org/2000/01/rdf-schema#'
>
  <foaf:Person>
    <foaf:name>Donna Fales</foaf:name>
    <foaf:nick>donna</foaf:nick>
  </foaf:Person>
</rdf:RDF>"""

class RDFTestCase(unittest.TestCase):
    backend = 'default'
    path = 'store'

    def setUp(self):
        self.store = Graph(store=self.backend)
        self.store.open(self.path)
        self.store.bind("dc", "http://http://purl.org/dc/elements/1.1/")
        self.store.bind("foaf", "http://xmlns.com/foaf/0.1/")

    def tearDown(self):
        self.store.close()

    def addDonna(self):
        self.donna = donna = BNode()
        self.store.add((donna, RDF.type, FOAF["Person"]))
        self.store.add((donna, FOAF["nick"], Literal("donna")))
        self.store.add((donna, FOAF["name"], Literal("Donna Fales")))

    def testRDFXML(self):
        self.addDonna()
        g = Graph()
        g.parse(data=self.store.serialize(format="pretty-xml"))
        self.assertEquals(self.store.isomorphic(g), True)

def test_suite():
    return unittest.makeSuite(RDFTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
