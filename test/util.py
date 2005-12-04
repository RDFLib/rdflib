import unittest

from rdflib import *
from rdflib.util import from_n3


class UtilTestCase(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()

    def tearDown(self):
        del self.graph

    def test_from_n3(self):
        """Test that from_n3 can handle unicode."""
        from_n3(u'"\302\251"') 

def test_suite():
    return unittest.makeSuite(UtilTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
