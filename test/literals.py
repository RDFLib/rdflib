from rdflib import Graph, Namespace, Literal

import unittest

# a collection of "tricky" literals

cases = ['no quotes',
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

NS = Namespace("http://quoting.test/")


def allgraph(): 
    g=Graph()
    for i, case in enumerate(cases):
        g.add((NS['subj'], NS['case%s' % i], Literal(case)))

    return g


class LiteralsTestCase(unittest.TestCase):

    def quoting(self, fmt):
        g = allgraph()
        n3txt = g.serialize(format=fmt)

        g2 = Graph()
        g2.parse(data=n3txt, format=fmt)
        for i, case in enumerate(cases):
            l = g2.value(NS['subj'], NS['case%s' % i])
            #print repr(l), repr(case)
            self.assertEqual(l, Literal(case))
