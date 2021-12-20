import pytest
import os
import shutil
import tempfile
import re
from pprint import pformat
import rdflib
from rdflib import (
    logger,
    BNode,
    Literal,
    Graph,
    ConjunctiveGraph,
    Dataset,
    Namespace,
    RDFS,
    URIRef,
)
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
    dataset = Dataset(store=store)
    dataset.open(tmppath, create=True)
    # tmppath = mkdtemp()
    if store != "default" and dataset.store.is_open():
        # delete the graph for each test!
        dataset.remove((None, None, None))
        for c in dataset.contexts():
            c.remove((None, None, None))
            assert len(c) == 0
            dataset.remove_graph(c)
    # logger.debug(f"Using store {dataset.store}")

    yield dataset

    dataset.close()
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


# # @pytest.mark.skip
# def test_dataset_default_graph_and_contexts_with_namespace_bound(get_dataset):
#     ds = get_dataset

#     dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)

#     # ADD ONE TRIPLE *without context* to the default graph

#     ds.bind("", "urn:", True)
#     ds.add((tarek, likes, pizza))

#     # logger.debug(f"\n\nTRIG serialization\n{repr(ds.serialize(format='trig'))}")
#     assert repr(ds.serialize(format="trig")) == repr(
#         "@prefix : <urn:> .\n"
#         "@prefix ns1: <urn:x-rdflib:> .\n"
#         "\n"
#         "ns1:default {\n"
#         "    :tarek :likes :pizza .\n"
#         "}\n"
#         "\n"
#     )

#     # logger.debug(
#     #     f"\n\nXML serialization\n{repr(dataset_default_graph.serialize(format='xml'))}"
#     # )
#     assert repr(dataset_default_graph.serialize(format="xml")) == repr(
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


