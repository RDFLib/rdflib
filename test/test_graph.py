import os
import tempfile
import shutil
from typing import Optional
import pytest
from urllib.error import URLError, HTTPError

from rdflib import URIRef, Graph, plugin
from rdflib.store import VALID_STORE
from rdflib.exceptions import ParserError
from rdflib.plugin import PluginException
from rdflib.namespace import Namespace

from pathlib import Path

from test.testutils import GraphHelper

michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")


# dynamically create classes for each registered Store

pluginstores = ["default"]

for s in plugin.plugins(None, plugin.Store):
    skip_reason: Optional[str] = None
    if s.name in (
        "default",
        "Memory",
        "Auditable",
        "Concurrent",
        "SPARQLStore",
        "SPARQLUpdateStore",
    ):
        continue  # these are tested by default

    if s.name in ("SimpleMemory",):
        # these (by design) won't pass some of the tests (like Intersection)
        continue
    pluginstores.append(s.name)


@pytest.fixture(
    scope="function",
    params=pluginstores,
)
def get_graph(request):
    store = request.param
    path = os.path.join(tempfile.gettempdir(), f"test_{store.lower()}")

    try:
        shutil.rmtree(path)
    except Exception:
        pass

    try:
        graph = Graph(store=store)
    except ImportError:
        pytest.skip("Dependencies for store '%s' not available!" % store)

    if store != "default":
        rt = graph.open(configuration=path, create=True)
        assert rt == VALID_STORE, "The underlying store is corrupt"

    assert (
        len(graph) == 0
    ), "There must be zero triples in the graph just after store (file) creation"

    # delete the graph for each test!
    graph.remove((None, None, None))

    yield graph

    graph.close()
    graph.destroy(configuration=path)


def addStuff(graph):
    graph.add((tarek, likes, pizza))
    graph.add((tarek, likes, cheese))
    graph.add((michel, likes, pizza))
    graph.add((michel, likes, cheese))
    graph.add((bob, likes, cheese))
    graph.add((bob, hates, pizza))
    graph.add((bob, hates, michel))  # gasp!


def removeStuff(graph):
    graph.remove((tarek, likes, pizza))
    graph.remove((tarek, likes, cheese))
    graph.remove((michel, likes, pizza))
    graph.remove((michel, likes, cheese))
    graph.remove((bob, likes, cheese))
    graph.remove((bob, hates, pizza))
    graph.remove((bob, hates, michel))  # gasp!


def test_add(get_graph):
    graph = get_graph
    addStuff(graph)


def test_remove(get_graph):
    graph = get_graph
    addStuff(graph)
    removeStuff(graph)


def test_triples(get_graph):
    graph = get_graph
    triples = graph.triples
    Any = None

    addStuff(graph)

    # unbound subjects
    assert len(list(triples((Any, likes, pizza)))) == 2
    assert len(list(triples((Any, hates, pizza)))) == 1
    assert len(list(triples((Any, likes, cheese)))) == 3
    assert len(list(triples((Any, hates, cheese)))) == 0

    # unbound objects
    assert len(list(triples((michel, likes, Any)))) == 2
    assert len(list(triples((tarek, likes, Any)))) == 2
    assert len(list(triples((bob, hates, Any)))) == 2
    assert len(list(triples((bob, likes, Any)))) == 1

    # unbound predicates
    assert len(list(triples((michel, Any, cheese)))) == 1
    assert len(list(triples((tarek, Any, cheese)))) == 1
    assert len(list(triples((bob, Any, pizza)))) == 1
    assert len(list(triples((bob, Any, michel)))) == 1

    # unbound subject, objects
    assert len(list(triples((Any, hates, Any)))) == 2
    assert len(list(triples((Any, likes, Any)))) == 5

    # unbound predicates, objects
    assert len(list(triples((michel, Any, Any)))) == 2
    assert len(list(triples((bob, Any, Any)))) == 3
    assert len(list(triples((tarek, Any, Any)))) == 2

    # unbound subjects, predicates
    assert len(list(triples((Any, Any, pizza)))) == 3
    assert len(list(triples((Any, Any, cheese)))) == 3
    assert len(list(triples((Any, Any, michel)))) == 1

    # all unbound
    assert len(list(triples((Any, Any, Any)))) == 7
    removeStuff(graph)
    assert len(list(triples((Any, Any, Any)))) == 0


def test_connected(get_graph):
    graph = get_graph

    addStuff(graph)
    assert graph.connected()

    jeroen = URIRef("jeroen")
    unconnected = URIRef("unconnected")

    graph.add((jeroen, likes, unconnected))

    assert graph.connected() is False


def test_sub(get_graph):

    g1 = get_graph

    g2 = Graph(store=g1.store)

    g1.add((tarek, likes, pizza))
    g1.add((bob, likes, cheese))

    g2.add((bob, likes, cheese))

    g3 = g1 - g2

    assert len(g3) == 1
    assert (tarek, likes, pizza) in g3
    assert (tarek, likes, cheese) not in g3

    assert (bob, likes, cheese) not in g3

    g1 -= g2

    assert len(g1) == 1
    assert (tarek, likes, pizza) in g1
    assert (tarek, likes, cheese) not in g1

    assert (bob, likes, cheese) not in g1


