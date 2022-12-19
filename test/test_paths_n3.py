import logging
from typing import Union

import pytest

from rdflib import RDF, RDFS, Graph
from rdflib.paths import (
    AlternativePath,
    InvPath,
    MulPath,
    NegatedPath,
    OneOrMore,
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
            RDF.type / RDFS.subClassOf * "*",
            f"<{RDF.type}>/<{RDFS.subClassOf}>*",
            "rdf:type/rdfs:subClassOf*",
        ),
        (
            -(RDF.type | RDFS.subClassOf),
            f"!(<{RDF.type}>|<{RDFS.subClassOf}>)",
            "!(rdf:type|rdfs:subClassOf)",
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
