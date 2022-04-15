import pytest

from rdflib.parser import create_input_source


class TestParser:
    def test_empty_arguments(self):
        """create_input_source() function must receive exactly one argument."""
        with pytest.raises(ValueError):
            create_input_source()

    def test_too_many_arguments(self):
        """create_input_source() function has a few conflicting arguments."""
        with pytest.raises(ValueError):
            create_input_source(source="a", location="b")
