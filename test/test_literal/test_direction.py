"""Tests for the RDF 1.2 Literal direction feature (rdf:dirLangString)."""

from __future__ import annotations

import pickle

import pytest

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

EX = Namespace("http://example.org/")


# --- Construction ---


def test_construction_ltr() -> None:
    """Literal can be constructed with direction='ltr'."""
    lit = Literal("hello", lang="en", direction="ltr")
    assert str(lit) == "hello"
    assert lit.language == "en"
    assert lit.direction == "ltr"


def test_construction_rtl() -> None:
    """Literal can be constructed with direction='rtl'."""
    lit = Literal("مرحبا", lang="ar", direction="rtl")
    assert str(lit) == "مرحبا"
    assert lit.language == "ar"
    assert lit.direction == "rtl"


def test_construction_no_direction() -> None:
    """Literal without direction has direction=None."""
    lit = Literal("hello", lang="en")
    assert lit.direction is None


# --- Validation ---


def test_direction_requires_lang() -> None:
    """Direction without lang raises ValueError."""
    with pytest.raises(ValueError, match="must also have a language tag"):
        Literal("hello", direction="ltr")


def test_direction_requires_lang_even_with_datatype() -> None:
    """Direction without lang raises ValueError even if datatype is given."""
    with pytest.raises(ValueError, match="must also have a language tag"):
        Literal("hello", datatype=RDF.dirLangString, direction="ltr")


def test_direction_must_be_ltr_or_rtl() -> None:
    """Direction must be 'ltr' or 'rtl'; other values raise ValueError."""
    with pytest.raises(ValueError, match="must be 'ltr' or 'rtl'"):
        Literal("hello", lang="en", direction="up")


def test_direction_must_be_ltr_or_rtl_empty_string() -> None:
    """Empty string direction raises ValueError."""
    with pytest.raises(ValueError, match="must be 'ltr' or 'rtl'"):
        Literal("hello", lang="en", direction="")


def test_direction_must_be_ltr_or_rtl_case_sensitive() -> None:
    """Direction is case-sensitive; 'LTR' is invalid."""
    with pytest.raises(ValueError, match="must be 'ltr' or 'rtl'"):
        Literal("hello", lang="en", direction="LTR")


# --- Datatype auto-setting ---


def test_datatype_auto_set_to_dir_lang_string() -> None:
    """Datatype is auto-set to rdf:dirLangString when direction is provided."""
    lit = Literal("hello", lang="en", direction="ltr")
    assert lit.datatype == RDF.dirLangString


def test_datatype_without_direction_is_none() -> None:
    """Without direction, a lang-tagged literal has datatype None (rdflib convention)."""
    lit = Literal("hello", lang="en")
    assert lit.datatype is None


# --- Equality ---


def test_equality_same_direction() -> None:
    """Literals with same text, lang, and direction are equal."""
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="en", direction="ltr")
    assert l1 == l2


def test_equality_different_direction() -> None:
    """Literals with different direction are not equal."""
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="en", direction="rtl")
    assert l1 != l2


def test_equality_direction_vs_no_direction() -> None:
    """Literal with direction is not equal to one without direction."""
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="en")
    assert l1 != l2


def test_equality_no_direction_vs_direction() -> None:
    """Literal without direction is not equal to one with direction (symmetric)."""
    l1 = Literal("hello", lang="en")
    l2 = Literal("hello", lang="en", direction="rtl")
    assert l1 != l2


def test_equality_same_text_different_lang_same_direction() -> None:
    """Same text and direction but different lang are not equal."""
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="fr", direction="ltr")
    assert l1 != l2


# --- Hashing ---


def test_hash_consistent_with_equality() -> None:
    """Equal literals with direction have the same hash."""
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="en", direction="ltr")
    assert hash(l1) == hash(l2)


def test_hash_different_direction() -> None:
    """Literals with different direction (likely) have different hashes."""
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="en", direction="rtl")
    # Not strictly guaranteed, but extremely likely
    assert hash(l1) != hash(l2)


def test_hash_direction_vs_no_direction() -> None:
    """Literal with direction has different hash from one without."""
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="en")
    # Not strictly guaranteed, but extremely likely
    assert hash(l1) != hash(l2)


def test_hash_usable_in_set() -> None:
    """Literals with direction can be used in sets with proper deduplication."""
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="en", direction="ltr")
    l3 = Literal("hello", lang="en", direction="rtl")
    l4 = Literal("hello", lang="en")
    s = {l1, l2, l3, l4}
    assert len(s) == 3


def test_hash_usable_as_dict_key() -> None:
    """Literals with direction work as dict keys."""
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="en", direction="ltr")
    d = {l1: "value"}
    assert d[l2] == "value"


# --- n3() output ---


def test_n3_ltr() -> None:
    """n3() outputs 'text'@lang--ltr format."""
    lit = Literal("hello", lang="en", direction="ltr")
    assert lit.n3() == '"hello"@en--ltr'


def test_n3_rtl() -> None:
    """n3() outputs 'text'@lang--rtl format."""
    lit = Literal("مرحبا", lang="ar", direction="rtl")
    assert lit.n3() == '"مرحبا"@ar--rtl'


