from io import BytesIO

import pytest

from rdflib import RDF, Graph, Literal, Namespace, Variable, plugin
from rdflib.exceptions import Error
from rdflib.query import Result, ResultSerializer

EX = Namespace("https://example.org/")
ERROR_PATTERN = (
    "Directional language-tagged Literal requires an RDF 1.2-capable serializer"
)


def _result(literal: Literal, via_query: bool) -> Result:
    if via_query:
        graph = Graph()
        graph.add((EX.subject, EX.label, literal))
        return graph.query(
            "SELECT ?label WHERE { ?s <https://example.org/label> ?label }"
        )

    result = Result("SELECT")
    result.vars = [Variable("label")]
    result.bindings = [{Variable("label"): literal}]
    return result


@pytest.mark.parametrize("format_name", ["xml", "json", "csv"])
@pytest.mark.parametrize("direction", ["ltr", "rtl"])
@pytest.mark.parametrize("via_query", [False, True], ids=["direct", "select"])
def test_result_serializers_reject_directional_literals(
    format_name: str, direction: str, via_query: bool
) -> None:
    result = _result(Literal("hello", lang="en", direction=direction), via_query)

    with pytest.raises(Error, match=ERROR_PATTERN):
        if via_query:
            result.serialize(format=format_name)
        else:
            serializer = plugin.get(format_name, ResultSerializer)(result)
            serializer.serialize(BytesIO(), encoding="utf-8")


@pytest.mark.parametrize("format_name", ["xml", "json"])
@pytest.mark.parametrize("via_query", [False, True], ids=["direct", "select"])
@pytest.mark.parametrize(
    "literal",
    [Literal("hello", lang="en"), Literal("hello", datatype=RDF.dirLangString)],
    ids=["language", "opaque-datatype"],
)
def test_result_serializers_preserve_non_directional_literals(
    format_name: str, via_query: bool, literal: Literal
) -> None:
    result = _result(literal, via_query)
    serialized = result.serialize(format=format_name)

    assert serialized is not None
    restored = Result.parse(BytesIO(serialized), format=format_name)
    assert restored.bindings == [{Variable("label"): literal}]


def test_csv_preserves_existing_lexical_export() -> None:
    result = _result(Literal("hello", lang="en"), via_query=False)

    assert result.serialize(format="csv") == b"label\r\nhello\r\n"


@pytest.mark.parametrize("direction", ["ltr", "rtl"])
def test_text_results_display_direction(direction: str) -> None:
    result = _result(Literal("hello", lang="en", direction=direction), via_query=True)
    serialized = result.serialize(format="txt")

    assert serialized is not None
    assert f'"hello"@en--{direction}'.encode() in serialized
