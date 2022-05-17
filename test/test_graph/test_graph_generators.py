import os
from test.data import TEST_DATA_DIR, bob, cheese, hates, likes, michel, pizza, tarek

from rdflib import Graph

timblcardn3 = open(os.path.join(TEST_DATA_DIR, "timbl-card.n3")).read()


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
    graph = Graph()
    add_stuff(graph)
    assert len([sub for sub in graph.subjects()]) == 11
    assert len([sub for sub in graph.subjects(unique=True)]) == 3


def test_unique_predicates():
    graph = Graph()
    add_stuff(graph)
    assert len([pred for pred in graph.predicates()]) == 11
    assert len([pred for pred in graph.predicates(unique=True)]) == 2


def test_unique_objects():
    graph = Graph()
    add_stuff(graph)
    assert len([obj for obj in graph.objects()]) == 11
    assert len([obj for obj in graph.objects(unique=True)]) == 5


def test_unique_subject_predicates():
    graph = Graph()
    add_stuff(graph)
    assert len([sub for sub in graph.subject_predicates()]) == 11
    assert len([sub for sub in graph.subject_predicates(unique=True)]) == 4


def test_unique_predicate_objects():
    graph = Graph()
    add_stuff(graph)
    assert len([pred for pred in graph.predicate_objects()]) == 11
    assert len([pred for pred in graph.predicate_objects(unique=True)]) == 7


def test_unique_subject_objects():
    graph = Graph()
    add_stuff(graph)
    assert len([obj for obj in graph.subject_objects()]) == 11
    assert len([obj for obj in graph.subject_objects(unique=True)]) == 11


no_of_statements_in_card = 86
no_of_unique_subjects = 20
no_of_unique_predicates = 58
no_of_unique_objects = 62


def test_parse_berners_lee_card_into_graph():
    graph = Graph()
    graph.parse(data=timblcardn3, format="n3")
    assert len(list(graph.subjects())) == no_of_statements_in_card
    assert len(list(graph.subjects(unique=True))) == no_of_unique_subjects
    assert len(list(graph.predicates(unique=True))) == no_of_unique_predicates
    assert len(list(graph.objects(unique=True))) == no_of_unique_objects
