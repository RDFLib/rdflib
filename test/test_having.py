import sys
import unittest
from rdflib import Graph

class GraphTestCase(unittest.TestCase):
    g = Graph()
    def setUp(self):
        data = """
        <urn:a> <urn:p> 1 .
        <urn:b> <urn:p> 3 .
        <urn:c> <urn:q> 1 .
        """

        self.g.parse(data=data, format="turtle")

    def testGroupBy(self):
        query = ("SELECT ?p ?o "
                 "WHERE { ?s ?p ?o } "
                 "GROUP BY ?p")
        qres = self.g.query(query)

        self.assertEqual(2, len(qres))

    def testHavingAggregateEqLiteral(self):

        query = ("SELECT ?p (avg(?o) as ?a) "
                 "WHERE { ?s ?p ?o } "
                 "GROUP BY ?p HAVING (avg(?o) = 2 )")
        qres = self.g.query(query)

        self.assertEqual(1, len(qres))

    def testHavingPrimaryExpressionVarNeqIri(self):
        query = ("SELECT ?p ?o"
                 "WHERE { ?s ?p ?o } "
                 "GROUP BY ?p HAVING (?p != <urn:foo> )")
        qres = self.g.query(query)

        self.assertEqual(2, len(qres))


if __name__ == '__main__':
    unittest.main(argv=sys.argv[:1])
