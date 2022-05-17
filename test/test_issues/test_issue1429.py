from rdflib import Graph
from rdflib.parser import iri2uri


def test_iri2uri() -> None:
    assert (
        iri2uri("https://dbpedia.org/resource/Almería")
        == 'https://dbpedia.org/resource/Almer%C3%ADa'
    )


def test_issue_1429_iri2uri() -> None:
    g = Graph()
    g.parse("https://dbpedia.org/resource/Almería")
