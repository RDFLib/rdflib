import unittest

from rdflib import *
from rdflib.StringInputSource import StringInputSource

class SeqTestCase(unittest.TestCase):

    def setUp(self):
        store = self.store = Graph()
        store.parse(StringInputSource(s))

    def testSeq(self):
        items = self.store.seq(URIRef("http://example.org/Seq"))
        self.assertEquals(len(items), 4)
        self.assertEquals(items[-1], URIRef("http://example.org/four"))
        self.assertEquals(items[2], URIRef("http://example.org/three"))        

def test_suite():
    return unittest.makeSuite(SeqTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

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
 </rdf:Seq>
</rdf:RDF>
"""

