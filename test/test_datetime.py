import sys
import unittest

from datetime import datetime

from isodate import datetime_isoformat, UTC
from isodate.isostrf import DATE_EXT_COMPLETE, TZ_EXT

from rdflib.term import URIRef
from rdflib.term import Literal
from rdflib.namespace import XSD
from six import text_type


class TestRelativeBase(unittest.TestCase):
    def test_equality(self):
        x = Literal("2008-12-01T18:02:00Z",
                    datatype=URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))
        self.assertEqual(x == x, True)

    def test_microseconds(self):
        import platform
        if platform.system() == 'Java' or (platform.system() != 'Java' and sys.version_info[:2] == (2, 5)):
            from nose import SkipTest
            raise SkipTest('datetime microseconds unsupported in Python2.5 and Jython')
        dt1 = datetime(2009, 6, 15, 23, 37, 6, 522630)
        l = Literal(dt1)

        # datetime with microseconds should be cast as a literal with using
        # XML Schema dateTime as the literal datatype
        self.assertEqual(text_type(l), '2009-06-15T23:37:06.522630')
        self.assertEqual(l.datatype, XSD.dateTime)

        dt2 = l.toPython()
        self.assertEqual(dt2, dt1)

    def test_to_python(self):
        dt = "2008-12-01T18:02:00"
        l = Literal(dt,
                    datatype=URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))

        self.assertTrue(isinstance(l.toPython(), datetime))
        self.assertEqual(l.toPython().isoformat(), dt)

    def test_timezone_z(self):
        dt = "2008-12-01T18:02:00.522630Z"
        l = Literal(dt,
                    datatype=URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))

        self.assertTrue(isinstance(l.toPython(), datetime))
        self.assertEqual(datetime_isoformat(l.toPython(),
                                             DATE_EXT_COMPLETE + 'T' + '%H:%M:%S.%f' + TZ_EXT),
                          dt)
        self.assertEqual(l.toPython().isoformat(),
                          "2008-12-01T18:02:00.522630+00:00")

    def test_timezone_offset(self):
        dt = "2010-02-10T12:36:00+03:00"
        l = Literal(dt,
                    datatype=URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))

        self.assertTrue(isinstance(l.toPython(), datetime))
        self.assertEqual(l.toPython().isoformat(), dt)

    def test_timezone_offset_to_utc(self):
        dt = "2010-02-10T12:36:00+03:00"
        l = Literal(dt,
                    datatype=URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))

        utc_dt = l.toPython().astimezone(UTC)
        self.assertEqual(datetime_isoformat(utc_dt),
                          "2010-02-10T09:36:00Z")

    def test_timezone_offset_millisecond(self):
        dt = "2011-01-16T19:39:18.239743+01:00"
        l = Literal(dt,
                    datatype=URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))

        self.assertTrue(isinstance(l.toPython(), datetime))
        self.assertEqual(l.toPython().isoformat(), dt)

if __name__ == "__main__":
    unittest.main()
