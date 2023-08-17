from rdflib.graph import Graph
from rdflib.namespace import RDF
from rdflib.plugins.parsers.rdfxml import CORE_SYNTAX_TERMS
from rdflib.term import BNode, Literal, URIRef

"""
Ah... it's coming back to me...
[6:32p] eikeon: think it's so transitivity holds...
[6:32p] eikeon: if a==b and b==c then a should == c
[6:32p] eikeon: "foo"==Literal("foo")
[6:33p] eikeon: We don't want URIRef("foo")==Literal("foo")
[6:33p] eikeon: But if we have URIRef("foo")=="foo" then it implies it.
[6:33p] chimezie: yes, definately not the other RDFLib 'typed' RDF (and N3) terms
[6:34p] eikeon: Why do you need URIRef("foo")=="foo" ?
[6:34p] chimezie: i'm just wondering if a URI and a string with the same lexical value, are by definition 'different'
[6:35p] eikeon: Think so, actually. Think of trying to serialize some triples.
[6:36p] eikeon: If they are the same you'd serialize them the same, no?
[6:36p] chimezie: I guess I was thinking of a 'string' in a native datatype sense, not in the RDF sense (where they would be distinctly different)
[6:37p] eikeon: We should try and brain dump some of this...
[6:37p] eikeon: it look a fairly long time to work out.
[6:37p] eikeon: But think we finally landed in the right spot.
[6:38p] eikeon: I know many of the backends break if URIRef("foo")==Literal("foo")
[6:39p] eikeon: And if we want "foo"==Literal("foo") --- then we really can't have URIRef("foo") also == "foo"
"""


class TestIdentifierEquality:
    def setup_method(self):
        self.uriref = URIRef("http://example.org/")
        self.bnode = BNode()
        self.literal = Literal("http://example.org/")
        self.python_literal = "http://example.org/"
        self.python_literal_2 = "foo"

    def testA(self):
        assert self.uriref != self.literal

    def testB(self):
        assert self.literal != self.uriref

    def testC(self):
        assert self.uriref != self.python_literal

    def testD(self):
        assert self.python_literal != self.uriref

    def testE(self):
        assert self.literal != self.python_literal

    def testE2(self):
        assert self.literal.eq(self.python_literal)

    def testF(self):
        assert self.python_literal != self.literal

    def testG(self):
        assert "foo" not in CORE_SYNTAX_TERMS

    def testH(self):
        assert (
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#RDF")
            in CORE_SYNTAX_TERMS
        )

    def testI(self):
        g = Graph()
        g.add((self.uriref, RDF.value, self.literal))
        g.add((self.uriref, RDF.value, self.uriref))
        assert len(g) == 2
