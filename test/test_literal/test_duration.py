from datetime import timedelta

from isodate import Duration, parse_duration

from rdflib.namespace import XSD
from rdflib.term import Literal


class TestDuration:
    def test_to_python_timedelta(self):
        l = Literal("P4DT5H6M7S", datatype=XSD.dayTimeDuration)
        assert isinstance(l.toPython(), timedelta)
        assert l.toPython() == parse_duration("P4DT5H6M7S")

    def test_to_python_ym_duration(self):
        l = Literal("P1Y2M", datatype=XSD.yearMonthDuration)
        assert isinstance(l.toPython(), Duration)
        assert l.toPython() == parse_duration("P1Y2M")

    def test_to_python_ymdhms_duration(self):
        l = Literal("P1Y2M4DT5H6M7S", datatype=XSD.duration)
        assert isinstance(l.toPython(), Duration)
        assert l.toPython() == parse_duration("P1Y2M4DT5H6M7S")

    def test_equalityself(self):
        x = Literal("P1Y2M3W4DT5H6M7S", datatype=XSD.duration)
        y = Literal("P1Y2M25DT5H6M7S", datatype=XSD.duration)
        assert x == y

    def test_duration_le(self):
        assert Literal("P4DT5H6M7S", datatype=XSD.duration) < Literal(
            "P8DT10H12M14S", datatype=XSD.duration
        )

    def test_duration_sum(self):
        assert Literal("P1Y2M4DT5H6M7S", datatype=XSD.duration) + Literal(
            "P1Y2M4DT5H6M7S", datatype=XSD.duration
        ).toPython() == Literal("P2Y4M8DT10H12M14S", datatype=XSD.duration)

    def test_duration_sub_pos(self):
        assert Literal("P1Y2M4DT5H6M7S", datatype=XSD.duration) - Literal(
            "P1Y2M3DT4H7M8S", datatype=XSD.duration
        ).toPython() == Literal("P1DT58M59S", datatype=XSD.duration)

    def test_duration_sub_neg(self):
        assert Literal("P1Y2M3DT4H7M8S", datatype=XSD.duration) - Literal(
            "P1Y2M4DT5H6M7S", datatype=XSD.duration
        ).toPython() == Literal("-P1DT58M59S", datatype=XSD.duration)
