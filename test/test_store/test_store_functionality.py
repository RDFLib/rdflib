# -*- coding: utf-8 -*-
import re
import shutil
import tempfile
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

from rdflib import RDF, RDFS, BNode, Dataset, Literal, URIRef, Variable, logger, plugin
from rdflib.graph import Graph, QuotedGraph
from rdflib.store import VALID_STORE
from test.pluginstores import (
    HOST,
    root,
    get_plugin_stores,
    set_store_and_path,
    open_store,
    cleanup,
    dburis,
)

implies = URIRef("http://www.w3.org/2000/10/swap/log#implies")

testN3 = """\
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
{:a :b :c;a :foo} => {:a :d :c,?y} .
_:foo a rdfs:Class .
:a :d :c .
"""

graphuri = URIRef("urn:example:graph")
othergraphuri = URIRef("urn:example:othergraph")


@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_dataset(request):
    storename = request.param

    store, path = set_store_and_path(storename)

    d = Dataset(store=store, identifier=URIRef("urn:example:testgraph"))

    dataset = open_store(d, storename, path)

    yield store, path, dataset

    cleanup(dataset, storename, path)


def test_simple_graph(get_dataset):
    store, path, ds = get_dataset
    graph = ds.graph(graphuri)
    graph.add((tarek, likes, pizza))
    graph.add((bob, likes, pizza))
    graph.add((bob, likes, cheese))

    g2 = ds.graph(othergraphuri)
    g2.add((michel, likes, pizza))

    assert len(graph) == 3, "graph contains 3 triples"
    assert len(g2) == 1, "other graph contains 1 triple"

    r = graph.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 2, "two people like pizza"

    r = graph.triples((None, likes, pizza))
    assert len(list(r)) == 2, "two people like pizza"

    # Test initBindings
    r = graph.query(
        "SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }",
        initBindings={"s": tarek},
    )
    assert len(list(r)) == 1, "i was asking only about tarek"

    r = graph.triples((tarek, likes, pizza))
    assert len(list(r)) == 1, "i was asking only about tarek"

    r = graph.triples((tarek, likes, cheese))
    assert len(list(r)) == 0, "tarek doesn't like cheese"

    g2.add((tarek, likes, pizza))
    graph.remove((tarek, likes, pizza))
    r = graph.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")


def test_conjunctive_default(get_dataset):
    store, path, ds = get_dataset
    ds.default_union = True

    subgraph1 = ds.graph(context1)

    subgraph1.add((tarek, likes, pizza))

    subgraph2 = ds.graph(context2)
    subgraph2.add((bob, likes, pizza))

    subgraph1.add((tarek, hates, cheese))

    assert len(subgraph1) == 2, "graph contains 2 triples"

    # the following are actually bad tests as they depend on your endpoint,
    # as pointed out in the sparqlstore.py code:
    #
    # # For ConjunctiveGraphs, reading is done from the "default graph" Exactly
    # # what this means depends on your endpoint, because SPARQL does not offer a
    # # simple way to query the union of all graphs as it would be expected for a
    # # ConjuntiveGraph.
    # #
    # # Fuseki/TDB has a flag for specifying that the default graph
    # # is the union of all graphs (tdb:unionDefaultGraph in the Fuseki config).
    assert (
        len(ds) == 3
    ), f"default union graph should contain three triples but contains {list(ds)}:\n"

    r = ds.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")

    assert len(list(r)) == 2, f"two people should like pizza, not {len(list(r))}"

    r = ds.query(
        "SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }",
        initBindings={"s": tarek},
    )
    assert len(list(r)) == 1, "i was asking only about tarek"

    r = ds.triples((tarek, likes, pizza))
    assert len(list(r)) == 1, "i was asking only about tarek"

    r = ds.triples((tarek, likes, cheese))
    assert len(list(r)) == 0, "tarek doesn't like cheese"

    subgraph2.remove((bob, likes, pizza))

    r = ds.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "only tarek likes pizza"


def test_update(get_dataset):
    store, path, ds = get_dataset
    ds.default_union = True
    ds.update(
        "INSERT DATA { GRAPH <urn:example:graph> { <urn:example:michel> <urn:example:likes> <urn:example:pizza> . } }"
    )

    graph = ds.graph(graphuri)
    assert len(graph) == 1, "graph contains 1 triple"


def test_update_with_initns(get_dataset):
    store, path, ds = get_dataset
    ds.default_union = True
    ds.update(
        "INSERT DATA { GRAPH ns:graph { ns:michel ns:likes ns:pizza . } }",
        initNs={"ns": URIRef("urn:example:")},
    )

    graph = ds.graph(graphuri)
    assert set(graph.triples((None, None, None))) == set(
        [(michel, likes, pizza)]
    ), "only michel likes pizza"


def test_update_with_initbindings(get_dataset):
    store, path, ds = get_dataset
    ds.default_union = True
    ds.update(
        "INSERT { GRAPH <urn:example:graph> { ?a ?b ?c . } } WherE { }",
        initBindings={
            "a": michel,
            "b": likes,
            "c": pizza,
        },
    )

    graph = ds.graph(graphuri)
    assert set(graph.triples((None, None, None))) == set(
        [(michel, likes, pizza)]
    ), "only michel likes pizza"


