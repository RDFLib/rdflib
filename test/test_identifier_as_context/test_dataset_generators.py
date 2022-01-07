import os
from rdflib import Dataset, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

timblcardn3 = open(
    os.path.join(
        os.path.dirname(__file__), "..", "consistent_test_data", "timbl-card.n3"
    )
).read()


timblcardnquads = open(
    os.path.join(
        os.path.dirname(__file__), "..", "consistent_test_data", "timbl-card.nquads"
    )
).read()


michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

c1 = URIRef("urn:example:context-1")
c2 = URIRef("urn:example:context-2")


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
    ds = Dataset()
    graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    add_stuff(graph)
    assert len(list(graph.subjects())) == 11
    assert len(list(graph.subjects(unique=True))) == 3


def test_unique_subjects_union():
    ds = Dataset(default_union=True)
    add_stuff(ds)
    assert len(list(ds.subjects())) == 11
    assert len(list(ds.subjects(unique=True))) == 3


def test_unique_predicates():
    ds = Dataset()
    graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    add_stuff(graph)
    assert len(list(graph.predicates())) == 11
    assert len(list(graph.predicates(unique=True))) == 2


def test_unique_predicates_union():
    ds = Dataset(default_union=True)
    add_stuff(ds)
    assert len(list(ds.predicates())) == 11
    assert len(list(ds.predicates(unique=True))) == 2


def test_unique_objects():
    ds = Dataset()
    graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    add_stuff(graph)
    assert len(list(graph.objects())) == 11
    assert len(list(graph.objects(unique=True))) == 5


def test_unique_objects_union():
    ds = Dataset(default_union=True)
    add_stuff(ds)
    assert len(list(ds.objects())) == 11
    assert len(list(ds.objects(unique=True))) == 5


def test_unique_subject_predicates():
    ds = Dataset()
    graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    add_stuff(graph)
    assert len(list(graph.subject_predicates())) == 11
    assert len(list(graph.subject_predicates(unique=True))) == 4


def test_unique_subject_predicates_union():
    ds = Dataset(default_union=True)
    add_stuff(ds)
    assert len(list(ds.subject_predicates())) == 11
    assert len(list(ds.subject_predicates(unique=True))) == 4


def test_unique_predicate_objects():
    ds = Dataset()
    graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    add_stuff(graph)
    assert len(list(graph.predicate_objects())) == 11
    assert len(list(graph.subject_objects())) == 11
    assert len(list(graph.predicate_objects(unique=True))) == 7


def test_unique_predicate_objects_union():
    ds = Dataset(default_union=True)
    add_stuff(ds)
    assert len(list(ds.predicate_objects())) == 11
    assert len(list(ds.subject_objects())) == 11
    assert len(list(ds.predicate_objects(unique=True))) == 7


def test_unique_subject_objects():
    ds = Dataset()
    graph = ds.get_context(DATASET_DEFAULT_GRAPH_ID)
    add_stuff(graph)
    assert len(list(graph.subject_objects())) == 11
    assert len(list(graph.subject_objects())) == 11
    assert len(list(graph.subject_objects(unique=True))) == 11


def test_unique_subject_objects_union():
    ds = Dataset(default_union=True)
    add_stuff(ds)
    assert len(list(ds.subject_objects())) == 11
    assert len(list(ds.subject_objects())) == 11
    assert len(list(ds.subject_objects(unique=True))) == 11


no_of_statements_in_card = 86
no_of_unique_subjects = 20
no_of_unique_predicates = 58
no_of_unique_objects = 62


def test_parse_berners_lee_card_into_dataset_default():

    ds = Dataset()
    graph = ds.graph(DATASET_DEFAULT_GRAPH_ID)

    graph.parse(data=timblcardnquads, format="nquads")
    assert len(list(graph.subjects())) == no_of_statements_in_card
    assert len(list(graph.subjects(unique=True))) == no_of_unique_subjects
    assert len(list(graph.predicates(unique=True))) == no_of_unique_predicates
    assert len(list(graph.objects(unique=True))) == no_of_unique_objects


def test_parse_berners_lee_card_into_dataset_default_union():

    ds = Dataset(default_union=True)

    ds.parse(data=timblcardnquads, format="nquads")
    assert len(list(ds.subjects())) == no_of_statements_in_card
    assert len(list(ds.subjects(unique=True))) == no_of_unique_subjects
    assert len(list(ds.predicates(unique=True))) == no_of_unique_predicates
    assert len(list(ds.objects(unique=True))) == no_of_unique_objects


def test_parse_berners_lee_card_into_dataset_graph():
    g = Dataset()
    graph = g.graph()
    graph.parse(data=timblcardn3, format="n3")
    assert len(list(graph.subjects())) == no_of_statements_in_card
    assert len(list(graph.subjects(unique=True))) == no_of_unique_subjects
    assert len(list(graph.predicates(unique=True))) == no_of_unique_predicates
    assert len(list(graph.objects(unique=True))) == no_of_unique_objects
