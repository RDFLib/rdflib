from __future__ import annotations

import copy
import pickle
from typing import Any

import pytest

import rdflib
from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef

EX = Namespace("https://example.org/")


@pytest.mark.parametrize(
    ("lexical", "language", "direction"),
    [
        ("hello", "en", "ltr"),
        ("مرحبا", "ar", "rtl"),
    ],
)
def test_directional_literal_construction(
    lexical: str, language: str, direction: str
) -> None:
    literal = Literal(lexical, lang=language, direction=direction)

    assert str(literal) == lexical
    assert literal.language == language
    assert literal.direction == direction
    assert literal.datatype == RDF.dirLangString
    assert literal.value is None
    assert literal.ill_typed is None


def test_direction_is_appended_to_constructor_signature() -> None:
    literal = Literal("hello", "en", None, None, "ltr")

    assert literal.direction == "ltr"
    assert literal.datatype == RDF.dirLangString


def test_existing_positional_constructor_arguments_are_unchanged() -> None:
    literal = Literal("01", None, XSD.integer, False)

    assert str(literal) == "01"
    assert literal.datatype == XSD.integer
    assert literal.direction is None


def test_direction_property_is_read_only() -> None:
    literal = Literal("hello", lang="en", direction="ltr")

    with pytest.raises(AttributeError):
        literal.direction = "rtl"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        del literal.direction


@pytest.mark.parametrize("direction", ["", "LTR", "RTL", "auto", "ltr ", 1])
def test_invalid_direction_is_rejected(direction: Any) -> None:
    with pytest.raises(ValueError, match="must be 'ltr' or 'rtl'"):
        Literal("hello", lang="en", direction=direction)


@pytest.mark.parametrize("language", [None, ""])
def test_direction_requires_non_empty_language(language: str | None) -> None:
    with pytest.raises(ValueError, match="requires a non-empty language tag"):
        Literal("hello", lang=language, direction="ltr")


def test_direction_still_validates_language_tag() -> None:
    with pytest.raises(ValueError, match="not a valid language tag"):
        Literal("hello", lang="en--US", direction="ltr")


