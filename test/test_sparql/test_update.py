import itertools
import logging
from typing import Callable

import pytest

from rdflib import Literal, Namespace, URIRef, Variable
from rdflib.compare import isomorphic
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, ConjunctiveGraph, Dataset, Graph
from test.data import TEST_DATA_DIR
from test.utils import GraphHelper
from test.utils.graph import GraphSource
from test.utils.namespace import EGDO


@pytest.mark.parametrize(
    ("graph_factory", "source"),
    itertools.product(
        [Graph, ConjunctiveGraph, Dataset],
        GraphSource.from_paths(
            TEST_DATA_DIR / "variants" / "simple_triple.ttl",
            TEST_DATA_DIR / "variants" / "relative_triple.ttl",
        ),
    ),
    ids=GraphSource.idfn,
)
def test_load_into_default(
    graph_factory: Callable[[], Graph], source: GraphSource
) -> None:
    """
    Evaluation of `LOAD <source>` into default graph works correctly.
    """

    expected_graph = graph_factory()
    source.load(graph=expected_graph)

    actual_graph = graph_factory()
    actual_graph.update(f"LOAD <{source.public_id_or_path_uri()}>")

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        debug_format = (
            "nquads" if isinstance(expected_graph, ConjunctiveGraph) else "ntriples"
        )
        logging.debug(
            "expected_graph = \n%s", expected_graph.serialize(format=debug_format)
        )
        logging.debug(
            "actual_graph = \n%s", actual_graph.serialize(format=debug_format)
        )

    if isinstance(expected_graph, ConjunctiveGraph):
        assert isinstance(actual_graph, ConjunctiveGraph)
        GraphHelper.assert_collection_graphs_equal(expected_graph, actual_graph)
    else:
        GraphHelper.assert_triple_sets_equals(expected_graph, actual_graph)


@pytest.mark.parametrize(
    ("graph_factory", "source"),
    itertools.product(
        [ConjunctiveGraph, Dataset],
        GraphSource.from_paths(
            TEST_DATA_DIR / "variants" / "simple_triple.ttl",
            TEST_DATA_DIR / "variants" / "relative_triple.ttl",
        ),
    ),
    ids=GraphSource.idfn,
)
def test_load_into_named(
    graph_factory: Callable[[], ConjunctiveGraph], source: GraphSource
) -> None:
    """
    Evaluation of `LOAD <source> INTO GRAPH <name>` works correctly.
    """

    expected_graph = graph_factory()
    source.load(graph=expected_graph.get_context(EGDO.graph))

    actual_graph = graph_factory()

    actual_graph.update(
        f"LOAD <{source.public_id_or_path_uri()}> INTO GRAPH <{EGDO.graph}>"
    )

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        debug_format = "nquads"
        logging.debug(
            "expected_graph = \n%s", expected_graph.serialize(format=debug_format)
        )
        logging.debug(
            "actual_graph = \n%s", actual_graph.serialize(format=debug_format)
        )

    GraphHelper.assert_collection_graphs_equal(expected_graph, actual_graph)


def test_reevaluation_between_updates_modify() -> None:
    """
    during an update the values should be bound once and then deleted and inserted
    once per valid binding.

    See https://github.com/RDFLib/rdflib/issues/3246
    """
    ex = Namespace("http://example.com/")

    g = Graph()
    g.bind("ex", ex)

    g.add((ex.foo, ex.value, Literal(1)))
    g.add((ex.foo, ex.value, Literal(11)))

    g.add((ex.bar, ex.value, Literal(3)))

    g.update(
        """
    DELETE {
        ex:bar ex:value ?oldValue .
    }
    INSERT {
        ex:bar ex:value ?newValue .
    }
    WHERE {
        ex:foo ex:value ?instValue .
        OPTIONAL { ex:bar ex:value ?oldValue . }
        BIND(COALESCE(?oldValue, 0) + ?instValue AS ?newValue)
    }
    """
    )

    result = g.query("SELECT ?x WHERE { ex:bar ex:value ?x }")
    values = {b.get(Variable("x")) for b in result}  # type: ignore
    assert values == {Literal(4), Literal(14)}


def test_reevaluation_between_updates_insert() -> None:
    """
    during an update the values should be bound once and then deleted and inserted
    once per valid binding.

    See https://github.com/RDFLib/rdflib/issues/3246
    """
    ex = Namespace("http://example.com/")

    g = Graph()
    g.bind("ex", ex)

    g.add((ex.foo, ex.value, Literal(1)))
    g.add((ex.foo, ex.value, Literal(11)))

    g.add((ex.bar, ex.value, Literal(3)))

    g.update(
        """
    INSERT {
        ex:bar ex:value ?newValue .
    }
    WHERE {
        ex:foo ex:value ?instValue .
        OPTIONAL { ex:bar ex:value ?oldValue . }
        BIND(COALESCE(?oldValue, 0) + ?instValue AS ?newValue)
    }
    """
    )

    result = g.query("SELECT ?x WHERE { ex:bar ex:value ?x }")
    values = {b.get(Variable("x")) for b in result}  # type: ignore
    assert values == {Literal(3), Literal(4), Literal(14)}


def test_inserts_in_named_graph():
    trig_data = """
    @prefix ex: <http://example.org/> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

    # Named graph 1
    ex:graph1 {
      ex:person1 ex:name "Alice" ;
                 ex:age 30 .
    }

    # Named graph 2
    ex:graph2 {
      ex:person1 ex:worksFor ex:company1 .
      ex:company1 ex:industry "Technology" .
    }
    """
    ds = Dataset().parse(data=trig_data, format="trig")
    ds.update(
        """
    INSERT {
        GRAPH <urn:graph> {
            ?s ?p ?o
        }

        ?s ?p ?o
    }
    WHERE {
        GRAPH ?g {
            ?s ?p ?o
        }
    }
    """
    )

    expected_trig = """
    @prefix ex: <http://example.org/> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    {
        ex:person1 ex:age 30 ;
            ex:name "Alice" ;
            ex:worksFor ex:company1 .

        ex:company1 ex:industry "Technology" .
    }

    <urn:graph> {
        ex:person1 ex:age 30 ;
            ex:name "Alice" ;
            ex:worksFor ex:company1 .

        ex:company1 ex:industry "Technology" .
    }

    ex:graph1 {
        ex:person1 ex:age 30 ;
            ex:name "Alice" .
    }

    ex:graph2 {
        ex:person1 ex:worksFor ex:company1 .

        ex:company1 ex:industry "Technology" .
    }
    """
    expected_ds = Dataset().parse(data=expected_trig, format="trig")

    # There should be exactly 4 graphs, including the default graph.
    # SPARQL Update inserts into the default graph should go into the default graph,
    # not to a new graph with a blank node label.
    # See https://github.com/RDFLib/rdflib/issues/3080
    expected_graph_names = [
        DATASET_DEFAULT_GRAPH_ID,
        URIRef("urn:graph"),
        URIRef("http://example.org/graph1"),
        URIRef("http://example.org/graph2"),
    ]
    assert set(expected_graph_names) == set(graph.identifier for graph in ds.graphs())

    for graph in ds.graphs():
        expected_graph = expected_ds.graph(graph.identifier)
        assert isomorphic(graph, expected_graph)
