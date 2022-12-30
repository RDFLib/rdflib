from rdflib import RDFS, Graph, Literal, URIRef

_graph_with_label = Graph()
_graph_with_label.add(
    (URIRef("http://example.com/something"), RDFS.label, Literal("Some label"))
)


def test_select_star_sub_select():
    """
    This tests the fix for a bug which returned no results when using `SELECT *` in the
      parent of a sub-select using `SELECT *`.
    """
    results = list(
        _graph_with_label.query(
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
    assert results[0].asdict() == {"label": Literal("Some label")}


def test_select_star_multiple_sub_select_star():
    """
    Ensure that we can define select * in multiple sub-selects and still select * (all)
      of the variables out in the parent.
    """
    results = list(
        _graph_with_label.query(
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

                {
                    SELECT *
                    WHERE {
                        [] rdfs:label ?label2.
                    }
                }
            }
            """
        )
    )

    assert len(results) == 1
    assert results[0].asdict() == {
        "label": Literal("Some label"),
        "label2": Literal("Some label"),
    }


def test_select_star_multiple_sub_select_mixed_projections():
    """
    Ensure that we can define select * from one sub-select and define
    projected variables on another sub-select and still select * out of the parent.
    """
    results = list(
        _graph_with_label.query(
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

                {
                    SELECT ?label2
                    WHERE {
                        [] rdfs:label ?label2.
                    }
                }
            }
            """
        )
    )

    assert len(results) == 1
    assert results[0].asdict() == {
        "label": Literal("Some label"),
        "label2": Literal("Some label"),
    }


def test_select_star_multiple_sub_select_defined_projections():
    """
    Ensure that we can define select * from multiple sub-selects which define
    projected variables.
    """
    results = list(
        _graph_with_label.query(
            """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT *
            WHERE {
                {
                    SELECT ?label
                    WHERE {
                        [] rdfs:label ?label.
                    }
                }

                {
                    SELECT ?label2
                    WHERE {
                        [] rdfs:label ?label2.
                    }
                }
            }
            """
        )
    )

    assert len(results) == 1
    assert results[0].asdict() == {
        "label": Literal("Some label"),
        "label2": Literal("Some label"),
    }
