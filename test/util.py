import unittest

from rdflib import *
from rdflib.store.NodePickler import NodePickler


class UtilTestCase(unittest.TestCase):

    def test_to_bits_from_bits_round_trip(self):
        np = NodePickler()

        a = Literal(u'''A test with a \\n (backslash n), "\u00a9" , and newline \n and a second line.
''')
        b = np.loads(np.dumps(a))
        self.assertEquals(a, b)


def testMe():
    unittest.main(defaultTest='test_suite')    

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
