import pytest

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.extras.infixowl import AnnotatableTerms, Individual

EXNS = Namespace("http://example.org/vocab/")
PZNS = Namespace(
    "http://www.co-ode.org/ontologies/pizza/2005/10/18/classified/pizza.owl#"
)


@pytest.fixture(scope="function")
def graph():
    g = Graph()
    g.bind("ex", EXNS)
    Individual.factoryGraph = g

    yield g

    del g


def test_annotatableterms_comment_gettersetter(graph):

    u = URIRef(EXNS.foo)

    at = AnnotatableTerms(u, graph, EXNS.foo, True)
    comment1 = Literal("A comment")
    comment2 = Literal("Another comment")

    at.comment = comment1

    assert list(at.comment) == [comment1]

    at.comment = [comment1, comment2]

    assert list(at.comment) == [comment1, comment2]


def test_annotatableterms_seealso_gettersetter(graph):

    u = URIRef(EXNS.foo)

    at = AnnotatableTerms(u, graph, EXNS.foo, True)

    at.seeAlso = None

    seealso1 = EXNS.tarek
    seealso2 = EXNS.pizza

    at.seeAlso = [seealso1, seealso2]

    assert list(at.seeAlso) == [seealso1, seealso2]


def test_annotatableterms_label_gettersetter(graph):

    u = URIRef(EXNS.foo)

    at = AnnotatableTerms(u, graph, EXNS.foo, True)

    at.label = None

    label1 = Literal("A label")
    label2 = Literal("Another label")

    at.label = label1

    assert list(at.label) == [u, label1]

    at.label = [label1, label2]

    assert list(at.label) == [u, label1, label2]
