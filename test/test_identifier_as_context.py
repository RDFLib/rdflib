# -*- coding: utf-8 -*-
import pytest
import os
import shutil
import tempfile
from pprint import pformat
from rdflib import logger, Graph, ConjunctiveGraph, Dataset, Literal, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

path = os.path.join(tempfile.gettempdir(), "test_dataset")


trig_example1 = """
# This document encodes one graph.
@prefix ex: <http://www.example.org/vocabulary#> .
@prefix : <http://www.example.org/exampleDocument#> .

:G1 { :Monica a ex:Person ;
              ex:name "Monica Murphy" ;
              ex:homepage <http://www.monicamurphy.org> ;
              ex:email <mailto:monica@monicamurphy.org> ;
              ex:hasSkill ex:Management ,
                          ex:Programming . }

"""

trig_example2 = """\
# This document contains a default graph and two named graphs.

@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

# default graph
    {
      <http://example.org/bob> dc:publisher "Bob" .
      <http://example.org/alice> dc:publisher "Alice" .
    }

<http://example.org/bob>
    {
       _:a foaf:name "Bob" .
       _:a foaf:mbox <mailto:bob@oldcorp.example.org> .
       _:a foaf:knows _:b .
    }

<http://example.org/alice>
    {
       _:b foaf:name "Alice" .
       _:b foaf:mbox <mailto:alice@work.example.org> .
    }
"""

trig_example3 = r"""
# This document contains a same data as the previous example.

@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

# default graph - no {} used.
<http://example.org/bob> dc:publisher "Bob" .
<http://example.org/alice> dc:publisher "Alice" .

# GRAPH keyword to highlight a named graph
# Abbreviation of triples using ;
GRAPH <http://example.org/bob>
{
   [] foaf:name "Bob" ;
      foaf:mbox <mailto:bob@oldcorp.example.org> ;
      foaf:knows _:b .
}

GRAPH <http://example.org/alice>
{
    _:b foaf:name "Alice" ;
        foaf:mbox <mailto:alice@work.example.org>
}
"""


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
def test_namedgraph(get_conjunctivegraph):
    graph = get_conjunctivegraph
    assert len(graph) == 0

    graph.parse(data=trig_example1, format="trig")
    logger.debug(f"""Named graph example 1\n{graph.serialize(format="trig")}""")
    graph.remove((None, None, None))
    assert len(graph) == 0

    graph.parse(data=trig_example2, format="trig")
    logger.debug(f"""Named graph example 2\n{graph.serialize(format="trig")}""")
    logger.debug(f"""Named graph 2\n{graph.serialize(format="xml")}""")
    graph.remove((None, None, None))
    assert len(graph) == 0

    graph.parse(data=trig_example3, format="trig")
    logger.debug(f"""Named graph example 3\n{graph.serialize(format="trig")}""")
    graph.remove((None, None, None))
    assert len(graph) == 0


# @pytest.mark.skip
def test_dataset(get_dataset):
    ds = get_dataset
    assert len(ds) == 0

    ds.parse(data=trig_example1, format="trig")
    logger.debug(f"""Dataset example 1\n{ds.serialize(format="trig")}""")
    ds.remove((None, None, None))
    assert len(ds) == 0

    ds.parse(data=trig_example2, format="trig")
    logger.debug(f"""Dataset example 2\n{ds.serialize(format="ttl")}""")
    logger.debug(f"""Dataset example 2\n{ds.serialize(format="xml")}""")
    ds.remove((None, None, None))
    assert len(ds) == 0

    ds.parse(data=trig_example3, format="trig")
    logger.debug(f"""Dataset example 3\n{ds.serialize(format="trig")}""")
    ds.remove((None, None, None))
    assert len(ds) == 0


