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
def get_dataset_default_union(request):
    store = request.param
    tmppath = os.path.join(tempfile.gettempdir(), f"test_{store.lower()}")
    dataset = Dataset(store=store, default_union=True)
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


# Think about __iadd__, __isub__ etc. for ConjunctiveGraph
# https://github.com/RDFLib/rdflib/issues/225

# Currently all operations are done on the default graph, i.e. if you add
# another graph, even if it's a conjunctive graph, all triples are added
# to the default graph.

# It may make sense to check if the other thing added is ALSO a
# conjunctive graph and merge the contexts:


def test_operators_with_conjunctivegraph(get_conjunctivegraph):

    cg = get_conjunctivegraph
    cg.parse(data=nquads, format="nquads")

    assert len(cg) == 7
    assert len(list(cg.contexts())) == 3

    for ctx in cg.contexts():
        quads = cg.quads((None, None, None, ctx))
        logger.debug(f"{ctx.identifier}: {len(list(quads))}")

    assert len(list(cg.triples((None, None, None)))) == 7
    assert len(list(cg.quads((None, None, None, None)))) == 7

    g = Graph()

    assert len(g + cg) == 7  # gets everything


@pytest.mark.skip
def test_operators_with_conjunctivegraph_and_graph(get_conjunctivegraph):

    cg = get_conjunctivegraph
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    assert len(cg + g) == 3  # adds cheese as liking

    assert len(cg - g) == 1  # removes pizza

    assert len(cg * g) == 1  # only pizza


@pytest.mark.skip
def test_reversed_operators_with_conjunctivegraph_and_graph(get_conjunctivegraph):

    cg = get_conjunctivegraph
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    # Semantically sane
    assert len(g + cg) == 3  # adds cheese as liking
    # logger.debug(
    #     f"add\ng:\n{g.serialize(format='json-ld')}\ncg\n{cg.serialize(format='json-ld')}\n(g+cg)\n{(g + cg).serialize(format='json-ld')})"
    # )

    # Semantically sane
    assert len(g - cg) == 1  # removes pizza
    # logger.debug(
    #     f"add\ng:\n{g.serialize(format='json-ld')}\ncg\n{cg.serialize(format='json-ld')}\n(g-cg)\n{(g - cg).serialize(format='json-ld')})"
    # )

    # Semantically sane
    assert len(g * cg) == 1  # only pizza
    # logger.debug(
    #     f"add\ng:\n{g.serialize(format='json-ld')}\ncg\n{cg.serialize(format='json-ld')}\n(g*cg)\n{(g * cg).serialize(format='json-ld')})"
    # )


@pytest.mark.skip
def test_operators_with_dataset_and_graph(get_dataset):

    ds = get_dataset
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    assert len(ds + g) == 3  # adds cheese as liking

    # with pytest.raises(ValueError):  # too many values to unpack (expected 3)
    #     assert len(ds - g) == 1  # removes pizza

    try:
        logger.debug(
            f"sub\nds:\n{ds.serialize(format='json-ld')}\ng\n{g.serialize(format='json-ld')})"
        )
        assert len(ds - g) == 1  # removes pizza
    except ValueError as e:
        assert repr(e) == "ValueError('too many values to unpack (expected 3)')"

    assert len(ds * g) == 1  # only pizza


@pytest.mark.skip
def test_reversed_operators_with_dataset_and_graph(get_dataset):

    ds = get_dataset
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    # assert len(g + ds) == 3  # adds cheese as liking

    with pytest.raises(ValueError):  # too many values to unpack (expected 3)
        assert len(g + ds) == 3  # adds cheese as liking

    # with pytest.raises(ValueError):  # too many values to unpack (expected 3)
    #     assert len(ds - g) == 1  # removes pizza

    # assert len(ds - g) == 1  # removes pizza

    try:
        # logger.debug(
        #     f"sub\ng:\n{g.serialize(format='json-ld')}\nds\n{ds.serialize(format='json-ld')}\n(g-ds)\n{(g - ds).serialize(format='json-ld')})"
        # )
        assert len(ds - g) == 1  # removes pizza
    except ValueError as e:
        assert repr(e) == "ValueError('too many values to unpack (expected 3)')"

    assert len(ds * g) == 1  # only pizza


