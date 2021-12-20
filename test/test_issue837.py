# Recovered from https://github.com/RDFLib/rdflib/pull/1068
import pytest
from rdflib import logger, Graph, URIRef
from pprint import pformat

michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")


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


# @pytest.mark.skip
def test_issue837_unique_subjects():
    graph = Graph()
    add_stuff(graph)
    assert len([sub for sub in graph.subjects()]) == 11
    assert len([sub for sub in graph.subjects(unique=True)]) == 3


# @pytest.mark.skip
def test_issue837_unique_predicates():
    graph = Graph()
    add_stuff(graph)
    assert len([pred for pred in graph.predicates()]) == 11
    assert len([pred for pred in graph.predicates(unique=True)]) == 2


# @pytest.mark.skip
def test_issue837_unique_objects():
    graph = Graph()
    add_stuff(graph)
    assert len([obj for obj in graph.objects()]) == 11
    assert len([obj for obj in graph.objects(unique=True)]) == 5


# @pytest.mark.skip
def test_issue837_unique_subject_predicates():
    graph = Graph()
    add_stuff(graph)
    assert len([sub for sub in graph.subject_predicates()]) == 11
    assert len([sub for sub in graph.subject_predicates(unique=True)]) == 4
    # logger.debug(f"\n{pformat(sorted(list(graph.subject_predicates(unique=True))))}")


# @pytest.mark.skip
def test_issue837_unique_predicate_objects():
    graph = Graph()
    add_stuff(graph)
    assert len([pred for pred in graph.predicate_objects()]) == 11
    assert len([pred for pred in graph.predicate_objects(unique=True)]) == 7
    # logger.debug(f"\n{pformat(list(graph.predicate_objects(unique=True)))}")


# @pytest.mark.skip
def test_issue837_unique_subject_objects():
    graph = Graph()
    add_stuff(graph)
    assert len([obj for obj in graph.subject_objects()]) == 11
    assert len([obj for obj in graph.subject_objects(unique=True)]) == 11
    # logger.debug(f"\n{pformat(sorted(list(graph.subject_objects(unique=True))))}")
