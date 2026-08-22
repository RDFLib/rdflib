from __future__ import annotations

import pytest

from rdflib import Dataset, Graph, Namespace, TripleTerm
from rdflib.exceptions import Error

EX = Namespace("http://example.org/")


@pytest.mark.parametrize(
    "format_name",
    [
        "xml",
        "pretty-xml",
        "n3",
        "turtle",
        "longturtle",
        "nt",
        "nt11",
        "json-ld",
        "hext",
    ],
)
def test_rdf11_graph_serializers_reject_triple_term(format_name: str) -> None:
    graph = Graph()
    term = TripleTerm(EX.embedded_subject, EX.embedded_predicate, EX.embedded_object)
    graph.add((EX.subject, EX.predicate, term))

    with pytest.raises(Error, match="TripleTerm requires an RDF 1.2 serializer"):
        graph.serialize(format=format_name)


@pytest.mark.parametrize("format_name", ["nquads", "trix", "trig", "patch"])
def test_rdf11_dataset_serializers_reject_triple_term(format_name: str) -> None:
    dataset = Dataset()
    term = TripleTerm(EX.embedded_subject, EX.embedded_predicate, EX.embedded_object)
    dataset.add((EX.subject, EX.predicate, term, dataset.graph(EX.graph)))

    with pytest.raises(Error, match="TripleTerm requires an RDF 1.2 serializer"):
        dataset.serialize(format=format_name)
