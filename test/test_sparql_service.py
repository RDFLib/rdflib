from rdflib import Graph, URIRef, Literal
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import isomorphic


def test_service():
    g = Graph()
    q = '''select ?dbpHypernym ?dbpComment
    where
    { service <http://DBpedia.org/sparql>
    { select ?dbpHypernym ?dbpComment
    where
    {
    <http://dbpedia.org/resource/John_Lilburne>
        <http://purl.org/linguistics/gold/hypernym> ?dbpHypernym ;
        <http://www.w3.org/2000/01/rdf-schema#comment> ?dbpComment .

    } } }'''
    results = g.query(q)
    # FILTER(LANGMATCHES(LANG(?dbpComment), "en"))

    self.assertTrue(False)

if __name__ == '__main__':
    # import nose
    # nose.main(defaultTest=__name__)
    test_service()
