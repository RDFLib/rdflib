from test.data import *

import pytest

from rdflib import BNode, Dataset, Graph, URIRef, logger
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


def test_dataset_contexts_with_triple():

    ds = Dataset()

    # Namespace bindings for clarity of output
    ds.bind("urn", URIRef("urn:"))
    ds.bind("ex", URIRef("urn:example:"))
    ds.bind("rdflib", URIRef("urn:x-rdflib:"))

    # 1. SPARQL update add quad, specifying the default graph
    ds.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:default> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )

    # 2. SPARQL update add triple to unspecified (i.e. default) graph
    ds.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:camembert> . } "
    )

    # 3. Create new BNODE-NAMED graph
    g = ds.graph(BNode())

    id_g = g.identifier

    # Add triple to new BNODE-NAMED graph
    g.parse(
        data="<urn:example:bob> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    assert (
        len(
            list(
                ds.graphs(
                    (
                        URIRef("urn:example:bob"),
                        URIRef("urn:example:likes"),
                        URIRef("urn:example:pizza"),
                    )
                )
            )
        )
        == 1
    ), "Should be just the one"

    logger.debug(
        f'{list(ds.graphs((URIRef("urn:example:bob"), URIRef("urn:example:likes"), URIRef("urn:example:pizza"))))}'
    )

    logger.debug(f"DS:\n{ds.serialize(format='trig')}")

    logger.debug(
        f"DSD:\n{ds.get_context(DATASET_DEFAULT_GRAPH_ID).serialize(format='trig')}"
    )

    logger.debug(f"DSG:\n{ds.get_context(id_g).serialize(format='trig')}")


def test_dataset_operations():

    dataset = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(dataset) == 0

    # The default graph is not treated as a context
    assert len(list(dataset.contexts())) == 0
    assert str(list(dataset.contexts())) == "[]"
    # But it does exist
    assert dataset.default_graph is not None
    assert type(dataset.default_graph) is Graph
    assert len(dataset.default_graph) == 0

    # Only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert dataset.default_graph.identifier == DATASET_DEFAULT_GRAPH_ID

    dataset_default_graph = dataset.graph(DATASET_DEFAULT_GRAPH_ID)

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
    assert len(list(dataset.graphs())) == 0
    # The default graph is the only graph in the dataset so the length of dataset.graphs() == 1
    assert len(dataset.graph(DATASET_DEFAULT_GRAPH_ID)) == 1

    # 2. SPARQL update add triple to unspecified (i.e. default) graph
    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:camembert> . } "
    )

    assert len(list(dataset.contexts())) == 0
    # Default graph has two triples
    assert len(dataset.graph(DATASET_DEFAULT_GRAPH_ID)) == 2

    # 3. Add triple to new, BNODE-NAMED graph
    g = dataset.graph(BNode())
    # Store the graph id
    id_g = g.identifier
    # Add triple to new, BNODE-NAMED graph
    g.parse(
        data="<urn:example:bob> <urn:example:likes> <urn:example:pizza> .", format="ttl"
    )
    # Now there a new context in the Dataset
    assert len(list(dataset.contexts())) == 1
    # The Dataset keeps track of the constituent graphs
    del g
    # The Dataset still has one context
    assert len(list(dataset.contexts())) == 1
    # The graph can be retrieved from the dataset
    g = dataset.graph(id_g)
    # And its content persists
    assert len(g) == 1

    # 4. Add a triple into a new unspecified graph
    g = dataset.graph()
    g.parse(
        data="<urn:example:michel> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    # Now there are two contexts in the Dataset
    assert len(list(dataset.contexts())) == 2

    # 5. Add quad with NAMED graph into new, BNode-referenced context (wierd but true)
    g = dataset.graph()

    g.parse(
        data="<urn:example:michel> <urn:example:hates> <urn:example:pizza> <urn:example:context-3> .",
        format="nquads",
    )

    # g is empty, the triple was stored in the named graph urn:example:context-3 as specified in the data
    assert len(g) == 0
    assert len(dataset.graph(URIRef("urn:example:context-3"))) == 1

    # There are now 4 contexts, one empty as the consequence of creating
    # a new BNode-referenced context and one created by adding a quad with
    # a new NAMED graph
    assert len(list(dataset.contexts())) == 4

    # 6. Add triple with a specified PUBLICID
    dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:michel> .",
        format="ttl",
        publicID="urn:example:context-4",
    )

    # There are now 5 contexts
    assert len(list(dataset.contexts())) == 5

    # 7. Merely for illustration of an alternative way of adding triples to the default graph

    dataset.default_graph.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    # Still 5 contexts
    assert len(list(dataset.contexts())) == 5

    # 8. SPARQL update add triple in a new, NAMED graph
    dataset.update(
        "INSERT DATA { GRAPH <urn:example:context-1> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )

    # Now 6 contexts
    assert len(list(dataset.contexts())) == 6

    # SPARQL update of context (i.e. NAMED graph)
    dataset.update(
        "INSERT DATA { GRAPH <urn:example:context-1> { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . } }"
    )

    # Still 6 contexts
    assert len(list(dataset.contexts())) == 6

    dataset.remove_graph(context1)

    # One fewer contexts in the Dataset
    assert len(list(dataset.contexts())) == 5

    # Re-create the context
    dataset.graph(context1)

    assert context1 in list(dataset.store.contexts())


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

    assert (
        str(dataset.serialize(format="trig"))
        == "@prefix ns1: <urn:example:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"
    )


def test_dataset_contexts():
    dataset = Dataset()
    dataset.bind("", URIRef("urn:x-rdflib:"))

    # The default graph is not treated as a context
    assert len(list(dataset.graphs())) == 0

    # Insert statement into the default graph
    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:pizza> . }"
    )

    # Inserting into the default graph should not create a new context so the length of
    # dataset.graphs() should still be 0
    assert len(list(dataset.graphs())) == 0

    # Only the default graph exists and is yielded by dataset.graphs()

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(dataset.contexts()) == set()
    assert dataset.default_graph.identifier == DATASET_DEFAULT_GRAPH_ID

    # There is now one triple in the default graph, so dataset length should be 1
    assert len(dataset) == 1

    r = dataset.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "one person likes pizza"

    assert (
        str(dataset.serialize(format="trig"))
        == "@prefix ns1: <urn:example:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"
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
    assert set(dataset.contexts()) == set()

    assert dataset.default_graph.identifier == DATASET_DEFAULT_GRAPH_ID


def test_add_graph_content_to_dataset_default_graph_via_sparqlupdate():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )

    assert len(list(dataset.contexts())) == 0


