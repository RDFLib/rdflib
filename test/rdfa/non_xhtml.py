from unittest import TestCase

from rdflib.graph import ConjunctiveGraph

class NonXhtmlTest(TestCase):
    """
    RDFa that is in not well-formed XHTML is passed through html5lib. 
    These tests make sure that this RDFa an be processed both from 
    a file, and from a URL.
    """

    def test_url(self):
        g = ConjunctiveGraph()
        g.parse(location='http://oreilly.com/catalog/9780596516499/',
                format='rdfa', 
                lax=True)
        self.assertTrue(len(g) > 0)

    def test_file(self):
        g = ConjunctiveGraph()
        g.parse(location='test/rdfa/oreilly.html',
                format='rdfa',
                lax=True)
        self.assertEqual(len(g), 77)
