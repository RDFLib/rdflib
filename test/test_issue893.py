import pickle

from rdflib.graph import Dataset
from rdflib.namespace import Namespace


def test_issue893_ds_unpickle():
    example = Namespace("http://example.com#")

    ds1 = Dataset()
    one = ds1.graph(example.one)

    one.add((example.dan, example.knows, example.lisa))
    one.add((example.lisa, example.knows, example.dan))

    two = ds1.graph(example.two)

    two.add((example.ben, example.knows, example.lisa))
    two.add((example.lisa, example.knows, example.ben))

    assert set(ds1.quads((None, None, None, None))) == set(
        ds1.quads((None, None, None, None))
    )

    picklestring = pickle.dumps(ds1)
    ds2 = pickle.loads(picklestring)

    ds1graphs = list(ds1.graphs())
    ds2graphs = list(ds2.graphs())

    ds1graphs.sort()
    ds2graphs.sort()

    for new_graph, graph in zip(ds2graphs, ds1graphs):
        assert new_graph.identifier == graph.identifier
        for new_triple, triple in zip(
            new_graph.triples((None, None, None)), graph.triples((None, None, None))
        ):
            assert new_triple in graph.triples((None, None, None))
            assert triple in new_graph.triples((None, None, None))
