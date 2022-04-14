import pytest

import rdflib
from rdflib import BNode, Dataset, Graph, Literal, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, RDFS, Namespace
from rdflib.plugins.sparql import prepareQuery, sparql
from rdflib.term import Variable


def test_named_filter_graph_query():
    ds = Dataset(default_union=True)
    ds.namespace_manager.bind("rdf", RDF)
    ds.namespace_manager.bind("rdfs", RDFS)
    ex = Namespace("https://ex.com/")
    ds.namespace_manager.bind("ex", ex)
    ds.graph(ex.g1).parse(
        format="turtle",
        data=f"""
    PREFIX ex: <{str(ex)}>
    PREFIX rdfs: <{str(RDFS)}>
    ex:Boris rdfs:label "Boris" .
    ex:Susan rdfs:label "Susan" .
    """,
    )
    ds.graph(ex.g2).parse(
        format="turtle",
        data=f"""
    PREFIX ex: <{str(ex)}>
    ex:Boris a ex:Person .
    """,
    )

    assert sorted(list(ds.quads((None, None, None, None)))) == [
        (
            rdflib.term.URIRef('https://ex.com/Boris'),
            rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
            rdflib.term.URIRef('https://ex.com/Person'),
            rdflib.term.URIRef('https://ex.com/g2'),
        ),
        (
            rdflib.term.URIRef('https://ex.com/Boris'),
            rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
            rdflib.term.Literal('Boris'),
            rdflib.term.URIRef('https://ex.com/g1'),
        ),
        (
            rdflib.term.URIRef('https://ex.com/Susan'),
            rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
            rdflib.term.Literal('Susan'),
            rdflib.term.URIRef('https://ex.com/g1'),
        ),
    ]

    assert len(list(ds.contexts())) == 2
    assert ex.g1 in list(ds.contexts())
    assert ex.g2 in list(ds.contexts())

    assert list(
        ds.query(
            "SELECT ?l WHERE { GRAPH ex:g1 { ?a rdfs:label ?l } ?a a ?type }",
            initNs={"ex": ex},
        )
    ) == [(Literal("Boris"),)]
    assert list(
        ds.query(
            "SELECT ?l WHERE { GRAPH ex:g1 { ?a rdfs:label ?l } FILTER EXISTS { ?a a ?type }}",
            initNs={"ex": ex},
        )
    ) == [(Literal("Boris"),)]
    assert list(
        ds.query(
            "SELECT ?l WHERE { GRAPH ex:g1 { ?a rdfs:label ?l } FILTER NOT EXISTS { ?a a ?type }}",
            initNs={"ex": ex},
        )
    ) == [(Literal("Susan"),)]
    assert list(
        ds.query(
            "SELECT ?l WHERE { GRAPH ?g { ?a rdfs:label ?l } ?a a ?type }",
            initNs={"ex": ex},
        )
    ) == [(Literal("Boris"),)]
    assert list(
        ds.query(
            "SELECT ?l WHERE { GRAPH ?g { ?a rdfs:label ?l } FILTER EXISTS { ?a a ?type }}",
            initNs={"ex": ex},
        )
    ) == [(Literal("Boris"),)]
    assert list(
        ds.query(
            "SELECT ?l WHERE { GRAPH ?g { ?a rdfs:label ?l } FILTER NOT EXISTS { ?a a ?type }}",
            initNs={"ex": ex},
        )
    ) == [(Literal("Susan"),)]
