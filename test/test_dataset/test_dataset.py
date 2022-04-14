# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
from test.data import context0, context1, likes, pizza, tarek, michel, bob, CONSISTENT_DATA_DIR
from test.pluginstores import HOST, root, get_plugin_stores, set_store_and_path, open_store, cleanup, dburis

import pytest

from rdflib import FOAF, XSD, BNode, Literal, URIRef, plugin
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

# Will also run SPARQLUpdateStore tests against local SPARQL1.1 endpoint if
# available. This assumes SPARQL1.1 query/update endpoints running locally at
# http://localhost:3030/db/
#
# Testing SPARQLUpdateStore Dataset behavior needs a different endpoint behavior
# than our Dataset tests in test_sparqlupdatestore.py!
#
# For the tests here to run, you can for example start fuseki with:
# ./fuseki-server --mem --update /db

# THIS WILL DELETE ALL DATA IN THE /db dataset


dgb = URIRef("http://rdflib/net/")

timblcardn3 = open(os.path.join(CONSISTENT_DATA_DIR, "timbl-card.n3")).read()

timblcardnquads = open(os.path.join(CONSISTENT_DATA_DIR, "timbl-card.nquads")).read()

no_of_statements_in_card = 86
no_of_unique_subjects = 20
no_of_unique_predicates = 58
no_of_unique_objects = 62


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_dataset(request):
    storename = request.param

    store, path = set_store_and_path(storename)

    dataset = Dataset(store=store, identifier=URIRef("urn:example:testgraph"))

    ds = open_store(dataset, storename, path)

    yield store, dataset

    cleanup(dataset, storename, path)


def test_graph_aware(get_dataset):

    store, dataset = get_dataset

    if not dataset.store.graph_aware:
        return

    # There are no triples in any context, so dataset length == 0
    assert len(dataset) == 0

    # The default graph is not treated as a context
    assert len(list(dataset.contexts())) == 0
    assert str(list(dataset.contexts())) == "[]"
    # But it does exist
    assert dataset.default_graph is not None
    assert type(dataset.default_graph) is Graph
    assert len(dataset.default_graph) == 0

    subgraph1 = dataset.graph(context1)

    # Some SPARQL endpoint backends (e.g. TDB) do not consider
    # empty named graphs
    if store == "SPARQLUpdateStore":
        assert set(dataset.contexts()) == set()
        assert set(dataset.graphs()) == set()
    else:
        assert set(dataset.contexts()) == set([context1])
        assert set(dataset.graphs()) == set([subgraph1])

    # added graph is empty
    assert len(subgraph1) == 0

    subgraph1.add((tarek, likes, pizza))

    # added graph still exists
    assert set(dataset.contexts()) == set([context1])
    assert set(dataset.graphs()) == set([subgraph1])

    # added graph contains one triple
    assert len(subgraph1) == 1

    subgraph1.remove((tarek, likes, pizza))

    # added graph is empty
    assert len(subgraph1) == 0

    # Some SPARQL endpoint backends (e.g. TDB) do not consider
    # empty named graphs
    if "SPARQLUpdateStore" == store:
        assert set(dataset.contexts()) == set()
        assert set(dataset.graphs()) == set()
    else:
        assert set(dataset.contexts()) == set([context1])
        assert set(dataset.graphs()) == set([subgraph1])

    dataset.remove_graph(context1)

    # graph is gone
    assert list(dataset.graphs()) == []


def test_default_graph(get_dataset):
    # Something the default graph is read-only (e.g. TDB in union mode)

    store, dataset = get_dataset

    if store == "SPARQLUpdateStore":
        print(
            "Please make sure updating the default graph "
            "is supported by your SPARQL endpoint"
        )

    dataset.add((tarek, likes, pizza))
    assert len(dataset) == 1
    # only default exists
    assert list(dataset.contexts()) == []

    # removing default graph removes triples but not actual graph
    dataset.remove_graph(DATASET_DEFAULT_GRAPH_ID)

    if store == "SPARQLUpdateStore":
        assert len(dataset) == 1
    else:
        assert len(dataset) == 0

    # default still exists
    assert set(dataset.contexts()) == set()


def test_not_union(get_dataset):

    store, dataset = get_dataset
    # Union depends on the SPARQL endpoint configuration
    if store == "SPARQLUpdateStore":
        print(
            "Please make sure your SPARQL endpoint has not configured "
            "its default graph as the union of the named graphs"
        )

    subgraph1 = dataset.graph(context1)
    subgraph1.add((tarek, likes, pizza))

    assert list(dataset.objects(tarek, None)) == []
    assert list(subgraph1.objects(tarek, None)) == [pizza]