# @pytest.mark.skip
def test_operators_with_two_conjunctivegraphs():

    cg1 = ConjunctiveGraph()
    cg1.add([tarek, likes, pizza])
    cg1.add([tarek, likes, michel])

    cg2 = ConjunctiveGraph()
    cg2.add([tarek, likes, pizza])
    cg2.add([tarek, likes, cheese])

    assert len(cg1 + cg2) == 3  # adds cheese as liking

    assert len(cg1 - cg2) == 1  # removes pizza

    assert len(cg1 * cg2) == 1  # only pizza


@pytest.mark.skip
def test_operators_with_dataset_and_conjunctivegraph(get_dataset, get_conjunctivegraph):

    ds = get_dataset
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    cg = get_conjunctivegraph
    cg.add([tarek, likes, pizza])
    cg.add([tarek, likes, cheese])

    assert len(ds + cg) == 3  # adds cheese as liking

    assert len(ds - cg) == 1  # removes pizza

    assert len(ds * cg) == 1  # only pizza


@pytest.mark.skip
def test_operators_with_dataset_and_namedgraph(get_dataset):

    ds = get_dataset
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    ng = ConjunctiveGraph(identifier=URIRef("context-1"))
    ng.add([tarek, likes, pizza])
    ng.add([tarek, likes, cheese])

    assert len(ds + ng) == 3  # adds cheese as liking

    assert len(ds - ng) == 1  # removes pizza

    assert len(ds * ng) == 1  # only pizza


# @pytest.mark.skip
def test_operators_with_two_datasets():

    ds1 = Dataset()
    ds1.add((tarek, likes, pizza))
    ds1.add((tarek, likes, michel))

    ds2 = Dataset()
    ds2.add((tarek, likes, pizza))
    ds2.add((tarek, likes, cheese))

    assert len(ds1 + ds2) == 3  # adds cheese as liking

    assert len(ds1 - ds2) == 1  # removes pizza

    assert len(ds1 * ds2) == 1  # only pizza


# @pytest.mark.skip
def test_operators_with_two_datasets_default_union(
    get_dataset_default_union, get_dataset
):

    ds1 = get_dataset_default_union
    ds1.add((tarek, likes, pizza))
    ds1.add((tarek, likes, michel))

    ds2 = get_dataset
    ds2.add((tarek, likes, pizza))
    ds2.add((tarek, likes, cheese))

    assert len(ds1 + ds2) == 3  # adds cheese as liking

    assert len(ds1 - ds2) == 1  # removes pizza

    assert len(ds1 * ds2) == 1  # only pizza


@pytest.mark.skip
def test_inplace_operators_with_conjunctivegraph_and_graph(get_conjunctivegraph):

    cg = get_conjunctivegraph
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    cg += g  # now cg contains everything
    # logger.debug(f"_iadd, cg contains everything\n{cg.serialize(format='json-ld')}")

    assert len(cg) == 3

    cg.remove((None, None, None, None))
    assert len(cg) == 0

    cg -= g
    # logger.debug(f"_isub, removes pizza\n{cg.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(cg) == 1  # removes pizza

    cg.remove((None, None, None, None))
    assert len(cg) == 0

    cg *= g
    # logger.debug(f"_imul, only pizza\n{cg.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(cg) == 1  # only pizza


@pytest.mark.skip
def test_inplace_operators_with_two_conjunctivegraphs(get_conjunctivegraph):

    cg1 = get_conjunctivegraph
    cg1.add((tarek, likes, pizza))
    cg1.add((tarek, likes, michel))

    cg2 = get_conjunctivegraph
    cg2.add((tarek, likes, pizza))
    cg2.add((tarek, likes, cheese))

    cg1 += cg2  # now cg1 contains everything
    # logger.debug(f"_iadd, cg1 contains everything\n{cg1.serialize(format='json-ld')}")

    assert len(cg1) == 3

    cg1.remove((None, None, None, None))
    assert len(cg1) == 0

    cg1 -= cg2
    # logger.debug(f"_isub, removes pizza\n{cg1.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):
        assert len(cg1) == 1  # removes pizza

    cg1.remove((None, None, None, None))
    assert len(cg1) == 0

    cg1 *= cg2
    # logger.debug(f"_imul, only pizza\n{cg1.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):
        assert len(cg1) == 1  # only pizza


