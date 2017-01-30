import sys
import platform
import warnings
from unittest import TestCase
from rdflib.graph import ConjunctiveGraph, URIRef

from six import unichr
from six.moves.html_entities import name2codepoint

from nose.exc import SkipTest
# Workaround for otherwise-dropped HTML entities

import re


def htmlentitydecode(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint),
            lambda m: unichr(name2codepoint[m.group(1)]), s)

html = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" \
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<body xmlns:dc="http://purl.org/dc/terms/">
<p about="http://example.com" property="dc:title">Exampl&eacute;</p>
</body>
</html>"""


class EntityTest(TestCase):

    def test_html_entity_xhtml(self):
        if sys.version_info[0] == 3:
            raise SkipTest('minidom parser strips HTML entities in Python 3.2')
        if platform.system() == "Java":
            raise SkipTest('problem with HTML entities for html5lib in Jython')
        g = ConjunctiveGraph()
        warnings.simplefilter('ignore', UserWarning)
        g.parse(data=html, format='rdfa')
        self.assertEqual(len(g), 1)
        self.assertTrue(g.value(URIRef("http://example.com"),
                                 URIRef("http://purl.org/dc/terms/title")
                                 ).eq(u"Exampl"))

    def test_html_decoded_entity_xhtml(self):
        if sys.version_info[0] == 3:
            raise SkipTest('html5lib not yet available for Python 3')
        if platform.system() == "Java":
            raise SkipTest('problem with HTML entities for html5lib in Jython')
        g = ConjunctiveGraph()
        g.parse(data=htmlentitydecode(html), format='rdfa')
        self.assertEqual(len(g), 1)
        self.assertTrue(g.value(URIRef("http://example.com"),
                                  URIRef("http://purl.org/dc/terms/title")
                                  ).eq(u"Exampl\xe9"))
