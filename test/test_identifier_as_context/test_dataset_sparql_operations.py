from rdflib import (
    BNode,
    Dataset,
    URIRef,
)
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")


def test_dataset_operations():

    ds = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is already instantiated so the length of ds.graphs() == 1
    assert len(list(ds.graphs())) == 1

    # Only the default graph exists and is yielded by ds.graphs() (or by ds.contexts())
    assert (
        str(list(ds.graphs()))
        == "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
    )

    # Only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.graphs()) == set([DATASET_DEFAULT_GRAPH_ID])

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)

    assert (
        str(dataset_default_graph)
        == "<urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    # Namespace bindings for clarity of output
    ds.bind("urn", URIRef("urn:"))
    ds.bind("ex", URIRef("urn:example:"))
    ds.bind("rdflib", URIRef("urn:x-rdflib:"))

    # 1. SPARQL update add quad, specifying the default graph
    ds.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:default> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )
    # The default graph is the only graph in the dataset so the length of ds.graphs() == 1
    assert len(list(ds.graphs())) == 1
    # The default graph is the only graph in the dataset so the length of ds.graphs() == 1
    assert len(ds.get_context(DATASET_DEFAULT_GRAPH_ID)) == 1

    # 2. SPARQL update add triple to unspecified (i.e. default) graph
    ds.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:camembert> . } "
    )

    # The default graph is the only graph in the dataset so the length of ds.graphs() == 1
    assert len(list(ds.graphs())) == 1
    # Default graph has two triples
    assert len(ds.get_context(DATASET_DEFAULT_GRAPH_ID)) == 2

    # 3. Add triple to new, BNODE-NAMED graph
    g = ds.graph(BNode())

    # Store the graph id
    id_g = g.identifier

    # Add triple to new, BNODE-NAMED graph
    g.parse(
        data="<urn:example:bob> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    # Now there are two graphs in the Dataset
    assert len(list(ds.graphs())) == 2

    # The Dataset keeps track of the constituent graphs
    del g

    # The Dataset still has two graphs
    assert len(list(ds.graphs())) == 2

    # The graph can be retrieved from the dataset
    g = ds.get_context(id_g)

    # And its content persists
    assert len(g) == 1

    # 4. Add a triple into a new unspecified graph
    g = ds.graph()
    g.parse(
        data="<urn:example:michel> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    # Now there are three graphs in the Dataset
    assert len(list(ds.graphs())) == 3

    # 5. Add quad with NAMED graph into new, BNode-NAMED graph (wierd but true)
    g = ds.graph()

    g.parse(
        data="<urn:example:michel> <urn:example:hates> <urn:example:pizza> <urn:example:context-3> .",
        format="nquads",
    )

    # g is empty, the triple was stored in the named graph urn:example:context-3 as specified in the data
    assert len(g) == 0
    assert len(ds.get_context(URIRef("urn:example:context-3"))) == 1

    # So there are now 5 contexts, one empty as a consequence of creating
    # a new BNode-named graph and adding a quad with a different NAMED graph
    assert len(list(ds.graphs())) == 5

    # 6. Add triple with a specified PUBLICID
    ds.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:michel> .",
        format="ttl",
        publicID="urn:example:context-4",
    )

    # There are now 6 graphs
    assert len(list(ds.graphs())) == 6

    # 7. Monkeypatch for illustration of alternative way of adding triples to the default graph
    ds.default_graph = ds.default_context
    ds.default_graph.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    # Still 6 graphs
    assert len(list(ds.graphs())) == 6

    # 8. SPARQL update add triple in a new, NAMED graph
    ds.update(
        "INSERT DATA { GRAPH <urn:example:context-1> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )

    # Now 7 graphs
    assert len(list(ds.graphs())) == 7

    # SPARQL update of NAMED graph"
    ds.update(
        "INSERT DATA { GRAPH <urn:example:context-1> { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . } }"
    )

    # Still 7 graphs
    assert len(list(ds.graphs())) == 7

    ds.remove_graph(c1)

    # One fewer graphs in the Dataset
    assert len(list(ds.graphs())) == 6

    ds.add_graph(c1)

 
    assert c1 in list(ds.store.contexts())

