import pytest

from rdflib import Dataset, Graph, Namespace, URIRef
from rdflib.plugins.serializers.longturtle import LongTurtleSerializer
from rdflib.plugins.serializers.n3 import N3Serializer
from rdflib.plugins.serializers.turtle import TurtleSerializer


def test_dataset_contexts_method():
    ds = Dataset()
    with pytest.warns(
        DeprecationWarning,
        match="Dataset.contexts is deprecated, use Dataset.graphs instead.",
    ):
        # Call list() to consume the generator to emit the warning.
        list(ds.contexts())


def test_dataset_default_context_property():
    ds = Dataset()
    with pytest.warns(
        DeprecationWarning,
        match="Dataset.default_context is deprecated, use Dataset.default_graph instead.",
    ):
        ds.default_context

    with pytest.warns(
        DeprecationWarning,
        match="Dataset.default_context is deprecated, use Dataset.default_graph instead.",
    ):
        ds.default_context = ds.graph()


def test_dataset_identifier_property():
    ds = Dataset()
    with pytest.warns(
        DeprecationWarning,
        match="Dataset.identifier is deprecated and will be removed in future versions.",
    ):
        ds.identifier


@pytest.mark.parametrize(
    ("serializer_cls", "warning_message"),
    [
        (
            TurtleSerializer,
            "TurtleSerializer.getQName is deprecated, use TurtleSerializer.get_pname instead.",
        ),
        (
            LongTurtleSerializer,
            "LongTurtleSerializer.getQName is deprecated, use LongTurtleSerializer.get_pname instead.",
        ),
        (
            N3Serializer,
            "N3Serializer.getQName is deprecated, use N3Serializer.get_pname instead.",
        ),
    ],
)
def test_serializer_getqname_method(
    serializer_cls,
    warning_message: str,
):
    graph = Graph()
    ex = Namespace("http://example.org/")
    graph.bind("ex", ex)
    serializer = serializer_cls(graph)

    with pytest.warns(DeprecationWarning, match=warning_message):
        qname = serializer.getQName(URIRef("http://example.org/value"))

    assert qname == "ex:value"