def test_iter(get_dataset):

    store, d = get_dataset
    """PR 1382: adds __iter__ to Dataset"""
    uri_a = URIRef("https://example.com/a")
    uri_b = URIRef("https://example.com/b")
    uri_c = URIRef("https://example.com/c")
    uri_d = URIRef("https://example.com/d")

    d.graph(URIRef("https://example.com/subgraph1"))
    d.add((uri_a, uri_b, uri_c, URIRef("https://example.com/subgraph1")))

    d.add(
        (uri_a, uri_b, uri_c, URIRef("https://example.com/subgraph1"))
    )  # pointless addition: duplicates above

    d.graph(URIRef("https://example.com/g2"))
    d.add((uri_a, uri_b, uri_c, URIRef("https://example.com/g2")))
    d.add((uri_a, uri_b, uri_d, URIRef("https://example.com/subgraph1")))

    # traditional iterator
    i_trad = 0
    for t in d.quads((None, None, None)):
        i_trad += 1

    # new Dataset.__iter__ iterator
    i_new = 0
    for t in d:
        i_new += 1

    assert i_new == i_trad  # both should be 3


def test_dataset_properties() -> None:

    # DEFAULT UNION = False (default)
    ds = Dataset()

    assert ds.identifier == URIRef("urn:x-rdflib:default")

    assert ds.default_union is False

    assert ds.default_graph.identifier == ds.identifier

    assert isinstance(ds.default_graph, Graph)

    assert len(ds.default_graph) == 0

    assert (
        str(ds)
        == "[a rdflib:Dataset;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']]"
    )


def test_identified_dataset_base_properties() -> None:

    # WITH IDENTIFIER
    ds = Dataset(identifier=context0)

    assert ds.identifier == context0

    assert ds.default_graph.identifier == URIRef("urn:x-rdflib:default")

    assert ds.default_union is False


def test_identified_dataset_properties() -> None:

    # WITH BNode AS IDENTIFIER
    bn = BNode()

    ds = Dataset(identifier=bn)

    assert ds.identifier == bn
    assert ds.default_graph.identifier == URIRef("urn:x-rdflib:default")

    # WITH Literal AS IDENTIFIER
    lit = Literal("example", datatype=XSD.string)
    ds = Dataset(identifier=lit)

    assert ds.identifier == lit
    assert ds.default_graph.identifier == URIRef("urn:x-rdflib:default")

    # WITH None AS IDENTIFIER
    ds = Dataset(identifier=None)

    assert ds.identifier == URIRef("urn:x-rdflib:default")
    assert ds.default_graph.identifier == URIRef("urn:x-rdflib:default")

    # ERROR WITH Graph AS IDENTIFIER
    with pytest.raises(ValueError):
        ds = Dataset(identifier=Graph())


def test_dataset_default_graph_base() -> None:

    # WITH DEFAULT GRAPH BASE
    # TODO APPARENTLY INEFFECTIVE
    ds = Dataset(store="Memory", default_graph_base=dgb)

    assert ds.identifier == DATASET_DEFAULT_GRAPH_ID

    assert ds.default_graph.identifier == DATASET_DEFAULT_GRAPH_ID

    assert ds.default_union is False

    ds.add((tarek, likes, pizza))

    ds.add((tarek, likes, URIRef("images/timbl-image-by-Coz-cropped.jpg")))

    with pytest.raises(AssertionError):
        assert (
            "http://rdflib/net/images/timbl-image-by-Coz-cropped.jpg"
            in ds.serialize(format='n3')
        )


def test_dataset_default_union_properties() -> None:

    # DEFAULT UNION = True
    ds = Dataset(store="Memory", default_union=True)

    assert ds.identifier == URIRef("urn:x-rdflib:default")

    assert ds.default_union is True

    assert ds.default_graph.identifier == ds.identifier

    assert (
        str(ds)
        == "[a rdflib:Dataset;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']]"
    )


def test_identified_dataset_default_union_properties() -> None:

    # WITH IDENTIFIER AND DEFAULT UNION = True
    ds = Dataset(store="Memory", identifier=context0, default_union=True)

    assert ds.identifier == context0

    assert ds.default_graph.identifier == DATASET_DEFAULT_GRAPH_ID

    assert (
        str(ds)
        == "[a rdflib:Dataset;rdflib:storage [a rdflib:Store;rdfs:label 'Memory']]"
    )


def test_dataset_graph_method() -> None:
    ds = Dataset()

    # CREATE GRAPH
    graph = ds.graph()

    assert type(graph) is Graph

    assert graph.identifier.n3().startswith(
        "<http://rdlib.net/.well-known/genid/rdflib/N"
    )


def test_dataset_bypass_graph_method() -> None:
    ds = Dataset()

    # CREATE GRAPH
    graph = Graph(identifier=context0)  # Not using the same store!
    graph.add((tarek, likes, pizza))

    ds.store.add_graph(graph)  # Silently accepts

    with pytest.raises(Exception):
        assert len(list(ds.contexts())) == 1

    with pytest.raises(Exception):
        assert list(ds.contexts()) == [context0]


