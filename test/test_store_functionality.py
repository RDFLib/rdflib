# -*- coding: utf-8 -*-
import os
import re
import shutil
import tempfile

import pytest

from rdflib import RDF, RDFS, BNode, ConjunctiveGraph, Literal, URIRef, Variable, plugin
from rdflib.graph import QuotedGraph
from rdflib.store import VALID_STORE

implies = URIRef("http://www.w3.org/2000/10/swap/log#implies")

testN3 = """\
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
{:a :b :c;a :foo} => {:a :d :c,?y} .
_:foo a rdfs:Class .
:a :d :c .
"""

michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

graphuri = URIRef("urn:example:graph")
othergraphuri = URIRef("urn:example:othergraph")


pluginstores = []

for s in plugin.plugins(None, plugin.Store):
    if s.name in (
        "default",
        "Memory",
        "Auditable",
        "Concurrent",
        "SimpleMemory",
        "SPARQLStore",
        "SPARQLUpdateStore",
    ):
        continue  # inappropriate for these tests

    pluginstores.append(s.name)


@pytest.fixture(
    scope="function",
    params=pluginstores,
)
def get_conjunctive_graph(request):
    store = request.param

    path = tempfile.mktemp()
    try:
        shutil.rmtree(path)
    except Exception:
        pass

    graph = ConjunctiveGraph(store=store)
    rt = graph.open(path, create=True)
    assert rt == VALID_STORE, "The underlying store is corrupt"

    yield graph, store, path

    graph.close()
    graph.destroy(configuration=path)


def test_simple_graph(get_conjunctive_graph):
    cg, store, path = get_conjunctive_graph
    graph = cg.get_context(graphuri)
    graph.add((tarek, likes, pizza))
    graph.add((bob, likes, pizza))
    graph.add((bob, likes, cheese))

    g2 = cg.get_context(othergraphuri)
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


def test_conjunctive_default(get_conjunctive_graph):
    cg, store, path = get_conjunctive_graph
    graph = cg.get_context(graphuri)

    graph.add((tarek, likes, pizza))

    g2 = cg.get_context(othergraphuri)
    g2.add((bob, likes, pizza))

    graph.add((tarek, hates, cheese))

    assert len(graph) == 2, "graph contains 2 triples"

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
    assert len(cg) == 3, f"default union graph should contain three triples but contains {list(cg)}:\n"

    r = cg.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 2, "two people like pizza"

    r = graph.query(
        "SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }",
        initBindings={"s": tarek},
    )
    assert len(list(r)) == 1, "i was asking only about tarek"

    r = graph.triples((tarek, likes, pizza))
    assert len(list(r)) == 1, "i was asking only about tarek"

    r = graph.triples((tarek, likes, cheese))
    assert len(list(r)) == 0, "tarek doesn't like cheese"

    g2.remove((bob, likes, pizza))

    r = graph.query("SELECT * WHERE { ?s <urn:example:likes> <urn:example:pizza> . }")
    assert len(list(r)) == 1, "only tarek likes pizza"


def test_update(get_conjunctive_graph):
    cg, store, path = get_conjunctive_graph
    cg.update("INSERT DATA { GRAPH <urn:example:graph> { <urn:example:michel> <urn:example:likes> <urn:example:pizza> . } }")

    graph = cg.get_context(graphuri)
    assert len(graph) == 1, "graph contains 1 triple"


def test_update_with_initns(get_conjunctive_graph):
    cg, store, path = get_conjunctive_graph
    cg.update(
        "INSERT DATA { GRAPH ns:graph { ns:michel ns:likes ns:pizza . } }",
        initNs={"ns": URIRef("urn:example:")},
    )

    graph = cg.get_context(graphuri)
    assert set(graph.triples((None, None, None))) == set([(michel, likes, pizza)]), "only michel likes pizza"


def test_update_with_initbindings(get_conjunctive_graph):
    cg, store, path = get_conjunctive_graph
    cg.update(
        "INSERT { GRAPH <urn:example:graph> { ?a ?b ?c . } } WherE { }",
        initBindings={
            "a": URIRef("urn:example:michel"),
            "b": URIRef("urn:example:likes"),
            "c": URIRef("urn:example:pizza"),
        },
    )

    graph = cg.get_context(graphuri)
    assert set(graph.triples((None, None, None))) == set([(michel, likes, pizza)]), "only michel likes pizza"


def test_multiple_update_with_initbindings(get_conjunctive_graph):
    cg, store, path = get_conjunctive_graph
    cg.update(
        "INSERT { GRAPH <urn:example:graph> { ?a ?b ?c . } } WHERE { };" "INSERT { GRAPH <urn:example:graph> { ?d ?b ?c . } } WHERE { }",
        initBindings={
            "a": URIRef("urn:example:michel"),
            "b": URIRef("urn:example:likes"),
            "c": URIRef("urn:example:pizza"),
            "d": URIRef("urn:example:bob"),
        },
    )

    graph = cg.get_context(graphuri)
    assert set(graph.triples((None, None, None))) == set([(michel, likes, pizza), (bob, likes, pizza)]), "michel and bob like pizza"


