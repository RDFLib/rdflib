import unittest

from rdflib import *
from rdflib.StringInputSource import StringInputSource

class SeqTestCase(unittest.TestCase):

    def setUp(self):
        store = self.store = Graph()
        store.parse(StringInputSource(s))

    def testSeq(self):
        s = URIRef("http://www.ssc.govt.nz/news/news.rss")
        _items = self.store.value(s, URIRef("http://purl.org/rss/1.0/items"))
        items = self.store.seq(_items)
        self.assertEquals(len(items), 2)
        self.assertEquals(items[-1], items[1])

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
<channel rdf:about="http://www.ssc.govt.nz/news/news.rss">
 <title>State Services Commission News</title>
 <link>http://www.ssc.govt.nz/news/</link>
 <description>The State Services Commission News</description>
 <items>
   <rdf:Seq>
     <rdf:li rdf:resource="http://www.ssc.govt.nz/disability-mentoring-day" />
     <rdf:li rdf:resource="http://www.ssc.govt.nz/appt-ce-natlib-oct02" />
   </rdf:Seq>
 </items>
</channel>
<item rdf:about="http://www.ssc.govt.nz/disability-mentoring-day">
  <title>Applications invited for Disability Mentoring Day</title>
  <link>http://www.ssc.govt.nz/disability-mentoring-day</link>
  <description>The State Services Commission, through its Mainstream Employment Programme, is pleased to host the first New Zealand Disability Mentoring Day: Career Development for the 21 Century. Disability Mentoring Day will be celebrated in Wellington on Tuesday 12 November 2002.</description>
  <nzgls:date.valid>2002-10-07</nzgls:date.valid>
  <nzgls:identifier>20021007-0015-SSC</nzgls:identifier>  
  <nzgls:type.agency>State Services Commission</nzgls:type.agency>
</item>
<item rdf:about="http://www.ssc.govt.nz/appt-ce-natlib-oct02">
  <title>Appointment of National Librarian announced</title>
  <link>http://www.ssc.govt.nz/appt-ce-natlib-oct02</link>
  <description>The State Services Commissioner, Michael Wintringham, announced today the appointment of Penny Carnaby as Chief Executive of National Library of New Zealand and National Librarian...</description>
  <nzgls:date.valid>2002-10-09</nzgls:date.valid>
  <nzgls:identifier>20021009-0016-SSC</nzgls:identifier>
  <nzgls:type.agency>State Services Commission</nzgls:type.agency>
</item>
</rdf:RDF>
"""

