import pytest

import rdflib
from rdflib import logger
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph
from rdflib.namespace import XSD, Namespace
from rdflib.term import BNode, Literal, Node, URIRef
from test.data import tarek, michel, likes, cheese, context1, context2


@pytest.fixture
def yield_dataset_for_sparql_clear():
    dataset = Dataset(default_union=True)

    # Namespace bindings for clarity of output
    dataset.bind("ex", URIRef("urn:example:"))
    dataset.bind("rdflib", URIRef("urn:x-rdflib:"))
    dataset.add((tarek, likes, URIRef("urn:example:camembert")))

    subgraph1 = dataset.graph(context1)
    subgraph1.add((tarek, likes, cheese))

    subgraph2 = dataset.graph(context2)
    subgraph2.add((michel, likes, cheese))

    assert len(list(dataset.contexts())) == 2
    assert len(list(dataset.graphs())) == 2

    yield dataset, subgraph1, subgraph2

    del dataset


def test_sparql_update_clear_default(yield_dataset_for_sparql_clear):
    dataset, subgraph1, subgraph2 = yield_dataset_for_sparql_clear

    assert len(dataset.default_graph) == 1
    assert len(subgraph1) == 1
    assert len(subgraph2) == 1

    # The DEFAULT keyword is used to remove all triples in the default graph of the Graph Store
    dataset.update("CLEAR DEFAULT")

    assert len(dataset.default_graph) == 0
    assert len(subgraph1) == 1
    assert len(subgraph2) == 1


def test_sparql_update_clear_graph(yield_dataset_for_sparql_clear):

    dataset, subgraph1, subgraph2 = yield_dataset_for_sparql_clear

    assert len(dataset.default_graph) == 1
    assert len(subgraph1) == 1
    assert len(subgraph2) == 1

    # The GRAPH keyword is used to remove all triples from a graph denoted by IRIref.
    dataset.update("CLEAR GRAPH ex:context-1")

    assert len(dataset.default_graph) == 1
    assert len(subgraph1) == 0
    assert len(subgraph2) == 1


def test_sparql_update_clear_named(yield_dataset_for_sparql_clear):
    dataset, subgraph1, subgraph2 = yield_dataset_for_sparql_clear

    assert len(subgraph1) == 1
    assert len(subgraph2) == 1

    # The NAMED keyword is used to remove all triples in all named graphs of the Graph Store
    dataset.update("CLEAR NAMED")

    assert len(dataset.default_graph) == 1
    assert len(subgraph1) == 0
    assert len(subgraph2) == 0


def test_sparql_update_clear_all(yield_dataset_for_sparql_clear):
    dataset, subgraph1, subgraph2 = yield_dataset_for_sparql_clear

    dataset, subgraph1, subgraph2 = yield_dataset_for_sparql_clear

    assert len(subgraph1) == 1
    assert len(subgraph2) == 1
    assert len(dataset.default_graph) == 1

    # The ALL keyword is used to remove all triples in all graphs of the Graph Store
    dataset.update("CLEAR ALL")

    assert len(subgraph1) == 0
    assert len(subgraph2) == 0
    assert len(dataset.default_graph) == 0


