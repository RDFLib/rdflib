import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from rdflib import Graph
from rdflib.namespace import NAMESPACE_PREFIXES_CORE, NAMESPACE_PREFIXES_RDFLIB


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
    assert len(list(g.namespaces())) == \
           len(NAMESPACE_PREFIXES_CORE) + len(list(NAMESPACE_PREFIXES_RDFLIB))

def test_cc_prefixes_bound():
    pass


def test_no_prefixes_bound():
    g = Graph(bind_namespaces=None)
    assert len(list(g.namespaces())) == 0


def test_invalid_prefixes_bound():
    with pytest.raises(ValueError):
        g = Graph(bind_namespaces="INVALID")
        list(g.namespaces())
