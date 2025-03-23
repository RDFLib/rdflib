from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDFS
from test.data import BOB, CHEESE, HATES, LIKES, MICHEL, PIZZA, TAREK

EX = Namespace("http://example.org/")


class TestGraphSlice:
    def test_slice(self):
        """
        We pervert the slice object, and use start, stop, step as subject, predicate,
        object

        All operations return generators over full triples
        """

        def sl(x):
            return len(list(x))

        def soe(x, y):
            return set([a[2] for a in x]) == set(y)  # equals objects

        g = Graph()
        g.add((TAREK, LIKES, PIZZA))
        g.add((TAREK, LIKES, CHEESE))
        g.add((MICHEL, LIKES, PIZZA))
        g.add((MICHEL, LIKES, CHEESE))
        g.add((BOB, LIKES, CHEESE))
        g.add((BOB, HATES, PIZZA))
        g.add((BOB, HATES, MICHEL))  # gasp!

        # Single terms are all trivial:

        # single index slices by subject, i.e. return triples((x,None,None))
        # tell me everything about "TAREK"
        assert sl(g[TAREK]) == 2

        # single slice slices by s,p,o, with : used to split
        # tell me everything about "TAREK" (same as above)
        assert sl(g[TAREK::]) == 2

        # give me every "LIKES" relationship
        assert sl(g[:LIKES:]) == 5

        # give me every relationship to PIZZA
        assert sl(g[::PIZZA]) == 3

        # give me everyone who LIKES PIZZA
        assert sl(g[:LIKES:PIZZA]) == 2

        # does TAREK like PIZZA?
        assert sorted(next(g[TAREK:LIKES:PIZZA])) == sorted(
            (
                URIRef("urn:example:tarek"),
                URIRef("urn:example:likes"),
                URIRef("urn:example:pizza"),
            )
        )

        # More intesting is using paths

        # everything hated or liked
        assert sl(g[: HATES | LIKES]) == 7


def test_graph_slice_eg():
    g = Graph()
    g.add((URIRef("urn:bob"), RDFS.label, Literal("Bob")))
    assert sorted(list(g[URIRef("urn:bob")])) == sorted(
        [(URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal("Bob"))]
    )

    assert sorted(list(g[: RDFS.label])) == sorted(
        [(URIRef("urn:bob"), Literal("Bob"))]
    )

    assert sorted(list(g[:: Literal("Bob")])) == sorted(
        [(URIRef("urn:bob"), URIRef("http://www.w3.org/2000/01/rdf-schema#label"))]
    )


def test_graph_slice_all():
    g = Graph()
    g.parse(
        data="""
        PREFIX ex: <http://example.org/>

        ex:a ex:b ex:c .
        ex:a ex:d ex:e .
        ex:f ex:b ex:c .
        ex:g ex:b ex:h .
        """
    )

    assert len(list(g[EX.a])) == 2

    assert len(list(g[EX.f])) == 1

    assert len(list(g[: EX.b])) == 3

    assert len(list(g[:: EX.c])) == 2

    assert len(list(g[EX.a : EX.b : EX.c])) == 1

    assert sorted(list(g[EX.a])) == sorted(list(g.predicate_objects(EX.a)))
