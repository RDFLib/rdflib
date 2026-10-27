import pytest

from rdflib import RDF, Graph, Literal, Namespace

EX = Namespace("https://example.org/")


@pytest.mark.parametrize(
    ("format_name", "data"),
    [
        (
            "turtle",
            "<https://example.org/s> <https://example.org/label> "
            '"x"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#dirLangString> .',
        ),
        (
            "nt",
            "<https://example.org/s> <https://example.org/label> "
            '"x"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#dirLangString> .',
        ),
        (
            "xml",
            '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
            'xmlns:ex="https://example.org/">'
            '<rdf:Description rdf:about="https://example.org/s">'
            '<ex:label rdf:datatype="http://www.w3.org/1999/02/22-rdf-syntax-ns#dirLangString">'
            "x</ex:label></rdf:Description></rdf:RDF>",
        ),
        (
            "json-ld",
            '[{"@id": "https://example.org/s", "https://example.org/label": '
            '[{"@value": "x", "@type": '
            '"http://www.w3.org/1999/02/22-rdf-syntax-ns#dirLangString"}]}]',
        ),
    ],
)
def test_rdf11_opaque_dir_lang_string_round_trip(format_name: str, data: str) -> None:
    graph = Graph().parse(data=data, format=format_name)
    literal = graph.value(EX.s, EX.label)

    assert isinstance(literal, Literal)
    assert str(literal) == "x"
    assert literal.datatype == RDF.dirLangString
    assert literal.language is None
    assert literal.direction is None
    assert literal.value is None
    assert literal.ill_typed is None

    restored = Graph().parse(
        data=graph.serialize(format=format_name), format=format_name
    )
    assert set(restored) == set(graph)
