import pytest

from rdflib import RDF, RDFS, Graph
from rdflib.paths import OneOrMore, ZeroOrMore, ZeroOrOne

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
        (RDFS.subClassOf * ZeroOrMore, f"<{RDFS.subClassOf}>*", "rdfs:subClassOf*"),
        (RDFS.subClassOf * OneOrMore, f"<{RDFS.subClassOf}>+", "rdfs:subClassOf+"),
        (RDFS.subClassOf * ZeroOrOne, f"<{RDFS.subClassOf}>?", "rdfs:subClassOf?"),
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
def test_paths_n3(path, no_nsm, with_nsm):
    assert path.n3() == no_nsm
    assert path.n3(nsm) == with_nsm
