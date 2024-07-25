from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Callable, Optional, Set, Tuple
from urllib.error import HTTPError, URLError

import pytest

from rdflib import Graph, URIRef
from rdflib.exceptions import ParserError
from rdflib.namespace import Namespace, NamespaceManager
from rdflib.plugin import PluginException
from rdflib.store import Store
from rdflib.term import BNode
from test.data import BOB, CHEESE, HATES, LIKES, MICHEL, PIZZA, TAREK, TEST_DATA_DIR
from test.utils import GraphHelper, get_unique_plugin_names
from test.utils.httpfileserver import HTTPFileServer, ProtoFileResource
from test.utils.outcome import ExceptionChecker, OutcomeChecker, OutcomePrimitive


def test_property_store() -> None:
    """
    The ``store`` property works correctly.
    """
    graph = Graph()
    assert isinstance(graph.store, Store)


def test_property_identifier_default() -> None:
    """
    The default identifier for a graph is a `rdflib.term.BNode`.
    """
    graph = Graph()
    assert isinstance(graph.identifier, BNode)


def test_property_identifier() -> None:
    """
    The ``identifier`` property works correctly.
    """
    id = URIRef("example:a")
    graph = Graph(identifier=id)
    assert id == graph.identifier


def test_property_namespace_manager() -> None:
    """
    The ``namespace_manager`` property works correctly.
    """
    graph = Graph()
    # check repeats as property is a signleton
    assert isinstance(graph.namespace_manager, NamespaceManager)
    assert isinstance(graph.namespace_manager, NamespaceManager)

    new_nsm = NamespaceManager(graph)
    new_nsm.reset()
    new_nsm.bind("test", URIRef("example:test:"))
    graph.namespace_manager = new_nsm
    assert isinstance(graph.namespace_manager, NamespaceManager)
    nss = list(graph.namespace_manager.namespaces())
    assert ("test", URIRef("example:test:")) in nss


def get_store_names() -> Set[Optional[str]]:
    names: Set[Optional[str]] = {*get_unique_plugin_names(Store)}
    names.difference_update(
        {
            "default",
            "Memory",
            "Auditable",
            "Concurrent",
            "SPARQLStore",
            "SPARQLUpdateStore",
            "SimpleMemory",
        }
    )
    names.add(None)

    logging.debug("names = %s", names)
    return names


GraphFactory = Callable[[], Graph]


@pytest.fixture(scope="function", params=get_store_names())
def make_graph(tmp_path: Path, request) -> GraphFactory:
    store_name: Optional[str] = request.param

    def make_graph() -> Graph:
        if store_name is None:
            graph = Graph()
        else:
            graph = Graph(store=store_name)

        use_path = tmp_path / f"{store_name}"
        use_path.mkdir(exist_ok=True, parents=True)
        logging.debug("use_path = %s", use_path)
        graph.open(f"{use_path}", create=True)
        return graph

    return make_graph


def populate_graph(graph: Graph):
    graph.add((TAREK, LIKES, PIZZA))
    graph.add((TAREK, LIKES, CHEESE))
    graph.add((MICHEL, LIKES, PIZZA))
    graph.add((MICHEL, LIKES, CHEESE))
    graph.add((BOB, LIKES, CHEESE))
    graph.add((BOB, HATES, PIZZA))
    graph.add((BOB, HATES, MICHEL))  # gasp!


def depopulate_graph(graph: Graph):
    graph.remove((TAREK, LIKES, PIZZA))
    graph.remove((TAREK, LIKES, CHEESE))
    graph.remove((MICHEL, LIKES, PIZZA))
    graph.remove((MICHEL, LIKES, CHEESE))
    graph.remove((BOB, LIKES, CHEESE))
    graph.remove((BOB, HATES, PIZZA))
    graph.remove((BOB, HATES, MICHEL))  # gasp!


def test_add(make_graph: GraphFactory):
    graph = make_graph()
    populate_graph(graph)


def test_remove(make_graph: GraphFactory):
    graph = make_graph()
    populate_graph(graph)
    depopulate_graph(graph)