# @pytest.mark.skip
def test_contexts(get_dataset):
    default_context = URIRef("urn:x-rdflib:default")

    # Create a new Dataset
    ds = get_dataset

    # logger.debug(f"ds store {ds.store}")
    # assert "rdflib.plugins.stores.memory.Memory object at 0x" in repr(ds.store)

    ds_contexts = list(ds.contexts())

    # Initialisation

    logger.debug(f"ds contexts on initialisation:\n{ds_contexts}")
    assert (
        repr(ds_contexts)
        == "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
    )

    logger.debug(
        f"ds default context identifier:\n{pformat(next(ds.contexts()).identifier)}"
    )
    assert next(ds.contexts()).identifier == default_context

    # simple triples goes to default graph
    ds.add(
        (
            URIRef("http://example.org/a"),
            URIRef("http://www.example.org/b"),
            Literal("foo"),
        )
    )

    # for context in ds.contexts():
    #     logger.debug(f"\n{context.identifier}\n{context.serialize(format='ttl')}")

    for fmt in ["nquads", "trix"]:
        assert len(ds.serialize(format=fmt)) > 1

    for fmt in [
        "trig",
        "turtle",
        "n3",
        "nt",
        "xml",
        "pretty-xml",
    ]:
        for context in ds.contexts():
            assert (
                len(
                    context.serialize(
                        format=fmt, encoding="ascii" if fmt == "nt" else "utf-8"
                    )
                )
                > 1  # noqa: W503
            )

    res = next(ds.contexts())
    logger.debug(f"res: “{res}” {len(res)} {type(res)}\n“{res.serialize(format='n3')}”")

    assert (
        res.serialize(format="n3")
        == """@prefix ns2: <http://www.example.org/> .\n\n<http://example.org/a> ns2:b "foo" .\n\n"""  # noqa: W503
    )

    # WIP

    # querying triples return them all regardless of the graph/context
    triples = list(ds.store.triples((None, None, None)))
    logger.debug(f"store triples = {len(triples)}")
    assert len(triples) == 1

    # Iterating over the Dataset, returns every triple in every context as quads
    quads = list(ds)
    logger.debug(f"quads = {len(quads)}")

    triples = list(ds.store.triples((None, None, None), context=default_context))
    logger.debug(f"store triples = {len(triples)}")
    assert len(triples) == 1

    g = ds.graph(URIRef("http://www.example.com/gr"))

    # add triples to the new graph as usual
    g.add(
        (
            URIRef("http://example.org/x"),
            URIRef("http://example.org/y"),
            Literal("bar"),
        )
    )

    # querying triples return them all regardless of the graph/context
    triples = list(ds.store.triples((None, None, None)))
    logger.debug(f"store triples = {len(triples)}")
    assert len(triples) == 2

    # for context in ds.contexts():
    #     logger.debug(f"\n{context.identifier}\n{context.serialize(format='ttl')}")
    # alternatively: add a quad to the dataset -> goes to the graph
    ds.add(
        (
            URIRef("http://example.org/x"),
            URIRef("http://example.org/z"),
            Literal("foo-bar"),
            g,
        )
    )

    # querying triples return them all regardless of the graph/context
    triples = list(ds.store.triples((None, None, None)))
    logger.debug(f"store triples = {len(triples)}")
    assert len(triples) == 3

    # Iterating over the Dataset, returns every triple in every context as quads
    quads = list(ds)
    logger.debug(f"quads = {len(quads)}")

    # Create a graph in the dataset, if the graph name has already been
    # used, the corresponding graph will be returned
    # (ie, the Dataset keeps track of the constituent graphs)

    g = ds.graph(URIRef("http://www.example.com/gr"))

    # add triples to the new graph as usual
    g.add(
        (
            URIRef("http://example.org/x"),
            URIRef("http://example.org/y"),
            Literal("bar"),
        )
    )

    # alternatively: add a quad to the dataset -> goes to the graph
    ds.add(
        (
            URIRef("http://example.org/x"),
            URIRef("http://example.org/z"),
            Literal("foo-bar"),
            g,
        )
    )

    # querying triples return them all regardless of the graph/context
    triples = list(ds.store.triples((None, None, None)))
    logger.debug(f"store triples = {len(triples)}")
    assert len(triples) == 3

    # Iterating over the Dataset, returns every triple in every context as quads
    quads = list(ds)
    logger.debug(f"quads = {len(quads)}")

    # for context in ds.contexts():
    #     logger.debug(f"\n{context.identifier}\n{context.serialize(format='ttl')}")

    # # querying quads() return quads; the fourth argument can be unrestricted
    # # (None) or restricted to a graph
    for q in ds.quads((None, None, None, None)):
        logger.debug(f"\n{pformat(q, width=240)}")

    # # querying quads() return quads; the fourth argument can be unrestricted
    # # (None) or restricted to a graph
    logger.debug(
        f"\n{pformat(list(ds.quads((None, None, None, default_context))), width=240)}"
    )

    # # querying quads() return quads; the fourth argument can be unrestricted
    # # (None) or restricted to a graph
    logger.debug(f"\n{pformat(list(ds), width=240)}")

    # graph names in the dataset can be queried:
    for c in ds.graphs():
        logger.debug(f"\n{pformat(c, width=120)}")

    # <Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>
    # <Graph identifier=http://www.example.com/gr (<class 'rdflib.graph.Graph'>)>

    # graph names in the dataset can be queried:
    # for c in ds.graphs():
    #     logger.debug(f"\n{pformat(c.identifier, width=120)}")

    # rdflib.term.URIRef('http://www.example.com/gr')
    # rdflib.term.URIRef('urn:x-rdflib:default')

    # restricting iteration to a graph:
    for q in ds.quads((None, None, None, g)):
        logger.debug(f"\n{pformat(q, width=240)}")

    # for context in ds.contexts():
    #     logger.debug(f"\n{context.identifier}\n{context.serialize(format='ttl')}")

    # ds = Dataset(default_union=True)

    # # querying triples return them all regardless of the graph
    # triples = list(ds.store.triples((None, None, None)))
    # logger.debug(f"store triples = {len(triples)}")

    # for t in ds.triples((None, None, None)):
    #     logger.debug(f"\nTriple: {pformat(t)}")

    # # querying triples return them all regardless of the graph
    # for t in ds.triples((None, None, None)):
    #     logger.debug(f"\n{pformat(t)}")

    # (rdflib.term.URIRef("http://example.org/a"),
    #  rdflib.term.URIRef("http://www.example.org/b"),
    #  rdflib.term.Literal("foo"))
    # (rdflib.term.URIRef("http://example.org/x"),
    #  rdflib.term.URIRef("http://example.org/z"),
    #  rdflib.term.Literal("foo-bar"))
    # (rdflib.term.URIRef("http://example.org/x"),
    #  rdflib.term.URIRef("http://example.org/y"),
    #  rdflib.term.Literal("bar"))

    # # a graph can also be removed from a dataset via ds.remove_graph(g)


