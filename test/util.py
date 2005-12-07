import unittest

from rdflib import *
from rdflib.util import from_bits


class UtilTestCase(unittest.TestCase):

    def test_to_bits_from_bits_round_trip(self):

        a = Literal(u'''A test with a \\n (backslash n), "\u00a9" , and newline \n and a second line.
''') 
        b = from_bits(a.to_bits())
        self.assertEquals(a, b)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
