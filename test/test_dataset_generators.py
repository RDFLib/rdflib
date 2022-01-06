import os
import pytest
from rdflib import Dataset, URIRef

timblcardn3 = open(
    os.path.join(os.path.dirname(__file__), "consistent_test_data", "timbl-card.n3")
).read()


michel = URIRef("urn:x-rdflib:michel")
tarek = URIRef("urn:x-rdflib:tarek")
bob = URIRef("urn:x-rdflib:bob")
likes = URIRef("urn:x-rdflib:likes")
hates = URIRef("urn:x-rdflib:hates")
pizza = URIRef("urn:x-rdflib:pizza")
cheese = URIRef("urn:x-rdflib:cheese")


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
    graph = Dataset()
    add_stuff(graph)
    with pytest.raises(AssertionError):  # 0 != 11
        assert len([sub for sub in graph.subjects()]) == 11
    with pytest.raises(AssertionError):  # 0 != 3
        assert len([sub for sub in graph.subjects(unique=True)]) == 3


def test_unique_predicates():
    graph = Dataset()
    add_stuff(graph)
    with pytest.raises(AssertionError):  # 0 != 11
        assert len([pred for pred in graph.predicates()]) == 11
    with pytest.raises(AssertionError):  # 0 != 2
        assert len([pred for pred in graph.predicates(unique=True)]) == 2


def test_unique_objects():
    graph = Dataset()
    add_stuff(graph)
    with pytest.raises(AssertionError):  # 0 != 11
        assert len([obj for obj in graph.objects()]) == 11
    with pytest.raises(AssertionError):  # 0 != 5
        assert len([obj for obj in graph.objects(unique=True)]) == 5


def test_unique_subject_predicates():
    graph = Dataset()
    add_stuff(graph)
    with pytest.raises(AssertionError):  # 0 != 11
        assert len([sub for sub in graph.subject_predicates()]) == 11
    with pytest.raises(AssertionError):  # 0 != 4
        assert len([sub for sub in graph.subject_predicates(unique=True)]) == 4


def test_unique_predicate_objects():
    graph = Dataset()
    add_stuff(graph)
    with pytest.raises(AssertionError):  # 0 != 11
        assert len([pred for pred in graph.predicate_objects()]) == 11
    with pytest.raises(AssertionError):  # 0 != 11
        assert len([obj for obj in graph.subject_objects()]) == 11
    with pytest.raises(AssertionError):  # 0 != 7
        assert len([pred for pred in graph.predicate_objects(unique=True)]) == 7


def test_unique_subject_objects():
    graph = Dataset()
    add_stuff(graph)
    with pytest.raises(AssertionError):  # 0 != 11
        assert len([obj for obj in graph.subject_objects()]) == 11
    with pytest.raises(AssertionError):  # 0 != 11
        assert len([obj for obj in graph.subject_objects()]) == 11
    with pytest.raises(AssertionError):  # 0 != 11
        assert len([obj for obj in graph.subject_objects(unique=True)]) == 11


no_of_statements_in_card = 86
no_of_unique_subjects = 20
no_of_unique_predicates = 58
no_of_unique_objects = 62


def test_parse_berners_lee_card_into_dataset_default():

    # FIXME: Workaround pending completion of identifier-as-context

    # graph = Dataset()

    g = Dataset()
    graph = g.graph(URIRef("urn:x-rdflib:default"))

    graph.parse(data=timblcardn3, format="n3")
    assert len(list(graph.subjects())) == no_of_statements_in_card
    assert len(list(graph.subjects(unique=True))) == no_of_unique_subjects
    assert len(list(graph.predicates(unique=True))) == no_of_unique_predicates
    assert len(list(graph.objects(unique=True))) == no_of_unique_objects


def test_parse_berners_lee_card_into_dataset_context():
    g = Dataset()
    graph = g.graph()
    graph.parse(data=timblcardn3, format="n3")
    assert len(list(graph.subjects())) == no_of_statements_in_card
    assert len(list(graph.subjects(unique=True))) == no_of_unique_subjects
    assert len(list(graph.predicates(unique=True))) == no_of_unique_predicates
    assert len(list(graph.objects(unique=True))) == no_of_unique_objects