def test_graph_add(get_graph):
    graph = get_graph

    g1 = graph
    g2 = Graph(store=g1.store)

    g1.add((tarek, likes, pizza))

    g2.add((bob, likes, cheese))

    g3 = g1 + g2

    assert len(g3) == 2
    assert (tarek, likes, pizza) in g3
    assert (tarek, likes, cheese) not in g3

    assert (bob, likes, cheese) in g3

    g1 += g2

    assert len(g1) == 2
    assert (tarek, likes, pizza) in g1
    assert (tarek, likes, cheese) not in g1

    assert (bob, likes, cheese) in g1


def test_graph_intersection(get_graph):
    graph = get_graph

    g1 = graph
    g2 = Graph(store=g1.store)

    g1.add((tarek, likes, pizza))
    g1.add((michel, likes, cheese))

    g2.add((bob, likes, cheese))
    g2.add((michel, likes, cheese))

    g3 = g1 * g2

    assert len(g3) == 1
    assert (tarek, likes, pizza) not in g3
    assert (tarek, likes, cheese) not in g3

    assert (bob, likes, cheese) not in g3

    assert (michel, likes, cheese) in g3

    g1 *= g2

    assert len(g1) == 1

    assert (tarek, likes, pizza) not in g1
    assert (tarek, likes, cheese) not in g1

    assert (bob, likes, cheese) not in g1

    assert (michel, likes, cheese) in g1


def testGuessFormatForParse(get_graph):
    graph = get_graph

    # files
    with pytest.raises(ParserError):
        graph.parse(__file__)  # here we are trying to parse a Python file!!

    # .nt can be parsed by Turtle Parser
    graph.parse("test/nt/anons-01.nt")
    # RDF/XML
    graph.parse("test/rdf/datatypes/test001.rdf")  # XML
    # bad filename but set format
    graph.parse("test/rdf/datatypes/test001.borked", format="xml")

    # strings
    graph = Graph()

    with pytest.raises(ParserError):
        graph.parse(data="rubbish")

    # Turtle - default
    graph.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> ."
    )

    # Turtle - format given
    graph.parse(
        data="<http://example.com/a> <http://example.com/a> <http://example.com/a> .",
        format="turtle",
    )

    # RDF/XML - format given
    rdf = """<rdf:RDF
  xmlns:ns1="http://example.org/#"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:nodeID="ub63bL2C1">
    <ns1:p rdf:resource="http://example.org/q"/>
    <ns1:r rdf:resource="http://example.org/s"/>
  </rdf:Description>
  <rdf:Description rdf:nodeID="ub63bL5C1">
    <ns1:r>
      <rdf:Description rdf:nodeID="ub63bL6C11">
        <ns1:s rdf:resource="http://example.org/#t"/>
      </rdf:Description>
    </ns1:r>
    <ns1:p rdf:resource="http://example.org/q"/>
  </rdf:Description>
</rdf:RDF>
    """
    graph.parse(data=rdf, format="xml")

    # URI
    graph = get_graph

    # only getting HTML
    with pytest.raises(PluginException):
        graph.parse(location="https://www.google.com")

    try:
        graph.parse(location="http://www.w3.org/ns/adms.ttl")
        graph.parse(location="http://www.w3.org/ns/adms.rdf")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass

    try:
        # persistent Australian Government online RDF resource without a file-like ending
        graph.parse(location="https://linked.data.gov.au/def/agrif?_format=text/turtle")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass


def test_parse_file_uri(get_graph):
    graph = get_graph

    EG = Namespace("http://example.org/#")
    graph.parse(Path("./test/nt/simple-04.nt").absolute().as_uri())
    triple_set = GraphHelper.triple_set(graph)
    assert triple_set == {
        (EG["Subject"], EG["predicate"], EG["ObjectP"]),
        (EG["Subject"], EG["predicate"], EG["ObjectQ"]),
        (EG["Subject"], EG["predicate"], EG["ObjectR"]),
    }


def test_transitive(get_graph):
    graph = get_graph

    person = URIRef("ex:person")
    dad = URIRef("ex:dad")
    mom = URIRef("ex:mom")
    mom_of_dad = URIRef("ex:mom_o_dad")
    mom_of_mom = URIRef("ex:mom_o_mom")
    dad_of_dad = URIRef("ex:dad_o_dad")
    dad_of_mom = URIRef("ex:dad_o_mom")

    parent = URIRef("ex:parent")

    graph.add((person, parent, dad))
    graph.add((person, parent, mom))
    graph.add((dad, parent, mom_of_dad))
    graph.add((dad, parent, dad_of_dad))
    graph.add((mom, parent, mom_of_mom))
    graph.add((mom, parent, dad_of_mom))

    # transitive parents of person
    assert set(graph.transitive_objects(subject=person, predicate=parent)) == {
        person,
        dad,
        mom_of_dad,
        dad_of_dad,
        mom,
        mom_of_mom,
        dad_of_mom,
    }
    # transitive parents of dad
    assert set(graph.transitive_objects(dad, parent)) == {dad, mom_of_dad, dad_of_dad}
    # transitive parents of dad_of_dad
    assert set(graph.transitive_objects(dad_of_dad, parent)) == {dad_of_dad}

    # transitive children (inverse of parents) of mom_of_mom
    assert set(graph.transitive_subjects(predicate=parent, object=mom_of_mom)) == {
        mom_of_mom,
        mom,
        person,
    }

    # transitive children (inverse of parents) of mom
    assert set(graph.transitive_subjects(parent, mom)) == {mom, person}
    # transitive children (inverse of parents) of person
    assert set(graph.transitive_subjects(parent, person)) == {person}