@pytest.mark.skip
# def test_issue319_add_graph_as_dataset_default(get_dataset):
def test_issue319_add_graph_as_dataset_default():

    # STATUS: FIXME remains an issue
    """
    uholzer commented on 1 Aug 2013

    Imagine, you are given a Graph, maybe created with Graph() or maybe
    backed by some arbitrary store. Maybe, for some reason you need a
    Dataset and you want your Graph to be the default graph of this
    Dataset. The Dataset should not and will not need to contain any other
    graphs.

    Is there a straightforward way to achieve this without copying all
    triples? As far as I know, Dataset needs a context_aware and
    graph_aware store, so it is not possible to just create a Dataset
    backed by the same store. Graham Klyne is interested in this because he
    wants to provide a SPARQL endpoint for a given rdflib.Graph, but my
    implementation of a SPARQL endpoint requires a Dataset. I don't really
    like to implement support for plain graphs, so I wonder whether there
    is a simple solution.

    Also, I wonder whether it would be useful to have a true union of
    several graphs backed by different stores.


    gromgull commented on 2 Aug 2013

    There is no way to do it currently, but it would be easy enough to add.

    In most cases, the underlying store WILL be context_aware, since most of our
    stores are, but even if it isn't, we could implement a special "single graph
    dataset" that will throw an exception if you try to get any other graphs?

    And actually, the DataSet is very similar to a graph, how would your endpoint
    implementation break if just handed a graph.

    For the actual SPARQL calls, I made an effort to work with both
    ConjunctiveGraph and DataSet (or rather, with graph_aware and not graph_aware
    stores) for the bits that require graphs, and even with a non context-aware
    graph/store for everything else.

    The true-union of graphs from different stores is easy to do naively and with
    poor performance, and probably impossible to make really scalable (if you
    have 1000 graphs ... ) It's probably another issue though :)

    uholzer commented on 2 Aug 2013

    Thinking about it again, some fixes to my implementation should indeed make
    it compatible with rdflib.Graph.

    uholzer commented on 10 Aug 2013

    There is a discrepancy between Graph and Dataset (note that the parsed triple
    is missing from the serialization):

    ds = rdflib.Dataset()
    ds.parse(data='<a> <b> <c>.', format='turtle')
    print(ds.serialize(format='turtle')) #doctring: +SKIP
    for c in ds.contexts(): print c
    ...
    [a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory']].
    <urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'IOMemory'].

    It is clear to me why this happens. ConjunctiveGraph parses into a fresh graph
    and Dataset inherits this behaviour. For ConjunctiveGraphs one does not
    observe the above, because the default is the union and hence contains the
    fresh graph.

    Is this behaviour intended? (It doesn't bother me much, I just wanted to note it.)

    iherman commented on 11 Aug 2013

    Well...

    One would have to look at the turtle parser behaviour to understand what is
    going on. But it also a rdflib design decision.

    Formally, a turtle file returns a graph. Not a dataset; a graph.

    Which means that the situation below is unclear at a certain level: what
    happens if one parses a turtle file (ie a graph) into a dataset.

    I guess the obvious answer is that it should be parsed into the default graph,
    but either the turtle parser is modified to do that explicitly in case or a
    Dataset, or an extra trick should be done in the Dataset object.

    And, of course, any modification to the turtle file should be done to all
    other parsers, which is a bit of a pain (though may be a much cleaner
    solution!).


    """
    # ds = get_dataset
    logger.debug("test_issue319_add_graph_as_dataset_default: initialising dataset")
    ds = Dataset()

    # There are no triples in any context, so dataset length == 0
    assert len(ds) == 0

    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    # Only the default graph exists and is yielded by ds.contexts()
    assert (
        repr(list(ds.contexts()))
        == "[<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>]"
    )

    # only the default graph exists and is properly identified as DATASET_DEFAULT_GRAPH_ID
    assert set(x.identifier for x in ds.contexts()) == set([DATASET_DEFAULT_GRAPH_ID])

    dataset_default_graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    # logger.debug(f"\n\nDATASET_DEFAULT_GRAPH\n{repr(dataset_default_graph)}")
    assert (
        repr(dataset_default_graph)
        == "<Graph identifier=urn:x-rdflib:default (<class 'rdflib.graph.Graph'>)>"
    )

    logger.debug(
        "test_issue319_add_graph_as_dataset_default: SPARQL update of DEFAULT graph"
    )
    ds.update(
        "INSERT DATA { GRAPH <urn:x-rdflib:default> { <urn:tarek> <urn:likes> <urn:cheese> . } }"
    )

    logger.debug(
        "test_issue319_add_graph_as_dataset_default: SPARQL update of DEFAULT graph"
    )
    ds.update("INSERT DATA { <urn:tarek> <urn:likes> <urn:camembert> . } ")

    # logger.debug(
    #     f" CONTEXT IDENTIFIERS {pformat([c.identifier for c in list(ds.contexts())])}"
    # )
    # The default graph is a context so the length of ds.contexts() == 1
    assert len(list(ds.contexts())) == 1

    logger.debug(
        "test_issue319_add_graph_as_dataset_default: SPARQL update of NAMED graph"
    )
    ds.update(
        "INSERT DATA { GRAPH <urn:context-1> { <urn:tarek> <urn:hates> <urn:pizza> . } }"
    )
    # logger.debug(
    #     f" CONTEXT IDENTIFIERS {pformat([c.identifier for c in list(ds.contexts())])}"
    # )
    assert len(list(ds.contexts())) == 2

    logger.debug(
        "test_issue319_add_graph_as_dataset_default: Parsing data into BNODE-named graph"
    )
    g = ds.graph(BNode())
    g.parse(data="<urn:bob> <urn:likes> <urn:pizza> .", format="ttl")
    # logger.debug(
    #     f" CONTEXT IDENTIFIERS {pformat([c.identifier for c in list(ds.contexts())])}"
    # )
    assert len(list(ds.contexts())) == 3

    logger.debug(
        "test_issue319_add_graph_as_dataset_default: Parsing data into UNNAMED graph"
    )
    g = ds.graph()
    g.parse(data="<urn:michel> <urn:likes> <urn:pizza> .", format="ttl")
    # logger.debug(
    #     f" CONTEXT IDENTIFIERS {pformat([c.identifier for c in list(ds.contexts())])}"
    # )
    assert len(list(ds.contexts())) == 4

    logger.debug(
        "test_issue319_add_graph_as_dataset_default: Parsing data into NAMED graph"
    )
    g = ds.graph()
    g.parse(
        data="<urn:michel> <urn:hates> <urn:pizza> <urn:context-3> .", format="nquads"
    )
    # logger.debug(
    #     f" CONTEXT IDENTIFIERS {pformat([c.identifier for c in list(ds.contexts())])}"
    # )
    assert len(list(ds.contexts())) == 6

    logger.debug(
        "test_issue319_add_graph_as_dataset_default: Parsing data into PUBLICID graph"
    )
    ds.parse(
        data="<urn:tarek> <urn:likes> <urn:michel> .",
        format="ttl",
        publicID="urn:context-4",
    )

    assert len(list(ds.contexts())) == 7

    logger.debug(
        "test_issue319_add_graph_as_dataset_default: Parsing data into DEFAULT graph"
    )
    ds.parse(data="<urn:tarek> <urn:likes> <urn:pizza> .", format="ttl")

    assert len(list(ds.contexts())) == 8

    logger.debug(
        f"test_issue319_add_graph_as_dataset_default: dataset:\n\n{ds.serialize(format='trig')}"
    )


