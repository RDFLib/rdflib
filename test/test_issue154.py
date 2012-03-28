import sys
from StringIO import StringIO
from unittest import TestCase
from rdflib.graph import ConjunctiveGraph, URIRef
from nose.exc import SkipTest

class EntityTest(TestCase):

    def test_html_entity_xhtml(self):
        if sys.version_info[0] == 3:
            raise SkipTest('minidom parser strips HTML entities in Python 3.2')
        g = ConjunctiveGraph()
        html = \
        """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <body xmlns:dc="http://purl.org/dc/terms/">
        <p about="http://example.com" property="dc:title">Exampl&eacute;</p>
        </body>
        </html>
        """
        g.parse(StringIO(html), format='rdfa')
        self.assertEqual(len(g), 1)
        self.assertEqual(g.value(URIRef("http://example.com"), 
                                 URIRef("http://purl.org/dc/terms/title")
                                 ), u"Exampl\xe9") 





