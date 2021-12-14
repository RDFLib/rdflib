import pytest
import os
import shutil
from tempfile import gettempdir
from pprint import pformat
import rdflib
from rdflib import logger, Literal, ConjunctiveGraph, Dataset, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

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
    tmppath = os.path.join(gettempdir(), f"test_{store.lower()}")
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
    tmppath = os.path.join(gettempdir(), f"test_{store.lower()}")
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
def test_dataset(get_dataset):
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
        "xml",
        "n3",
        "turtle",
        "longturtle",
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
        "xml",
        "n3",
        "turtle",
        "longturtle",
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
        # "nquads",
        # "trix",
        "trig",
        "hext",
    ]:
        for c in ds.contexts():
            logger.debug(
                f"""\nContext {c.identifier} serialized as {p}\n{c.serialize(format=p)}\n"""
            )

    # logger.debug(f"""Dataset serialized as {[]}\n{ds.serialize(format=p)}\n""")
    # logger.debug(f"""Dataset example 2\n{ds.serialize(format="xml")}""")