@pytest.mark.skip
def test_inplace_operators_with_dataset_and_graph(get_dataset):

    ds = get_dataset
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    g = Graph()
    g.add([tarek, likes, pizza])
    g.add([tarek, likes, cheese])

    ds += g  # now ds contains everything
    # logger.debug(f"_iadd, ds contains everything\n{ds.serialize(format='json-ld')}")

    assert len(ds) == 3

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds -= g
    # logger.debug(f"_isub, removes pizza\n{ds.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # removes pizza

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds *= g
    # logger.debug(f"_imul, only pizza\n{ds.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # only pizza


@pytest.mark.skip
def test_inplace_operators_with_dataset_and_conjunctivegraph(get_dataset):

    ds = get_dataset
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    cg = ConjunctiveGraph()
    cg.add([tarek, likes, pizza])
    cg.add([tarek, likes, cheese])

    ds += cg  # now ds contains everything
    # logger.debug(f"_iadd, ds contains everything\n{ds.serialize(format='json-ld')}")

    assert len(ds) == 3

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds -= cg
    # logger.debug(f"_isub, removes pizza\n{ds.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # removes pizza

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds *= cg
    # logger.debug(f"_imul, only pizza\n{ds.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # only pizza


@pytest.mark.skip
def test_inplace_operators_with_dataset_and_namedgraph(get_dataset):

    ds = get_dataset
    ds.add((tarek, likes, pizza))
    ds.add((tarek, likes, michel))

    cg = ConjunctiveGraph(identifier=URIRef("context-1"))
    cg.add((tarek, likes, pizza))
    cg.add((tarek, likes, cheese))

    ds += cg  # now ds contains everything
    # logger.debug(f"_iadd, ds contains everything\n{ds.serialize(format='json-ld')}")

    assert len(ds) == 3

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds -= cg
    # logger.debug(f"_isub, removes pizza\n{ds.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # removes pizza

    ds.remove((None, None, None, None))
    assert len(ds) == 0

    ds *= cg
    # logger.debug(f"_imul, only pizza\n{ds.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds) == 1  # only pizza


@pytest.mark.skip
def test_inplace_operators_with_two_datasets(get_dataset):

    ds1 = get_dataset
    ds1.add((tarek, likes, pizza))
    ds1.add((tarek, likes, michel))

    ds2 = get_dataset
    ds2.add((tarek, likes, pizza))
    ds2.add((tarek, likes, cheese))

    # with pytest.raises(AssertionError):  # Context associated with s, p, o is None
    #     ds1 += ds2  # now ds1 contains everything
    #     assert len(ds1) == 3

    try:
        # logger.debug(
        #     f"sub\nds1:\n{ds1.serialize(format='json-ld')}\nds2\n{ds2.serialize(format='json-ld')})"
        # )
        ds1 += ds2  # now ds1 contains everything
        # logger.debug(f"_iadd, ds1 contains everything\n{ds1.serialize(format='json-ld')}")
    except Exception as e:
        assert repr(e) in [
            "AssertionError('Context associated with urn:tarek urn:likes urn:pizza is None!')",
            "AssertionError('Context associated with urn:tarek urn:likes urn:michel is None!')",
            "AssertionError('Context associated with urn:tarek urn:likes urn:cheese is None!')",
        ]

    # Yet ...
    assert len(ds1) == 3

    ds1.remove((None, None, None, None))
    assert len(ds1) == 0

    ds1 -= ds2
    # logger.debug(f"_isub, removes pizza\n{ds1.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds1) == 1  # removes pizza

    ds1.remove((None, None, None, None))
    assert len(ds1) == 0

    ds1 *= ds2
    # logger.debug(f"_imul, only pizza\n{ds1.serialize(format='json-ld')}")

    with pytest.raises(AssertionError):  # 0 == 1
        assert len(ds1) == 1  # only pizza


if __name__ == "__main__":
    test_inplace_operators_with_dataset_and_graph(get_dataset)
