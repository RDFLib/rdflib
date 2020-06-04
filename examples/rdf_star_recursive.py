from rdflib import Graph
from rdflib.namespace import RDF, Namespace
from pyparsing import ParseException

"""
An Rdf Star Graph with Recursively Embedded Triples of the form 
                        <<?s1 ?p1 <<?s2 ?p2 ?o2>> >> ?p ?o .
along with simple embedded triples.
"""


rdf_graph = """
    PREFIX ex:<http://example.org/>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    PREFIX dct:<http://purl.org/dc/terms/>

    ex:bob foaf:name "Bob" ;
            foaf:knows _:s2 .
    _:s rdf:type rdf:Statement ;
    rdf:subject ex:bob ;
    rdf:predicate foaf:knows ;
    rdf:object _:s2 .

    _:s2 rdf:type rdf:Statement ;
    rdf:subject ex:alice ;
    rdf:predicate foaf:name ;
    rdf:object "Alice" .

    _:s dct:creator <http://example.com/crawlers#c1> ;
        dct:source <http://example.net/bob.html> .

    _:s2 dct:source <http://example.net/alice.html> .

    ex:welles foaf:name "John Welles" ;
                ex:mentioned ex:kubrick .
    ex:kubrick foaf:name "Stanley Kubrick" ;
                ex:influencedBy ex:welles .
    _:s1 rdf:type rdf:Statement ;
    rdf:subject ex:kubrick ;
    rdf:predicate ex:influencedBy ;
    rdf:object ex:welles .

    _:s1 dct:creator <http://example.com/names#examples> ;
        dct:source <http://example.net/people.html> .

    """

sparql_query = """
    PREFIX ex:<http://example.org/>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    PREFIX dct:<http://purl.org/dc/terms/>

    SELECT ?x ?y ?srcX ?srcY WHERE {
    ?x foaf:knows ?r2 .
    ?r rdf:type rdf:Statement ;
    rdf:subject ?x ;
    rdf:predicate foaf:knows ;
    rdf:object ?r2 ;
    dct:source ?srcX . 

    ?r2 rdf:type rdf:Statement ;
    rdf:subject ?y ;
    rdf:predicate foaf:name ;
    rdf:object ?name ;
    dct:source ?srcY
    }
"""

rdf_Star_graph = """
    PREFIX ex:<http://example.org/>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    PREFIX dct:<http://purl.org/dc/terms/>

    ex:bob foaf:name "Bob" .
    <<ex:bob foaf:knows <<ex:alice foaf:name "Alice">>>> dct:creator <http://example.com/crawlers#c1> ;
    dct:source <http://example.net/bob.html> .

    <<ex:alice foaf:name "Alice">> dct:source <http://example.net/alice.html> .

    ex:welles foaf:name "John Welles" ;
                ex:mentioned ex:kubrick .
    ex:kubrick foaf:name "Stanley Kubrick" .
    <<ex:kubrick ex:influencedBy ex:welles>> dct:creator <http://example.com/names#examples> ;
    dct:source <http://example.net/people.html> .

"""

sparql_star_query = """
    PREFIX ex:<http://example.org/>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf:<http://xmlns.com/foaf/0.1/>
    PREFIX dct:<http://purl.org/dc/terms/>

    SELECT ?x ?y ?srcX ?srcY WHERE 
    { <<ex:bob foaf:knows <<?y foaf:name ?name>>>> dct:source ?srcX . 
    <<?y foaf:name ?name>> dct:source ?srcY .}

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