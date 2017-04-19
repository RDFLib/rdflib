from unittest import TestCase
from six import b
from rdflib.graph import ConjunctiveGraph


class EntityTest(TestCase):

    def test_turtle_namespace_prefixes(self):

        g = ConjunctiveGraph()
        n3 = \
        """
        @prefix _9: <http://data.linkedmdb.org/resource/movie/> .
        @prefix p_9: <urn:test:> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

        p_9:a p_9:b p_9:c .

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
        s=g.serialize(format="turtle")

        self.assertTrue(b('@prefix _9') not in s)
