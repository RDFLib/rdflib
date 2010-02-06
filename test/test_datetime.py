import sys
import unittest

from datetime import datetime

from rdflib.term import URIRef
from rdflib.term import Literal
from rdflib.namespace import XSD


class TestRelativeBase(unittest.TestCase):
    def setUp(self):
        self.x = Literal("2008-12-01T18:02:00Z",
                         datatype=URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))

    def test_equality(self):        
        self.assertEquals(self.x == self.x, True)

    def test_microseconds(self):
        dt1 = datetime(2009, 6, 15, 23, 37, 6, 522630)
        l = Literal(dt1)

        # datetime with microseconds should be cast as a literal with using
        # XML Schema dateTime as the literal datatype
        self.assertEquals(l.title(), '2009-06-15T23:37:06.522630')
        self.assertEquals(l.datatype, XSD.dateTime)

        # 2.6.0 added the %f format to datetime.strftime, so we should have
        # a lossless conversion back to the datetime
        # http://bugs.python.org/issue1982
        if sys.version_info >= (2,6,0):
            dt2 = l.toPython()
            self.assertEqual(dt2, dt1)

        # otherwise, we just get back the same literal again
        else:
            dt2 = l.toPython()
            l2 = Literal('2009-06-15T23:37:06.522630', datatype=XSD.dateTime)
            self.assertTrue(l2, l.toPython())


if __name__ == "__main__":
    unittest.main()