def test_dataset_sparql_update():

    ds = Dataset()

    # Namespace bindings for clarity of output
    ds.bind("ex", URIRef("urn:example:"))
    ds.bind("rdflib", URIRef("urn:x-rdflib:"))

    ds.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:camembert> . } "
    )

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 1

    ds.update(
        "INSERT DATA { GRAPH <urn:example:context1> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")

    assert len(list(r)) == 2

    ds.update(
        "INSERT DATA { GRAPH <urn:example:context2> { <urn:example:michel> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 3

    ds.update("CLEAR GRAPH <urn:example:context2>")

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 2

    ds.update(
        "INSERT DATA { GRAPH <urn:example:context2> { <urn:example:michel> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 3

    # The NAMED keyword is used to remove all triples in all named graphs of the Graph Store
    ds.update("CLEAR NAMED")

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 1

    ds.update(
        "INSERT DATA { GRAPH <urn:example:context1> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )
    ds.update(
        "INSERT DATA { GRAPH <urn:example:context2> { <urn:example:michel> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 3

    # The DEFAULT keyword is used to remove all triples in the default graph of the Graph Store
    ds.update("CLEAR DEFAULT")

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 2

    ds.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:camembert> . } "
    )
    ds.update(
        "INSERT DATA { GRAPH <urn:example:context1> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )
    ds.update(
        "INSERT DATA { GRAPH <urn:example:context2> { <urn:example:michel> <urn:example:likes> <urn:example:cheese> . } }"
    )
    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 3

    # The ALL keyword is used to remove all triples in all graphs of the Graph Store
    ds.update("CLEAR ALL")
    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")

    assert len(list(r)) == 0


@pytest.mark.xfail(
    reason="Incorrect/unexpected results from SPARQL query when default_union=True"
)
def test_dataset_sparql_update_default_union_match():

    ds = Dataset(default_union=True)

    # Namespace bindings for clarity of output
    ds.bind("ex", URIRef("urn:example:"))
    ds.bind("rdflib", URIRef("urn:x-rdflib:"))

    ds.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:camembert> . } "
    )

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 1

    ds.update(
        "INSERT DATA { GRAPH <urn:example:context1> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")

    lr = [row.asdict() for row in r]

    # tarek liking cheese incorrectly reported twice, once in
    # default graph (incorrect), once correctly in context
    assert lr[:2] in [
        # either
        [
            {
                'o': rdflib.term.URIRef('urn:example:camembert'),
                'p': rdflib.term.URIRef('urn:example:likes'),
                's': rdflib.term.URIRef('urn:example:tarek'),
            },
            {
                'o': rdflib.term.URIRef('urn:example:cheese'),
                'p': rdflib.term.URIRef('urn:example:likes'),
                's': rdflib.term.URIRef('urn:example:tarek'),
            },
        ],
        # or
        [
            {
                'o': rdflib.term.URIRef('urn:example:cheese'),
                'p': rdflib.term.URIRef('urn:example:likes'),
                's': rdflib.term.URIRef('urn:example:tarek'),
            },
            {
                'o': rdflib.term.URIRef('urn:example:camembert'),
                'p': rdflib.term.URIRef('urn:example:likes'),
                's': rdflib.term.URIRef('urn:example:tarek'),
            },
        ],
    ]

    assert lr[2] == {
        'g': rdflib.term.URIRef('urn:example:context1'),
        'o': rdflib.term.URIRef('urn:example:cheese'),
        'p': rdflib.term.URIRef('urn:example:likes'),
        's': rdflib.term.URIRef('urn:example:tarek'),
    }

    assert len(lr) == 2

    ds.update(
        "INSERT DATA { GRAPH <urn:example:context2> { <urn:example:michel> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 5

    ds.update("CLEAR GRAPH <urn:example:context2>")

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 3

    ds.update(
        "INSERT DATA { GRAPH <urn:example:context2> { <urn:example:michel> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 5

    # The NAMED keyword is used to remove all triples in all named graphs of the Graph Store
    ds.update("CLEAR NAMED")

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 1

    ds.update(
        "INSERT DATA { GRAPH <urn:example:context1> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )
    ds.update(
        "INSERT DATA { GRAPH <urn:example:context2> { <urn:example:michel> <urn:example:likes> <urn:example:cheese> . } }"
    )

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 5

    # The DEFAULT keyword is used to remove all triples in the default graph of the Graph Store
    ds.update("CLEAR DEFAULT")

    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 4

    ds.update(
        "INSERT DATA { <urn:example:tarek> <urn:example:likes> <urn:example:camembert> . } "
    )
    ds.update(
        "INSERT DATA { GRAPH <urn:example:context1> { <urn:example:tarek> <urn:example:likes> <urn:example:cheese> . } }"
    )
    ds.update(
        "INSERT DATA { GRAPH <urn:example:context2> { <urn:example:michel> <urn:example:likes> <urn:example:cheese> . } }"
    )
    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")
    assert len(list(r)) == 5

    # The ALL keyword is used to remove all triples in all graphs of the Graph Store
    ds.update("CLEAR ALL")
    r = ds.query("SELECT * { {?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } }}")

    assert len(list(r)) == 0
