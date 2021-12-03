import unittest
import io
import json
from rdflib import Graph, RDF, RDFS, Namespace


class TestIssue1484_json(unittest.TestCase):
    def test_issue_1484_json(self):
        """
        Test JSON-LD parsing of result from json.dump
        """
        n = Namespace("http://example.org/")
        jsondata = {"@id": n.s, "@type": [n.t], n.p: {"@id": n.o}}

        s = io.StringIO()
        json.dump(jsondata, s, indent=2, separators=(",", ": "))
        s.seek(0)

        DEBUG = False
        if DEBUG:
            print("S: ", s.read())
            s.seek(0)

        b = n.base
        g = Graph()
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)
        g.parse(source=s, publicID=b, format="json-ld")

        assert (n.s, RDF.type, n.t) in g
        assert (n.s, n.p, n.o) in g


if __name__ == "__main__":
    unittest.main()
