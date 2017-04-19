import unittest
import logging
import os
import re
from rdflib import Graph, Literal, URIRef
from rdflib.plugins.parsers import ntriples
from six import binary_type, text_type, b
from six.moves.urllib.request import urlopen

log = logging.getLogger(__name__)

class NTTestCase(unittest.TestCase):

    def testIssue78(self):
        g = Graph()
        g.add((URIRef("foo"), URIRef("foo"), Literal(u"R\u00E4ksm\u00F6rg\u00E5s")))
        s = g.serialize(format='nt')
        self.assertEqual(type(s), binary_type)
        self.assertTrue(b(r"R\u00E4ksm\u00F6rg\u00E5s") in s)

    def testIssue146(self):
        g = Graph()
        g.add((URIRef("foo"), URIRef("foo"), Literal("test\n", lang="en")))
        s = g.serialize(format="nt").strip()
        self.assertEqual(s, b('<foo> <foo> "test\\n"@en .'))

    def test_sink(self):
        s = ntriples.Sink()
        self.assertTrue(s.length == 0)
        s.triple(None, None, None)
        self.assertTrue(s.length == 1)

    def test_nonvalidating_unquote(self):
        safe = """<http://example.org/alice/foaf.rdf#me> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> <http://example.org/alice/foaf1.rdf> ."""
        ntriples.validate = False
        res = ntriples.unquote(safe)
        self.assertTrue(isinstance(res, text_type))

    def test_validating_unquote(self):
        quot = """<http://example.org/alice/foaf.rdf#me> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> <http://example.org/alice/foaf1.rdf> ."""
        ntriples.validate = True
        res = ntriples.unquote(quot)
        # revert to default
        ntriples.validate = False
        log.debug("restype %s" % type(res))

    def test_validating_unquote_raises(self):
        ntriples.validate = True
        uniquot = """<http://www.w3.org/People/Berners-Lee/card#cm> <http://xmlns.com/foaf/0.1/name> "R\\u00E4ksm\\u00F6rg\\u00E5s" <http://www.w3.org/People/Berners-Lee/card> ."""
        self.assertRaises(ntriples.ParseError, ntriples.unquote, uniquot)
        uniquot = """<http://www.w3.org/People/Berners-Lee/card#cm> <http://xmlns.com/foaf/0.1/name> "R\\\\u00E4ksm\\u00F6rg\\u00E5s" <http://www.w3.org/People/Berners-Lee/card> ."""
        self.assertRaises(ntriples.ParseError, ntriples.unquote, uniquot)
        # revert to default
        ntriples.validate = False

    def test_nonvalidating_uriquote(self):
        ntriples.validate = False
        safe = """<http://example.org/alice/foaf.rdf#me> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> <http://example.org/alice/foaf1.rdf> ."""
        res = ntriples.uriquote(safe)
        self.assertTrue(res == safe)

    def test_validating_uriquote(self):
        ntriples.validate = True
        uniquot = """<http://www.w3.org/People/Berners-Lee/card#cm> <http://xmlns.com/foaf/0.1/name> "R\\u00E4ksm\\u00F6rg\\u00E5s" <http://www.w3.org/People/Berners-Lee/card> ."""
        res = ntriples.uriquote(uniquot)
        # revert to default
        ntriples.validate = False
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
        with open(fname, 'r') as f:
            data = f.read()
        p = ntriples.NTriplesParser()
        res = p.parsestring(data)
        self.assertTrue(res == None)

    def test_w3_ntriple_variants(self):
        uri = "file:///"+os.getcwd()+"/test/nt/test.ntriples"

        parser = ntriples.NTriplesParser()
        u = urlopen(uri)
        sink = parser.parse(u)
        u.close()
        # ATM we are only really interested in any exceptions thrown
        self.assertTrue(sink is not None)

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
        p.line = "baz"
        self.assertRaises(ntriples.ParseError, p.subject)
        self.assertRaises(ntriples.ParseError, p.object)
        # p.line = '"baz"@fr^^<http://example.org/datatype1>'
        # self.assertRaises(ntriples.ParseError, p.literal)


if __name__ == "__main__":
    unittest.main()
