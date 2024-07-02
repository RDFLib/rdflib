import os
from test.data import TEST_DATA_DIR

from rdflib import ConjunctiveGraph, URIRef

timblcardn3 = open(os.path.join(TEST_DATA_DIR, "timbl-card.n3")).read()


michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")


def add_stuff(graph):
    graph.add((tarek, likes, pizza))
    graph.add((tarek, likes, cheese))
    graph.add((tarek, likes, bob))
    graph.add((tarek, likes, michel))
    graph.add((michel, likes, pizza))
    graph.add((michel, likes, cheese))
    graph.add((michel, likes, tarek))
    graph.add((bob, likes, cheese))
    graph.add((bob, hates, pizza))
    graph.add((bob, hates, michel))
    graph.add((bob, likes, tarek))


def test_unique_subjects():
    graph = ConjunctiveGraph()
    add_stuff(graph)
    assert len(list(graph.subjects())) == 11
    assert len(list(graph.subjects(unique=True))) == 3


def test_unique_predicates():
    graph = ConjunctiveGraph()
    add_stuff(graph)
    assert len(list(graph.predicates())) == 11
    assert len(list(graph.predicates(unique=True))) == 2


def test_unique_objects():
    graph = ConjunctiveGraph()
    add_stuff(graph)
    assert len(list(graph.objects())) == 11
    assert len(list(graph.objects(unique=True))) == 5


def test_unique_subject_predicates():
    graph = ConjunctiveGraph()
    add_stuff(graph)
    assert len(list(graph.subject_predicates())) == 11
    assert len(list(graph.subject_predicates(unique=True))) == 4


def test_unique_predicate_objects():
    graph = ConjunctiveGraph()
    add_stuff(graph)
    assert len(list(graph.predicate_objects())) == 11
    assert len(list(graph.predicate_objects(unique=True))) == 7


def test_unique_subject_objects():
    graph = ConjunctiveGraph()
    add_stuff(graph)
    assert len(list(graph.subject_objects())) == 11
    assert len(list(graph.subject_objects(unique=True))) == 11


no_of_statements_in_card = 86
no_of_unique_subjects = 20
no_of_unique_predicates = 58
no_of_unique_objects = 62


def test_parse_berners_lee_card_into_conjunctivegraph_default():
    graph = ConjunctiveGraph()
    graph.parse(data=timblcardn3, format="n3")
    assert len(list(graph.subjects())) == no_of_statements_in_card
    assert len(list(graph.subjects(unique=True))) == no_of_unique_subjects
    assert len(list(graph.predicates(unique=True))) == no_of_unique_predicates
    assert len(list(graph.objects(unique=True))) == no_of_unique_objects


def test_parse_berners_lee_card_into_named_graph():
    graph = ConjunctiveGraph(identifier=URIRef("context-1"))
    graph.parse(data=timblcardn3, format="n3")
    assert len(list(graph.subjects())) == no_of_statements_in_card
    assert len(list(graph.subjects(unique=True))) == no_of_unique_subjects
    assert len(list(graph.predicates(unique=True))) == no_of_unique_predicates
    assert len(list(graph.objects(unique=True))) == no_of_unique_objects
