import unittest
import pickle

from rdflib.term import Literal

from rdflib.store import NodePickler

# same as nt/more_literals.nt
cases = [
    'no quotes',
    "single ' quote",
    'double " quote',
    'triple """ quotes',
    'mixed "\'""" quotes',
    '"',
    "'",
    '"\'"',
    '\\', # len 1
    '\\"', # len 2
    '\\\\"', # len 3
    '\\"\\', # len 3
    '<a some="typical" html="content">here</a>',
]


class UtilTestCase(unittest.TestCase):

    def test_to_bits_from_bits_round_trip(self):
        np = NodePickler()

        a = Literal(u'''A test with a \\n (backslash n), "\u00a9" , and newline \n and a second line.
''')
        b = np.loads(np.dumps(a))
        self.assertEqual(a, b)

    def test_literal_cases(self):
        np = NodePickler()

        for l in cases:
            a = Literal(l)
            b = np.loads(np.dumps(a))
            self.assertEqual(a, b)

    def test_pickle(self):
        np = NodePickler()
        dump = pickle.dumps(np)
        np2 = pickle.loads(dump)
        self.assertEqual(np._ids, np2._ids)
        self.assertEqual(np._objects,  np2._objects)


if __name__ == '__main__':
    unittest.main()
