import pytest
import pyparsing.exceptions
from rdflib import ConjunctiveGraph, SDO, RDFS, URIRef


def test_issue1277_clear_named_parse_error():
    graph = ConjunctiveGraph()

    graph.add(
        (
            SDO.title,
            RDFS.subPropertyOf,
            RDFS.label,
            URIRef("https://example.org"),
        )
    )

    assert list(graph)

    # Fails:
    #     raise ParseException(instring, loc, self.errmsg, self)
    #     E   pyparsing.ParseException: Expected end of text, found 'C'
    #         (at char 0), (line:1, col:1)
    with pytest.raises(pyparsing.exceptions.ParseException):
        graph.update(
            "CLEAR GRAPH ?g",
            initBindings={
                "g": URIRef("https://example.org"),
            },
        )

    with pytest.raises(AssertionError):
        assert not list(graph)
