from pathlib import Path

import pytest

pytest.importorskip("pyoxigraph")
from pyoxigraph import DefaultGraph, NamedNode, RdfFormat, Store

from rdflib import Namespace, URIRef
from rdflib.namespace import RDF
from rdflib.plugins.inference import DeductiveClosure
from rdflib.plugins.inference.owlrl import OWLRL_Semantics

RELS = Namespace("http://example.org/relatives#")


def test_dataset():
    # create an RDF graph, load a simple OWL ontology and data
    s = Store()
    s.bulk_load(
        None,
        path=Path(__file__).with_name("relatives.ttl"),
        format=RdfFormat.TURTLE,
    )

    # count no. rels:Person class instances, no inferencing, should find 14 results (one Child)
    cnt = 0

    person_instances = s.quads_for_pattern(
        None, NamedNode(RDF.type), NamedNode(RELS.Person), None
    )
    for _ in person_instances:
        cnt += 1

    assert cnt == 14

    dest_uri = NamedNode("urn:test:dest")
    # count no. of hasGrandparent predicates, no inferencing, should find 0 results
    cnt = 0
    has_grandparent_predicates = s.quads_for_pattern(
        None, NamedNode(RELS.hasGrandparent), None, dest_uri
    )
    for _ in has_grandparent_predicates:
        cnt += 1
    assert cnt == 0

    # expand the graph with OWL-RL semantics
    DeductiveClosure(OWLRL_Semantics).expand(s, destination=URIRef("urn:test:dest"))

    # count no. rels:Person class instances, after inferencing, should find 1 result in the Dest graph
    cnt = 0
    has_person_instances = s.quads_for_pattern(
        None, NamedNode(RDF.type), NamedNode(RELS.Person), dest_uri
    )
    for _ in has_person_instances:
        cnt += 1

    assert cnt == 1

    # count no. rels:Person class instances, after inferencing, should find 15 results in the whole dataset
    cnt = 0
    has_person_instances = s.quads_for_pattern(
        None, NamedNode(RDF.type), NamedNode(RELS.Person), None
    )
    for _ in has_person_instances:
        cnt += 1

    assert cnt == 15

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results in the Dest graph
    cnt = 0
    has_grandparent_predicates = s.quads_for_pattern(
        None, NamedNode(RELS.hasGrandparent), None, dest_uri
    )
    for _ in has_grandparent_predicates:
        cnt += 1
    assert cnt == 7

    # count no. of hasGrandparent predicates, after inferencing, should find 7 results in the whole dataset
    cnt = 0
    has_grandparent_predicates = s.quads_for_pattern(
        None, NamedNode(RELS.hasGrandparent), None, None
    )
    for _ in has_grandparent_predicates:
        cnt += 1
    assert cnt == 7

    # count no. of hasGrandparent predicates, after inferencing, should find 0 results in the default graph
    cnt = 0
    has_grandparent_predicates = s.quads_for_pattern(
        None, NamedNode(RELS.hasGrandparent), None, DefaultGraph()
    )
    for _ in has_grandparent_predicates:
        cnt += 1
    assert cnt == 0
