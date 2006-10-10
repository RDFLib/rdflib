import unittest
#import sys
#sys.path[:0]=[".."]
from rdflib import Literal, Namespace, StringInputSource
from rdflib.Graph import Graph

cases = ['no quotes',
         "single ' quote",
         'double " quote',
         '"',
         "'",
         '"\'"',
         '\\', # len 1
         '\\"', # len 2
         '\\\\"', # len 3
         '\\"\\', # len 3
         '<a some="typical" html="content">here</a>',
         ]

class N3Quoting(unittest.TestCase):
    def test(self):
        g = Graph()
        NS = Namespace("http://quoting.test/")
        for i, case in enumerate(cases):
            g.add((NS['subj'], NS['case%s' % i], Literal(case)))
        n3txt = g.serialize(format="n3")
        print n3txt

        g2 = Graph()
        g2.parse(StringInputSource(n3txt), format="n3")
        for i, case in enumerate(cases):
            l = g2.value(NS['subj'], NS['case%s' % i])
            print repr(l), repr(case)
            self.assertEqual(l, Literal(case))


if __name__ == "__main__":
    unittest.main()
