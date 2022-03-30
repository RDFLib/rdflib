import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.absolute()))
from rdflib import Graph
from rdflib.namespace import NAMESPACE_PREFIXES_CORE, NAMESPACE_PREFIXES_RDFLIB
from rdflib.namespace import OWL


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


def test_rebinding():
    g = Graph()  # 'core' bind_namespaces (default)
    print()
    # 'owl' should be bound
    assert "owl" in [x for x, y in list(g.namespaces())]

    # replace 'owl' with 'sowa'
    # 'sowa' should be bound
    # 'owl' should not be bound
    g.bind("sowa", OWL, replace=True)

    assert "sowa" in [x for x, y in list(g.namespaces())]
    assert "owl" not in [x for x, y in list(g.namespaces())]



test_rebinding()
