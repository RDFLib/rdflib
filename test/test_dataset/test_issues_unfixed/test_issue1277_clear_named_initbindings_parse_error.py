import pytest
from pyparsing import exceptions as pyparsingexceptions
from rdflib import Dataset, SDO, RDFS, URIRef


@pytest.mark.xfail(reason="pyparsing.ParseException: Expected end of text, found 'C'")
def test_issue1277_clear_named_parse_error():
    graph = Dataset()

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
    graph.update(
        "CLEAR GRAPH ?g",
        initBindings={
            "g": URIRef("https://example.org"),
        },
    )

    assert not list(graph)