def test_triples(make_graph: GraphFactory):
    graph = make_graph()
    triples = graph.triples
    Any = None  # noqa: N806

    populate_graph(graph)

    # unbound subjects
    assert len(list(triples((Any, LIKES, PIZZA)))) == 2
    assert len(list(triples((Any, HATES, PIZZA)))) == 1
    assert len(list(triples((Any, LIKES, CHEESE)))) == 3
    assert len(list(triples((Any, HATES, CHEESE)))) == 0

    # unbound objects
    assert len(list(triples((MICHEL, LIKES, Any)))) == 2
    assert len(list(triples((TAREK, LIKES, Any)))) == 2
    assert len(list(triples((BOB, HATES, Any)))) == 2
    assert len(list(triples((BOB, LIKES, Any)))) == 1

    # unbound predicates
    assert len(list(triples((MICHEL, Any, CHEESE)))) == 1
    assert len(list(triples((TAREK, Any, CHEESE)))) == 1
    assert len(list(triples((BOB, Any, PIZZA)))) == 1
    assert len(list(triples((BOB, Any, MICHEL)))) == 1

    # unbound subject, objects
    assert len(list(triples((Any, HATES, Any)))) == 2
    assert len(list(triples((Any, LIKES, Any)))) == 5

    # unbound predicates, objects
    assert len(list(triples((MICHEL, Any, Any)))) == 2
    assert len(list(triples((BOB, Any, Any)))) == 3
    assert len(list(triples((TAREK, Any, Any)))) == 2

    # unbound subjects, predicates
    assert len(list(triples((Any, Any, PIZZA)))) == 3
    assert len(list(triples((Any, Any, CHEESE)))) == 3
    assert len(list(triples((Any, Any, MICHEL)))) == 1

    # all unbound
    assert len(list(triples((Any, Any, Any)))) == 7
    depopulate_graph(graph)
    assert len(list(triples((Any, Any, Any)))) == 0


def test_connected(make_graph: GraphFactory):
    graph = make_graph()
    populate_graph(graph)
    assert graph.connected() is True

    jeroen = URIRef("jeroen")
    unconnected = URIRef("unconnected")

    graph.add((jeroen, LIKES, unconnected))

    assert graph.connected() is False


def test_graph_sub(make_graph: GraphFactory):
    g1 = make_graph()
    g2 = make_graph()

    g1.add((TAREK, LIKES, PIZZA))
    g1.add((BOB, LIKES, CHEESE))

    g2.add((BOB, LIKES, CHEESE))

    g3 = g1 - g2

    assert len(g3) == 1
    assert (TAREK, LIKES, PIZZA) in g3
    assert (TAREK, LIKES, CHEESE) not in g3

    assert (BOB, LIKES, CHEESE) not in g3

    g1 -= g2

    assert len(g1) == 1
    assert (TAREK, LIKES, PIZZA) in g1
    assert (TAREK, LIKES, CHEESE) not in g1

    assert (BOB, LIKES, CHEESE) not in g1


def test_graph_add(make_graph: GraphFactory):
    g1 = make_graph()
    g2 = make_graph()

    g1.add((TAREK, LIKES, PIZZA))
    g2.add((BOB, LIKES, CHEESE))

    g3 = g1 + g2

    assert len(g3) == 2
    assert (TAREK, LIKES, PIZZA) in g3
    assert (TAREK, LIKES, CHEESE) not in g3

    assert (BOB, LIKES, CHEESE) in g3

    g1 += g2

    assert len(g1) == 2
    assert (TAREK, LIKES, PIZZA) in g1
    assert (TAREK, LIKES, CHEESE) not in g1

    assert (BOB, LIKES, CHEESE) in g1


def test_graph_intersection(make_graph: GraphFactory):
    g1 = make_graph()
    g2 = make_graph()

    g1.add((TAREK, LIKES, PIZZA))
    g1.add((MICHEL, LIKES, CHEESE))

    g2.add((BOB, LIKES, CHEESE))
    g2.add((MICHEL, LIKES, CHEESE))

    g3 = g1 * g2

    assert len(g3) == 1
    assert (TAREK, LIKES, PIZZA) not in g3
    assert (TAREK, LIKES, CHEESE) not in g3

    assert (BOB, LIKES, CHEESE) not in g3

    assert (MICHEL, LIKES, CHEESE) in g3

    g1 *= g2

    assert len(g1) == 1

    assert (TAREK, LIKES, PIZZA) not in g1
    assert (TAREK, LIKES, CHEESE) not in g1

    assert (BOB, LIKES, CHEESE) not in g1

    assert (MICHEL, LIKES, CHEESE) in g1


def test_guess_format_for_parse(
    make_graph: GraphFactory, http_file_server: HTTPFileServer
):
    graph = make_graph()

    # files
    with pytest.raises(ParserError):
        graph.parse(__file__)  # here we are trying to parse a Python file!!

    # .nt can be parsed by Turtle Parser
    graph.parse(os.path.join(TEST_DATA_DIR, "suites", "nt_misc", "anons-01.nt"))
    # RDF/XML
    graph.parse(
        os.path.join(
            TEST_DATA_DIR, "suites", "w3c", "rdf-xml", "datatypes", "test001.rdf"
        )
    )  # XML
    # bad filename but set format
    graph.parse(
        os.path.join(TEST_DATA_DIR, "w3c-rdfxml-test001.borked"),
        format="xml",
    )

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
    file_info = http_file_server.add_file_with_caching(
        ProtoFileResource(
            (("Content-Type", "text/html; charset=UTF-8"),),
            TEST_DATA_DIR / "html5lib_tests1.html",
        ),
    )

    # only getting HTML
    with pytest.raises(PluginException):
        graph.parse(location=file_info.request_url)
    try:
        # persistent Australian Government online RDF resource without a file-like ending
        graph.parse(location="https://linked.data.gov.au/def/agrif?_format=text/turtle")
    except (URLError, HTTPError):
        # this endpoint is currently not available, ignore this test.
        pass


