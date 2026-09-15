import io
import sys

from rdflib import RDFS, XSD, Graph, Literal
from test.utils.namespace import EGDO


def test_issue_1043():
    expected = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

<http://example.org/number>
    rdfs:label 4e-08 ;
.

"""
    capturedOutput = io.StringIO()  # noqa: N806
    sys.stdout = capturedOutput
    g = Graph()
    g.add((EGDO.number, RDFS.label, Literal(0.00000004, datatype=XSD.decimal)))
    g.print()
    sys.stdout = sys.__stdout__
    assert capturedOutput.getvalue() == expected
