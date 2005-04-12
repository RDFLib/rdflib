import unittest

from rdflib import *
from rdflib.constants import RDFS_LABEL, DATATYPE

from rdflib import RDF

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

    def setUp(self):
        self.store = Graph()
        self.store.bind("dc", "http://http://purl.org/dc/elements/1.1/")
        self.store.bind("foaf", "http://xmlns.com/foaf/0.1/")

    def addDonna(self):
        self.donna = donna = BNode()
        self.store.add((donna, RDF.type, FOAF["Person"]))
        self.store.add((donna, FOAF["nick"], Literal("donna")))
        self.store.add((donna, FOAF["name"], Literal("Donna Fales")))

    def testRDFXML(self):
        self.addDonna()
        self.assertEquals(self.store.serialize(format="pretty-xml"), rdfxml)

def test_suite():
    return unittest.makeSuite(RDFTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