def test_dataset_graph_method_named_graph() -> None:
    ds = Dataset()

    # CREATE NAMED GRAPH
    graph = ds.graph(identifier=context0)

    assert type(graph) is Graph

    assert graph.identifier.n3() == "<urn:example:context-0>"


def test_dataset_default_graph() -> None:
    ds = Dataset()

    # Add a triple to DEFAULT GRAPH
    ds.add((tarek, likes, pizza))

    assert (tarek, likes, pizza) in ds

    assert len(ds) == 1

    # Add a second triple to DEFAULT GRAPH
    ds.add((michel, likes, pizza))

    assert len(ds) == 2

    # Remove the second triple from DEFAULT GRAPH
    ds.remove((michel, likes, pizza))

    assert len(ds) == 1

    assert (
        str(ds.serialize(format="ttl"))
        == "@prefix ns1: <urn:example:> .\n\nns1:tarek ns1:likes ns1:pizza .\n\n"
    )


def test_dataset_default_graph_with_bound_namespace() -> None:
    ds = Dataset()

    ds.bind("ex", URIRef("urn:example:"))

    ds.add((tarek, likes, pizza))

    assert (
        str(ds.serialize(format="ttl"))
        == "@prefix ex: <urn:example:> .\n\nex:tarek ex:likes ex:pizza .\n\n"
    )


def test_idempotency_of_dataset_graph_method() -> None:
    ds = Dataset()

    # Create NAMED GRAPH in Dataset
    newgraph = ds.graph(identifier=context1)

    # Add a triple to NAMED GRAPH
    newgraph.add((tarek, likes, pizza))

    # Retrieve NAMED GRAPH from Dataset
    samegraph = ds.graph(identifier=context1)

    # Verify it's the same NAMED GRAPH
    assert newgraph == samegraph

    assert len(list(ds.graphs())) == 1

    df = ds.default_graph

    ndf = ds.graph(DATASET_DEFAULT_GRAPH_ID)

    assert ds.graph(ndf.identifier) == ds.graph(df.identifier)

    assert len(list(ds.graphs())) == 1


def test_dataset_graphs_method() -> None:
    ds = Dataset()

    assert len(list(ds.graphs())) == 0

    # Create NAMED GRAPH in Dataset
    subgraph1 = ds.graph(identifier=context0)

    assert len(list(ds.graphs())) == 1
    assert sorted(list(ds.contexts()))[0] == context0

    # ADD TRIPLE TO NAMED GRAPH
    subgraph1.add((tarek, likes, pizza))

    # CREATE SECOND NAMED GRAPH
    subgraph2 = ds.graph(identifier=context1)

    # ADD TRIPLE TO SECOND NAMED GRAPH
    subgraph2.add((bob, likes, michel))  # 2 people like, 2 people like pizza

    subgraph2.add((bob, likes, pizza))  # 3 people like, 2 people like pizza

    assert len(ds) == 0

    assert len(subgraph1) == 1
    assert (tarek, likes, pizza) in subgraph1

    assert len(subgraph2) == 2
    assert (bob, likes, pizza) in subgraph2

    assert len(list((ds.graphs((bob, likes, pizza))))) == 1

    assert len(list((ds.graphs((None, None, None))))) == 2

    assert len(list((ds.graphs((tarek, None, None))))) == 1

    assert len(list((ds.store.contexts((tarek, None, None))))) == 1

    assert len(list((ds.graphs((None, likes, None))))) == 2

    assert len(list((ds.graphs((None, None, pizza))))) == 2

    assert len(list((ds.graphs((None, likes, pizza))))) == 2

    # FIXME: Same behaviour as RDFLib master
    with pytest.raises(AssertionError):  # 0 != 2
        assert len(list((ds.subjects((None, likes, pizza))))) == 1


def test_triples_with_path():
    ds = Dataset()
    ds.add((tarek, likes, pizza))
    ds.add((tarek, FOAF.knows, michel))

    assert len(list(ds.triples((tarek, FOAF.knows / FOAF.name, None)))) == 0


def test_variant_1():
    simple_triple_ttl = """@prefix test: <http://example.org/>.
@prefix object: <http://example.org/object>.
test:subject test:predicate object:.
"""
    ds = Dataset()
    ds.parse(data=simple_triple_ttl, format="turtle")

def test_variant_2():
    ds = Dataset()
    variant_file = os.path.join(CONSISTENT_DATA_DIR, "..", "variants", "simple_triple-variant-prefix_dot.ttl")
    with open(variant_file, 'r') as fp:
        ds.parse(file=fp, format="turtle")