@pytest.mark.skip
def test_issue1188_with_graph():
    """

    # urbanmatthias commented on 14 Oct 2020

    It seems to me that RDFLib behaves differently with graphs
    than it does with sets.

    While |= performs an in-place union when used with sets,
    RDFLib creates a new Graph when used with Graphs.

    ---

    # ashleysommer commented on 15 Oct 2020

    Hi @urbanmatthias

    Yep, you're right. That union operator does work differently on a Graph than
    it does on a set, and it does look like its that way on purpose.

    I don't know what is more "correct" here.

    I think the idea behind creating a new graph on this operation is to avoid
    polluting an existing graph. Or the graph a might be read-only, so the most
    consistent and reliable way of completing the union would be to create a new
    graph and union into that.

    Note, I found in my testing that a += c does do what you'd expect a |= c to
    do. But I think that is wrong too, because += should add a single triple or a
    list of triples, where |= should union the graphs as it does for a set.

    My thoughts for changes in RDFLib v6.0.0 are:

    - `a |= c` (where a is a graph and c is a second graph) should should modify
      and write into a, without creating a new graph

    ++++++++++++++++++++++++++++++++++++++++++++++++++
    operator.__ior__(a, b)

        a = ior(a, b) is equivalent to a |= b.
    ++++++++++++++++++++++++++++++++++++++++++++++++++

    - `a += (s, p, o)` should be the same as `a.add((s,p,o))`

    - `a += [(s1,p1,o1), (s2,p2,o2)]` should be the same as `a.addN([(s1,p1,o1), (s2,p2,o2)])`

    ++++++++++++++++++++++++++++++++++++++++++++++++++
    operator.__iadd__(a, b)

        a = iadd(a, b) is equivalent to a += b.
    ++++++++++++++++++++++++++++++++++++++++++++++++++

    Implemented as:
    ==================================================

    def __iadd__(self, other):

        '''Add all triples in Graph other to Graph.
        BNode IDs are not changed.'''

        self.addN((s, p, o, self) for s, p, o in other)
        return self

    ==================================================

    BUT

    ==================================================

    def __add__(self, other):
        '''Set-theoretic union
        BNode IDs are not changed.'''

        try:
            retval = type(self)()
        except TypeError:
            retval = Graph()
        for (prefix, uri) in set(list(self.namespaces()) + list(other.namespaces())):
            retval.bind(prefix, uri)
        for x in self:
            retval.add(x)
        for y in other:
            retval.add(y)
        return retval

    ==================================================
    ---

    #  FlorianLudwig commented on 15 Oct 2020

    Some more context from the python stdlib:

    The `<operator>=` like `+=` or `|=` are called "in place" in python and for
    mutable objects (like sets) it means that the left-hand object is changed.

    I don't think the python convention is that "in place" means the left-hand
    MUST be mutated (so the current implementation is not wrong) but CAN or
    SHOULD(for performance reasons).

    I think the idea behind creating a new graph on this operation is to avoid
    polluting an existing graph.

    As in-place operators do "pollute" objects with standard types I don't think
    this is a behaviour is expected. If needed, `a = a + c` can still be used.

    Or the graph a might be read-only, so the most consistent and reliable way of
    completing the union would be to create a new graph and union into that.

    The standard library does create new objects for immutable objects, like tuples:

    >>> a = (1, 2)
    >>> a + (3, 4)
    (1, 2, 3, 4)

    >>> a += (3, 4)
    >>> a
    (1, 2, 3, 4)

    ---

    # white-gecko commented on 15 Oct 2020

    I think changing this for v6 would be a good idea. I would expect the in-place
    operators to actually work in-place.

    Actually I do not understand, what could be the difference between `+=` and `|=`
    on graphs. I would expect both to behave in the same way, also if left and
    right are graphs or left is a graph and right is a triple. Is there a
    difference for sets between `+=` and `|=`?

    # FlorianLudwig commented on 15 Oct 2020

    @white-gecko
    sets do not support `+=`

    # jbmchuck commented on 15 Oct 2020 •

    Updating `|=` to perform an in-place union would be nice. I believe it's doing
    an update rather than a union if we are going by set's semantics.

    I'd like if RDFLib could keep current `|=` behavior but as | and/or
    Graph.union - this would mirror the behavior of set and would give a
    migration path for code relying on `|=`'s current behavior.

    """
    a = set()
    b = a
    a |= {"elem"}

    assert a is b

    logger.debug(f"{a}, {b}")
    # ({'elem'}, {'elem'})

    a = Graph()
    b = a

    c = Graph()
    c.add((URIRef("s"), URIRef("p"), URIRef("o")))

    a |= c

    with pytest.raises(AssertionError):
        assert a is b

    # logger.debug(f"\na = {list(a)}\nb = {list(b)}")
    # ([(URIRef('s'), URIRef('p'), URIRef('o'))], [])

    # `a += (s, p, o)` should be the same as `a.add((s,p,o))`
    a = Graph()

    triple = (tarek, likes, pizza)
    with pytest.raises(ValueError):  # expects a graph
        a += triple

    b = Graph()
    b.add((triple))
    logger.debug(f"\nb is {b.serialize(format='json-ld')}")

    a += b
    logger.debug(f"\na += b is {a.serialize(format='json-ld')}")

    # `a |= c` (where a is a graph and c is a second graph) should should modify and write into a, without creating a new graph
    # a = Graph()
    # b = Graph()

    # `a += [(s1,p1,o1), (s2,p2,o2)]` should be the same as `a.addN([(s1,p1,o1), (s2,p2,o2)])`
    # a = Graph()


