import sys
import os
from tempfile import mkdtemp, mkstemp

import pytest
from rdflib import RDF, RDFS, URIRef, BNode, Variable, plugin
from rdflib.graph import QuotedGraph, Dataset
from rdflib.store import NO_STORE, VALID_STORE, Store
from test.pluginstores import HOST, root, get_plugin_stores, set_store_and_path, open_store, cleanup, dburis
from test.data import context0


implies = URIRef("http://www.w3.org/2000/10/swap/log#implies")
testN3 = """
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
{:a :b :c;a :foo} => {:a :d :c,?y}.
_:foo a rdfs:Class.
:a :d :c."""


# Thorough test suite for formula-aware store

@pytest.fixture(
    scope="function",
    params=get_plugin_stores(),
)
def get_dataset(request):
    storename = request.param

    store, path = set_store_and_path(storename)

    s = plugin.get(storename, Store)(identifier=context0)

    if not s.formula_aware:
        pytest.skip(reason=f"{store} not formula-aware")

    d = Dataset(store=store, identifier=URIRef("urn:example:testgraph"), default_union=True)

    dataset = open_store(d, storename, path)

    yield store, path, dataset

    cleanup(dataset, storename, path)


def test_formula_store(get_dataset):

    store, path, g = get_dataset

    g.parse(data=testN3, format="n3")

    try:
        for s, p, o in g.triples((None, implies, None)):
            formulaA = s
            formulaB = o

        assert type(formulaA) == QuotedGraph and type(formulaB) == QuotedGraph
        a = URIRef('http://test/a')
        b = URIRef("http://test/b")
        c = URIRef("http://test/c")
        d = URIRef("http://test/d")
        v = Variable("y")

        universe = Dataset(g.store)

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

        # #context tests
        # #test contexts with triple argument
        # assert len(list(universe.contexts((a, d, c)))) == 1, \
        #                     [ct for ct in universe.contexts((a, d, c))]

        # (a, d, c) is in both the formula and the default graph but for a 
        # Dataset the latter is not considered a context

        if store == "SQLiteDBStore":  # The only Store that handles this correctly
            assert len(list(universe.contexts((a, d, c)))) == 1
        else:
            assert len(list(universe.contexts((a, d, c)))) == 0

        assert len(list(universe.default_graph.triples((a, d, c)))) == 1

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
        universe.remove_graph(formulaB)
        assert len(list(universe.triples((None, RDF.type, None)))) == 0
        assert len(universe) == 1
        assert len(formulaB) == 0

        universe.remove((None, None, None))
        assert len(universe) == 0


    except Exception as e:
        if store != "Memory":
            if store == "SPARQLUpdateStore":
                g.remove((None, None, None))
                g.close()
            else:
                try:
                    g.close()
                    g.destroy(configuration=path)
                except Exception:
                    pass
            try:
                shutil.rmtree(path)
            except Exception:
                pass
        raise Exception(e)
