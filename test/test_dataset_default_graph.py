import pytest
import os
import shutil
import tempfile
from pprint import pformat
import rdflib
from rdflib import logger, Literal, Graph, ConjunctiveGraph, Dataset, Namespace, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from pathlib import Path
from urllib.error import URLError, HTTPError


michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")

c1 = URIRef("urn:context-1")
c2 = URIRef("urn:context-2")


# store = "BerkeleyDB"
# store = "SQLiteLSM"
# store = "LevelDB"

nquads = """\
<http://example.com/resource/student_10> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.com/ontology/Student> <http://example.org/graph/students> .
<http://example.com/resource/student_10> <http://xmlns.com/foaf/0.1/name> "Venus Williams"                                       <http://example.org/graph/students> .
<http://example.com/resource/student_20> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.com/ontology/Student> <http://example.org/graph/students> .
<http://example.com/resource/student_20> <http://xmlns.com/foaf/0.1/name> "Demi Moore"                                           <http://example.org/graph/students> .
<http://example.com/resource/sport_100> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.com/ontology/Sport>    <http://example.org/graph/sports> .
<http://example.com/resource/sport_100> <http://www.w3.org/2000/01/rdf-schema#label> "Tennis"                                    <http://example.org/graph/sports> .
<http://example.com/resource/student_10> <http://example.com/ontology/practises> <http://example.com/resource/sport_100>         <http://example.org/graph/practise> .
"""

list_of_nquads = [
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Student"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://xmlns.com/foaf/0.1/name"),
        Literal("Venus Williams"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_20"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Student"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_20"),
        URIRef("http://xmlns.com/foaf/0.1/name"),
        Literal("Demi Moore"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Sport"),
        URIRef("http://example.org/graph/sports"),
    ),
    (
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
        Literal("Tennis"),
        URIRef("http://example.org/graph/sports"),
    ),
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://example.com/ontology/practises"),
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://example.org/graph/practise"),
    ),
]


@pytest.fixture(
    # scope="function", params=["default", "BerkeleyDB", "SQLiteLSM", "LevelDB", "SQLAlchemy"]
    scope="function",
    params=["default"],
)
def get_dataset(request):
    store = request.param
    tmppath = os.path.join(tempfile.gettempdir(), f"test_{store.lower()}")
    graph = Dataset(store=store)
    graph.open(tmppath, create=True)
    # tmppath = mkdtemp()
    if store != "default" and graph.store.is_open():
        # delete the graph for each test!
        graph.remove((None, None, None))
        for c in graph.contexts():
            c.remove((None, None, None))
            assert len(c) == 0
            graph.remove_graph(c)
    # logger.debug(f"Using store {graph.store}")
    yield graph

    graph.close()
    if os.path.isdir(tmppath):
        shutil.rmtree(tmppath)
    else:
        try:
            os.remove(tmppath)
        except Exception:
            pass


@pytest.fixture(
    # scope="function", params=["default", "BerkeleyDB", "SQLiteLSM", "LevelDB", "SQLAlchemy"]
    scope="function",
    params=["default"],
)
def get_conjunctivegraph(request):
    store = request.param
    tmppath = os.path.join(tempfile.gettempdir(), f"test_{store.lower()}")
    graph = ConjunctiveGraph(store=store)
    graph.open(tmppath, create=True)
    # tmppath = mkdtemp()
    if store != "default" and graph.store.is_open():
        # delete the graph for each test!
        graph.remove((None, None, None))
        for c in graph.contexts():
            c.remove((None, None, None))
            assert len(c) == 0
            graph.remove_graph(c)
    # logger.debug(f"Using store {graph.store}")
    yield graph

    graph.close()
    if os.path.isdir(tmppath):
        shutil.rmtree(tmppath)
    else:
        try:
            os.remove(tmppath)
        except Exception:
            pass


# @pytest.mark.skip
def test_simple_dataset_default_graph_and_contexts_programmatic_modelling(get_dataset):
    ds = get_dataset

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        str(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    )

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    # logger.debug(f"\n\nDATASET_DEFAULT_GRAPH\n{str(dataset_default_graph)}")
    assert (
        str(dataset_default_graph)
        == "<urn:x-rdflib-default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']."
    )

    # logger.debug(f"\n\nXML serialization\n{str(dataset_default_graph.serialize(format='xml'))}")
    assert str(dataset_default_graph.serialize(format="xml")) == str(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<rdf:RDF\n"
        '   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        ">\n"
        "</rdf:RDF>\n"
    )


