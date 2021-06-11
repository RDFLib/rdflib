import unittest

from rdflib.namespace import RDF, RDFS
from rdflib.term import URIRef
from rdflib.term import Literal
from rdflib.graph import Graph


class ParserTestCase(unittest.TestCase):
    backend = "default"
    path = "store"

    def setUp(self):
        self.graph = Graph(store=self.backend)
        self.graph.open(self.path)

    def tearDown(self):
        self.graph.close()

    def testNoPathWithHash(self):
        g = self.graph
        g.parse(
            data="""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
>

<rdfs:Class rdf:about="http://example.org#">
  <rdfs:label>testing</rdfs:label>
</rdfs:Class>

</rdf:RDF>
""",
            format="xml",
            publicID="http://example.org",
        )

        subject = URIRef("http://example.org#")
        label = g.value(subject, RDFS.label)
        self.assertEqual(label, Literal("testing"))
        type = g.value(subject, RDF.type)
        self.assertEqual(type, RDFS.Class)


class TestGitHubIssues(unittest.TestCase):
    def test_issue_1228_a(self):
        data = """
        PREFIX sdo: <https://schema.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        <x:> sdo:startDate "1982"^^xsd:gYear .
        """

        g = Graph().parse(data=data, format="ttl")
        self.assertNotIn("1982-01-01", data)
        self.assertNotIn("1982-01-01", g.serialize(format="ttl"))

    def test_issue_1228_b(self):
        data = """\
<?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:sdo="https://schema.org/"
    >
    <rdf:Description rdf:about="x:">
        <sdo:startDate
            rdf:datatype="http://www.w3.org/2001/XMLSchema#gYear">1982</sdo:startDate>
    </rdf:Description>
</rdf:RDF>"""

        g = Graph().parse(data=data, format="xml")
        self.assertNotIn("1982-01-01", data)
        self.assertNotIn("1982-01-01", g.serialize(format="xml"))

    def test_issue_806(self):
        data = (
            "<http://dbpedia.org/resource/Australian_Labor_Party> "
            "<http://dbpedia.org/ontology/formationYear> "
            '"1891"^^<http://www.w3.org/2001/XMLSchema#gYear> .'
        )
        g = Graph()
        g.parse(data=data, format="nt")
        for _, _, o in g:
            self.assertNotIn("1891-01-01", o.n3())


if __name__ == "__main__":
    unittest.main()