def test_n3_without_direction() -> None:
    """n3() without direction does not include --dir suffix."""
    lit = Literal("hello", lang="en")
    assert lit.n3() == '"hello"@en'
    assert "--" not in lit.n3()


# --- repr() ---


def test_repr_shows_direction() -> None:
    """repr() includes direction when present."""
    lit = Literal("hello", lang="en", direction="ltr")
    r = repr(lit)
    assert "direction=" in r
    assert "'ltr'" in r


def test_repr_no_direction() -> None:
    """repr() does not show direction when not present."""
    lit = Literal("hello", lang="en")
    r = repr(lit)
    assert "direction" not in r


# --- Use in a Graph ---


def test_literal_with_direction_in_graph() -> None:
    """Literal with direction can be added to and retrieved from a Graph."""
    g = Graph()
    lit = Literal("hello", lang="en", direction="ltr")
    g.add((EX.subject, EX.label, lit))
    assert len(g) == 1

    triples = list(g.triples((EX.subject, EX.label, None)))
    assert len(triples) == 1
    retrieved = triples[0][2]
    assert isinstance(retrieved, Literal)
    assert retrieved.direction == "ltr"
    assert retrieved == lit


def test_different_directions_are_distinct_in_graph() -> None:
    """Literals with different directions are distinct triples in a Graph."""
    g = Graph()
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="en", direction="rtl")
    l3 = Literal("hello", lang="en")
    g.add((EX.subject, EX.label, l1))
    g.add((EX.subject, EX.label, l2))
    g.add((EX.subject, EX.label, l3))
    assert len(g) == 3


def test_same_direction_deduplicates_in_graph() -> None:
    """Adding the same literal with direction twice doesn't duplicate."""
    g = Graph()
    l1 = Literal("hello", lang="en", direction="ltr")
    l2 = Literal("hello", lang="en", direction="ltr")
    g.add((EX.subject, EX.label, l1))
    g.add((EX.subject, EX.label, l2))
    assert len(g) == 1


# --- Explicit datatype with lang (RDF 1.2 spec compliance) ---


def test_explicit_dir_lang_string_datatype_with_lang() -> None:
    """Explicit datatype=rdf:dirLangString with lang and direction is allowed."""
    lit = Literal("hello", lang="en", datatype=RDF.dirLangString, direction="ltr")
    assert lit.language == "en"
    assert lit.direction == "ltr"
    assert lit.datatype == RDF.dirLangString


def test_explicit_lang_string_datatype_with_lang() -> None:
    """Explicit datatype=rdf:langString with lang is allowed (no TypeError)."""
    lit = Literal("hello", lang="en", datatype=RDF.langString)
    assert lit.language == "en"
    assert lit.datatype == RDF.langString


def test_explicit_non_lang_datatype_with_lang_raises() -> None:
    """Explicit non-lang datatype with lang raises TypeError."""
    with pytest.raises(TypeError, match="can only have one of lang or datatype"):
        Literal("hello", lang="en", datatype=URIRef("http://example.org/mytype"))


# --- Pickling ---


def test_pickle_roundtrip_ltr() -> None:
    """Literal with direction='ltr' survives pickle/unpickle."""
    lit = Literal("hello", lang="en", direction="ltr")
    pickled = pickle.dumps(lit)
    unpickled = pickle.loads(pickled)
    assert unpickled == lit
    assert unpickled.language == "en"
    assert unpickled.direction == "ltr"
    assert unpickled.datatype == RDF.dirLangString


def test_pickle_roundtrip_rtl() -> None:
    """Literal with direction='rtl' survives pickle/unpickle."""
    lit = Literal("مرحبا", lang="ar", direction="rtl")
    pickled = pickle.dumps(lit)
    unpickled = pickle.loads(pickled)
    assert unpickled == lit
    assert unpickled.language == "ar"
    assert unpickled.direction == "rtl"
    assert unpickled.datatype == RDF.dirLangString


def test_pickle_roundtrip_no_direction() -> None:
    """Literal without direction still pickles correctly (no regression)."""
    lit = Literal("hello", lang="en")
    pickled = pickle.dumps(lit)
    unpickled = pickle.loads(pickled)
    assert unpickled == lit
    assert unpickled.language == "en"
    assert unpickled.direction is None


# --- Copy construction ---


def test_copy_construction_preserves_direction() -> None:
    """Constructing a Literal from another directional Literal preserves direction."""
    original = Literal("hello", lang="en", direction="ltr")
    copy = Literal(original)
    assert copy == original
    assert copy.language == "en"
    assert copy.direction == "ltr"
    assert copy.datatype == RDF.dirLangString


def test_copy_construction_preserves_rtl_direction() -> None:
    """Constructing a Literal from an RTL directional Literal preserves direction."""
    original = Literal("مرحبا", lang="ar", direction="rtl")
    copy = Literal(original)
    assert copy == original
    assert copy.language == "ar"
    assert copy.direction == "rtl"


def test_copy_construction_no_direction_no_regression() -> None:
    """Constructing a Literal from a lang-tagged Literal without direction works."""
    original = Literal("hello", lang="en")
    copy = Literal(original)
    assert copy == original
    assert copy.language == "en"
    assert copy.direction is None