# @pytest.mark.skip
def test_serialization_of_simple_dataset_default_graph_and_contexts_programmatic_modelling(
    get_dataset,
):
    ds = get_dataset
    # Serialization of the empty dataset is sane

    # logger.debug(f"\n\nTRIG serialization\n{ds.serialize(format='trig')}")
    assert str(ds.serialize(format="trig")) == str("@prefix ns1: <urn:> .\n\n")

    # logger.debug(f"\n\nNQUADS serialization\n{ds.serialize(format='nquads')}")
    assert str(ds.serialize(format="nquads")) == str("\n")

    # logger.debug(f"\n\nJSON-LD serialization\n{ds.serialize(format='json-ld')}")
    assert str(ds.serialize(format="json-ld")) == str("[]")

    # logger.debug(f"\n\nHEXT serialization\n{ds.serialize(format='hext')}")
    assert str(ds.serialize(format="hext")) == str("")

    # logger.debug(f"\n\nTRIX serialization\n{str(ds.serialize(format='trix'))}")
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
        '  xmlns:ns1="urn:"\n'
        '  xmlns="http://www.w3.org/2004/03/trix/trix-1/"\n>'
        "\n"
        "  <graph>\n"
        "    <uri>urn:x-rdflib-default</uri>\n"
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
        == "[<Graph identifier=urn:x-rdflib-default (<class 'rdflib.graph.Graph'>)>]"
    )

    # logger.debug(f"\n\nTRIG serialization\n{str(ds.serialize(format='trig'))}")
    assert str(ds.serialize(format="trig")) in [
        str("@prefix ns1: <urn:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"),
    ]

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)

    logger.debug(
        f"\n\nXML serialization\n{str(dataset_default_graph.serialize(format='xml'))}"
    )
    assert str(dataset_default_graph.serialize(format="xml")) == str(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<rdf:RDF\n"
        '   xmlns:ns1="urn:"\n'
        '   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        ">\n"
        '  <rdf:Description rdf:about="urn:tarek">\n'
        '    <ns1:likes rdf:resource="urn:pizza"/>\n'
        "  </rdf:Description>\n"
        "</rdf:RDF>"
        "\n"
    )

    # For exhaustive completeness: The default graph behaves as a Graph -
    # logger.debug(
    #     f"\n\nTURTLE serialization\n{str(dataset_default_graph.serialize(format='ttl'))}"
    # )
    assert str(dataset_default_graph.serialize(format="ttl")) == str(
        "@prefix ns1: <urn:> .\n\nns1:tarek ns1:likes ns1:pizza .\n\n"
    )

    # logger.debug(
    #     f"\n\nJSON-LD serialization\n{str(dataset_default_graph.serialize(format='json-ld'))}"
    # )
    assert str(dataset_default_graph.serialize(format="json-ld")) == str(
        "[\n"
        "  {\n"
        '    "@graph": [\n'
        "      {\n"
        '        "@id": "urn:tarek",\n'
        '        "urn:likes": [\n'
        "          {\n"
        '            "@id": "urn:pizza"\n'
        "          }\n"
        "        ]\n"
        "      }\n"
        "    ],\n"
        '    "@id": "urn:x-rdflib-default"\n'
        "  }\n"
        "]"
    )

    # Serializes correctly
    # logger.debug(
    #     f"\n\nTRIG serializes ns1 as <urn:x-rdflib:> and uses id for default graph\n{str(ds.serialize(format='trig'))}"
    # )
    assert str(ds.serialize(format="trig")) == str(
        "@prefix ns1: <urn:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"
    )


# @pytest.mark.skip
def test_removal_of_simple_dataset_default_graph_and_contexts_programmatic_modelling(
    get_dataset,
):

    ds = get_dataset

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


# @pytest.mark.skip
def test_simple_dataset_default_graph_and_contexts_sparql_modelling(get_dataset):
    ds = get_dataset

    # ADD ONE TRIPLE *without context* to the default graph

    ds.update("INSERT DATA { <urn:tarek> <urn:likes> <urn:pizza> . }")

    # There is now one triple in the default graph, so dataset length == 1
    assert len(ds) == 1

    r = ds.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
    assert len(list(r)) == 1, "one person likes pizza"

    # logger.debug(f"\n\nTRIG serialization\n{str(ds.serialize(format='trig'))}")
    assert str(ds.serialize(format="trig")) == str(
        "@prefix ns1: <urn:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"
    )


