import unittest

from rdflib.namespace import RDF, RDFS
from rdflib.term import URIRef
from rdflib.term import Literal
from rdflib.graph import Graph


def failingFunc(g):
	g.parse('test/a_faulty.n3' , ignore_error=False)
class ParserFormatTestCase(unittest.TestCase):
	backend='default'
	path = 'store'

	def setUp(self):
		self.graph = Graph(store=self.backend)
		self.graph.open(self.path)

	def tearDown(self):
		self.graph.close()

	def testIgnoreErrorTrue(self):
		g = self.graph
		g.parse('test/a_faulty.n3', format='n3' , ignore_errors=True)
		self.assertEqual(True , True)

	def testIgnoreErrorFalse(self):
		self.graph = Graph(store=self.backend)
		g = self.graph
		self.assertRaises(Exception , failingFunc , g)


if __name__=="__main__":
	unittest.main()