# FIXME: basically a duplicate of the above (sigh)
# @pytest.mark.skip
def test_read_quads_into_dataset(get_dataset):
    ds = get_dataset
    ds.parse(data=nquads, format="nquads")

    # logger.debug(f"ds contexts\n{pformat(list(ds.contexts()))}")

    # [<Graph identifier=N21945f30f9a64062aed1465b45cdd9d4 (<class 'rdflib.graph.Graph'>)>,
    #  <Graph identifier=http://example.org/graph/sports (<class 'rdflib.graph.Graph'>)>,
    #  <Graph identifier=http://example.org/graph/practise (<class 'rdflib.graph.Graph'>)>,
    #  <Graph identifier=http://example.org/graph/students (<class 'rdflib.graph.Graph'>)>,
    #  <Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]

    ctxlist = pformat(
        [[context.identifier.n3(), len(context)] for context in list(ds.contexts())],
        width=80,
    )
    logger.debug(f"ds contexts\n{ctxlist}")
    # [['<http://example.org/graph/students>', 4],
    #  ['_:N328d847194364096a4aada33bcfeade5', 0],
    #  ['<http://example.org/graph/practise>', 1],
    #  ['<http://example.org/graph/sports>', 2],
    #  ['<urn:x-rdflib:default>', 0]]


# @pytest.mark.skip
def test_read_list_of_quads_into_dataset(get_dataset):
    ds = get_dataset
    for quad in list_of_nquads:
        ds.add(quad)

    # logger.debug(f"ds contexts\n{pformat(list(ds.contexts()))}")

    # [<Graph identifier=N21945f30f9a64062aed1465b45cdd9d4 (<class 'rdflib.graph.Graph'>)>,
    #  <Graph identifier=http://example.org/graph/sports (<class 'rdflib.graph.Graph'>)>,
    #  <Graph identifier=http://example.org/graph/practise (<class 'rdflib.graph.Graph'>)>,
    #  <Graph identifier=http://example.org/graph/students (<class 'rdflib.graph.Graph'>)>,
    #  <Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]

    ctxlist = pformat(
        [[context.identifier.n3(), len(context)] for context in list(ds.contexts())],
        width=80,
    )
    logger.debug(f"ds contexts\n{ctxlist}")
    # [['<http://example.org/graph/students>', 4],
    #  ['_:N328d847194364096a4aada33bcfeade5', 0],
    #  ['<http://example.org/graph/practise>', 1],
    #  ['<http://example.org/graph/sports>', 2],
    #  ['<urn:x-rdflib:default>', 0]]


