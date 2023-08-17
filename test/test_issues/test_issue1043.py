import io
import sys
import unittest

from rdflib import RDFS, XSD, Graph, Literal, Namespace


class TestIssue1043(unittest.TestCase):
    def test_issue_1043(self):
        expected = """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/number> rdfs:label 4e-08 .


"""
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        g = Graph()
        g.bind("xsd", XSD)
        g.bind("rdfs", RDFS)
        n = Namespace("http://example.org/")
        g.add((n.number, RDFS.label, Literal(0.00000004, datatype=XSD.decimal)))
        g.print()
        sys.stdout = sys.__stdout__
        self.assertEqual(capturedOutput.getvalue(), expected)


if __name__ == "__main__":
    unittest.main()