@pytest.mark.parametrize(
    ("file", "content_type", "expected_result"),
    (
        (TEST_DATA_DIR / "defined_namespaces/adms.rdf", "application/rdf+xml", 132),
        (TEST_DATA_DIR / "defined_namespaces/adms.ttl", "text/turtle", 132),
        (TEST_DATA_DIR / "defined_namespaces/adms.ttl", None, 132),
        (
            TEST_DATA_DIR / "defined_namespaces/adms.rdf",
            None,
            ExceptionChecker(
                ParserError,
                r"Could not guess RDF format .* from file extension so tried Turtle",
            ),
        ),
    ),
)
def test_guess_format_for_parse_http(
    make_graph: GraphFactory,
    http_file_server: HTTPFileServer,
    file: Path,
    content_type: Optional[str],
    expected_result: OutcomePrimitive[int],
) -> None:
    graph = make_graph()
    headers: Tuple[Tuple[str, str], ...] = tuple()
    if content_type is not None:
        headers = (("Content-Type", content_type),)

    file_info = http_file_server.add_file_with_caching(
        ProtoFileResource(headers, file),
        suffix=f"/{file.name}",
    )
    checker = OutcomeChecker.from_primitive(expected_result)
    assert 0 == len(graph)
    with checker.context():
        graph.parse(location=file_info.request_url)
        checker.check(len(graph))


@pytest.mark.webtest
def test_guess_format_for_parse_http_text_plain():
    # Any raw url of a file from GitHub will return the content-type with text/plain.
    url = "https://raw.githubusercontent.com/AGLDWG/vocpub-profile/master/validators/validator.ttl"
    graph = Graph().parse(url)
    assert len(graph) > 0

    # A url that returns content-type text/html.
    url = "https://github.com/RDFLib/rdflib/issues/2734"
    with pytest.raises(PluginException):
        graph = Graph().parse(url)


def test_parse_file_uri(make_graph: GraphFactory):
    EG = Namespace("http://example.org/#")  # noqa: N806
    g = make_graph()
    g.parse(
        Path(os.path.join(TEST_DATA_DIR, "suites", "nt_misc", "simple-04.nt"))
        .absolute()
        .as_uri()
    )
    triple_set = GraphHelper.triple_set(g)
    assert triple_set == {
        (EG["Subject"], EG["predicate"], EG["ObjectP"]),
        (EG["Subject"], EG["predicate"], EG["ObjectQ"]),
        (EG["Subject"], EG["predicate"], EG["ObjectR"]),
    }


def test_transitive(make_graph: GraphFactory):
    person = URIRef("ex:person")
    dad = URIRef("ex:dad")
    mom = URIRef("ex:mom")
    mom_of_dad = URIRef("ex:mom_o_dad")
    mom_of_mom = URIRef("ex:mom_o_mom")
    dad_of_dad = URIRef("ex:dad_o_dad")
    dad_of_mom = URIRef("ex:dad_o_mom")

    parent = URIRef("ex:parent")

    g = make_graph()
    g.add((person, parent, dad))
    g.add((person, parent, mom))
    g.add((dad, parent, mom_of_dad))
    g.add((dad, parent, dad_of_dad))
    g.add((mom, parent, mom_of_mom))
    g.add((mom, parent, dad_of_mom))

    # transitive parents of person
    assert set(g.transitive_objects(subject=person, predicate=parent)) == {
        person,
        dad,
        mom_of_dad,
        dad_of_dad,
        mom,
        mom_of_mom,
        dad_of_mom,
    }
    # transitive parents of dad
    assert set(g.transitive_objects(dad, parent)) == {dad, mom_of_dad, dad_of_dad}
    # transitive parents of dad_of_dad
    assert set(g.transitive_objects(dad_of_dad, parent)) == {dad_of_dad}

    # transitive children (inverse of parents) of mom_of_mom
    assert set(g.transitive_subjects(predicate=parent, object=mom_of_mom)) == {
        mom_of_mom,
        mom,
        person,
    }
    # transitive children (inverse of parents) of mom
    assert set(g.transitive_subjects(parent, mom)) == {mom, person}
    # transitive children (inverse of parents) of person
    assert set(g.transitive_subjects(parent, person)) == {person}