def test_named_graph_update(get_conjunctive_graph):
    cg, store, path = get_conjunctive_graph
    graph = cg.get_context(graphuri)
    r1 = "INSERT DATA { <urn:example:michel> <urn:example:likes> <urn:example:pizza> }"
    graph.update(r1)
    assert set(graph.triples((None, None, None))) == set([(michel, likes, pizza)]), "only michel likes pizza"

    r2 = (
        "DELETE { <urn:example:michel> <urn:example:likes> <urn:example:pizza> } "
        + "INSERT { <urn:example:bob> <urn:example:likes> <urn:example:pizza> } WHERE {}"
    )
    graph.update(r2)
    assert set(graph.triples((None, None, None))) == set([(bob, likes, pizza)]), "only bob likes pizza"
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

    r4 = "\n".join(["INSERT DATA { <urn:example:michel> <urn:example:says> %s } ;" % s for s in r4strings])
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


def test_named_graph_update_with_initbindings(get_conjunctive_graph):
    cg, store, path = get_conjunctive_graph
    graph = cg.get_context(graphuri)
    r = "INSERT { ?a ?b ?c } WHERE {}"
    graph.update(r, initBindings={"a": michel, "b": likes, "c": pizza})
    assert set(graph.triples((None, None, None))) == set([(michel, likes, pizza)]), "only michel likes pizza"


def test_empty_literal(get_conjunctive_graph):
    # test for https://github.com/RDFLib/rdflib/issues/457
    # also see test_issue457.py which is sparql store independent!
    cg, store, path = get_conjunctive_graph
    graph = cg.get_context(graphuri)
    graph.add(
        (
            URIRef("http://example.com/s"),
            URIRef("http://example.com/p"),
            Literal(""),
        )
    )

    o = tuple(graph)[0][2]
    assert Literal("") == o, repr(o)


def test_n3_store_conjunctive_graph(get_conjunctive_graph):
    """Thorough test suite for formula-aware store"""
    graph, store, path = get_conjunctive_graph

    graph.parse(data=testN3, format="n3")

    formulaA = BNode()
    formulaB = BNode()

    try:
        for s, p, o in graph.triples((None, implies, None)):
            formulaA = s
            formulaB = o

        assert type(formulaA) == QuotedGraph and type(formulaB) == QuotedGraph
        a = URIRef("http://test/a")
        b = URIRef("http://test/b")
        c = URIRef("http://test/c")
        d = URIRef("http://test/d")
        v = Variable("y")

        universe = ConjunctiveGraph(graph.store)

        # test formula as terms
        assert len(list(universe.triples((formulaA, implies, formulaB)))) == 1

        # test variable as term and variable roundtrip
        assert len(list(formulaB.triples((None, None, v)))) == 1
        for s, p, o in formulaB.triples((None, d, None)):
            if o != c:
                assert isinstance(o, Variable)
                assert o == v
        s = list(universe.subjects(RDF.type, RDFS.Class))[0]
        assert isinstance(s, BNode)
        assert len(list(universe.triples((None, implies, None)))) == 1
        assert len(list(universe.triples((None, RDF.type, None)))) == 1
        assert len(list(formulaA.triples((None, RDF.type, None)))) == 1
        assert len(list(formulaA.triples((None, None, None)))) == 2
        assert len(list(formulaB.triples((None, None, None)))) == 2
        assert len(list(universe.triples((None, None, None)))) == 3
        assert len(list(formulaB.triples((None, URIRef("http://test/d"), None)))) == 2
        assert len(list(universe.triples((None, URIRef("http://test/d"), None)))) == 1

        # context tests
        # test contexts with triple argument
        assert len(list(universe.contexts((a, d, c)))) == 1

        # Remove test cases
        universe.remove((None, implies, None))
        assert len(list(universe.triples((None, implies, None)))) == 0
        assert len(list(formulaA.triples((None, None, None)))) == 2
        assert len(list(formulaB.triples((None, None, None)))) == 2

        formulaA.remove((None, b, None))
        assert len(list(formulaA.triples((None, None, None)))) == 1
        formulaA.remove((None, RDF.type, None))
        assert len(list(formulaA.triples((None, None, None)))) == 0

        universe.remove((None, RDF.type, RDFS.Class))

        # remove_context tests
        universe.remove_context(formulaB)
        assert len(list(universe.triples((None, RDF.type, None)))) == 0
        assert len(universe) == 1
        assert len(formulaB) == 0

        universe.remove((None, None, None))
        assert len(universe) == 0

        graph.close()
        graph.store.destroy(path)
    except Exception as e:
        graph.store.close()
        graph.store.destroy(path)
        raise Exception(f"{e}")


xmltestdoc = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns="http://example.org/"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:about="http://example.org/a">
    <b rdf:resource="http://example.org/c"/>
  </rdf:Description>
</rdf:RDF>
"""

n3testdoc = """@prefix : <http://example.org/> .

:a :b :c .
"""

nttestdoc = "<http://example.org/a> <http://example.org/b> <http://example.org/c> .\n"
