from rdflib.graph import Graph
from rdflib.term import BNode, URIRef
from rdflib.plugins.parsers.notation3 import LOG_implies_URI

DATA = """
@prefix : <http://example.org/#>.

:a :b _:c.
{ :a :b _:c } => { :b :c _:c }.
"""

LOG = URIRef(LOG_implies_URI)

class TestBlankNodesInFormulas:
    def test_bnodes_in_a_formula_are_the_same(self):
        g = Graph().parse(data=DATA, format="n3")
        assert len(g) == 2
        formula = next(g.triples((None, LOG, None)))
        assert len(formula) == 3
        head, _, body = formula
        assert len(head) == 1
        head_clause = next(iter(head))
        assert isinstance(head_clause, tuple)
        assert isinstance(head_clause[2], BNode)
        assert len(body) == 1
        body_clause = next(iter(body))
        assert isinstance(head_clause, tuple)
        assert head_clause[2] == body_clause[2]

    def test_bnodes_in_a_formula_and_parent_graph_are_the_same(self):
        g = Graph().parse(data=DATA, format="n3")
        assert len(g) == 2
        for triples in g:
            if triples[1] == LOG:
                formula = triples
            else:
                fact = triples
        head, _, _ = formula
        assert len(head) == 1
        head_clause = next(iter(head))
        assert isinstance(fact[2], BNode)
        assert fact[2] == head_clause[2]
