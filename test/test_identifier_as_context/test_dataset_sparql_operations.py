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

    dataset = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(dataset) == 0

    # The default graph is already instantiated so the length of dataset.graphs() == 1
    assert len(list(dataset.graphs())) == 1

    # Only the default graph exists and is yielded by dataset.graphs() (or by dataset.contexts())
    assert (
        str(list(dataset.graphs()))
        == "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
    )

    # Only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in dataset.graphs()) == set(
        [DATASET_DEFAULT_GRAPH_ID]
    )

    dataset_default_graph = dataset.get_context(DATASET_DEFAULT_GRAPH_ID)

    assert (
        str(dataset_default_graph)
        == "<urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    # Namespace bindings for clarity of output
    dataset.bind("urn", URIRef("urn:"))
    dataset.bind("ex", URIRef("urn:example:"))
    dataset.bind("rdflib", URIRef("urn:x-rdflib:"))

    # 1. SPARQL update add quad, specifying the default graph
    dataset.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:default> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )
    # The default graph is the only graph in the dataset so the length of dataset.graphs() == 1
    assert len(list(dataset.graphs())) == 1
    # The default graph is the only graph in the dataset so the length of dataset.graphs() == 1
    assert len(dataset.get_context(DATASET_DEFAULT_GRAPH_ID)) == 1

    # 2. SPARQL update add triple to unspecified (i.e. default) graph
    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:camembert> . } "
    )

    # The default graph is the only graph in the dataset so the length of dataset.graphs() == 1
    assert len(list(dataset.graphs())) == 1
    # Default graph has two triples
    assert len(dataset.get_context(DATASET_DEFAULT_GRAPH_ID)) == 2

    # 3. Add triple to new, BNODE-NAMED graph
    g = dataset.graph(BNode())

    # Store the graph id
    id_g = g.identifier

    # Add triple to new, BNODE-NAMED graph
    g.parse(
        data="<urn:example:bob> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    # Now there are two graphs in the Dataset
    assert len(list(dataset.graphs())) == 2

    # The Dataset keeps track of the constituent graphs
    del g

    # The Dataset still has two graphs
    assert len(list(dataset.graphs())) == 2

    # The graph can be retrieved from the dataset
    g = dataset.get_context(id_g)

    # And its content persists
    assert len(g) == 1

    # 4. Add a triple into a new unspecified graph
    g = dataset.graph()
    g.parse(
        data="<urn:example:michel> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    # Now there are three graphs in the Dataset
    assert len(list(dataset.graphs())) == 3

    # 5. Add quad with NAMED graph into new, BNode-NAMED graph (wierd but true)
    g = dataset.graph()

    g.parse(
        data="<urn:example:michel> <urn:example:hates> <urn:example:pizza> <urn:example:context-3> .",
        format="nquads",
    )

    # g is empty, the triple was stored in the named graph urn:example:context-3 as specified in the data
    assert len(g) == 0
    assert len(dataset.get_context(URIRef("urn:example:context-3"))) == 1

    # So there are now 5 contexts, one empty as a consequence of creating
    # a new BNode-named graph and adding a quad with a different NAMED graph
    assert len(list(dataset.graphs())) == 5

    # 6. Add triple with a specified PUBLICID
    dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:michel> .",
        format="ttl",
        publicID="urn:example:context-4",
    )

    # There are now 6 graphs
    assert len(list(dataset.graphs())) == 6

    # 7. Monkeypatch for illustration of alternative way of adding triples to the default graph
    dataset.default_graph = dataset.default_context
    dataset.default_graph.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    # Still 6 graphs
    assert len(list(dataset.graphs())) == 6

    # 8. SPARQL update add triple in a new, NAMED graph
    dataset.update(
        "INSERT DATA { GRAPH <urn:example:context-1> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )

    # Now 7 graphs
    assert len(list(dataset.graphs())) == 7

    # SPARQL update of NAMED graph"
    dataset.update(
        "INSERT DATA { GRAPH <urn:example:context-1> { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . } }"
    )

    # Still 7 graphs
    assert len(list(dataset.graphs())) == 7

    dataset.remove_graph(c1)

    # One fewer graphs in the Dataset
    assert len(list(dataset.graphs())) == 6

    dataset.add_graph(c1)

    assert c1 in list(dataset.store.contexts())


def test_dataset_default_graph_and_contexts():
    dataset = Dataset()
    dataset.bind("", URIRef("urn:x-rdflib:"))

    # ADD ONE TRIPLE *without context* to the default graph

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:pizza> . }"
    )

    # There is now one triple in the default graph, so dataset length == 1
    assert len(dataset) == 1

    r = dataset.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "one person likes pizza"

    assert str(dataset.serialize(format="trig")) == str(
        "@prefix : <urn:x-rdflib:> .\n@prefix ns1: <urn:example:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"
    )


def test_dataset_contexts():
    dataset = Dataset()
    dataset.bind("", URIRef("urn:x-rdflib:"))

    # The default graph is a context so the length of dataset.contexts() should be 1
    assert len(list(dataset.contexts())) == 1

    # Insert statement into the default graph
    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:pizza> . }"
    )

    # Inserting into the default graph should not create a new context so the length of
    # dataset.contexts() should still be 1
    assert len(list(dataset.contexts())) == 1

    # Only the default graph exists and is yielded by dataset.contexts()

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in dataset.contexts()) == set(
        [DATASET_DEFAULT_GRAPH_ID]
    )

    # There is now one triple in the default graph, so dataset length should be 1
    assert len(dataset) == 1

    r = dataset.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "one person likes pizza"

    assert str(dataset.serialize(format="trig")) == str(
        "@prefix : <urn:x-rdflib:> .\n@prefix ns1: <urn:example:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"
    )

    # Insert into the NAMED default graph
    dataset.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:default> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = dataset.query(
        "SELECT * WHERE { ?s <urn:example:likes> <urn:example:cheese> . }"
    )

    assert len(list(r)) == 1, "one person likes cheese"

    # There is now two triples in the default graph, so dataset length == 2
    assert len(dataset) == 2

    # removing default graph removes triples but not actual graph
    dataset.update("CLEAR DEFAULT")

    assert len(dataset) == 0

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in dataset.contexts()) == set(
        [DATASET_DEFAULT_GRAPH_ID]
    )


def test_add_graph_content_to_dataset_default_graph_via_sparqlupdate():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )

    assert len(list(dataset.contexts())) == 1


def test_add_graph_content_to_dataset_named_default_via_sparqlupdate():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:default> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )
    assert len(list(dataset.contexts())) == 1


def test_add_graph_as_new_dataset_subgraph_via_sparqlupdate():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:context1> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )
    assert len(list(dataset.contexts())) == 2
