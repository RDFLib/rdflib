from __future__ import annotations

from rdflib import Graph
from rdflib.compare import graph_diff


def test_graph_diff_with_unrelated_blank_nodes() -> None:
    g1t = """@prefix : <http://test.org#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .

:C1 a owl:Class ;
    rdfs:subClassOf [ a owl:Restriction ;
                      owl:minCardinality "1"^^xsd:int ;
                      owl:onProperty rdfs:label ] ;
    rdfs:label "C1"@en ."""

    g2t = (
        g1t
        + """
:C2 a owl:Class ;
    rdfs:subClassOf [ a owl:Restriction ;
                      owl:minCardinality "1"^^xsd:int ;
                      owl:onProperty rdfs:comment ] ;
    rdfs:label "C2"@en ."""
    )

    g1 = Graph().parse(data=g1t, format="turtle")
    g2 = Graph().parse(data=g2t, format="turtle")

    in_both, in_first, in_second = graph_diff(g1, g2)
    assert len(in_first) == 0
    assert len(in_both) == len(g1)
    assert len(in_second) == len(g2) - len(g1)
