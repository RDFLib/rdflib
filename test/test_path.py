from __future__ import annotations

import logging
from typing import Union

import pytest

from rdflib import RDF, RDFS, Graph, URIRef
from rdflib.namespace import DCAT, DCTERMS
from rdflib.paths import (
    AlternativePath,
    InvPath,
    MulPath,
    NegatedPath,
    OneOrMore,
    Path,
    SequencePath,
    ZeroOrMore,
    ZeroOrOne,
)

g = Graph()
nsm = g.namespace_manager


@pytest.mark.parametrize(
    "path, no_nsm, with_nsm",
    [
        (~RDF.type, f"^<{RDF.type}>", "^rdf:type"),
        (
            RDF.type / RDFS.subClassOf,
            f"<{RDF.type}>/<{RDFS.subClassOf}>",
            "rdf:type/rdfs:subClassOf",
        ),
        (
            RDF.type | RDFS.subClassOf,
            f"<{RDF.type}>|<{RDFS.subClassOf}>",
            "rdf:type|rdfs:subClassOf",
        ),
        (-RDF.type, f"!(<{RDF.type}>)", "!(rdf:type)"),
        # type errors: Unsupported operand types for * ("URIRef" and "str")
        # note on type errors: The operator is defined but in an odd place
        (
            RDFS.subClassOf * ZeroOrMore,  # type: ignore[operator]
            f"<{RDFS.subClassOf}>*",
            "rdfs:subClassOf*",
        ),
        (
            RDFS.subClassOf * OneOrMore,  # type: ignore[operator]
            f"<{RDFS.subClassOf}>+",
            "rdfs:subClassOf+",
        ),
        (
            RDFS.subClassOf * ZeroOrOne,  # type: ignore[operator]
            f"<{RDFS.subClassOf}>?",
            "rdfs:subClassOf?",
        ),
        (
            RDF.type / MulPath(RDFS.subClassOf, "*"),
            f"<{RDF.type}>/<{RDFS.subClassOf}>*",
            "rdf:type/rdfs:subClassOf*",
        ),
        (
            RDF.type / ((SequencePath(RDFS.subClassOf)) * "*"),
            f"<{RDF.type}>/<{RDFS.subClassOf}>*",
            "rdf:type/rdfs:subClassOf*",
        ),
        (
            RDF.type / RDFS.subClassOf * "*",
            f"(<{RDF.type}>/<{RDFS.subClassOf}>)*",
            "(rdf:type/rdfs:subClassOf)*",
        ),
        (
            -(RDF.type | RDFS.subClassOf),
            f"!(<{RDF.type}>|<{RDFS.subClassOf}>)",
            "!(rdf:type|rdfs:subClassOf)",
        ),
        (
            -(RDF.type | ((SequencePath(RDFS.subClassOf)) * "*")),
            f"!(<{RDF.type}>|<{RDFS.subClassOf}>*)",
            "!(rdf:type|rdfs:subClassOf*)",
        ),
        (
            SequencePath(RDFS.subClassOf),
            f"<{RDFS.subClassOf}>",
            "rdfs:subClassOf",
        ),
        (
            AlternativePath(RDFS.subClassOf),
            f"<{RDFS.subClassOf}>",
            "rdfs:subClassOf",
        ),
    ],
)
def test_paths_n3(
    path: Union[InvPath, SequencePath, AlternativePath, MulPath, NegatedPath],
    no_nsm: str,
    with_nsm: str,
) -> None:
    logging.debug("path = %s", path)
    assert path.n3() == no_nsm
    assert path.n3(nsm) == with_nsm


def test_mulpath_n3():
    uri = "http://example.com/foo"
    n3 = (URIRef(uri) * ZeroOrMore).n3()
    assert n3 == "<" + uri + ">*"


@pytest.mark.parametrize(
    ["lhs", "rhs"],
    [
        (DCTERMS.temporal / DCAT.endDate, DCTERMS.temporal / DCAT.endDate),
        (SequencePath(DCTERMS.temporal, DCAT.endDate), DCTERMS.temporal / DCAT.endDate),
    ],
)
def test_eq(lhs: Path, rhs: Path) -> None:
    logging.debug("lhs = %s/%r, rhs = %s/%r", type(lhs), lhs, type(rhs), rhs)
    assert lhs == rhs


@pytest.mark.parametrize(
    ["lhs", "rhs"],
    [
        (DCTERMS.temporal / DCAT.endDate, DCTERMS.temporal / DCAT.endDate),
        (SequencePath(DCTERMS.temporal, DCAT.endDate), DCTERMS.temporal / DCAT.endDate),
    ],
)
def test_hash(lhs: Path, rhs: Path) -> None:
    logging.debug("lhs = %s/%r, rhs = %s/%r", type(lhs), lhs, type(rhs), rhs)
    assert hash(lhs) == hash(rhs)


@pytest.mark.parametrize(
    ["insert_path", "check_path"],
    [
        (DCTERMS.temporal / DCAT.endDate, DCTERMS.temporal / DCAT.endDate),
        (SequencePath(DCTERMS.temporal, DCAT.endDate), DCTERMS.temporal / DCAT.endDate),
    ],
)
def test_dict_key(insert_path: Path, check_path: Path) -> None:
    d = {insert_path: "foo"}
    assert d[check_path] == "foo"
