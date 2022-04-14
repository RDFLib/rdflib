from test.data import *

import pytest

from rdflib import URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph
from rdflib.term import BNode


def test_dataset_default_graph():
    dataset = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(dataset) == 0

    # The default graph is not treated as a context so the length of dataset.contexts() == 0
    assert len(list(dataset.contexts())) == 0

    # Only the default graph exists but is not yielded by dataset.contexts()
    assert list(dataset.contexts()) == []

    # Same for graphs)_

    # The default graph is not treated as a context so the length of dataset.graphs() == 0
    assert len(list(dataset.graphs())) == 0

    # Only the default graph exists but is not yielded by dataset.graphs()
    assert list(dataset.graphs()) == []

    # The default graph is just a Graph
    dataset_default_graph = dataset.graph(DATASET_DEFAULT_GRAPH_ID)

    assert dataset == dataset_default_graph

    assert (
        str(dataset_default_graph)
        == "<urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    dataset_default_graph.add((tarek, likes, pizza))

    assert (
        len(dataset) == 1
    )  # Dataset is responsible for tracking changes to constituents


def test_removal_of_dataset_default_graph():

    dataset = Dataset()

    # ADD ONE TRIPLE *without context* to the default graph

    dataset.add((tarek, likes, pizza))

    # There is now one triple in the default graph, so dataset length == 1
    assert len(dataset) == 1

    # Removing default graph removes triples but not the actual graph
    dataset.remove_graph(DATASET_DEFAULT_GRAPH_ID)

    assert len(dataset) == 0

    assert set(list(dataset.graphs())) == set([])

    # Default graph still exists
    assert dataset.default_graph is not None


def test_trig_serialization_of_empty_dataset_default_graph():
    dataset = Dataset()

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:example:"))

    assert str(dataset.serialize(format="trig")) == str("\n")


def test_nquads_serialization_of_empty_dataset_default_graph():
    dataset = Dataset()

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:example:"))

    assert str(dataset.serialize(format="nquads")) == str("\n")


def test_jsonld_serialization_of_empty_dataset_default_graph():
    dataset = Dataset()

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:example:"))

    assert str(dataset.serialize(format="json-ld")) == str("[]")


def test_hext_serialization_of_empty_dataset_default_graph():
    dataset = Dataset()

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:example:"))

    assert str(dataset.serialize(format="hext")) == str("")


@pytest.mark.xfail(reason="pending merge of changes namespace bindings")
def test_trix_serialization_of_empty_dataset_default_graph():
    dataset = Dataset()

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:example:"))

    assert str(dataset.serialize(format="trix")) == str(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<TriX\n'
        '  xmlns:owl="http://www.w3.org/2002/07/owl#"\n'
        '  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        '  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n'
        '  xmlns:xsd="http://www.w3.org/2001/XMLSchema#"\n'
        '  xmlns:xml="http://www.w3.org/XML/1998/namespace"\n'
        '  xmlns="http://www.w3.org/2004/03/trix/trix-1/"\n'
        '/>\n'
    )


def test_serialization_of_dataset_default_graph():
    dataset = Dataset()

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:example:"))

    # ADD ONE TRIPLE *without context* to the default graph

    dataset.add((tarek, likes, pizza))

    # There is now one triple in the default graph, so dataset length == 1
    assert len(dataset) == 1

    # The default graph is a not treated as a separate context so the length of dataset.graphs() == 0
    assert len(list(dataset.graphs())) == 0

    # Although the default graph exists it is not yielded by dataset.graphs()
    assert str(list(dataset.graphs())) == "[]"

    assert (
        str(dataset.serialize(format="trig"))
        == "@prefix : <urn:example:> .\n\n{\n    :tarek :likes :pizza .\n}\n\n"
    )

    dataset_default_graph = dataset.graph(DATASET_DEFAULT_GRAPH_ID)

    assert str(dataset_default_graph.serialize(format="xml")) == str(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<rdf:RDF\n"
        '   xmlns="urn:example:"\n'
        '   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        ">\n"
        '  <rdf:Description rdf:about="urn:example:tarek">\n'
        '    <likes rdf:resource="urn:example:pizza"/>\n'
        "  </rdf:Description>\n"
        "</rdf:RDF>"
        "\n"
    )

    # For exhaustive completeness: The default graph behaves as a Graph -
    assert str(dataset_default_graph.serialize(format="ttl")) == str(
        "@prefix : <urn:example:> .\n\n:tarek :likes :pizza .\n\n"
    )

    assert (
        str(dataset_default_graph.serialize(format="json-ld"))
        == """[
  {
    "@id": "urn:example:tarek",
    "urn:example:likes": [
      {
        "@id": "urn:example:pizza"
      }
    ]
  }
]"""
    )


def test_trig_serialization_of_empty_dataset_default_graph_with_default_union():
    dataset = Dataset(default_union=True)

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:x-rdflib:"))

    assert str(dataset.serialize(format="trig")) == str("\n")


def test_nquads_serialization_of_empty_dataset_default_graph_with_default_union():
    dataset = Dataset(default_union=True)

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:x-rdflib:"))

    assert str(dataset.serialize(format="nquads")) == str("\n")


def test_jsonld_serialization_of_empty_dataset_default_graph_with_default_union():
    dataset = Dataset(default_union=True)

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:x-rdflib:"))

    assert str(dataset.serialize(format="json-ld")) == str("[]")


def test_hext_serialization_of_empty_dataset_default_graph_with_default_union():
    dataset = Dataset(default_union=True)

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:x-rdflib:"))

    assert str(dataset.serialize(format="hext")) == str("")


@pytest.mark.xfail(reason="pending merge of changes namespace bindings")
def test_trix_serialization_of_empty_dataset_default_graph_with_default_union():
    dataset = Dataset(default_union=True)

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:x-rdflib:"))

    assert str(dataset.serialize(format="trix")) == str(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<TriX\n'
        '  xmlns:owl="http://www.w3.org/2002/07/owl#"\n'
        '  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        '  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n'
        '  xmlns:xsd="http://www.w3.org/2001/XMLSchema#"\n'
        '  xmlns:xml="http://www.w3.org/XML/1998/namespace"\n'
        '  xmlns="http://www.w3.org/2004/03/trix/trix-1/"\n'
        '/>\n'
    )


def test_serialization_of_dataset_default_graph_with_default_union():
    dataset = Dataset(default_union=True)

    # Serialization of the empty dataset is sane
    dataset.bind("", URIRef("urn:x-rdflib:"))

    # ADD ONE TRIPLE *without context* to the default graph

    dataset.add((tarek, likes, pizza))

    # There is now one triple in the default graph, so dataset length == 1
    assert len(dataset) == 1

    # The default graph is a not treated as a separate context so the length of dataset.graphs() == 0
    assert len(list(dataset.graphs())) == 0

    # Although the default graph exists it is not yielded by dataset.graphs()
    assert set(list(dataset.graphs())) == set()

    assert (
        str(dataset.serialize(format="trig"))
        == "@prefix ns1: <urn:example:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"
    )

    dataset_default_graph = dataset.graph(DATASET_DEFAULT_GRAPH_ID)

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

    assert (
        str(dataset_default_graph.serialize(format="json-ld"))
        == """[
  {
    "@id": "urn:example:tarek",
    "urn:example:likes": [
      {
        "@id": "urn:example:pizza"
      }
    ]
  }
]"""
    )


def test_simple_dataset_default_graph_sparql_modelling():
    dataset = Dataset()
    dataset.bind("", URIRef("urn:example:"))

    # ADD ONE TRIPLE *without context* to the default graph

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:pizza> . }"
    )

    # There is now one triple in the default graph, so dataset length == 1
    assert len(dataset) == 1

    r = dataset.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "one person likes pizza"

    assert str(dataset.serialize(format="trig")) == str(
        "@prefix : <urn:example:> .\n\n{\n    :tarek :likes :pizza .\n}\n\n"
    )


