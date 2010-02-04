import unittest

import rdflib
from rdflib.term import Literal

from rdflib.store import NodePickler


class UtilTestCase(unittest.TestCase):

    def test_to_bits_from_bits_round_trip(self):
        np = NodePickler()

        a = Literal(u'''A test with a \\n (backslash n), "\u00a9" , and newline \n and a second line.
''')
        b = np.loads(np.dumps(a))
        self.assertEquals(a, b)

    def test_default_namespaces_method(self):
        g = rdflib.Graph()
        g.add((rdflib.URIRef("http://example.org/foo#bar1"), 
               rdflib.URIRef("http://example.org/foo#bar2"),                
               rdflib.URIRef("http://example.org/foo#bar3")))
        g.serialize()


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
