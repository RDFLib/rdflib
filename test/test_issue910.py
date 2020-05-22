from rdflib import Namespace, Graph, BNode, Literal
import unittest


class TestIssue910(unittest.TestCase):

	def testA(self):
		g = Graph()
		qres = g.query("""SELECT * {
		{ BIND ("a" AS ?a) }
		UNION
		{ BIND ("a" AS ?a) }
		}""")
		self.assertEqual(len(qres) == 2, True)
		for row in qres:
			print (row)

		print ("Test A successful.")

	def testB(self):
		g = Graph()
		qres = g.query("""SELECT * {
		{ BIND ("a" AS ?a) }
		UNION
		{ VALUES ?a { "a" } }
		UNION
		{ SELECT ("a" AS ?a) {} }
		}""")
		self.assertEqual(len(qres) == 3, True)
		for row in qres:
			print (row)

		print ("Test B successful.")

	def testC(self):
		g = Graph()
		qres = g.query("""SELECT * {
		{ BIND ("a" AS ?a) }
		UNION
		{ VALUES ?a { "a" } }
		UNION
		{ SELECT ("b" AS ?a) {} }
		}""")
		self.assertEqual(len(qres) == 3, True)
		for row in qres:
			print (row)

		print ("Test C successful.")

	def testD(self):
		g = Graph()
		qres = g.query("""SELECT * {
		{ BIND ("a" AS ?a) }
		UNION
		{ VALUES ?a { "b" } }
		UNION
		{ SELECT ("c" AS ?a) {} }
		}""")
		self.assertEqual(len(qres) == 3, True)
		for row in qres:
			print (row)

		print ("Test D successful.")
        


if __name__ == "__main__":
    unittest.main()