def test_simple_dataset_contexts_sparql_modelling():
    dataset = Dataset()
    dataset.bind("", URIRef("urn:example:"))

    # The default graph is not treated as a context so the length of dataset.contexts() should be 0
    assert len(list(dataset.contexts())) == 0

    # Insert statement into the default graph
    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:pizza> . }"
    )

    # Inserting into the default graph should not create a new context so the length of
    # dataset.contexts() should still be 0
    assert len(list(dataset.contexts())) == 0
    assert set(list(dataset.contexts())) == set([])

    # There is now one triple in the default graph, so dataset length should be 1
    assert len(dataset) == 1

    r = dataset.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "one person likes pizza"

    assert str(dataset.serialize(format="trig")) == str(
        "@prefix : <urn:example:> .\n\n{\n    :tarek :likes :pizza .\n}\n\n"
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
    assert set(list(dataset.contexts())) == set([])

    # Add to a NAMED GRAPH

    dataset.update(
        "INSERT DATA { GRAPH <urn:example:context-1> { <urn:example:michel> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = dataset.query(
        "SELECT * WHERE { ?s <urn:example:likes> <urn:example:cheese> . }"
    )

    assert len(list(r)) == 0, "no-one in the default graph likes cheese"

    r = dataset.query(
        """SELECT (COUNT(?g) AS ?c) WHERE {SELECT DISTINCT ?g WHERE { GRAPH ?g {?s ?p ?o} } }"""
    )

    assert len(list(r)) == 1, "*someone* likes cheese"

    r = dataset.query("SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o }}")

    assert [rr.g for rr in r] == list(dataset.contexts())

    assert len(r) == 1, "juuust one contexto, give eet to meee."

    ######################### WORKING ######################################

    # r = dataset.query("SELECT * FROM :context-1 WHERE { ?s <urn:example:likes> <urn:example:cheese> . }")

    # r = dataset.query("SELECT * FROM NAMED :context-1 {GRAPH ?g { ?s <urn:example:likes> <urn:example:cheese> . } }")

    # CLEAR GRAPH example:exampleGraph
    # DROP GRAPH example:exampleGraph
    # DELETE { GRAPH example:exampleGraph { ?s ?p ?o }} WHERE {?s ?p ?o .}

    assert len(list(r)) == 1, "one person in the default graph likes cheese"

    # Re-insert into the NAMED default graph
    dataset.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:default> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )

    assert len(list(r)) == 1, "one person likes cheese"

    # There is now two triples in the default graph, so dataset length == 2
    assert len(dataset) == 1

    # removing default graph removes triples but not actual graph
    dataset.update("CLEAR DEFAULT")

    assert len(dataset) == 0

    # The NAMED graph remains in the list of contexts
    assert set(list(dataset.contexts())) == set([context1])

    assert len(dataset.graph(context1)) == 1

    # removing default graph removes triples but not actual graph
    dataset.update("CLEAR GRAPH <urn:example:context-1>")

    assert set(list(dataset.contexts())) == set([context1])