def test_explicit_dir_lang_string_is_allowed_with_complete_metadata() -> None:
    literal = Literal(
        "hello",
        lang="en",
        datatype=RDF.dirLangString,
        direction="ltr",
    )

    assert literal.datatype == RDF.dirLangString
    assert literal.direction == "ltr"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"datatype": RDF.dirLangString},
        {"lang": "en", "datatype": RDF.dirLangString},
        {"datatype": RDF.dirLangString, "direction": "ltr"},
    ],
)
def test_dir_lang_string_requires_language_and_direction(
    kwargs: dict[str, Any],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        Literal("hello", **kwargs)


@pytest.mark.parametrize(
    "datatype",
    [RDF.langString, XSD.string, URIRef("https://example.org/datatype")],
)
def test_direction_rejects_conflicting_datatype(datatype: URIRef) -> None:
    with pytest.raises(TypeError):
        Literal("hello", lang="en", datatype=datatype, direction="ltr")


def test_existing_language_and_datatype_restriction_is_unchanged() -> None:
    with pytest.raises(TypeError, match="only have one of lang or datatype"):
        Literal("hello", lang="en", datatype=RDF.langString)


def test_ordinary_language_literal_is_unchanged() -> None:
    literal = Literal("hello", lang="en")

    assert literal.language == "en"
    assert literal.direction is None
    assert literal.datatype is None
    assert literal.value == "hello"
    assert literal.toPython() == "hello"
    assert literal.n3() == '"hello"@en'
    assert repr(literal) == "rdflib.term.Literal('hello', lang='en')"


def test_term_equality_and_hash_include_direction() -> None:
    ltr = Literal("hello", lang="en", direction="ltr")
    same_ltr = Literal("hello", lang="EN", direction="ltr")
    rtl = Literal("hello", lang="en", direction="rtl")
    ordinary = Literal("hello", lang="en")

    assert ltr == same_ltr
    assert hash(ltr) == hash(same_ltr)
    assert ltr != rtl
    assert ltr != ordinary
    assert len({ltr, same_ltr, rtl, ordinary}) == 3
    assert {ltr: "ltr", rtl: "rtl"}[same_ltr] == "ltr"


def test_value_equality_includes_direction() -> None:
    ltr = Literal("hello", lang="en", direction="ltr")
    same_ltr = Literal("hello", lang="EN", direction="ltr")
    rtl = Literal("hello", lang="en", direction="rtl")
    other_lexical = Literal("goodbye", lang="en", direction="ltr")

    assert ltr.eq(same_ltr) is True
    assert ltr.eq(rtl) is False
    assert rtl.eq(ltr) is False
    assert ltr.eq(other_lexical) is False


def test_directional_comparability_includes_language_and_direction() -> None:
    ltr = Literal("hello", lang="en", direction="ltr")

    assert ltr._comparable_to(Literal("hello", lang="EN", direction="ltr"))
    assert not ltr._comparable_to(Literal("hello", lang="en", direction="rtl"))
    assert not ltr._comparable_to(Literal("hello", lang="fr", direction="ltr"))


def test_ordering_uses_direction_after_case_insensitive_language() -> None:
    ltr = Literal("hello", lang="EN", direction="ltr")
    rtl = Literal("hello", lang="en", direction="rtl")

    assert ltr < rtl
    assert rtl > ltr
    assert ltr <= rtl
    assert rtl >= ltr
    assert not rtl < ltr
    assert not ltr > rtl
    assert sorted([rtl, ltr]) == [ltr, rtl]


def test_ordering_equal_directional_literals_is_non_contradictory() -> None:
    lower_case = Literal("hello", lang="en", direction="ltr")
    upper_case = Literal("hello", lang="EN", direction="ltr")

    assert lower_case == upper_case
    assert not lower_case < upper_case
    assert not upper_case < lower_case
    assert not lower_case > upper_case
    assert not upper_case > lower_case
    assert lower_case <= upper_case
    assert lower_case >= upper_case


def test_ordering_is_antisymmetric_for_directional_literals() -> None:
    literals = [
        Literal("a", lang="en", direction="ltr"),
        Literal("a", lang="en", direction="rtl"),
        Literal("b", lang="en", direction="ltr"),
        Literal("a", lang="fr", direction="ltr"),
    ]

    for left in literals:
        for right in literals:
            if left == right:
                continue
            assert (left < right) != (right < left)
            assert (left > right) != (right > left)


def test_copy_construction_preserves_direction() -> None:
    original = Literal("hello", lang="en", direction="ltr")
    copied = Literal(original)

    assert copied == original
    assert copied is not original
    assert copied.language == "en"
    assert copied.direction == "ltr"
    assert copied.datatype == RDF.dirLangString


def test_copy_construction_can_add_or_replace_direction() -> None:
    ordinary = Literal("hello", lang="en")
    ltr = Literal(ordinary, direction="ltr")
    rtl = Literal(ltr, direction="rtl")

    assert ltr.direction == "ltr"
    assert rtl.direction == "rtl"
    assert rtl.language == "en"
    assert rtl.datatype == RDF.dirLangString


def test_copy_construction_rejects_directional_datatype_override() -> None:
    original = Literal("hello", lang="en", direction="ltr")

    with pytest.raises(TypeError, match="must use rdf:dirLangString"):
        Literal(original, datatype=XSD.string)


def test_shallow_and_deep_copy_preserve_direction() -> None:
    original = Literal("مرحبا", lang="ar", direction="rtl")

    for copied in (copy.copy(original), copy.deepcopy(original)):
        assert copied == original
        assert copied.direction == "rtl"
        assert copied.datatype == RDF.dirLangString


def test_normalize_preserves_direction() -> None:
    original = Literal("hello", lang="en", direction="ltr", normalize=False)
    normalized = original.normalize()
    reconstructed = Literal(original, normalize=True)

    assert normalized == original
    assert normalized.direction == "ltr"
    assert reconstructed == original
    assert reconstructed.direction == "ltr"


def test_addition_preserves_direction() -> None:
    original = Literal("hello", lang="en", direction="ltr")
    result = original + " world"

    assert result == Literal("hello world", lang="en", direction="ltr")
    assert result.direction == "ltr"
    assert result.datatype == RDF.dirLangString


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_round_trip_preserves_direction(protocol: int) -> None:
    original = Literal("مرحبا", lang="ar", direction="rtl")
    restored = pickle.loads(pickle.dumps(original, protocol=protocol))

    assert restored == original
    assert restored.language == "ar"
    assert restored.direction == "rtl"
    assert restored.datatype == RDF.dirLangString


def test_old_pickle_constructor_arguments_remain_readable() -> None:
    restored = Literal("hello", "en", None)

    assert restored == Literal("hello", lang="en")
    assert restored.direction is None


def test_old_pickle_state_without_direction_remains_readable() -> None:
    restored = Literal("hello")
    restored.__setstate__((None, {"language": "en", "datatype": None}))

    assert restored.language == "en"
    assert restored.datatype is None
    assert restored.direction is None


def test_pickle_state_contains_direction() -> None:
    literal = Literal("hello", lang="en", direction="ltr")
    _, state = literal.__getstate__()

    assert state["direction"] == "ltr"


def test_repr_round_trip_preserves_direction_without_redundant_datatype() -> None:
    original = Literal("hello", lang="en", direction="ltr")
    representation = repr(original)
    restored = eval(representation, {"rdflib": rdflib})

    assert representation == (
        "rdflib.term.Literal('hello', lang='en', direction='ltr')"
    )
    assert "datatype=" not in representation
    assert restored == original
    assert restored.direction == "ltr"


@pytest.mark.parametrize(
    ("literal", "expected"),
    [
        (Literal("hello", lang="en", direction="ltr"), '"hello"@en--ltr'),
        (Literal("مرحبا", lang="ar", direction="rtl"), '"مرحبا"@ar--rtl'),
        (
            Literal('say "hello"', lang="en", direction="ltr"),
            '"say \\"hello\\""@en--ltr',
        ),
    ],
)
def test_n3_renders_directional_syntax(literal: Literal, expected: str) -> None:
    assert literal.n3() == expected
    assert literal._literal_n3(use_plain=True) == expected


def test_n3_preserves_language_tag_casing() -> None:
    literal = Literal("hello", lang="EN-gb", direction="ltr")

    assert literal.n3() == '"hello"@EN-gb--ltr'


def test_n3_does_not_render_implied_datatype() -> None:
    literal = Literal("hello", lang="en", direction="ltr")

    def unexpected_datatype_qname(_: URIRef) -> str:
        pytest.fail("directional syntax must not render a datatype QName")

    assert literal._literal_n3(qname_callback=unexpected_datatype_qname) == (
        '"hello"@en--ltr'
    )


def test_to_python_preserves_directional_metadata() -> None:
    literal = Literal("hello", lang="en", direction="ltr")

    assert literal.toPython() is literal


def test_graph_keeps_directions_as_distinct_terms() -> None:
    graph = Graph()
    ltr = Literal("hello", lang="en", direction="ltr")
    rtl = Literal("hello", lang="en", direction="rtl")

    graph.add((EX.subject, EX.label, ltr))
    graph.add((EX.subject, EX.label, rtl))

    assert len(graph) == 2
    assert set(graph.objects(EX.subject, EX.label)) == {ltr, rtl}
    assert (EX.subject, EX.label, ltr) in graph
    assert (EX.subject, EX.label, rtl) in graph

    graph.remove((EX.subject, EX.label, ltr))

    assert (EX.subject, EX.label, ltr) not in graph
    assert (EX.subject, EX.label, rtl) in graph
