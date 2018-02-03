import unittest
from datetime import timedelta

from isodate import Duration, parse_duration

from rdflib.namespace import XSD
from rdflib.term import Literal


class TestDuration(unittest.TestCase):
    def test_to_python_timedelta(self):
        l = Literal("P4DT5H6M7S", datatype=XSD.dayTimeDuration)
        self.assertTrue(isinstance(l.toPython(), timedelta))
        self.assertEqual(l.toPython(), parse_duration("P4DT5H6M7S"))

    def test_to_python_ym_duration(self):
        l = Literal("P1Y2M", datatype=XSD.yearMonthDuration)
        self.assertTrue(isinstance(l.toPython(), Duration))
        self.assertEqual(l.toPython(), parse_duration("P1Y2M"))

    def test_to_python_ymdhms_duration(self):
        l = Literal("P1Y2M4DT5H6M7S", datatype=XSD.duration)
        self.assertTrue(isinstance(l.toPython(), Duration))
        self.assertEqual(l.toPython(), parse_duration("P1Y2M4DT5H6M7S"))

    def test_equality(self):
        x = Literal("P1Y2M3W4DT5H6M7S", datatype=XSD.duration)
        y = Literal("P1Y2M25DT5H6M7S", datatype=XSD.duration)
        self.assertTrue(x == y)

    def test_duration_le(self):
        self.assertTrue(
            Literal("P4DT5H6M7S", datatype=XSD.duration) < Literal("P8DT10H12M14S", datatype=XSD.duration)
        )

    def test_duration_sum(self):
        self.assertEqual(
            Literal("P1Y2M4DT5H6M7S", datatype=XSD.duration) + Literal("P1Y2M4DT5H6M7S", datatype=XSD.duration).toPython(),
            Literal("P2Y4M8DT10H12M14S", datatype=XSD.duration)
        )

if __name__ == "__main__":
    unittest.main()
