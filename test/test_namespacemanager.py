import logging
import sys
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Dict, Optional, Set, Tuple, Type, Union

import pytest

from rdflib.graph import Dataset
from rdflib.term import URIRef

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from rdflib import Graph
from rdflib.namespace import (
    _NAMESPACE_PREFIXES_CORE,
    _NAMESPACE_PREFIXES_RDFLIB,
    OWL,
    RDFS,
    NamespaceManager,
)


def test_core_prefixes_bound():
    # we should have RDF, RDFS, OWL, XSD & XML bound
    g = Graph()

    # prefixes in Graph
    assert len(list(g.namespaces())) == len(_NAMESPACE_PREFIXES_CORE)
    pre = sorted([x[0] for x in list(g.namespaces())])
    assert pre == ["owl", "rdf", "rdfs", "xml", "xsd"]


def test_rdflib_prefixes_bound():
    g = Graph(bind_namespaces="rdflib")

    # the core 5 + the extra 23 namespaces with prefixes
    assert len(list(g.namespaces())) == len(_NAMESPACE_PREFIXES_CORE) + len(
        list(_NAMESPACE_PREFIXES_RDFLIB)
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


def test_invalid_selector() -> None:
    graph = Graph()
    with pytest.raises(ValueError):
        NamespaceManager(graph, bind_namespaces="invalid")  # type: ignore[arg-type]


NamespaceSet = Set[Tuple[str, URIRef]]


def check_graph_ns(
    graph: Graph,
    expected_nsmap: Dict[str, Any],
    check_namespaces: Optional[NamespaceSet] = None,
) -> None:
    expected_namespaces = {
        (prefix, URIRef(f"{uri}")) for prefix, uri in expected_nsmap.items()
    }
    logging.debug("expected_namespaces = %s", expected_namespaces)
    graph_namespaces = {*graph.namespaces()}
    assert expected_namespaces == graph_namespaces
    nman_namespaces = {*graph.namespace_manager.namespaces()}
    assert expected_namespaces == nman_namespaces
    if check_namespaces is not None:
        assert expected_namespaces == check_namespaces
        logging.debug("check_namespaces = %s", check_namespaces)


@pytest.mark.parametrize(
    ["selector", "expected_result"],
    [
        (None, ValueError),
        ("invalid", ValueError),
        ("core", _NAMESPACE_PREFIXES_CORE),
        ("rdflib", {**_NAMESPACE_PREFIXES_CORE, **_NAMESPACE_PREFIXES_RDFLIB}),
        ("none", {}),
    ],
)
def test_graph_bind_namespaces(
    selector: Any,
    expected_result: Union[Dict[str, Any], Type[Exception]],
) -> None:
    namespaces: Optional[NamespaceSet] = None
    with ExitStack() as xstack:
        if not isinstance(expected_result, dict):
            xstack.enter_context(pytest.raises(expected_result))
        graph = Graph(bind_namespaces=selector)
        namespaces = {*graph.namespaces()}
    if isinstance(expected_result, dict):
        assert namespaces is not None
        check_graph_ns(graph, expected_result, namespaces)
    else:
        assert namespaces is None


@pytest.mark.parametrize(
    ["selector", "expected_result"],
    [
        (None, ValueError),
        ("invalid", ValueError),
        ("core", _NAMESPACE_PREFIXES_CORE),
        ("rdflib", {**_NAMESPACE_PREFIXES_CORE, **_NAMESPACE_PREFIXES_RDFLIB}),
        ("none", {}),
    ],
)
def test_nman_bind_namespaces(
    selector: Any,
    expected_result: Union[Dict[str, Any], Type[Exception]],
) -> None:
    with ExitStack() as xstack:
        if not isinstance(expected_result, dict):
            xstack.enter_context(pytest.raises(expected_result))
        graph = Dataset()
        graph.namespace_manager = NamespaceManager(graph, selector)
    if isinstance(expected_result, dict):
        check_graph_ns(graph, expected_result)


def test_compute_qname_no_generate() -> None:
    g = Graph()  # 'core' bind_namespaces (default)
    with pytest.raises(KeyError):
        g.namespace_manager.compute_qname_strict(
            "https://example.org/unbound/test", generate=False
        )
