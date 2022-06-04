from test.data import bob, cheese, hates, likes, michel, pizza, tarek

from rdflib import Graph


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
        g.add((tarek, likes, pizza))
        g.add((tarek, likes, cheese))
        g.add((michel, likes, pizza))
        g.add((michel, likes, cheese))
        g.add((bob, likes, cheese))
        g.add((bob, hates, pizza))
        g.add((bob, hates, michel))  # gasp!

        # Single terms are all trivial:

        # single index slices by subject, i.e. return triples((x,None,None))
        # tell me everything about "tarek"
        sl(g[tarek], 2)

        # single slice slices by s,p,o, with : used to split
        # tell me everything about "tarek" (same as above)
        sl(g[tarek::], 2)

        # give me every "likes" relationship
        sl(g[:likes:], 5)

        # give me every relationship to pizza
        sl(g[::pizza], 3)

        # give me everyone who likes pizza
        sl(g[:likes:pizza], 2)

        # does tarek like pizza?
        assert g[tarek:likes:pizza] is True

        # More intesting is using paths

        # everything hated or liked
        sl(g[: hates | likes], 7)
