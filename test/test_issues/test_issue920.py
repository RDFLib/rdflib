"""
Issue 920 - NTriples fails to parse URIs with only a scheme

from rdflib import Graph
g=Graph()
g.parse(data='<a:> <b:> <c:> .', format='nt') # nquads also fails

N3, by contrast, succeeds:

g.parse(data='<a:> <b:> <c:> .', format='n3')
"""
from rdflib import Graph
import unittest


class TestIssue920(unittest.TestCase):
    def test_issue_920(self):
        g = Graph()
        # NT tests
        g.parse(data="<a:> <b:> <c:> .", format="nt")
        g.parse(data="<http://a> <http://b> <http://c> .", format="nt")
        g.parse(data="<https://a> <http://> <http://c> .", format="nt")

        # related parser tests
        g.parse(data="<a:> <b:> <c:> .", format="turtle")
        g.parse(data="<http://a> <http://b> <http://c> .", format="turtle")
        g.parse(data="<https://a> <http://> <http://c> .", format="turtle")

        g.parse(data="<a:> <b:> <c:> .", format="n3")
        g.parse(data="<http://a> <http://b> <http://c> .", format="n3")
        g.parse(data="<https://a> <http://> <http://c> .", format="n3")


if __name__ == "__main__":
    unittest.main()
