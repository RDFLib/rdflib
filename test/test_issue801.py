  """
Issue 801 - Problem with prefixes created for URIs containing %20
"""

from rdflib import Namespace, Graph, BNode, Literal
import unittest

class TestIssue801(unittest.TestCase):

    def test_issue_801(self):
        g = Graph()
        example = Namespace('http://example.org/')
        g.bind('', example)
        node = BNode()
        g.add((node, example['first%20name'], Literal('John')))
        print(g.serialize(format="turtle").decode())


if __name__ == "__main__":
    unittest.main()
