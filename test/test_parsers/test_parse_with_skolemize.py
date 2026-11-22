import pytest

from rdflib import BNode, Dataset, Graph
from rdflib.compare import isomorphic


@pytest.mark.parametrize(
    "data, data_format, expected_data, expected_data_format",
    [
        [
            """
        <urn:object> <urn:hasPart> _:internal-bnode-id-1 .
        _:internal-bnode-id-1 <urn:value> "..." .
        """,
            "ntriples",
            """
            <urn:object> <urn:hasPart> <https://rdflib.github.io/.well-known/genid/rdflib/internal-bnode-id-1> .
            <https://rdflib.github.io/.well-known/genid/rdflib/internal-bnode-id-1> <urn:value> "..." .
        """,
            "ntriples",
        ]
    ],
)
def test_parse_with_skolemize_triples(
    data: str, data_format: str, expected_data: str, expected_data_format: str
):
    graph = Graph().parse(data=data, format=data_format, skolemize=True)
    assert len(graph)

    expected_graph = Graph().parse(data=expected_data, format=expected_data_format)
    assert len(expected_graph)

    assert isomorphic(graph, expected_graph)

    de_skolem_graph = graph.de_skolemize()
    expected_de_skolem_graph = expected_graph.de_skolemize()
    assert isomorphic(de_skolem_graph, expected_de_skolem_graph)


@pytest.mark.parametrize(
    "data, data_format, expected_data, expected_data_format, anonymous_graph_name",
    [
        [
            """
            <urn:object> <urn:hasPart> _:internal-bnode-id-1 _:graph-id .
            _:internal-bnode-id-1 <urn:value> "..." _:graph-id .
        """,
            "nquads",
            """
            <urn:object> <urn:hasPart> <https://rdflib.github.io/.well-known/genid/rdflib/internal-bnode-id-1> <https://rdflib.github.io/.well-known/genid/rdflib/graph-id>  .
            <https://rdflib.github.io/.well-known/genid/rdflib/internal-bnode-id-1> <urn:value> "..." <https://rdflib.github.io/.well-known/genid/rdflib/graph-id> .
        """,
            "nquads",
            "graph-id",
        ],
        [
            """
                ["urn:object", "urn:hasPart", "_:internal-bnode-id-1", "localId", "", "_:graph-id"]
                ["_:internal-bnode-id-1", "urn:value", "...", "http://www.w3.org/2001/XMLSchema#string", "", "_:graph-id"]
            """,
            "hext",
            """
                <urn:object> <urn:hasPart> <https://rdflib.github.io/.well-known/genid/rdflib/internal-bnode-id-1> <https://rdflib.github.io/.well-known/genid/rdflib/graph-id>  .
                <https://rdflib.github.io/.well-known/genid/rdflib/internal-bnode-id-1> <urn:value> "..."^^<http://www.w3.org/2001/XMLSchema#string> <https://rdflib.github.io/.well-known/genid/rdflib/graph-id> .
            """,
            "nquads",
            "graph-id",
        ],
        [
            """
                [
                    {
                        "@id": "_:graph-id",
                        "@graph": [
                            {
                                "@id": "urn:object",
                                "urn:hasPart": {
                                    "@id": "_:internal-bnode-id-1"
                                }
                            },
                            {
                                "@id": "_:internal-bnode-id-1",
                                "urn:value": "..."
                            }
                        ]
                    }
                ]
            """,
            "json-ld",
            """
                <urn:object> <urn:hasPart> <https://rdflib.github.io/.well-known/genid/rdflib/internal-bnode-id-1> <https://rdflib.github.io/.well-known/genid/rdflib/graph-id>  .
                <https://rdflib.github.io/.well-known/genid/rdflib/internal-bnode-id-1> <urn:value> "..." <https://rdflib.github.io/.well-known/genid/rdflib/graph-id> .
            """,
            "nquads",
            "graph-id",
        ],
    ],
)
def test_parse_with_skolemize_quads(
    data: str,
    data_format: str,
    expected_data: str,
    expected_data_format: str,
    anonymous_graph_name,
):
    ds = Dataset(default_union=True)
    ds.parse(data=data, format=data_format, skolemize=True)
    assert len(ds)

    expected_ds = Dataset(default_union=True)
    expected_ds.parse(data=expected_data, format=expected_data_format)
    assert len(expected_ds)

    graph_name = BNode(anonymous_graph_name)
    skolem_graph_name = graph_name.skolemize()

    skolem_graph = ds.graph(skolem_graph_name)
    expected_skolem_graph = expected_ds.graph(skolem_graph_name)
    assert len(skolem_graph)
    assert len(expected_skolem_graph)
    assert isomorphic(skolem_graph, expected_skolem_graph)
    assert isomorphic(skolem_graph.de_skolemize(), expected_skolem_graph.de_skolemize())

    # Note: Datasets must have default_union set to True, otherwise calling
    # de_skolemize returns an empty graph.
    assert isomorphic(ds.de_skolemize(), expected_ds.de_skolemize())

    # TODO: There's no way to roundtrip datasets with skolemization?
