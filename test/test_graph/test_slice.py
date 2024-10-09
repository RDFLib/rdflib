from rdflib import Graph
from test.data import BOB, CHEESE, HATES, LIKES, MICHEL, PIZZA, TAREK


class TestGraphSlice:
    def test_slice(self):
        """
        We pervert the slice object,
        and use start, stop, step as subject, predicate, object

        all operations return generators over full triples
        """

        def sl(x, y):
            return len(list(x)) == y

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
        sl(g[TAREK], 2)

        # single slice slices by s,p,o, with : used to split
        # tell me everything about "TAREK" (same as above)
        sl(g[TAREK::], 2)

        # give me every "LIKES" relationship
        sl(g[:LIKES:], 5)

        # give me every relationship to PIZZA
        sl(g[::PIZZA], 3)

        # give me everyone who LIKES PIZZA
        sl(g[:LIKES:PIZZA], 2)

        # does TAREK like PIZZA?
        assert g[TAREK:LIKES:PIZZA] is True

        # More intesting is using paths

        # everything hated or liked
        sl(g[: HATES | LIKES], 7)
