from unittest import TestCase
from six.moves.urllib.error import URLError

from rdflib.graph import ConjunctiveGraph

from nose import SkipTest
raise SkipTest("Suspended while test suite is being updated.")


class NonXhtmlTest(TestCase):
    """
    RDFa that is in not well-formed XHTML is passed through html5lib.
    These tests make sure that this RDFa can be processed both from
    a file, and from a URL. We can only run these tests if html5lib
    is installed. Currently html5lib isn't a dependency.
    """

    def test_url(self):
        if self.html5lib_installed():
            try:
                g = ConjunctiveGraph()
                g.parse(location='http://oreilly.com/catalog/9780596516499/',
                        format='rdfa')
                self.assertTrue(len(g), 77)
            except URLError:
                from nose import SkipTest
                raise SkipTest('No networking, test skipped')

    def test_file(self):
        if self.html5lib_installed():
            g = ConjunctiveGraph()
            g.parse(location='test/rdfa/oreilly.html', format='rdfa')
            self.assertEqual(len(g), 77)

    def html5lib_installed(self):
        try:
            import html5lib
            return True
        except:
            return False
