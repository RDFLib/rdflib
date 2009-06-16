import sys
import unittest

from datetime import datetime

from rdflib.term import URIRef
from rdflib.term import Literal


class TestRelativeBase(unittest.TestCase):
    def setUp(self):
        self.x = Literal("2008-12-01T18:02:00Z",
                         datatype=URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))

    def test_equality(self):        
        self.assertEquals(self.x == self.x, True)

    def test_millis(self):
        now = datetime.now()
        l = Literal(now)
        self.assertEquals(l.datatype,
                URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))
        # 2.6.0 added the %f format to datetime.strftime
        # http://bugs.python.org/issue1982
        if sys.version_info >= (2,6,0):
            self.assertEqual(now, l.toPython())


if __name__ == "__main__":
    unittest.main()

