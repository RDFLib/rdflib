import unittest

from rdflib import Graph


class TestIssue910(unittest.TestCase):
    def testA(self):
        g = Graph()
        q = g.query(
            """
			SELECT * {
			{ BIND ("a" AS ?a) }
			UNION
			{ BIND ("a" AS ?a) }
			}
			"""
        )
        self.assertEqual(len(q) == 2, True)

    def testB(self):
        g = Graph()
        q = g.query(
            """
			SELECT * {
				{ BIND ("a" AS ?a) }
				UNION
				{ VALUES ?a { "a" } }
				UNION
				{ SELECT ("a" AS ?a) {} }
			}
			"""
        )
        self.assertEqual(len(q) == 3, True)

    def testC(self):
        g = Graph()
        q = g.query(
            """
			SELECT * {
				{ BIND ("a" AS ?a) }
				UNION
				{ VALUES ?a { "a" } }
				UNION
				{ SELECT ("b" AS ?a) {} }
			}
			"""
        )
        self.assertEqual(len(q) == 3, True)

    def testD(self):
        g = Graph()
        q = g.query(
            """SELECT * {
				{ BIND ("a" AS ?a) }
				UNION
				{ VALUES ?a { "b" } }
				UNION
				{ SELECT ("c" AS ?a) {} }
			}
			"""
        )
        self.assertEqual(len(q) == 3, True)


if __name__ == "__main__":
    unittest.main()
