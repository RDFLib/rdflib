import unittest

from rdflib.namespace import RDF, RDFS
from rdflib.term import URIRef
from rdflib.term import Literal
from rdflib.graph import Graph
import rdflib.parser

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


class URLInputSourceTestCase(unittest.TestCase):

    def testLinkHeaderParse_1(self):
        header = '<http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=text/turtle>; rel="alternate"; type="text/turtle"; profile="http://purl.org/dc/terms/"'
        parsed = rdflib.parser.parse_link_header(header)
        assert len(parsed["alternate"]) == 1
        assert parsed["alternate"][0]["type"] == "text/turtle"

    def testLinkHeaderParse_2(self):
        header = '<http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=text/turtle>; rel="alternate"; type="text/turtle"; profile="http://purl.org/dc/terms/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=application/rdf+xml>; rel="alternate"; type="application/rdf+xml"; profile="http://purl.org/dc/terms/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=application/ld+json>; rel="alternate"; type="application/ld+json"; profile="http://purl.org/dc/terms/"'
        parsed = rdflib.parser.parse_link_header(header)
        assert len(parsed["alternate"]) == 3
        assert parsed["alternate"][2]["type"] == "application/ld+json"
        assert parsed["alternate"][2]["target"] == "http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=application/ld+json"

    def testLinkHeaderParse_3(self):
        # real example from the wilds
        header = '<http://www.w3.org/ns/dx/prof/Profile>; rel="type"; token="csirov3"; anchor=<https://confluence.csiro.au/display/AusIGSN/CSIRO+IGSN+IMPLEMENTATION>, <http://www.w3.org/ns/dx/prof/Profile>; rel="type"; token="dct"; anchor=<http://purl.org/dc/terms/>, <http://www.w3.org/ns/dx/prof/Profile>; rel="type"; token="igsn"; anchor=<http://schema.igsn.org/description/>, <http://www.w3.org/ns/dx/prof/Profile>; rel="type"; token="igsn-r1"; anchor=<http://schema.igsn.org/description/1.0>, <http://www.w3.org/ns/dx/prof/Profile>; rel="type"; token="igsn-o"; anchor=<http://pid.geoscience.gov.au/def/ont/ga/igsn>, <http://www.w3.org/ns/dx/prof/Profile>; rel="type"; token="prov"; anchor=<http://www.w3.org/ns/prov/>, <http://www.w3.org/ns/dx/prof/Profile>; rel="type"; token="sosa"; anchor=<http://www.w3.org/ns/sosa/>, <http://www.w3.org/ns/dx/prof/Profile>; rel="type"; token="alternates"; anchor=<https://w3id.org/profile/alt>, <http://www.w3.org/ns/dx/prof/Profile>; rel="type"; token="all"; anchor=<http://www.w3.org/ns/dx/conneg/altr>, <http://pid.geoscience.gov.au/sample/AU1547827?_view=csirov3&_format=text/xml>; rel="alternate"; type="text/xml"; profile="https://confluence.csiro.au/display/AusIGSN/CSIRO+IGSN+IMPLEMENTATION", <http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=text/html>; rel="alternate"; type="text/html"; profile="http://purl.org/dc/terms/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=text/turtle>; rel="alternate"; type="text/turtle"; profile="http://purl.org/dc/terms/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=application/rdf+xml>; rel="alternate"; type="application/rdf+xml"; profile="http://purl.org/dc/terms/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=application/ld+json>; rel="alternate"; type="application/ld+json"; profile="http://purl.org/dc/terms/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=application/xml>; rel="alternate"; type="application/xml"; profile="http://purl.org/dc/terms/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=text/n3>; rel="alternate"; type="text/n3"; profile="http://purl.org/dc/terms/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=text/n-triples>; rel="alternate"; type="text/n-triples"; profile="http://purl.org/dc/terms/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=dct&_format=text/xml>; rel="alternate"; type="text/xml"; profile="http://purl.org/dc/terms/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=igsn&_format=text/xml>; rel="alternate"; type="text/xml"; profile="http://schema.igsn.org/description/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=igsn-r1&_format=text/xml>; rel="alternate"; type="text/xml"; profile="http://schema.igsn.org/description/1.0", <http://pid.geoscience.gov.au/sample/AU1547827?_view=igsn-o&_format=text/html>; rel="self"; type="text/html"; profile="http://pid.geoscience.gov.au/def/ont/ga/igsn", <http://pid.geoscience.gov.au/sample/AU1547827?_view=igsn-o&_format=text/turtle>; rel="alternate"; type="text/turtle"; profile="http://pid.geoscience.gov.au/def/ont/ga/igsn", <http://pid.geoscience.gov.au/sample/AU1547827?_view=igsn-o&_format=application/rdf+xml>; rel="alternate"; type="application/rdf+xml"; profile="http://pid.geoscience.gov.au/def/ont/ga/igsn", <http://pid.geoscience.gov.au/sample/AU1547827?_view=igsn-o&_format=application/ld+json>; rel="alternate"; type="application/ld+json"; profile="http://pid.geoscience.gov.au/def/ont/ga/igsn", <http://pid.geoscience.gov.au/sample/AU1547827?_view=prov&_format=text/html>; rel="alternate"; type="text/html"; profile="http://www.w3.org/ns/prov/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=prov&_format=text/turtle>; rel="alternate"; type="text/turtle"; profile="http://www.w3.org/ns/prov/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=prov&_format=application/rdf+xml>; rel="alternate"; type="application/rdf+xml"; profile="http://www.w3.org/ns/prov/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=prov&_format=application/ld+json>; rel="alternate"; type="application/ld+json"; profile="http://www.w3.org/ns/prov/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=sosa&_format=text/turtle>; rel="alternate"; type="text/turtle"; profile="http://www.w3.org/ns/sosa/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=sosa&_format=application/rdf+xml>; rel="alternate"; type="application/rdf+xml"; profile="http://www.w3.org/ns/sosa/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=sosa&_format=application/ld+json>; rel="alternate"; type="application/ld+json"; profile="http://www.w3.org/ns/sosa/", <http://pid.geoscience.gov.au/sample/AU1547827?_view=alternates&_format=text/html>; rel="alternate"; type="text/html"; profile="https://w3id.org/profile/alt", <http://pid.geoscience.gov.au/sample/AU1547827?_view=alternates&_format=application/json>; rel="alternate"; type="application/json"; profile="https://w3id.org/profile/alt", <http://pid.geoscience.gov.au/sample/AU1547827?_view=alternates&_format=text/turtle>; rel="alternate"; type="text/turtle"; profile="https://w3id.org/profile/alt", <http://pid.geoscience.gov.au/sample/AU1547827?_view=alternates&_format=application/rdf+xml>; rel="alternate"; type="application/rdf+xml"; profile="https://w3id.org/profile/alt", <http://pid.geoscience.gov.au/sample/AU1547827?_view=alternates&_format=application/ld+json>; rel="alternate"; type="application/ld+json"; profile="https://w3id.org/profile/alt", <http://pid.geoscience.gov.au/sample/AU1547827?_view=alternates&_format=text/n3>; rel="alternate"; type="text/n3"; profile="https://w3id.org/profile/alt", <http://pid.geoscience.gov.au/sample/AU1547827?_view=alternates&_format=application/n-triples>; rel="alternate"; type="application/n-triples"; profile="https://w3id.org/profile/alt", <http://pid.geoscience.gov.au/sample/AU1547827?_view=all&_format=text/html>; rel="alternate"; type="text/html"; profile="http://www.w3.org/ns/dx/conneg/altr", <http://pid.geoscience.gov.au/sample/AU1547827?_view=all&_format=application/json>; rel="alternate"; type="application/json"; profile="http://www.w3.org/ns/dx/conneg/altr", <http://pid.geoscience.gov.au/sample/AU1547827?_view=all&_format=text/turtle>; rel="alternate"; type="text/turtle"; profile="http://www.w3.org/ns/dx/conneg/altr", <http://pid.geoscience.gov.au/sample/AU1547827?_view=all&_format=application/rdf+xml>; rel="alternate"; type="application/rdf+xml"; profile="http://www.w3.org/ns/dx/conneg/altr", <http://pid.geoscience.gov.au/sample/AU1547827?_view=all&_format=application/ld+json>; rel="alternate"; type="application/ld+json"; profile="http://www.w3.org/ns/dx/conneg/altr", <http://pid.geoscience.gov.au/sample/AU1547827?_view=all&_format=text/n3>; rel="alternate"; type="text/n3"; profile="http://www.w3.org/ns/dx/conneg/altr", <http://pid.geoscience.gov.au/sample/AU1547827?_view=all&_format=application/n-triples>; rel="alternate"; type="application/n-triples"; profile="http://www.w3.org/ns/dx/conneg/altr", <http://pid.geoscience.gov.au/sample/AU1547827/pingback>; rel="http://www.w3.org/ns/prov#pingback"'
        parsed = rdflib.parser.parse_link_header(header)
        assert len(parsed["alternate"]) == 35
        assert parsed["alternate"][23]["type"] == "text/turtle"
        assert parsed["alternate"][23]["target"] == "http://pid.geoscience.gov.au/sample/AU1547827?_view=alternates&_format=text/turtle"
        assert parsed["alternate"][23]["profile"] == "https://w3id.org/profile/alt"

        
if __name__ == "__main__":
    unittest.main()
