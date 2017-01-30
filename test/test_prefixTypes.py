import unittest


from rdflib import Graph
from six import b

graph = Graph().parse(format='n3', data="""
@prefix dct: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/doc> a foaf:Document;
    dct:created "2011-03-20"^^xsd:date .
""")

class PrefixTypesTest(unittest.TestCase):

    """N3/Turtle serializers should use prefixes,
    also for types and datatypes

    This is issue 161
    http://code.google.com/p/rdflib/issues/detail?id=161
    """


    def test(self):
        s=graph.serialize(format='n3')
        print(s)
        self.assertTrue(b("foaf:Document") in s)
        self.assertTrue(b("xsd:date") in s)



if __name__ == '__main__':
    unittest.main()
