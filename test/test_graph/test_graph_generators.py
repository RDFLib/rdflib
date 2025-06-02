import os

from rdflib import Graph
from test.data import BOB, CHEESE, HATES, LIKES, MICHEL, PIZZA, TAREK, TEST_DATA_DIR

timblcardn3 = open(os.path.join(TEST_DATA_DIR, "timbl-card.n3")).read()


def add_stuff(graph):
    graph.add((TAREK, LIKES, PIZZA))
    graph.add((TAREK, LIKES, CHEESE))
    graph.add((TAREK, LIKES, BOB))
    graph.add((TAREK, LIKES, MICHEL))
    graph.add((MICHEL, LIKES, PIZZA))
    graph.add((MICHEL, LIKES, CHEESE))
    graph.add((MICHEL, LIKES, TAREK))
    graph.add((BOB, LIKES, CHEESE))
    graph.add((BOB, HATES, PIZZA))
    graph.add((BOB, HATES, MICHEL))
    graph.add((BOB, LIKES, TAREK))


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


def test_subjects_multi():
    graph = Graph()
    add_stuff(graph)
    assert len([subj for subj in graph.subjects(LIKES, [CHEESE, PIZZA])]) == 5
    assert len([subj for subj in graph.subjects(LIKES, [])]) == 0
    assert len([subj for subj in graph.subjects(LIKES | HATES, [CHEESE, PIZZA])]) == 6


def test_objects_multi():
    graph = Graph()
    add_stuff(graph)
    assert len([obj for obj in graph.objects([TAREK, BOB], LIKES)]) == 6
    assert len([obj for obj in graph.objects([], LIKES)]) == 0
    assert len([obj for obj in graph.objects([TAREK, BOB], LIKES | HATES)]) == 8