@pytest.mark.skip
def test_issue1188_with_dataset_and_graph(get_dataset):
    # STATUS: PASS
    g1 = get_dataset
    g2 = Graph()
    u = URIRef("http://example.com/foo")
    g1.add((u, RDFS.label, Literal("foo")))
    g1.add((u, RDFS.label, Literal("bar")))

    g2.add([u, RDFS.label, Literal("foo")])
    g2.add([u, RDFS.label, Literal("bing")])

    try:
        assert len(g1 + g2) == 3  # adds bing as label
    except AssertionError as e:
        assert repr(e) in [
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label foo is None!')",
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label bar is None!')",
        ]
    try:
        assert len(g1 - g2) == 1  # removes foo
    except ValueError as e:
        assert repr(e) == "ValueError('too many values to unpack (expected 3)')"

    assert len(g1 * g2) == 1  # only foo

    g1 += g2  # now g1 contains everything
    assert len(g1) == 3


@pytest.mark.skip
def test_issue1188_with_dataset_and_conjunctivegraph(get_dataset):
    # STATUS: PASS
    g1 = get_dataset
    g2 = ConjunctiveGraph()
    u = URIRef("http://example.com/foo")
    g1.add((u, RDFS.label, Literal("foo")))
    g1.add((u, RDFS.label, Literal("bar")))

    g2.add([u, RDFS.label, Literal("foo")])
    g2.add([u, RDFS.label, Literal("bing")])

    try:
        assert len(g1 + g2) == 3  # adds bing as label
    except AssertionError as e:
        assert repr(e) in [
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label foo is None!')",
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label bar is None!')",
        ]

    assert len(g1 - g2) == 1  # removes foo
    assert len(g1 * g2) == 1  # only foo

    g1 += g2  # now g1 contains everything
    assert len(g1) == 3


