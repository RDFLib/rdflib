import rdflib
from nose.exc import SkipTest
import unittest


class TestSerialization(unittest.TestCase):

    def test_issue_248(self):
        """
        Ed Summers Thu, 24 May 2007 12:21:17 -0700

        As discussed with eikeon in #redfoot it appears that the n3 serializer
        is ignoring the base option to Graph.serialize...example follows:

        --

        #!/usr/bin/env python

        from rdflib.Graph import Graph
        from rdflib.URIRef import URIRef
        from rdflib import Literal, Namespace, RDF

        graph = Graph()
        DC = Namespace('http://purl.org/dc/terms/')
        SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
        LCCO = Namespace('http://loc.gov/catdir/cpso/lcco/')

        graph.bind('dc', DC)
        graph.bind('skos', SKOS)
        graph.bind('lcco', LCCO)

        concept = URIRef(LCCO['1'])
        graph.add((concept, RDF.type, SKOS['Concept']))
        graph.add((concept, SKOS['prefLabel'], Literal('Scrapbooks')))
        graph.add((concept, DC['LCC'], Literal('AC999.0999 - AC999999.Z9999')))

        print graph.serialize(format='n3', base=LCCO)

        --

        Which generates:

        --

        @prefix dc: <http://purl.org/dc/terms/>.
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
        @prefix skos: <http://www.w3.org/2004/02/skos/core#>.

         <http://loc.gov/catdir/cpso/lcco/1> a skos:Concept;
            dc:LCC "AC999.0999 - AC999999.Z9999";
            skos:prefLabel "Scrapbooks".

        --

        Notice

         <http://loc.gov/catdir/cpso/lcco/1> a skos:Concept;

        instead of:

         <1> a skos:Concept;

        //Ed

        """
        graph = rdflib.Graph()
        DC = rdflib.Namespace('http://purl.org/dc/terms/')
        SKOS = rdflib.Namespace('http://www.w3.org/2004/02/skos/core#')
        LCCO = rdflib.Namespace('http://loc.gov/catdir/cpso/lcco/')

        graph.bind('dc', DC)
        graph.bind('skos', SKOS)
        graph.bind('lcco', LCCO)

        concept = rdflib.URIRef(LCCO['1'])
        graph.add(
            (concept,
             rdflib.RDF.type,
             SKOS['Concept']))
        graph.add(
            (concept,
             SKOS['prefLabel'],
             rdflib.Literal('Scrapbooks')))
        graph.add(
            (concept,
             DC['LCC'],
             rdflib.Literal('AC999.0999 - AC999999.Z9999')))
        sg = graph.serialize(format='n3', base=LCCO).decode('utf8')
        # See issue 248
        # Actual test should be the inverse of the below ...
        self.assertTrue('<1> a skos:Concept ;' in sg, sg)

if __name__ == "__main__":
    unittest.main()
