"""
Issue 715 - path query chaining issue
Some incorrect matches were found when using oneOrMore ('+') and
zeroOrMore ('*') property paths and specifying neither the
subject or the object.
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
