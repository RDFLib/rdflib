import sys
from pathlib import Path

from rdflib.term import URIRef

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from rdflib import Graph
from rdflib.namespace import (
    NAMESPACE_PREFIXES_CORE,
    NAMESPACE_PREFIXES_RDFLIB,
    OWL,
    RDFS,
)


def test_core_prefixes_bound():
    # we should have RDF, RDFS, OWL, XSD & XML bound
    g = Graph()

    # prefixes in Graph
    assert len(list(g.namespaces())) == len(NAMESPACE_PREFIXES_CORE)
    pre = sorted([x[0] for x in list(g.namespaces())])
    assert pre == ["owl", "rdf", "rdfs", "xml", "xsd"]


def test_rdflib_prefixes_bound():
    g = Graph(bind_namespaces="rdflib")

    # the core 5 + the extra 23 namespaces with prefixes
    assert len(list(g.namespaces())) == len(NAMESPACE_PREFIXES_CORE) + len(
        list(NAMESPACE_PREFIXES_RDFLIB)
    )


def test_cc_prefixes_bound():
    pass


def test_rebinding():
    g = Graph()  # 'core' bind_namespaces (default)
    print()
    # 'owl' should be bound
    assert "owl" in [x for x, y in list(g.namespaces())]
    assert "rdfs" in [x for x, y in list(g.namespaces())]

    # replace 'owl' with 'sowa'
    # 'sowa' should be bound
    # 'owl' should not be bound
    g.bind("sowa", OWL, override=True)

    assert "sowa" in [x for x, y in list(g.namespaces())]
    assert "owl" not in [x for x, y in list(g.namespaces())]

    # try bind srda with override set to False
    g.bind("srda", RDFS, override=False)

    # binding should fail because RDFS is already bound to rdfs prefix
    assert "srda" not in [x for x, y in list(g.namespaces())]
    assert "rdfs" in [x for x, y in list(g.namespaces())]


def test_replace():
    g = Graph()  # 'core' bind_namespaces (default)

    assert ("rdfs", URIRef(RDFS)) in list(g.namespaces())

    g.bind("rdfs", "http://example.com", replace=False)

    assert ("rdfs", URIRef("http://example.com")) not in list(
        g.namespace_manager.namespaces()
    )
    assert ("rdfs1", URIRef("http://example.com")) in list(
        g.namespace_manager.namespaces()
    )

    g.bind("rdfs", "http://example.com", replace=True)

    assert ("rdfs", URIRef("http://example.com")) in list(
        g.namespace_manager.namespaces()
    )
