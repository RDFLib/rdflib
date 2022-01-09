import pytest
from rdflib import BNode, ConjunctiveGraph, Dataset, Graph, URIRef
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


def test_simple_dataset_default_graph_and_contexts_programmatic_modelling():
    ds = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        str(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
    )

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)

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


def test_serialization_of_simple_dataset_default_graph_and_contexts_programmatic_modelling():
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


def test_removal_of_simple_dataset_default_graph_and_contexts_programmatic_modelling():

    ds = Dataset()

    # ADD ONE TRIPLE *without context* to the default graph

    ds.add((tarek, likes, pizza))

    # There is now one triple in the default graph, so dataset length == 1
    assert len(ds) == 1

    # removing default graph removes triples but not actual graph
    ds.remove_graph(DATASET_DEFAULT_GRAPH_ID)

    assert len(ds) == 0

    # default still exists
    assert set(context.identifier for context in ds.contexts()) == set(
        [DATASET_DEFAULT_GRAPH_ID]
    )


def test_simple_dataset_default_graph_and_contexts_sparql_modelling():
    ds = Dataset()
    ds.bind("", URIRef("urn:x-rdflib:"))

    # ADD ONE TRIPLE *without context* to the default graph

    ds.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:pizza> . }"
    )

    # There is now one triple in the default graph, so dataset length == 1
    assert len(ds) == 1

    r = ds.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "one person likes pizza"

    assert str(ds.serialize(format="trig")) == str(
        "@prefix : <urn:x-rdflib:> .\n@prefix ns1: <urn:example:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"
    )


def test_simple_dataset_contexts_sparql_modelling():
    ds = Dataset()
    ds.bind("", URIRef("urn:x-rdflib:"))

    # The default graph is a context so the length of ds.contexts() should be 1
    assert len(list(ds.contexts())) == 1

    # Insert statement into the default graph
    ds.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:pizza> . }"
    )

    # Inserting into the default graph should not create a new context so the length of
    # ds.contexts() should still be 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])

    # There is now one triple in the default graph, so dataset length should be 1
    assert len(ds) == 1

    r = ds.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "one person likes pizza"

    assert str(ds.serialize(format="trig")) == str(
        "@prefix : <urn:x-rdflib:> .\n@prefix ns1: <urn:example:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"
    )

    # Insert into the NAMED default graph
    ds.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:default> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = ds.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:cheese> . }")

    assert len(list(r)) == 1, "one person likes cheese"

    # There is now two triples in the default graph, so dataset length == 2
    assert len(ds) == 2

    # removing default graph removes triples but not actual graph
    ds.update("CLEAR DEFAULT")

    assert len(ds) == 0

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])


def test_dataset_add_graph():

    data = """
    <http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
    <http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
    """

    ds = Dataset()

    subgraph_identifier = URIRef("urn:x-rdflib:subgraph1")

    g = ds.graph(subgraph_identifier)

    g.parse(data=data, format="n3")

    assert len(g) == 2

    subgraph = ds.get_context(subgraph_identifier)

    assert type(subgraph) is Graph

    assert len(subgraph) == 2


def test_dataset_equal_to_dataset_default():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    default_graph = dataset.graph(DATASET_DEFAULT_GRAPH_ID)

    assert dataset == default_graph


def test_add_graph_content_to_dataset_DEFAULT_via_sparqlupdate():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )

    assert len(list(dataset.contexts())) == 1


def test_add_graph_content_to_dataset_NAMED_DEFAULT_via_sparqlupdate():
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


def test_add_graph_as_new_dataset_CONTEXT_via_sparqlupdate():
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


def test_parse_graph_as_new_dataset_CONTEXT_nquads():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 1

    dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> <urn:x-rdflib:context-0> .",
        format="nquads",
    )

    assert len(list(dataset.contexts())) == 2


def test_parse_graph_as_new_dataset_CONTEXT_trig():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 1

    dataset.parse(
        data="@prefix ex: <http://example.org/graph/> . @prefix ont: <http://example.com/ontology/> . ex:practise { <http://example.com/resource/student_10> ont:practises <http://example.com/resource/sport_100> . }",
        format="trig",
    )

    assert len(list(dataset.contexts())) == 2


def test_parse_graph_with_publicid_as_new_dataset_CONTEXT():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 1

    dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .",
        publicID="urn:x-rdflib:context-a",
        format="ttl",
    )
    assert len(list(dataset.contexts())) == 2


def test_parse_graph_with_bnode_as_new_dataset_CONTEXT():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 1

    data = """_:a <urn:example:likes> <urn:example:pizza> ."""

    dataset.parse(data=data, format="ttl")

    assert (
        len(list(dataset.contexts())) == 2
    )  # Now contains a context with a BNode graph


def test_parse_graph_with_bnode_identifier_as_new_dataset_CONTEXT():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 1

    g = dataset.graph(identifier=BNode())
    g.parse(data="<a> <b> <c> .", format="ttl")

    assert len(list(dataset.contexts())) == 2


def test_default_graph_method_add_parsed_turtle_graph_to_dataset_DEFAULT():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 1

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 1

    dataset.default_graph = (
        dataset.default_context
    )  # Monkeypatch to exploit ConjunctiveGraph inheritance and make the use pattern explicit

    dataset.default_graph.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    assert len(list(dataset.contexts())) == 1