@pytest.mark.skip
def test_issue1188_with_dataset_and_namedgraph(get_dataset):
    # STATUS: PASS
    g1 = get_dataset
    g2 = ConjunctiveGraph(identifier=URIRef("context-1"))

    u = URIRef("http://example.com/foo")
    g1.add((u, RDFS.label, Literal("foo")))
    g1.add((u, RDFS.label, Literal("bar")))

    g2.add((u, RDFS.label, Literal("foo")))
    g2.add((u, RDFS.label, Literal("bing")))

    try:
        assert len(g1 + g2) == 3  # adds bing as label
    except AssertionError as e:
        assert repr(e) in [
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label foo is None!')",
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label bar is None!')",
        ]

    assert len(g1 - g2) == 1  # removes foo
    assert len(g1 * g2) == 1  # only foo

    g1 += g2  # now g1 contains everything
    assert len(g1) == 3


@pytest.mark.skip
def test_issue1188_with_two_datasets(get_dataset):
    # STATUS: PASS
    g1 = get_dataset
    g2 = get_dataset
    u = URIRef("http://example.com/foo")
    g1.add((u, RDFS.label, Literal("foo")))
    g1.add((u, RDFS.label, Literal("bar")))

    g2.add((u, RDFS.label, Literal("foo")))
    g2.add((u, RDFS.label, Literal("bing")))

    try:
        assert len(g1 + g2) == 3  # adds bing as label
    except AssertionError as e:
        assert repr(e) in [
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label foo is None!')",
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label bar is None!')",
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label bing is None!')",
        ]

    with pytest.raises(AssertionError):
        assert len(g1 - g2) == 1  # removes foo
    assert len(g1 - g2) == 0  # removes everything!!

    with pytest.raises(AssertionError):
        assert len(g1 * g2) == 1  # only foo
    assert len(g1 * g2) == 3  # everything!!

    try:
        g1 += g2  # now g1 contains everything
    except AssertionError as e:
        assert repr(e) in [
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label foo is None!')",
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label bar is None!')",
            "AssertionError('Context associated with http://example.com/foo http://www.w3.org/2000/01/rdf-schema#label bing is None!')",
        ]


@pytest.mark.skip
def test_issue1188_with_two_conjunctivegraphs(get_conjunctivegraph):
    # STATUS: PASS
    g1 = get_conjunctivegraph
    g2 = get_conjunctivegraph
    u = URIRef("http://example.com/foo")

    g1.add((u, RDFS.label, Literal("foo")))
    g1.add((u, RDFS.label, Literal("bar")))

    g2.add((u, RDFS.label, Literal("foo")))
    g2.add((u, RDFS.label, Literal("bing")))

    # assert len(g1 + g2) == 3  # adds bing as label

    with pytest.raises(AssertionError):
        assert len(g1 - g2) == 1  # removes foo
    assert len(g1 - g2) == 0  # removes everything!!

    # with pytest.raises(AssertionError):
    #     assert len(g1 * g2) == 1  # only foo
    # assert len(g1 * g2) == 3  # everything!!

    # g1 += g2  # now g1 contains everything
    # assert len(g1) == 3


# @pytest.mark.skip
def test_issue837_memory():
    mgraph = Graph()
    mgraph.parse("https://www.w3.org/People/Berners-Lee/card")
    g = mgraph.skolemize()
    assert len(list(g.subjects())) > 0
    triples = list(g.triples((None, None, None)))

    sgraph = Graph(store="SPARQLUpdateStore", identifier=URIRef("context0"))
    sgraph.open(configuration="http://localhost:3030/db/update")
    for triple in triples:
        sgraph.add(triple)

    qgraph = Graph(
        store="SPARQLStore", identifier=URIRef("http://server/unset-base/context0")
    )
    qgraph.open(configuration="http://localhost:3030/db/sparql")
    logger.debug(f"{pformat(list(qgraph.subjects(unique=True)))}")


# if __name__ == "__main__":
#     test_issue319_add_graph_as_dataset_default()
