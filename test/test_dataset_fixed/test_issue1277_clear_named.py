from rdflib import SDO, RDFS, URIRef


def test_issue1277_clear_named(get_conjunctivegraph):
    graph = get_conjunctivegraph

    graph.add(
        (
            SDO.title,
            RDFS.subPropertyOf,
            RDFS.label,
            URIRef("https://example.org"),
        )
    )

    assert list(graph)