def pytest_assertdatasetcontexts_compare(op, left, right):
    if (
        isinstance(left, list)
        and isinstance(left[0], Graph)
        and isinstance(right, list)
        and isinstance(right[0], Graph)
        and op == "=="
    ):
        return [
            "Comparing Dataset contexts:",
            "   vals: {} != {}".format(left.val, right.val),
        ]


# @pytest.mark.skip
def test_simple_dataset_contexts_sparql_modelling(get_dataset):
    ds = get_dataset
    # ds = Dataset()

    # dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)

    # ADD ONE TRIPLE *without context* to the default graph
    # ds.update("ADD TAREK LIKES PIZZA")
    # ds.add((tarek, likes, pizza))

    """
    ## 3.1.1 INSERT DATA

    The INSERT DATA operation adds some triples, given inline in the
    request, into the Graph Store:

    `INSERT DATA  ---QuadData---`

    where `QuadData` are formed by `TriplesTemplates`, i.e., sets of triple
    patterns, optionally wrapped into a GRAPH block.

    `( GRAPH  VarOrIri )? { TriplesTemplate? }`

    Variables in `QuadDatas` are disallowed in `INSERT DATA` requests
    (see Notes 8 in the grammar). That is, the `INSERT DATA` statement only
    allows to insert ground triples. Blank nodes in `QuadDatas` are assumed
    to be disjoint from the blank nodes in the Graph Store, i.e., will be
    inserted with "fresh" blank nodes.

    **If no graph is described in the `QuadData`, then the default graph is
    presumed.** If data is inserted into a graph that does not exist in the
    Graph Store, it SHOULD be created (there may be implementations
    providing an update service over a fixed set of graphs which in such
    case MUST return with failure for update requests that insert data
    into an unallowed graph).
    """

    ds.update("INSERT DATA { <urn:tarek> <urn:likes> <urn:pizza> . }")

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])

    # There is now one triple in the default graph, so dataset length == 1
    assert len(ds) == 1

    r = ds.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
    assert len(list(r)) == 1, "one person likes pizza"

    # logger.debug(f"\n\nTRIG serialization\n{str(ds.serialize(format='trig'))}")

    assert str(ds.serialize(format="trig")) == str(
        "@prefix ns1: <urn:> .\n\n{\n    ns1:tarek ns1:likes ns1:pizza .\n}\n\n"
    )

    ds.update(
        "INSERT DATA { GRAPH <urn:x-rdflib-default> { <urn:tarek> <urn:likes> <urn:cheese> . } }"
    )

    r = ds.query("SELECT * WHERE { ?s <urn:likes> <urn:cheese> . }")
    assert len(list(r)) == 1, "one person likes cheese"

    # There is now two triples in the default graph, so dataset length == 2
    assert len(ds) == 2

    # removing default graph removes triples but not actual graph
    ds.update("CLEAR DEFAULT")

    assert len(ds) == 0

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])


# @pytest.mark.skip
def test_dataset_add_graph(get_dataset):

    data = """
    <http://data.yyx.me/jack> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_a> .
    <http://data.yyx.me/david> <http://onto.yyx.me/work_for> <http://data.yyx.me/company_b> .
    """

    g = Graph(identifier="subgraph")
    g.parse(data=data, format="n3")
    assert len(g) == 2

    ds = get_dataset
    ds.add_graph(g)

    # logger.debug(f"\n\nDataset contexts\n{list(ds.contexts())}")

    # logger.debug(
    #     f"\n\nDataset context identifiers\n{[context.identifier for context in ds.contexts()]}"
    # )

    # logger.debug(f"\n\nDataset context\n{ds.get_context('subgraph')}")

    sg = ds.get_context("subgraph")
    assert len(sg) == 2

    # logger.debug(f"\n\nXML serialization\n{str(sg.serialize(format='xml'))}")


# # @pytest.mark.skip
# def test_dataset_default_graph_and_contexts_with_namespace_bound(get_dataset):
#     ds = get_dataset

#     dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)

#     # ADD ONE TRIPLE *without context* to the default graph

#     ds.bind("", "urn:", True)
#     ds.add((tarek, likes, pizza))

