import unittest
from tempfile import mktemp
from rdflib import ConjunctiveGraph, URIRef
from rdflib.store import VALID_STORE


class BerkeleyDBTestCase(unittest.TestCase):
    def setUp(self):
        self.store_name = "BerkeleyDB"
        self.path = mktemp()
        self.g = ConjunctiveGraph(store=self.store_name)
        self.rt = self.g.open(self.path, create=True)
        assert self.rt == VALID_STORE, "The underlying store is corrupt"
        assert (
            len(self.g) == 0
        ), "There must be zero triples in the graph just after store (file) creation"
        data = """
                PREFIX : <https://example.org/>

                :a :b :c .
                :d :e :f .
                :d :g :h .
                """
        self.g.parse(data=data, format="ttl")

    def tearDown(self):
        self.g.close()

    def test_write(self):
        assert (
            len(self.g) == 3
        ), "There must be three triples in the graph after the first data chunk parse"
        data2 = """
                PREFIX : <https://example.org/>
                
                :d :i :j .
                """
        self.g.parse(data=data2, format="ttl")
        assert (
            len(self.g) == 4
        ), "There must be four triples in the graph after the second data chunk parse"
        data3 = """
                PREFIX : <https://example.org/>
                
                :d :i :j .
                """
        self.g.parse(data=data3, format="ttl")
        assert (
            len(self.g) == 4
        ), "There must still be four triples in the graph after the thrd data chunk parse"

    def test_read(self):
        sx = None
        for s in self.g.subjects(
            predicate=URIRef("https://example.org/e"),
            object=URIRef("https://example.org/f"),
        ):
            sx = s
        assert sx == URIRef("https://example.org/d")

    def test_sparql_query(self):
        q = """
            PREFIX : <https://example.org/>
            
            SELECT (COUNT(*) AS ?c)
            WHERE { 
                :d ?p ?o .
            }"""

        c = 0
        for row in self.g.query(q):
            c = int(row.c)
        assert c == 2, "SPARQL COUNT must return 2"

    def test_sparql_insert(self):
        q = """
            PREFIX : <https://example.org/>
            
            INSERT DATA {
                :x :y :z .
            }"""

        self.g.update(q)
        assert len(self.g) == 4, "After extra triple insert, length must be 4"

    def test_multigraph(self):
        q = """
            PREFIX : <https://example.org/>

            INSERT DATA {
                GRAPH :m {
                    :x :y :z .
                }
                GRAPH :n {
                    :x :y :z .
                }                
            }"""

        self.g.update(q)

        q = """
            SELECT (COUNT(?g) AS ?c)
            WHERE {
                SELECT DISTINCT ?g
                WHERE {
                    GRAPH ?g {
                        ?s ?p ?o 
                    }
                }
            }
            """
        c = 0
        for row in self.g.query(q):
            c = int(row.c)
        assert c == 3, "SPARQL COUNT must return 3 (default, :m & :n)"

    def test_open_shut(self):
        assert len(self.g) == 3, "Initially we must have 3 triples from setUp"
        self.g.close()
        self.g = None

        # reopen the graph
        self.g = ConjunctiveGraph("BerkeleyDB")
        self.g.open(self.path, create=False)
        assert (
            len(self.g) == 3
        ), "After close and reopen, we should still have the 3 originally added triples"
