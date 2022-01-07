import pytest
from rdflib import (
    Dataset,
    URIRef,
)

tarek = URIRef("urn:example:tarek")
likes = URIRef("urn:example:likes")
pizza = URIRef("urn:example:pizza")
michel = URIRef("urn:example:michel")
cheese = URIRef("urn:example:cheese")

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")


def test_dataset_contexts_with_triple():
    ds = Dataset()

    ds.add((tarek, likes, pizza))

    g1 = ds.graph(c1)
    g1.add((tarek, likes, cheese))
    g1.add((michel, likes, tarek))

    g2 = ds.graph(c2)
    g2.add((michel, likes, cheese))
    g2.add((michel, likes, pizza))

    assert len(list(ds.contexts((michel, likes, cheese)))) == 2  # Is only in one graph

    with pytest.raises(AssertionError):
        assert len(list(ds.contexts((michel, likes, cheese)))) == 1

    assert (
        str(list(ds.contexts((michel, likes, cheese))))
        == "[<Graph identifier=urn:example:context-2 (<class 'rdflib.graph.Graph'>)>, <Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
    )  # Should yield only urn:example:context-2

    with pytest.raises(AssertionError):
        assert (
            str(list(ds.contexts((michel, likes, cheese))))
            == "[<Graph identifier=urn:example:context-2 (<class 'rdflib.graph.Graph'>)>]"
        )

    assert len(list(ds.contexts((None, likes, None)))) == 1  # Is in all 3 graphs

    with pytest.raises(AssertionError):
        assert len(list(ds.contexts((None, likes, None)))) == 3

    assert (
        str(list(ds.contexts((None, likes, None))))
        == "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
    )  # Should yield all three graphs

    with pytest.raises(AssertionError):
        assert (
            str(list(ds.contexts((michel, likes, cheese))))
            == "[<Graph identifier=urn:example:context-2 (<class 'rdflib.graph.Graph'>)>, [<Graph identifier=urn:example:context-1 (<class 'rdflib.graph.Graph'>)>, <Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
        )
