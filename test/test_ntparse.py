import unittest
import logging
import os
import re
from rdflib import Graph, Literal, URIRef
from rdflib.plugins.parsers import ntriples
from rdflib.py3compat import bytestype, b
log = logging.getLogger(__name__)

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

    def test_sink(self):
        s = ntriples.Sink()
        self.assert_(s.length == 0)
        s.triple(None, None, None)
        self.assert_(s.length == 1)

    def test_nonvalidating_unquote(self):
        safe = b("""<http://example.org/alice/foaf.rdf#me> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> <http://example.org/alice/foaf1.rdf> .""")
        ntriples.validate = False
        res = ntriples.unquote(safe)
        self.assert_(isinstance(res, unicode))

    def test_validating_unquote(self):
        quot = b("""<http://example.org/alice/foaf.rdf#me> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> <http://example.org/alice/foaf1.rdf> .""")
        ntriples.validate = True
        res = ntriples.unquote(quot)
        log.debug("restype %s" % type(res))

    def test_validating_unquote_raises(self):
        ntriples.validate = True
        uniquot = b("""<http://www.w3.org/People/Berners-Lee/card#cm> <http://xmlns.com/foaf/0.1/name> "R\\u00E4ksm\\u00F6rg\\u00E5s" <http://www.w3.org/People/Berners-Lee/card> .""")
        self.assertRaises(ntriples.ParseError, ntriples.unquote, uniquot)
        uniquot = b("""<http://www.w3.org/People/Berners-Lee/card#cm> <http://xmlns.com/foaf/0.1/name> "R\\\\u00E4ksm\\u00F6rg\\u00E5s" <http://www.w3.org/People/Berners-Lee/card> .""")
        self.assertRaises(ntriples.ParseError, ntriples.unquote, uniquot)

    def test_nonvalidating_uriquote(self):
        ntriples.validate = False
        safe = """<http://example.org/alice/foaf.rdf#me> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> <http://example.org/alice/foaf1.rdf> ."""
        res = ntriples.uriquote(safe)
        self.assert_(res == safe)

    def test_validating_uriquote(self):
        ntriples.validate = True
        uniquot = """<http://www.w3.org/People/Berners-Lee/card#cm> <http://xmlns.com/foaf/0.1/name> "R\\u00E4ksm\\u00F6rg\\u00E5s" <http://www.w3.org/People/Berners-Lee/card> ."""
        res = ntriples.uriquote(uniquot)
        self.assertEqual(res, uniquot)

    def test_NTriplesParser_fpath(self):
        fpath = "test/nt/"+os.listdir('test/nt')[0]
        p = ntriples.NTriplesParser()
        self.assertRaises(ntriples.ParseError, p.parse, fpath)

    def test_NTriplesParser_parsestring(self):
        p = ntriples.NTriplesParser()
        data = 3
        self.assertRaises(ntriples.ParseError, p.parsestring, data)
        fname = "test/nt/lists-02.nt"
        print fname
        data = open(fname, 'r').read()
        p = ntriples.NTriplesParser()
        res = p.parsestring(data)
        self.assert_(res == None)

    def test_w3_ntriple_variants(self):
        uri = "file:///"+os.getcwd()+"/test/nt/test.ntriples"
        import urllib
        parser = ntriples.NTriplesParser()
        u = urllib.urlopen(uri)
        sink = parser.parse(u)
        u.close()
        # ATM we are only really interested in any exceptions thrown
        self.assert_(sink is not None)

    def test__no_EOF(self):
        data = '''<http://example.org/resource32> <http://example.org/property> <http://example.org/datatype1> .'''
        p = ntriples.NTriplesParser()
        self.assertRaises(ntriples.ParseError, p.parsestring, data)

    def test_bad_line(self):
        data = '''<http://example.org/resource32> 3 <http://example.org/datatype1> .\n'''
        p = ntriples.NTriplesParser()
        self.assertRaises(ntriples.ParseError, p.parsestring, data)

    def test_cover_eat(self):
        data = '''<http://example.org/resource32> 3 <http://example.org/datatype1> .\n'''
        p = ntriples.NTriplesParser()
        p.line = data
        self.assertRaises(ntriples.ParseError, p.eat, re.compile('<http://example.org/datatype1>'))

    def test_cover_subjectobjectliteral(self):
        # data = '''<http://example.org/resource32> 3 <http://example.org/datatype1> .\n'''
        p = ntriples.NTriplesParser()
        p.line = b("baz")
        self.assertRaises(ntriples.ParseError, p.subject)
        self.assertRaises(ntriples.ParseError, p.object)
        # p.line = '"baz"@fr^^<http://example.org/datatype1>'
        # self.assertRaises(ntriples.ParseError, p.literal)

def check_nt_parse(fpath, fmt):
    fp = open(fpath, 'rb')
    p = ntriples.NTriplesParser(sink=ntriples.Sink()) 
    sink = p.parse(fp) # file; use parsestring for a string
    fp.close() 
    assert(sink is not None)

def _get_test_files_formats():
    for f in os.listdir('test/nt'):
        fpath = "test/nt/"+f
        if f.endswith('.rdf'):
            yield fpath, 'xml'
        elif f.endswith('.nt'):
            yield fpath, 'nt'

def test_all_nt_serialize():
    skiptests = [
        # http://inamidst.com/sw/n3p/test/
        'test/nt/anons-02.nt',
        'test/nt/anons-03.nt',
        'test/nt/formulae-01.nt',
        'test/nt/formulae-02.nt',
        'test/nt/formulae-03.nt',
        'test/nt/formulae-05.nt',
        'test/nt/formulae-06.nt',
        'test/nt/formulae-10.nt',
        'test/nt/keywords-08.nt',
        'test/nt/lists-06.nt',
        'test/nt/literals-01.nt',
        'test/nt/numeric-01.nt',
        'test/nt/numeric-02.nt',
        'test/nt/numeric-03.nt',
        'test/nt/numeric-04.nt',
        'test/nt/numeric-05.nt',
        'test/nt/paths-04.nt',
        'test/nt/paths-06.nt',
        'test/nt/qname-01.nt',
        ]
    for fpath, fmt in _get_test_files_formats():
        if fpath in skiptests:
            log.debug("Skipping %s, known issue" % fpath)
        else:
            yield check_nt_parse, fpath, fmt

if __name__ == "__main__":
    unittest.main()