# @pytest.mark.skip
def test_read_quads_into_conjunctivegraph(get_conjunctivegraph):
    cj = get_conjunctivegraph
    cj.parse(data=nquads, format="nquads")

    #  <Graph identifier=http://example.org/graph/sports (<class 'rdflib.graph.Graph'>)>,
    #  <Graph identifier=http://example.org/graph/practise (<class 'rdflib.graph.Graph'>)>,
    #  <Graph identifier=http://example.org/graph/students (<class 'rdflib.graph.Graph'>)>,

    ctxlist = pformat(
        [[context.identifier.n3(), len(context)] for context in list(cj.contexts())],
        width=80,
    )

    logger.debug(f"cj contexts\n{ctxlist}")
    # [['<http://example.org/graph/students>', 4],
    #  ['<http://example.org/graph/practise>', 1],
    #  ['<http://example.org/graph/sports>', 2],


# @pytest.mark.skip
def test_read_triple_into_dataset(get_dataset):
    # Create a new Dataset
    ds = get_dataset
    # simple triples goes to default graph
    ds.add(
        (
            URIRef("http://example.org/a"),
            URIRef("http://www.example.org/b"),
            Literal("foo"),
        )
    )
    ctxlist = pformat(
        [[context.identifier.n3(), len(context)] for context in list(ds.contexts())],
        width=80,
    )
    assert str(ctxlist) == "[['<urn:x-rdflib:default>', 1]]"

    # Create a graph in the dataset, if the graph name has already been
    # used, the corresponding graph will be returned
    # (ie, the Dataset keeps track of the constituent graphs)
    g = ds.graph(URIRef("http://www.example.com/gr"))

    ds.add(
        (
            URIRef("http://example.org/a"),
            URIRef("http://www.example.org/b"),
            Literal("foo"),
        )
    )

    # add triples to the new graph as usual
    g.add(
        (URIRef("http://example.org/x"), URIRef("http://example.org/y"), Literal("bar"))
    )
    ctxlist = pformat(
        [[context.identifier.n3(), len(context)] for context in list(ds.contexts())],
        width=80,
    )
    assert str(ctxlist) in [
        "[['<http://www.example.com/gr>', 1], ['<urn:x-rdflib:default>', 1]]",
        "[['<urn:x-rdflib:default>', 1], ['<http://www.example.com/gr>', 1]]",
    ]
    # alternatively: add a quad to the dataset -> goes to the graph
    ds.add(
        (
            URIRef("http://example.org/x"),
            URIRef("http://example.org/z"),
            Literal("foo-bar"),
            g,
        )
    )
    ctxlist = pformat(
        [[context.identifier.n3(), len(context)] for context in list(ds.contexts())],
        width=80,
    )
    assert str(ctxlist) in [
        "[['<http://www.example.com/gr>', 2], ['<urn:x-rdflib:default>', 1]]",
        "[['<urn:x-rdflib:default>', 1], ['<http://www.example.com/gr>', 2]]",
    ]

    # querying triples return them all regardless of the graph
    # FAIL
    for t in ds.triples((None, None, None)):
        print(t)
        logger.debug(f"triple {t}")

    triples = [t for t in ds.triples((None, None, None))]
    assert triples == []

    # querying the store's triples return them all regardless of the graph/context
    # PASS
    triples = list(ds.store.triples((None, None, None)))
    # logger.debug(f"store triples = {len(triples)}")
    assert len(triples) == 3

    # querying quads() return quads; the fourth argument can be unrestricted
    # (None) or restricted to a graph
    quads = [q for q in ds.quads((None, None, None, None))]
    assert len(quads) == 3

    # unrestricted looping is equivalent to iterating over the entire Dataset
    quads = [q for q in ds]
    assert len(quads) == 3

    # restricting iteration to a graph:
    quads = [q for q in ds.quads((None, None, None, g))]
    assert len(quads) == 2
    logger.debug(f"quads\n{pformat(quads, width=80)}")

    # Note that in the call above -
    # ds.quads((None,None,None,"http://www.example.com/gr"))
    # would have been accepted, too
    quads = [q for q in ds.quads((None, None, None, "http://www.example.com/gr"))]
    assert len(quads) == 2
    logger.debug(f"quads\n{pformat(quads, width=80)}")

    # graph names in the dataset can be queried:
    gnames = [c for c in ds.graphs()]
    logger.debug(f"graph names\n{pformat(gnames, width=80)}")
    assert str(gnames) in [
        "[<Graph identifier=http://www.example.com/gr (<class 'rdflib.graph.Graph'>)>, <Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]",
        "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>, <Graph identifier=http://www.example.com/gr (<class 'rdflib.graph.Graph'>)>]",
    ]

    # A graph can be created without specifying a name; a skolemized genid
    # is created on the fly
    h = ds.graph()
    assert h is not None
    gnames = [c for c in ds.graphs()]
    logger.debug(f"graph names\n{pformat(gnames, width=80)}")
    assert len(gnames) == 3

    # Note that the Dataset.graphs() call returns names of empty graphs,
    # too. This can be restricted:
    # gnames = [c for c in ds.graphs(empty=False)]
    # logger.debug(f"graph names\n{pformat(gnames, width=80)}")

    # a graph can also be removed from a dataset via ds.remove_graph(g)
    ds.remove_graph(h.identifier)
    gnames = [c for c in ds.graphs()]
    logger.debug(f"graph names\n{pformat(gnames, width=80)}")
    assert len(gnames) == 2

    # a graph can also be removed from a dataset via ds.remove_graph(g)
    h = ds.graph()
    ds.remove_graph(h)
    gnames = [c for c in ds.graphs()]
    logger.debug(f"graph names\n{pformat(gnames, width=80)}")
    assert len(gnames) == 2

    # logger.debug(f"cj contexts\n{ctxlist}")


