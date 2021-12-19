import unittest

from rdflib.parser import create_input_source


class ParserTestCase(unittest.TestCase):
    def test_empty_arguments(self):
        """create_input_source() function must receive exactly one argument."""
        self.assertRaises(
            ValueError,
            create_input_source,
        )

    def test_too_many_arguments(self):
        """create_input_source() function has a few conflicting arguments."""
        self.assertRaises(
            ValueError,
            create_input_source,
            source="a",
            location="b",
        )


if __name__ == "__main__":
    unittest.main()
