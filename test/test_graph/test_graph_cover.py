import re
from pathlib import Path
from test.data import (
    bob,
    cheese,
    context1,
    context2,
    hates,
    likes,
    michel,
    pizza,
    tarek,
)

import pytest

from rdflib import FOAF, XSD, logger
from rdflib.graph import (
    DATASET_DEFAULT_GRAPH_ID,
    Dataset,
    Graph,
    UnSupportedGraphOperation,
)
from rdflib.term import BNode, IdentifiedNode, Literal, Node, URIRef

t1 = (tarek, likes, pizza)
t2 = (tarek, likes, cheese)

dgb = URIRef("http://rdflib/net/")


def test_graph_topython():

    g = Graph()
    assert (
        str(g.toPython())
        == "[a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']]."
    )


def test_graph_n3():

    g = Graph()
    assert re.match(r"\[_:N(.*?)\]", g.n3()) is not None


def test_graph_slicing():

    g = Graph()
    g.add(t1)
    g.add(t2)

    assert t1 in list(g[:])

    assert (likes, pizza) in list(g[tarek:None:])

    assert (pizza) in list(g[tarek:likes])

    assert (likes) in list(g[tarek:None:pizza])

    with pytest.raises(TypeError):
        assert t1 in list(g["foo"])


def test_dataset_set_get_state():
    d = Dataset()
    s = d.__getstate__()
    with pytest.raises(AttributeError):
        d.__setstate__(s)


def test_graph_comparators():

    g1 = Graph(identifier=context1)
    g2 = Graph(identifier=context2)

    g1.add(t1)
    g2.add(t2)
    assert g1.__cmp__(g2) == -1
    assert g1.__cmp__(context2) is 1
    assert g1.__cmp__(None) == -1

    assert g1 < g2

    assert g1 <= g2

    assert g1 > g2

    assert g2 >= g1

    with pytest.raises(UnSupportedGraphOperation):
        assert g1 + Dataset() == None

    with pytest.raises(UnSupportedGraphOperation):
        g1 += Dataset()

    with pytest.raises(UnSupportedGraphOperation):
        assert g1 - Dataset() == None

    with pytest.raises(UnSupportedGraphOperation):
        g1 -= Dataset()

    with pytest.raises(UnSupportedGraphOperation):
        assert g1 * Dataset() == None


def test_graph_value():

    g = Graph()
    g.add(t1)
    assert g.value(None, None) == None
    assert g.value(tarek, None, pizza) == likes

    assert g.value(tarek, likes, None, any=False) == pizza


def test_graph_triples_with_path():
    g = Graph()
    g.add(t1)
    g.add((tarek, FOAF.knows, michel))

    assert len(list(g.triples((tarek, FOAF.knows / FOAF.name, None)))) == 0


def test_graph_transitive_closure():
    from rdflib.collection import Collection
    from rdflib.namespace import RDF, RDFS

    def topList(node, g):
        for s in g.subjects(RDF.rest, node):
            yield s

    def reverseList(node, g):
        for s in g.subjects(RDF.rest, node):
            yield s

    g = Graph()
    a = BNode("foo")
    b = BNode("bar")
    c = BNode("baz")
    g.add((a, RDF.first, RDF.type))

    g.add((a, RDF.rest, b))
    g.add((b, RDF.first, RDFS.label))

    g.add((b, RDF.rest, c))
    g.add((c, RDF.first, RDFS.comment))
    g.add((c, RDF.rest, RDF.nil))

    assert [rt for rt in g.transitiveClosure(topList, RDF.nil)] == [c, b, a]


def test_graph_transitive_subject():

    person = URIRef("ex:person")
    dad = URIRef("ex:d")
    mom = URIRef("ex:m")
    momOfDad = URIRef("ex:gm0")
    momOfMom = URIRef("ex:gm1")
    dadOfDad = URIRef("ex:gf0")
    dadOfMom = URIRef("ex:gf1")

    parent = URIRef("ex:parent")

    g = Dataset(default_union=True)

    g.add((person, parent, dad))
    g.add((person, parent, mom))
    g.add((dad, parent, momOfDad))
    g.add((dad, parent, dadOfDad))
    g.add((mom, parent, momOfMom))
    g.add((mom, parent, dadOfMom))

    # "Parents, forward from `ex:person`:
    assert URIRef('ex:gm1') in list(g.transitive_objects(person, parent))

    # Parents, *backward* from `ex:gm1`:
    assert URIRef('ex:gm1') in list(g.transitive_subjects(parent, momOfMom))


def test_graph_serialize_destinations():
    import tempfile

    g = Graph()
    g.add(t1)
    fd, name = tempfile.mkstemp()
    g.serialize(destination=name, format="ttl")


def test_graph_isomorphic():
    g1 = Graph(identifier=context1)
    g2 = Graph(identifier=context2)

    g1.add(t1)
    g2.add(t2)
    assert g1.isomorphic(g2) is False

    g2.add((bob, likes, cheese))

    assert g1.isomorphic(g2) is False


def test_graph_connected():

    g = Graph()
    assert g.connected() is False


def test_graph_resource():
    from rdflib.graph import Resource

    graph = Graph()
    resource = graph.resource(context1)
    assert isinstance(resource, Resource)
    assert resource.identifier is context1
    assert resource.graph is graph


def test_dataset_init():
    with pytest.raises(ValueError):
        d = Dataset(identifier=Graph())


def test_dataset_pickle_unpickle():
    import pickle

    d = Dataset()

    dump = pickle.dumps(d)
    newd = pickle.loads(dump)

    assert newd == d


def test_dataset_triples():

    d = Dataset()
    d.add(t1)
    d.add(t2)
    assert len(list(d.triples((None, None, None), DATASET_DEFAULT_GRAPH_ID))) == 2

    assert len(list(d.triples((tarek, Path("/tmp/foo"), None)))) == 0

    # assert len(list(d.triples((None, Path(), None), DATASET_DEFAULT_GRAPH_ID))) == 0


def test_dataset_triples_choices():

    d = Dataset()
    d.add(t1)
    d.add(t2)

    choices = [likes, hates]

    assert t1 in list(d.triples_choices((tarek, choices, None)))


def test_dataset_get_context_deprecation():
    d = Dataset()
    with pytest.deprecated_call():
        assert isinstance(d.get_context(context1), Graph)
