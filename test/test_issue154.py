import sys
from unittest import TestCase
from rdflib.graph import ConjunctiveGraph, URIRef
from nose.exc import SkipTest

# Workaround for otherwise-dropped HTML entities

import re
from htmlentitydefs import name2codepoint
def htmlentitydecode(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint), 
            lambda m: unichr(name2codepoint[m.group(1)]), s)

class EntityTest(TestCase):

    def test_html_entity_xhtml(self):
        if sys.version_info[0] == 3 or sys.version_info[:2] < (2,5):
            raise SkipTest('minidom parser strips HTML entities in Python 3.2')
        g1 = ConjunctiveGraph()
        html = \
        """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <body xmlns:dc="http://purl.org/dc/terms/">
        <p about="http://example.com" property="dc:title">Exampl&eacute;</p>
        </body>
        </html>
        """
        g1.parse(data=html, format='rdfa')
        self.assertEqual(len(g1), 1)
        self.assertEqual(g1.value(URIRef("http://example.com"), 
                                  URIRef("http://purl.org/dc/terms/title")
                                  ), u"Exampl") 
        g2 = ConjunctiveGraph()
        g2.parse(data=htmlentitydecode(html), format='rdfa')
        self.assertEqual(len(g2), 1)
        self.assertEqual(g2.value(URIRef("http://example.com"), 
                                  URIRef("http://purl.org/dc/terms/title")
                                  ), u"Exampl\xe9") 





