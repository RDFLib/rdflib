from rdflib import (
    logger,
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
        == 2
    ), "Should be just the one"

    logger.debug(
        f'{list(ds.graphs((URIRef("urn:example:bob"), URIRef("urn:example:likes"), URIRef("urn:example:pizza"))))}'
    )

    logger.debug(f"DS:\n{ds.serialize(format='trig')}")

    logger.debug(
        f"DSD:\n{ds.get_context(DATASET_DEFAULT_GRAPH_ID).serialize(format='trig')}"
    )

    logger.debug(f"DSG:\n{ds.get_context(id_g).serialize(format='trig')}")