# @pytest.mark.skip
def test_default_graph(get_dataset):
    d = get_dataset

    d.add((tarek, likes, pizza))

    assert len(d) == 1
    # only default exists
    assert set(
        x.identifier if isinstance(x, Graph) else x for x in d.contexts()
    ) == set([DATASET_DEFAULT_GRAPH_ID])

    # removing default graph removes triples but not actual graph
    d.remove_graph(DATASET_DEFAULT_GRAPH_ID)

    assert len(d) == 0
    # default still exists
    assert set(
        x.identifier if isinstance(x, Graph) else x for x in d.contexts()
    ) == set([DATASET_DEFAULT_GRAPH_ID])


# @pytest.mark.skip
def test_not_union(get_dataset):
    ds = get_dataset

    # Union depends on the SPARQL endpoint configuration
    g1 = ds.graph(c1)
    g1.add((tarek, likes, pizza))

    assert list(ds.objects(tarek, None)) == []
    assert list(g1.objects(tarek, None)) == [pizza]


# @pytest.mark.skip
def test_graph_aware(get_dataset):
    graph = get_dataset
    if not graph.store.graph_aware:
        logger.debug("test_graph_aware returning, store not graph-aware")
        return

    g = graph
    g1 = g.graph(c1)

    # added graph exists

    assert set(x.identifier for x in graph.contexts()) == set(
        [c1, DATASET_DEFAULT_GRAPH_ID]
    )

    # added graph is empty
    assert len(g1) == 0

    g1.add((tarek, likes, pizza))

    # added graph still exists
    assert set(x.identifier for x in graph.contexts()) == set(
        [c1, DATASET_DEFAULT_GRAPH_ID]
    )

    # added graph contains one triple
    assert len(g1) == 1

    g1.remove((tarek, likes, pizza))

    # added graph is empty
    assert len(g1) == 0

    assert set(x.identifier for x in graph.contexts()) == set(
        [c1, DATASET_DEFAULT_GRAPH_ID]
    )

    g.remove_graph(c1)

    # graph is gone
    assert set(x.identifier for x in graph.contexts()) == set(
        [DATASET_DEFAULT_GRAPH_ID]
    )
