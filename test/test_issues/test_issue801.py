"""
Issue 801 - Problem with prefixes created for URIs containing %20
"""

from rdflib import BNode, Graph, Literal
from test.utils.namespace import EGDO


def test_issue_801():
    g = Graph()
    g.bind("", EGDO)
    node = BNode()
    g.add((node, EGDO["first%20name"], Literal("John")))
    assert g.serialize(format="turtle").split("\n")[-3] == '[] :first%20name "John" .'
