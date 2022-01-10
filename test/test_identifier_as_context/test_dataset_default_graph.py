from rdflib import Dataset, URIRef
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


def test_dataset_default_graph():
    dataset = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(dataset) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(dataset.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        str(list(dataset.contexts()))
        == "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
    )

    # Only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in dataset.contexts()) == set(
        [DATASET_DEFAULT_GRAPH_ID]
    )

    # A graph in the Dataset can be bound to a variable, operations on the variable are
    # operations on the Graph in the Dataset
    dataset_default_graph = dataset.get_context(DATASET_DEFAULT_GRAPH_ID)

    assert dataset == dataset_default_graph

    assert (
        str(dataset_default_graph)
        == "<urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    assert str(dataset_default_graph.serialize(format="xml")) == str(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<rdf:RDF\n"
        '   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        ">\n"
        "</rdf:RDF>\n"
    )

    dataset_default_graph.add((tarek, likes, pizza))

    assert (
        len(dataset) == 1
    )  # Dataset is responsible for tracking changes to constituents


def test_removal_of_dataset_default_graph():

    ds = Dataset()

    # ADD ONE TRIPLE *without context* to the default graph

    ds.add((tarek, likes, pizza))

    # There is now one triple in the default graph, so dataset length == 1
    assert len(ds) == 1

    # Removing default graph removes triples but not the actual graph
    ds.remove_graph(DATASET_DEFAULT_GRAPH_ID)

    assert len(ds) == 0

    # Default graph still exists
    assert set(context.identifier for context in ds.contexts()) == set(
        [DATASET_DEFAULT_GRAPH_ID]
    )


def test_serialization_of_dataset_default_graph():
    ds = Dataset()

    # Serialization of the empty dataset is sane
    ds.bind("", URIRef("urn:x-rdflib:"))

    assert str(ds.serialize(format="trig")) == str("@prefix : <urn:x-rdflib:> .\n\n")

    assert str(ds.serialize(format="nquads")) == str("\n")

    assert str(ds.serialize(format="json-ld")) == str("[]")

    assert str(ds.serialize(format="hext")) == str("")

    assert str(ds.serialize(format="trix")) == str(
        '<?xml version="1.0" encoding="utf-8"?>\n<TriX\n'
        '  xmlns:brick="https://brickschema.org/schema/Brick#"\n'
        '  xmlns:csvw="http://www.w3.org/ns/csvw#"\n'
        '  xmlns:dc="http://purl.org/dc/elements/1.1/"\n'
        '  xmlns:dcat="http://www.w3.org/ns/dcat#"\n'
        '  xmlns:dcmitype="http://purl.org/dc/dcmitype/"\n'
        '  xmlns:dcterms="http://purl.org/dc/terms/"\n'
        '  xmlns:dcam="http://purl.org/dc/dcam/"\n'
        '  xmlns:doap="http://usefulinc.com/ns/doap#"\n'
        '  xmlns:foaf="http://xmlns.com/foaf/0.1/"\n'
        '  xmlns:odrl="http://www.w3.org/ns/odrl/2/"\n'
        '  xmlns:geo="http://www.opengis.net/ont/geosparql#"\n'
        '  xmlns:org="http://www.w3.org/ns/org#"\n'
        '  xmlns:owl="http://www.w3.org/2002/07/owl#"\n'
        '  xmlns:prof="http://www.w3.org/ns/dx/prof/"\n'
        '  xmlns:prov="http://www.w3.org/ns/prov#"\n'
        '  xmlns:qb="http://purl.org/linked-data/cube#"\n'
        '  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        '  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n'
        '  xmlns:schema="https://schema.org/"\n'
        '  xmlns:sh="http://www.w3.org/ns/shacl#"\n'
        '  xmlns:skos="http://www.w3.org/2004/02/skos/core#"\n'
        '  xmlns:sosa="http://www.w3.org/ns/sosa/"\n'
        '  xmlns:ssn="http://www.w3.org/ns/ssn/"\n'
        '  xmlns:time="http://www.w3.org/2006/time#"\n'
        '  xmlns:vann="http://purl.org/vocab/vann/"\n'
        '  xmlns:void="http://rdfs.org/ns/void#"\n'
        '  xmlns:xsd="http://www.w3.org/2001/XMLSchema#"\n'
        '  xmlns:xml="http://www.w3.org/XML/1998/namespace"\n'
        '  xmlns="http://www.w3.org/2004/03/trix/trix-1/"\n>'
        "\n"
        "  <graph>\n"
        "    <uri>urn:x-rdflib:default</uri>\n"
        "  </graph>\n</TriX>\n"
    )

    # ADD ONE TRIPLE *without context* to the default graph

    ds.add((tarek, likes, pizza))

    # There is now one triple in the default graph, so dataset length == 1
    assert len(ds) == 1

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        str(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
    )

    # Pro tem, cater for Dataset initialisation with identifier as DATASET_DEFAULT_GRAPH_ID
    # and without.

    # "With" yields the first output, "without" yields the second output in which
    # a "default" keyword is included.

    assert str(ds.serialize(format="trig")) in [
        "@prefix : <urn:x-rdflib:> .\n\n{\n    :tarek :likes :pizza .\n}\n\n",
        "@prefix : <urn:x-rdflib:> .\n\n:default {\n    :tarek :likes :pizza .\n}\n\n",
        "@prefix : <urn:x-rdflib:> .\n@prefix ns1: <urn:example:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n",
    ]

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)

    assert str(dataset_default_graph.serialize(format="xml")) == str(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<rdf:RDF\n"
        '   xmlns:ns1="urn:example:"\n'
        '   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        ">\n"
        '  <rdf:Description rdf:about="urn:example:tarek">\n'
        '    <ns1:likes rdf:resource="urn:example:pizza"/>\n'
        "  </rdf:Description>\n"
        "</rdf:RDF>"
        "\n"
    )

    # For exhaustive completeness: The default graph behaves as a Graph -
    assert str(dataset_default_graph.serialize(format="ttl")) == str(
        "@prefix ns1: <urn:example:> .\n\nns1:tarek ns1:likes ns1:pizza .\n\n"
    )

    assert str(dataset_default_graph.serialize(format="json-ld")) == str(
        "[\n"
        "  {\n"
        '    "@graph": [\n'
        "      {\n"
        '        "@id": "urn:example:tarek",\n'
        '        "urn:example:likes": [\n'
        "          {\n"
        '            "@id": "urn:example:pizza"\n'
        "          }\n"
        "        ]\n"
        "      }\n"
        "    ],\n"
        '    "@id": "urn:x-rdflib:default"\n'
        "  }\n"
        "]"
    )
