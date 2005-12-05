import unittest

from rdflib import *
from rdflib.util import from_n3


class UtilTestCase(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()

    def tearDown(self):
        del self.graph

    def __test_from_n3(self):
        """Test that from_n3 can handle unicode."""
        a = u'"\302\251"'
        from_n3(a.encode("utf-8")) 
        #from_n3(a) 

    def test_round_trip(self):
        #a = Literal(u'A test with a unicode character, "\302\251" and a newline \n second line.') 
        a = Literal(u'A test with a newline \\n second line.') 
        #a = Literal(u'A test')
        b = from_n3(a.n3())
        self.assertEquals(a, b)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