#     # logger.debug(f"\n\nTRIG serialization\n{str(ds.serialize(format='trig'))}")
#     assert str(ds.serialize(format="trig")) == str(
#         "@prefix : <urn:> .\n"
#         "@prefix ns1: <urn:x-rdflib:> .\n"
#         "\n"
#         "ns1:default {\n"
#         "    :tarek :likes :pizza .\n"
#         "}\n"
#         "\n"
#     )

#     # logger.debug(
#     #     f"\n\nXML serialization\n{str(dataset_default_graph.serialize(format='xml'))}"
#     # )
#     assert str(dataset_default_graph.serialize(format="xml")) == str(
#         '<?xml version="1.0" encoding="utf-8"?>\n'
#         "<rdf:RDF\n"
#         '   xmlns="urn:"\n'
#         '   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
#         ">\n"
#         '  <rdf:Description rdf:about="urn:tarek">\n'
#         '    <likes rdf:resource="urn:pizza"/>\n'
#         "  </rdf:Description>\n"
#         "</rdf:RDF>\n"
#     )

# if __name__ == "__main__":
#     test_simple_dataset_contexts_sparql_modelling()


@pytest.mark.skip
def test_dataset_and_context_serialization(get_dataset):

    ds = get_dataset

    logger.debug(
        f"""\nLength of ds contexts on initialisation: {len(list(ds.contexts()))}\n"""
    )
    assert len(list(ds.contexts())) == 1

    logger.debug(f"""\nds contexts on initialisation: {list(ds.contexts())}\n""")

    ds.add((tarek, likes, pizza))

    logger.debug(
        f"""\nLength of ds after one triple added to default graph: {len(ds)}\n"""
    )
    assert len(ds) == 1

    logger.debug(
        f"""\nLength of ds contexts after one triple added to default graph: {len(list(ds.contexts()))}\n"""
    )
    assert len(list(ds.contexts())) == 1

    for fmt in [
        # Triples serializers do not render the contents of the default graph
        "xml",  # Empty
        "n3",  # Empty
        "turtle",  # Empty
        "longturtle",  # Empty
        "ntriples",
        "json-ld",
        "nquads",
        "trix",
        "trig",
        "hext",
    ]:
        logger.debug(
            f"""\nDataset serialised as {fmt}:\n“{ds.serialize(format=fmt)}”\n"""
        )

    logger.debug("\n\n>>>> ADDING 7 TRIPLES IN 3 CONTEXTS <<<<\n")

    # DEVNOTE

    ds.parse(data=nquads, format="nquads")

    # DEVNOTE
    # raises a warning:
    #  ,,,/rdflib/graph.py:1992: UserWarning: Got a Graph
    # [a rdflib:Dataset;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']],
    # should be a URIRef, passed by parse in test_dataset in pytest_pyfunc_call

    # DEVNOTE

    # ds.addN(list_of_nquads)

    # Doesn't raise a warning

    logger.debug(
        f"""\nLength of ds after 7 triples added to three contexts: {len(ds)}\n"""
    )
    assert len(ds) == 8

    logger.debug(
        f"""\nLength of ds contexts after 7 triples added to three contexts: {len(list(ds.contexts()))}\n"""
    )

    logger.debug(
        f"""\nContents of ds contexts after 7 triples added to three contexts:\n\n{pformat(list(ds.contexts()))}\n\n"""
    )

    assert len(list(ds.contexts())) == 4

    for fmt in [
        # Triples serializers do not render the contents of any of the contexts, not even the default graph
        "xml",  # Empty
        "n3",  # Empty
        "turtle",  # Empty
        "longturtle",  # Empty
        # Quads serializers render the contents of the default graph
        "ntriples",
        "json-ld",
        "nquads",
        "trix",
        "trig",
        "hext",
    ]:
        logger.debug(
            f"""\n\nDataset serialized as {fmt}\n{ds.serialize(format=fmt)}\n\n"""
        )

    for p in [
        "xml",
        "n3",
        "turtle",
        "longturtle",
        "ntriples",
        "json-ld",
        "trig",
        "hext",
        # Contexts only yield triples so can't use quad-expecting serializers
        # "nquads",
        # "trix",
    ]:
        for c in ds.contexts():
            logger.debug(
                f"""\nContext {c.identifier} serialized as {p}\n{c.serialize(format=p)}\n"""
            )
