import unittest
import rdflib
from rdflib.compare import graph_diff

"""Test for graph_diff - much more extensive testing 
would certainly be possible"""

class TestDiff(unittest.TestCase):
    """Unicode literals for graph_diff test
    (issue 151)"""

    def testA(self): 
        """with bnode"""
        g=rdflib.Graph()
        g.add( (rdflib.BNode(), rdflib.URIRef("urn:p"), rdflib.Literal(u'\xe9') ) ) 

        diff=graph_diff(g,g)

    def testB(self): 

        """Curiously, this one passes, even before the fix in issue 151"""

        g=rdflib.Graph()
        g.add( (rdflib.URIRef("urn:a"), rdflib.URIRef("urn:p"), rdflib.Literal(u'\xe9') ) ) 

        diff=graph_diff(g,g)


if __name__ == "__main__":
    unittest.main()

