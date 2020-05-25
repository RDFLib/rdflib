import unittest

from rdflib.namespace import RDF, RDFS
from rdflib.term import URIRef
from rdflib.term import Literal
from rdflib.graph import Graph


def failingFunc(g):
	g.parse('test/test_parser.py')

class ParserFormatTestCase(unittest.TestCase):
	backend='default'
	path = 'store'

	def setUp(self):
		self.graph = Graph(store=self.backend)
		self.graph.open(self.path)

	def tearDown(self):
		self.graph.close()

	def testDifferentFormat(self):
		g = self.graph
		g.parse('test/a.n3')
		self.assertEqual(True , True)

	def testAnotherFormat(self):
		self.graph = Graph(store=self.backend)
		g = self.graph
		g.parse('test/a.ttl')
		self.assertEqual(True , True)

	def testFailingFormat(self):
		self.graph = Graph(store=self.backend)
		g = self.graph
		self.assertRaises(Exception , failingFunc , g)


if __name__=="__main__":
	unittest.main()