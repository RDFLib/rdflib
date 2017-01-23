import unittest

from rdflib.term import URIRef
from rdflib.graph import Graph

s = """\
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns="http://purl.org/rss/1.0/"
 xmlns:nzgls="http://www.nzgls.govt.nz/standard/"
>
 <rdf:Seq rdf:about="http://example.org/Seq">
   <rdf:li rdf:resource="http://example.org/one" />
   <rdf:li rdf:resource="http://example.org/two" />
   <rdf:li rdf:resource="http://example.org/three" />
   <rdf:li rdf:resource="http://example.org/four" />
   <rdf:li rdf:resource="http://example.org/five_five" />
   <rdf:li rdf:resource="http://example.org/six" />
 </rdf:Seq>
</rdf:RDF>
"""



class SeqTestCase(unittest.TestCase):
    backend = 'default'
    path = 'store'

    def setUp(self):
        store = self.store = Graph(store=self.backend)
        store.open(self.path)
        store.parse(data=s)

    def tearDown(self):
        self.store.close()

    def testSeq(self):
        items = self.store.seq(URIRef("http://example.org/Seq"))
        self.assertEqual(len(items), 6)
        self.assertEqual(items[-1], URIRef("http://example.org/six"))
        self.assertEqual(items[2], URIRef("http://example.org/three"))
        # just make sure we can serialize
        self.store.serialize()

def test_suite():
    return unittest.makeSuite(SeqTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