def test_multiple_update_with_initbindings(get_dataset):
    store, path, ds = get_dataset
    ds.default_union = True
    ds.update(
        "INSERT { GRAPH <urn:example:graph> { ?a ?b ?c . } } WHERE { };"
        "INSERT { GRAPH <urn:example:graph> { ?d ?b ?c . } } WHERE { }",
        initBindings={
            "a": michel,
            "b": likes,
            "c": pizza,
            "d": bob,
        },
    )

    graph = ds.graph(graphuri)
    assert set(graph.triples((None, None, None))) == set(
        [(michel, likes, pizza), (bob, likes, pizza)]
    ), "michel and bob like pizza"


def test_named_graph_update(get_dataset):
    store, path, ds = get_dataset
    graph = ds.graph(graphuri)
    r1 = "INSERT DATA { <urn:example:michel> <urn:example:likes> <urn:example:pizza> }"
    graph.update(r1)
    assert set(graph.triples((None, None, None))) == set(
        [(michel, likes, pizza)]
    ), "only michel likes pizza"

    r2 = (
        "DELETE { <urn:example:michel> <urn:example:likes> <urn:example:pizza> } "
        + "INSERT { <urn:example:bob> <urn:example:likes> <urn:example:pizza> } WHERE {}"
    )
    graph.update(r2)
    assert set(graph.triples((None, None, None))) == set(
        [(bob, likes, pizza)]
    ), "only bob likes pizza"
    says = URIRef("urn:example:says")

    # Strings with unbalanced curly braces
    tricky_strs = ["With an unbalanced curly brace %s " % brace for brace in ["{", "}"]]
    for tricky_str in tricky_strs:
        r3 = (
            """INSERT { ?b <urn:example:says> "%s" }
        WHERE { ?b <urn:example:likes> <urn:example:pizza>} """
            % tricky_str
        )
        graph.update(r3)

    values = set()
    for v in graph.objects(bob, says):
        values.add(str(v))
    assert values == set(tricky_strs)

    # Complicated Strings
    r4strings = []
    r4strings.append(r'''"1: adfk { ' \\\" \" { "''')
    r4strings.append(r'''"2: adfk } <foo> #éï \\"''')

    r4strings.append(r"""'3: adfk { " \\\' \' { '""")
    r4strings.append(r"""'4: adfk } <foo> #éï \\'""")

    r4strings.append(r'''"""5: adfk { ' \\\" \" { """''')
    r4strings.append(r'''"""6: adfk } <foo> #éï \\"""''')
    r4strings.append('"""7: ad adsfj \n { \n sadfj"""')

    r4strings.append(r"""'''8: adfk { " \\\' \' { '''""")
    r4strings.append(r"""'''9: adfk } <foo> #éï \\'''""")
    r4strings.append("'''10: ad adsfj \n { \n sadfj'''")

    r4 = "\n".join(
        [
            "INSERT DATA { <urn:example:michel> <urn:example:says> %s } ;" % s
            for s in r4strings
        ]
    )
    graph.update(r4)
    values = set()
    for v in graph.objects(michel, says):
        values.add(str(v))
    assert values == set(
        [
            re.sub(
                r"\\(.)",
                r"\1",
                re.sub(r"^'''|'''$|^'|'$|" + r'^"""|"""$|^"|"$', r"", s),
            )
            for s in r4strings
        ]
    )

    # IRI Containing ' or #
    # The fragment identifier must not be misinterpreted as a comment
    # (commenting out the end of the block).
    # The ' must not be interpreted as the start of a string, causing the }
    # in the literal to be identified as the end of the block.
    r5 = """INSERT DATA { <urn:example:michel> <urn:example:hates> <urn:example:foo'bar?baz;a=1&b=2#fragment>, "'}" }"""

    graph.update(r5)
    values = set()
    for v in graph.objects(michel, hates):
        values.add(str(v))
    assert values == set(["urn:example:foo'bar?baz;a=1&b=2#fragment", "'}"])

    # Comments
    r6 = """
        INSERT DATA {
            <urn:example:bob> <urn:example:hates> <urn:example:bob> . # No closing brace: }
            <urn:example:bob> <urn:example:hates> <urn:example:michel>.
        }
    #Final { } comment"""

    graph.update(r6)
    values = set()
    for v in graph.objects(bob, hates):
        values.add(v)
    assert values == set([bob, michel])


def test_named_graph_update_with_initbindings(get_dataset):
    store, path, ds = get_dataset
    graph = ds.graph(graphuri)
    r = "INSERT { ?a ?b ?c } WHERE {}"
    graph.update(r, initBindings={"a": michel, "b": likes, "c": pizza})
    assert set(graph.triples((None, None, None))) == set(
        [(michel, likes, pizza)]
    ), "only michel likes pizza"


def test_empty_literal(get_dataset):
    # test for https://github.com/RDFLib/rdflib/issues/457
    # also see test_issue457.py which is sparql store independent!
    store, path, ds = get_dataset
    graph = ds.graph(graphuri)
    graph.add(
        (
            URIRef("http://example.com/s"),
            URIRef("http://example.com/p"),
            Literal(""),
        )
    )

    o = tuple(graph)[0][2]
    assert Literal("") == o, repr(o)
