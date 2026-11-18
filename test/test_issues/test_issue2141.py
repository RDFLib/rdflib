from __future__ import annotations

import rdflib
from rdflib import Literal, URIRef, Variable
from rdflib.plugins.stores.memory import Memory


def test_insert_data_graph_var_init_bindings() -> None:
    store = Memory()
    graph = rdflib.Graph(identifier=URIRef("urn:example:graph"), store=store)
    dataset = rdflib.Dataset(store=store)
    dataset.add_graph(graph)

    s = URIRef("urn:example:subject")
    p = URIRef("urn:example:predicate")
    o = Literal("another value")

    dataset.update(
        """
        INSERT DATA {
            GRAPH ?g { <urn:example:subject> <urn:example:predicate> "another value" }
        }
        """,
        initBindings={"g": graph.identifier},
    )

    graph_ids = {ctx.identifier for ctx in dataset.graphs()}
    assert Variable("g") not in graph_ids
    assert URIRef("g") not in graph_ids
    assert graph_ids == {graph.identifier, dataset.default_graph.identifier}
    assert (s, p, o) in graph


def test_delete_data_graph_var_init_bindings() -> None:
    dataset = rdflib.Dataset()
    graph = dataset.graph(URIRef("urn:example:graph"))
    s = URIRef("urn:example:subject")
    p = URIRef("urn:example:predicate")
    o = Literal("value")
    graph.add((s, p, o))

    dataset.update(
        """
        DELETE DATA {
            GRAPH ?g { <urn:example:subject> <urn:example:predicate> "value" }
        }
        """,
        initBindings={"g": graph.identifier},
    )

    assert (s, p, o) not in graph


def test_delete_where_and_modify_graph_var_init_bindings() -> None:
    dataset = rdflib.Dataset()
    graph = dataset.graph(URIRef("urn:example:graph"))
    other = dataset.graph(URIRef("urn:example:other"))
    s = URIRef("urn:example:subject")
    p = URIRef("urn:example:predicate")
    o1 = Literal("old")
    o2 = Literal("new")
    graph.add((s, p, o1))
    other.add((s, p, o1))

    dataset.update(
        """
        DELETE { GRAPH ?g { ?s ?p "old" } }
        INSERT { GRAPH ?g { ?s ?p "new" } }
        WHERE { GRAPH ?g { ?s ?p "old" } }
        """,
        initBindings={"g": graph.identifier},
    )
    assert (s, p, o1) not in graph
    assert (s, p, o2) in graph
    assert (s, p, o1) in other

    dataset.update(
        """
        DELETE WHERE {
            GRAPH ?g { ?s ?p ?o }
        }
        """,
        initBindings={"g": graph.identifier},
    )
    assert len(graph) == 0
    assert (s, p, o1) in other