def test_add_graph_content_to_dataset_named_default_via_sparqlupdate():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 0
    assert len(dataset) == 1

    dataset.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:default> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )
    assert len(list(dataset.contexts())) == 0
    assert len(dataset) == 2


def test_add_graph_as_new_dataset_subgraph_via_sparqlupdate():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 0
    assert len(dataset) == 1

    dataset.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:context1> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )
    assert len(list(dataset.contexts())) == 1
    assert len(dataset.graph(URIRef("urn:x-rdflib:context1"))) == 1


def test_union_insert():
    dataset = Dataset()

    """
    # https://stackoverflow.com/a/18450978

    INSERT { 
      GRAPH <[http://example/bookStore2]> { ?book ?p ?v }
    }
    WHERE{ 
      {
        GRAPH  <[http://example/bookStore]> {
          ?book dc:date ?date .
          FILTER ( ?date > "1970-01-01T00:00:00-02:00"^^xsd:dateTime )
          ?book ?p ?v
        }
      }
      UNION
      {
        GRAPH <[http://example/bookStore3]> {
          ?book dc:date ?date .
          FILTER ( ?date > "1980-01-01T00:00:00-02:00"^^xsd:dateTime )
          ?book ?p ?v
        }
      }
    }
    """

    sparqltext = """\
        INSERT { 
          GRAPH <urn:example:fratclub> { ?s ?p ?o }
        }
        WHERE{ 
          {
            GRAPH  <urn:example:frathouse1> {
              ?s p ?o .
              FILTER ( ?s == <urn:example:tarek> )
              ?s ?p ?o
            }
          }
          UNION
          {
            GRAPH <urn:example:frathouse2> {
              ?s ?p ?o .
              FILTER ( ?s > <urn:example:tarek> )
              ?s ?p ?o
            }
          }
        }
    """

    # dataset.update(sparqltext)