def test_dataset_add_graph():

    data = """
    <http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
    <http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
    """

    dataset = Dataset()

    subgraph_identifier = URIRef("urn:example:subgraph1")

    g = dataset.graph(subgraph_identifier)

    g.parse(data=data, format="n3")

    assert len(g) == 2

    subgraph = dataset.graph(subgraph_identifier)

    assert type(subgraph) is Graph

    assert len(subgraph) == 2


def test_dataset_equal_to_dataset_default():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    default_graph = dataset.graph(DATASET_DEFAULT_GRAPH_ID)

    assert dataset == default_graph


def test_add_graph_content_to_dataset_default_via_sparqlupdate():
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

    dataset.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:default> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )
    assert len(list(dataset.contexts())) == 0


def test_add_graph_as_new_dataset_context_via_sparqlupdate():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { GRAPH <urn:example:context1> { <urn:example:tarek> <urn:example:hates> <urn:example:pizza> . } }"
    )
    assert len(list(dataset.contexts())) == 1


def test_parse_graph_as_new_dataset_context_nquads():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 0

    dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> <urn:example:context-0> .",
        format="nquads",
    )

    assert len(list(dataset.contexts())) == 1


def test_parse_graph_as_new_dataset_context_trig():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 0

    dataset.parse(
        data="@prefix ex: <http://example.org/graph/> . @prefix ont: <http://example.com/ontology/> . ex:practise { <http://example.com/resource/student_10> ont:practises <http://example.com/resource/sport_100> . }",
        format="trig",
    )

    assert len(list(dataset.contexts())) == 1


def test_parse_graph_with_publicid_as_new_dataset_context():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 0

    res = dataset.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .",
        publicID="urn:example:context-a",
        format="ttl",
    )

    assert res.identifier == dataset.identifier

    assert len(list(dataset.contexts())) == 1


def test_parse_graph_with_bnode_as_new_dataset_context():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 0

    data = """_:a <urn:example:likes> <urn:example:pizza> ."""

    dataset.parse(data=data, format="ttl")

    assert (
        len(list(dataset.contexts())) == 0
    )  # Now contains a context with a BNode graph


def test_parse_graph_with_bnode_identifier_as_new_dataset_context():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 0

    g = dataset.graph(identifier=BNode())
    g.parse(data="<a> <b> <c> .", format="ttl")

    assert len(list(dataset.contexts())) == 1


def test_default_graph_method_add_parsed_turtle_graph_to_dataset_default():
    dataset = Dataset()
    assert len(list(dataset.contexts())) == 0

    dataset.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:hates> <urn:example:cheese> . }"
    )
    assert len(list(dataset.contexts())) == 0

    dataset.default_graph.parse(
        data="<urn:example:tarek> <urn:example:likes> <urn:example:pizza> .",
        format="ttl",
    )

    assert len(list(dataset.contexts())) == 0
