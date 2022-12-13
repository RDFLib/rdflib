from __future__ import annotations

import logging
import re
import sys
from contextlib import ExitStack
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Set, Tuple, Type, Union

import pytest

from rdflib.graph import Dataset
from rdflib.term import URIRef

if TYPE_CHECKING:
    from rdflib._type_checking import _NamespaceSetString


sys.path.append(str(Path(__file__).parent.parent.absolute()))
from rdflib import Graph
from rdflib.namespace import (
    _NAMESPACE_PREFIXES_CORE,
    _NAMESPACE_PREFIXES_RDFLIB,
    OWL,
    RDFS,
    Namespace,
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


@pytest.mark.parametrize(
    [
        "uri",
        "generate",
        "bind_namespaces",
        "manager_prefixes",
        "graph_prefixes",
        "store_prefixes",
        "expected_result",
    ],
    [
        (
            "http://example.org/here#",
            True,
            "none",
            {"here": Namespace("http://example.org/here#")},
            None,
            None,
            ("here", URIRef("http://example.org/here#"), ""),
        ),
        (
            "http://example.org/here#",
            True,
            "none",
            None,
            {"here": Namespace("http://example.org/here#")},
            None,
            ("here", URIRef("http://example.org/here#"), ""),
        ),
        (
            "http://example.org/here#",
            True,
            "none",
            None,
            None,
            {"here": Namespace("http://example.org/here#")},
            ("here", URIRef("http://example.org/here#"), ""),
        ),
        (
            "http://example.org/here#",
            True,
            "none",
            None,
            None,
            None,
            ValueError("Can't split"),
        ),
    ],
)
def test_compute_qname(
    uri: str,
    generate: bool,
    bind_namespaces: _NamespaceSetString,
    manager_prefixes: Optional[Mapping[str, Namespace]],
    graph_prefixes: Optional[Mapping[str, Namespace]],
    store_prefixes: Optional[Mapping[str, Namespace]],
    expected_result: Union[Tuple[str, URIRef, str], Type[Exception], Exception],
) -> None:
    """
    :param uri: argument to compute_qname()
    :param generate: argument to compute_qname()
    :param bind_namespaces: argument to Graph()

    :param manager_prefixes: additional namespaces to bind on NamespaceManager.
    :param graph_prefixes: additional namespaces to bind on Graph.
    :param store_prefixes: additional namespaces to bind on Store.

    :param expected_result: Expected result tuple or exception.
    """
    graph = Graph(bind_namespaces=bind_namespaces)
    if graph_prefixes is not None:
        for prefix, ns in graph_prefixes.items():
            graph.bind(prefix, ns)

    store = graph.store
    if store_prefixes is not None:
        for prefix, ns in store_prefixes.items():
            store.bind(prefix, URIRef(f"{ns}"))

    nm = graph.namespace_manager
    if manager_prefixes is not None:
        for prefix, ns in manager_prefixes.items():
            nm.bind(prefix, ns)

    def check() -> None:
        catcher: Optional[pytest.ExceptionInfo[Exception]] = None
        with ExitStack() as xstack:
            if isinstance(expected_result, type) and issubclass(
                expected_result, Exception
            ):
                catcher = xstack.enter_context(pytest.raises(expected_result))
            if isinstance(expected_result, Exception):
                catcher = xstack.enter_context(pytest.raises(type(expected_result)))
            actual_result = nm.compute_qname(uri, generate)
            logging.debug("actual_result = %s", actual_result)
        if catcher is not None:
            assert catcher is not None
            assert catcher.value is not None
            if isinstance(expected_result, Exception):
                assert re.match(expected_result.args[0], f"{catcher.value}")
        else:
            assert isinstance(expected_result, tuple)
            assert isinstance(actual_result, tuple)
            assert actual_result == expected_result

    check()
    # Run a second time to check caching
    check()


@pytest.mark.parametrize(
    ["uri", "generate", "bind_namespaces", "additional_prefixes", "expected_result"],
    [
        (
            "http://example.org/here#",
            True,
            "none",
            {"here": Namespace("http://example.org/here#")},
            ValueError(".*there is no valid way to shorten"),
        ),
        (
            "http://example.org/here#",
            True,
            "none",
            None,
            ValueError("Can't split"),
        ),
    ],
)
def test_compute_qname_strict(
    uri: str,
    generate: bool,
    bind_namespaces: _NamespaceSetString,
    additional_prefixes: Optional[Mapping[str, Namespace]],
    expected_result: Union[Tuple[str, URIRef, str], Type[Exception], Exception],
) -> None:
    graph = Graph(bind_namespaces=bind_namespaces)
    nm = graph.namespace_manager

    if additional_prefixes is not None:
        for prefix, ns in additional_prefixes.items():
            nm.bind(prefix, ns)

    def check() -> None:
        catcher: Optional[pytest.ExceptionInfo[Exception]] = None
        with ExitStack() as xstack:
            if isinstance(expected_result, type) and issubclass(
                expected_result, Exception
            ):
                catcher = xstack.enter_context(pytest.raises(expected_result))
            if isinstance(expected_result, Exception):
                catcher = xstack.enter_context(pytest.raises(type(expected_result)))
            actual_result = nm.compute_qname_strict(uri, generate)
            logging.debug("actual_result = %s", actual_result)
        if catcher is not None:
            assert catcher is not None
            assert catcher.value is not None
            if isinstance(expected_result, Exception):
                assert re.match(expected_result.args[0], f"{catcher.value}")
        else:
            assert isinstance(expected_result, tuple)
            assert isinstance(actual_result, tuple)
            assert actual_result == expected_result

    check()
    # Run a second time to check caching
    check()
