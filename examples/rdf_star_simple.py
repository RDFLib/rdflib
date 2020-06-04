from rdflib import Graph
from rdflib.namespace import RDF, Namespace
from pyparsing import ParseException


"""
A very basic Rdf Star graph with only 1 embedded triple as Subject.
"""


rdf_graph = """
    PREFIX ex:<http://example.org/>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    PREFIX dct:<http://purl.org/dc/terms/>

    ex:bob foaf:name "Bob" ;
    foaf:age 23 .
    _:s1 rdf:type rdf:Statement ;
    rdf:subject ex:bob ;
    rdf:predicate foaf:age ;
    rdf:object 23 .

    _:s1 dct:creator <http://example.com/crawlers#c1> ;
        dct:source <http://example.net/listing.html> .

    """

sparql_query = """
    PREFIX ex:<http://example.org/>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    PREFIX dct:<http://purl.org/dc/terms/>

    SELECT ?x ?age ?src WHERE {
    ?x foaf:age ?age .
    ?r rdf:type rdf:Statement ;
    rdf:subject ?x ;
    rdf:predicate foaf:age ;
    rdf:object ?age ;
    dct:source ?src . }
"""

rdf_Star_graph = """
    PREFIX ex:<http://example.org/>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    PREFIX dct:<http://purl.org/dc/terms/>

    ex:bob foaf:name "Bob" .
    <<ex:bob foaf:age 23>> dct:creator <http://example.com/crawlers#c1> ;
    dct:source <http://example.net/listing.html> .
"""

sparql_star_query = """
    PREFIX ex:<http://example.org/>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    PREFIX dct:<http://purl.org/dc/terms/>

    SELECT ?x ?age ?src WHERE { <<?x foaf:age ?age>> dct:source ?src . }

"""


def test_rdf_basic():
    g = Graph()
    g.parse(data=rdf_graph, format="turtle")

    print("Result on Rdf Graph:")
    for row in g.query(sparql_query):
        print(row)


def test_rdf_star():
    g = Graph()
    g.parse(data=rdf_Star_graph, format="turtle")

    print("Result on Rdf* Graph:")
    for row in g.query(sparql_query):
        print(row)


if __name__ == '__main__':
    test_rdf_basic()
    test_rdf_star()