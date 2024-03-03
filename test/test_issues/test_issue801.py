"""
Issue 801 - Problem with prefixes created for URIs containing %20
"""
import unittest
from test.utils.namespace import EGDO

from rdflib import BNode, Graph, Literal


class TestIssue801(unittest.TestCase):
    def test_issue_801(self):
        g = Graph()
        g.bind("", EGDO)
        node = BNode()
        g.add((node, EGDO["first%20name"], Literal("John")))
        self.assertEqual(
            g.serialize(format="turtle").split("\n")[-3], '[] :first%20name "John" .'
        )


if __name__ == "__main__":
    unittest.main()
