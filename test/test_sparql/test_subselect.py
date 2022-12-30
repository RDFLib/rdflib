from rdflib import RDFS, Graph, Literal, URIRef


def test_select_star_sub_select():
    """
    This tests the fix for a bug which returned no results when using `SELECT *` in the
      parent of a sub-select using `SELECT *`.
    """
    graph = Graph()
    graph.add(
        (URIRef("http://example.com/something"), RDFS.label, Literal("Some label"))
    )

    results = list(
        graph.query(
            """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT *
            WHERE {
                {
                    SELECT *
                    WHERE {
                        [] rdfs:label ?label.
                    }
                }
            }
            """
        )
    )

    assert len(results) == 1
    assert results[0][0] == Literal("Some label")
