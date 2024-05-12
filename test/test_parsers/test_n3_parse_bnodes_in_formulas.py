from rdflib.graph import Graph
from rdflib.term import BNode, URIRef

DATA = """
{ <http://example.org/#a> <http://example.org/#b> _:c } => { <http://example.org/#b> <http://example.org/#c> _:c }.
"""


class TestBlankNodesInFormulas:
    def test_bnodes_in_a_formula_are_the_same(self):
        g = Graph().parse(data=DATA, format="n3")
        assert len(g) == 1
        formula = next(iter(g))
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
