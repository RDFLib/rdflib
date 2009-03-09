
import unittest
from rdflib.Graph import Graph
from rdflib.StringInputSource import StringInputSource
import rdflib

class FakeBlankNode(object):
    def __cmp__(self, other):
        if other.__class__ == rdflib.BNode:
            return True
        return False

blank_node = FakeBlankNode()

def create_graph(n3data):
    '''
    @param n3data: data to create the graph from.
    @return: rdflib.Graph.Graph instance containing parsed graph.
    '''
    g = Graph()
    g.parse(StringInputSource(n3data), format='n3')
    return g

class TestSimpleQueries(unittest.TestCase):
    """
    http://www.w3.org/TR/rdf-sparql-query/#basicpatterns
    """

    def test_simple_query(self):
        '''
        http://www.w3.org/TR/rdf-sparql-query/#WritingSimpleQueries
        '''
        g = create_graph("""
<http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> "SPARQL Tutorial" .
        """)
        results = g.query("""
        SELECT ?title
        WHERE
        {
          <http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> ?title .
        }    
        """)
        result_data = list(results)
        self.assertEqual(len(result_data), 1)
        self.assertEqual(len(result_data[0]), 1)
        self.assertEqual(result_data[0][0], 'SPARQL Tutorial')
        self.assertEqual(result_data[0][0].__class__, rdflib.Literal)

    def test_multiple_matches(self):
        '''
        http://www.w3.org/TR/rdf-sparql-query/#MultipleMatches
        '''
        g = create_graph("""
        @prefix foaf:  <http://xmlns.com/foaf/0.1/> .

        _:a  foaf:name   "Johnny Lee Outlaw" .
        _:a  foaf:mbox   <mailto:jlow@example.com> .
        _:b  foaf:name   "Peter Goodguy" .
        _:b  foaf:mbox   <mailto:peter@example.org> .
        _:c  foaf:mbox   <mailto:carol@example.org> .
        """)
        results = list(g.query("""
        PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
        SELECT ?name ?mbox
        WHERE
          { ?x foaf:name ?name .
            ?x foaf:mbox ?mbox }
        """))
        expected_results = [
            (rdflib.Literal(name), rdflib.URIRef(mbox)) for name, mbox in 
            [("Johnny Lee Outlaw", "mailto:jlow@example.com"),
             ("Peter Goodguy", "mailto:peter@example.org")]]
        results.sort()
        expected_results.sort()
        self.assertEqual(results, expected_results)

    def test_blank_node_labels(self):
        """
        http://www.w3.org/TR/rdf-sparql-query/#BlankNodesInResults
        """
        g = create_graph("""
        @prefix foaf:  <http://xmlns.com/foaf/0.1/> .

        _:a  foaf:name   "Alice" .
        _:b  foaf:name   "Bob" .
        """)
        results = list(g.query("""
        PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
        SELECT ?x ?name
        WHERE  { ?x foaf:name ?name }
        """))
        col1, col2 = zip(*results)
        col1 = sorted(col1)
        col2 = sorted(col2)

        expected_results = sorted([
            rdflib.Literal("Alice"),
            rdflib.Literal("Bob"),
        ])
        self.assertEqual(col2, expected_results)
        self.assertNotEqual(col1[0], col1[1])
        self.assertEqual(col1[0].__class__, rdflib.BNode)

    def test_construct(self):
        """
        http://www.w3.org/TR/rdf-sparql-query/#constructGraph
        """

        g = create_graph("""
        @prefix org:    <http://example.com/ns#> .

        _:a  org:employeeName   "Alice" .
        _:a  org:employeeId     12345 .

        _:b  org:employeeName   "Bob" .
        _:b  org:employeeId     67890 .
        """)

        results = g.query("""
        PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
        PREFIX org:    <http://example.com/ns#>

        CONSTRUCT { ?x foaf:name ?name }
        WHERE  { ?x org:employeeName ?name }
        """)

        expected_results = g.create_graph("""
        @prefix org: <http://example.com/ns#> .
              
        _:x foaf:name "Alice" .
        _:y foaf:name "Bob" .
        """)

        self.assertEqual(results, expected_results)

class TestRDFLiterals(unittest.TestCase):
    """
    http://www.w3.org/TR/rdf-sparql-query/#matchingRDFLiterals
    """

    data = """
        @prefix dt:   <http://example.org/datatype#> .
        @prefix ns:   <http://example.org/ns#> .
        @prefix :     <http://example.org/ns#> .
        @prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

        :x   ns:p     "cat"@en .
        :y   ns:p     "42"^^xsd:integer .
        :z   ns:p     "abc"^^dt:specialDatatype .
        """

    def test_match_language_tags(self):
        '''
        http://www.w3.org/TR/rdf-sparql-query/#matchLangTags
        '''
        g = create_graph(self.data)
        results = list(g.query("""
        SELECT ?v WHERE { ?v ?p "cat" }
        """))
        expected_results = []
        self.assertEqual(results, expected_results)

    def test_match_literal_numeric_type(self):
        g = create_graph(self.data)
        results = list(g.query("""
        SELECT ?v WHERE { ?v ?p 42 }
        """))
        expected_results = [(rdflib.URIRef('http://example.org/ns#y'),)]
        self.assertEqual(results, expected_results)

    def test_match_literal_arbitary_type(self):
        g = create_graph(self.data)
        results = list(g.query("""
        SELECT ?v WHERE { ?v ?p "abc"^^<http://example.org/datatype#specialDatatype> }
        """))
        expected_results = [(rdflib.URIRef('http://example.org/ns#z'),)]
        self.assertEqual(results, expected_results)

class TestTermConstraints(unittest.TestCase):
    data = """
    @prefix dc:   <http://purl.org/dc/elements/1.1/> .
    @prefix :     <http://example.org/book/> .
    @prefix ns:   <http://example.org/ns#> .

    :book1  dc:title  "SPARQL Tutorial" .
    :book1  ns:price  42 .
    :book2  dc:title  "The Semantic Web" .
    :book2  ns:price  23 .
    """
    def test_string_values(self):
        g = create_graph(self.data)

        results = sorted(g.query("""
        PREFIX  dc:  <http://purl.org/dc/elements/1.1/>
        SELECT  ?title
        WHERE   { ?x dc:title ?title
                  FILTER regex(?title, "^SPARQL") 
                }
        """))
        expected_results = [(rdflib.Literal("SPARQL Tutorial"),)]
        self.assertEqual(results, expected_results)

    def test_case_insentitive(self):

        g = create_graph(self.data)

        results = sorted(g.query("""
        PREFIX  dc:  <http://purl.org/dc/elements/1.1/>
        SELECT  ?title
        WHERE   { ?x dc:title ?title
                  FILTER regex(?title, "web", "i" ) 
                }
        """))
        expected_results = [(rdflib.Literal("The Semantic Web"),)]
        self.assertEqual(results, expected_results)

    def test_numeric_values(self):

        g = create_graph(self.data)

        results = sorted(g.query("""
        PREFIX  dc:  <http://purl.org/dc/elements/1.1/>
        PREFIX  ns:  <http://example.org/ns#>
        SELECT  ?title ?price
        WHERE   { ?x ns:price ?price .
                  FILTER (?price < 30.5)
                  ?x dc:title ?title . }
        """))
        expected_results = [(rdflib.Literal("The Semantic Web"), rdflib.Literal(23))]
        self.assertEqual(results, expected_results)


if __name__ == '__main__':
    unittest.main()
