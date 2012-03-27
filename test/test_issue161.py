from unittest import TestCase
from rdflib.graph import ConjunctiveGraph
from nose.exc import SkipTest

class EntityTest(TestCase):

    def test_turtle_namespace_prefixes(self):
        raise SkipTest('Skipping: Turtle serializer preserves n3 prefixes (eg. "_9") that violate Turtle syntax.')
        g = ConjunctiveGraph()
        n3 = \
        """
        @prefix _9: <http://data.linkedmdb.org/resource/movie/> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

        <http://data.linkedmdb.org/resource/director/1> a
        <http://data.linkedmdb.org/resource/movie/director>;
            rdfs:label "Cecil B. DeMille (Director)";
            _9:director_name "Cecil B. DeMille" ."""
        g.parse(data=n3, format='n3')
        turtle = g.serialize(format="turtle")
        # Check round-tripping, just for kicks.
        g = ConjunctiveGraph()
        g.parse(data=turtle, format='turtle')
        # Shouldn't have got to here
        self.assert_('_9' not in g.serialize(format="turtle"))




