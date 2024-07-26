from __future__ import annotations

import logging
from contextlib import ExitStack
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Set, Tuple, Type, Union

import pytest

from rdflib import Graph
from rdflib.graph import Dataset
from rdflib.namespace import (
    _NAMESPACE_PREFIXES_CORE,
    _NAMESPACE_PREFIXES_RDFLIB,
    OWL,
    RDFS,
    Namespace,
    NamespaceManager,
)
from rdflib.term import URIRef
from test.utils.outcome import ExceptionChecker, OutcomeChecker, OutcomePrimitive

if TYPE_CHECKING:
    from rdflib._type_checking import _NamespaceSetString


def test_core_prefixes_bound():
    # we should have RDF, RDFS, OWL, XSD & XML bound
    g = Graph()

    # prefixes in Graph
    assert len(list(g.namespaces())) == len(
        {**_NAMESPACE_PREFIXES_RDFLIB, **_NAMESPACE_PREFIXES_CORE}
    )
    pre = sorted([x[0] for x in list(g.namespaces())])
    assert pre == [
        "brick",
        "csvw",
        "dc",
        "dcam",
        "dcat",
        "dcmitype",
        "dcterms",
        "doap",
        "foaf",
        "geo",
        "odrl",
        "org",
        "owl",
        "prof",
        "prov",
        "qb",
        "rdf",
        "rdfs",
        "schema",
        "sh",
        "skos",
        "sosa",
        "ssn",
        "time",
        "vann",
        "void",
        "wgs",
        "xml",
        "xsd",
    ]


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


@pytest.mark.parametrize(
    ["selector", "expected_bindings"],
    [
        (
            None,
            {
                "brick": "https://brickschema.org/schema/Brick#",
                "csvw": "http://www.w3.org/ns/csvw#",
                "dc": "http://purl.org/dc/elements/1.1/",
                "dcat": "http://www.w3.org/ns/dcat#",
                "dcmitype": "http://purl.org/dc/dcmitype/",
                "dcterms": "http://purl.org/dc/terms/",
                "dcam": "http://purl.org/dc/dcam/",
                "doap": "http://usefulinc.com/ns/doap#",
                "foaf": "http://xmlns.com/foaf/0.1/",
                "odrl": "http://www.w3.org/ns/odrl/2/",
                "geo": "http://www.opengis.net/ont/geosparql#",
                "org": "http://www.w3.org/ns/org#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "prof": "http://www.w3.org/ns/dx/prof/",
                "prov": "http://www.w3.org/ns/prov#",
                "qb": "http://purl.org/linked-data/cube#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "schema": "https://schema.org/",
                "sh": "http://www.w3.org/ns/shacl#",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "sosa": "http://www.w3.org/ns/sosa/",
                "ssn": "http://www.w3.org/ns/ssn/",
                "time": "http://www.w3.org/2006/time#",
                "vann": "http://purl.org/vocab/vann/",
                "void": "http://rdfs.org/ns/void#",
                "wgs": "https://www.w3.org/2003/01/geo/wgs84_pos#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "xml": "http://www.w3.org/XML/1998/namespace",
            },
        ),
        (
            "rdflib",
            {
                "brick": "https://brickschema.org/schema/Brick#",
                "csvw": "http://www.w3.org/ns/csvw#",
                "dc": "http://purl.org/dc/elements/1.1/",
                "dcat": "http://www.w3.org/ns/dcat#",
                "dcmitype": "http://purl.org/dc/dcmitype/",
                "dcterms": "http://purl.org/dc/terms/",
                "dcam": "http://purl.org/dc/dcam/",
                "doap": "http://usefulinc.com/ns/doap#",
                "foaf": "http://xmlns.com/foaf/0.1/",
                "odrl": "http://www.w3.org/ns/odrl/2/",
                "geo": "http://www.opengis.net/ont/geosparql#",
                "org": "http://www.w3.org/ns/org#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "prof": "http://www.w3.org/ns/dx/prof/",
                "prov": "http://www.w3.org/ns/prov#",
                "qb": "http://purl.org/linked-data/cube#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "schema": "https://schema.org/",
                "sh": "http://www.w3.org/ns/shacl#",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "sosa": "http://www.w3.org/ns/sosa/",
                "ssn": "http://www.w3.org/ns/ssn/",
                "time": "http://www.w3.org/2006/time#",
                "vann": "http://purl.org/vocab/vann/",
                "void": "http://rdfs.org/ns/void#",
                "wgs": "https://www.w3.org/2003/01/geo/wgs84_pos#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "xml": "http://www.w3.org/XML/1998/namespace",
            },
        ),
        (
            "core",
            {
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "xml": "http://www.w3.org/XML/1998/namespace",
            },
        ),
    ],
)
def test_bound_namespaces_subset(
    selector: Optional[Any], expected_bindings: Dict[str, str]
) -> None:
    if selector is not None:
        graph = Graph(bind_namespaces=selector)
    else:
        graph = Graph()
    bound_namespaces = dict(
        (key, str(value)) for key, value in graph.namespace_manager.namespaces()
    )
    assert (
        expected_bindings.items() <= bound_namespaces.items()
    ), f"missing items {expected_bindings.items() - bound_namespaces.items()}"
    empty_graph = Graph(bind_namespaces="none")
    if selector is not None:
        nman = NamespaceManager(empty_graph, bind_namespaces=selector)
    else:
        nman = NamespaceManager(empty_graph)
    nman_bound_namespaces = dict((key, str(value)) for key, value in nman.namespaces())
    assert bound_namespaces == nman_bound_namespaces


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
    expected_result: OutcomePrimitive[Tuple[str, URIRef, str]],
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
        checker = OutcomeChecker[Tuple[str, URIRef, str]].from_primitive(
            expected_result
        )
        with checker.context():
            actual_result = nm.compute_qname(uri, generate)
            logging.debug("actual_result = %s", actual_result)
            checker.check(actual_result)

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
    expected_result: OutcomePrimitive[Tuple[str, str, str]],
) -> None:
    graph = Graph(bind_namespaces=bind_namespaces)
    nm = graph.namespace_manager

    if additional_prefixes is not None:
        for prefix, ns in additional_prefixes.items():
            nm.bind(prefix, ns)

    def check() -> None:
        checker = OutcomeChecker[Tuple[str, str, str]].from_primitive(expected_result)
        with checker.context():
            actual_result = nm.compute_qname_strict(uri, generate)
            logging.debug("actual_result = %s", actual_result)
            checker.check(actual_result)

    check()
    # Run a second time to check caching
    check()


def make_test_nsm() -> NamespaceManager:
    namespaces = [
        ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
        ("", "http://example.org/"),
        (
            # Because of <https://github.com/RDFLib/rdflib/issues/2077> this
            # will have no effect on the namespace manager.
            "eg",
            "http://example.org/",
        ),
    ]
    graph = Graph(bind_namespaces="none")
    for prefix, namespace in namespaces:
        graph.bind(prefix, namespace, override=False)

    return graph.namespace_manager


@pytest.fixture(scope="session")
def test_nsm_session() -> NamespaceManager:
    return make_test_nsm()


@pytest.fixture(scope="function")
def test_nsm_function() -> NamespaceManager:
    return make_test_nsm()


@pytest.mark.parametrize(
    ["curie", "expected_result"],
    [
        ("rdf:type", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        (":foo", "http://example.org/foo"),
        ("too_small", ExceptionChecker(ValueError, "Malformed curie argument")),
        (
            "egdo:bar",
            ExceptionChecker(ValueError, 'Prefix "egdo" not bound to any namespace'),
        ),
        pytest.param(
            "eg:foo",
            "http://example.org/foo",
            marks=pytest.mark.xfail(
                raises=ValueError,
                reason="This is failing because of https://github.com/RDFLib/rdflib/issues/2077",
            ),
        ),
    ],
)
def test_expand_curie(
    test_nsm_session: NamespaceManager,
    curie: str,
    expected_result: OutcomePrimitive[str],
) -> None:
    nsm = test_nsm_session
    if isinstance(expected_result, str):
        expected_result = URIRef(expected_result)
    checker = OutcomeChecker[str].from_primitive(expected_result)
    with checker.context():
        actual_result = nsm.expand_curie(curie)
        checker.check(actual_result)


@pytest.mark.parametrize(
    ["uri", "generate", "expected_result"],
    [
        ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", None, "rdf:type"),
        ("http://example.org/foo", None, ":foo"),
        ("http://example.com/a#chair", None, "ns1:chair"),
        ("http://example.com/a#chair", True, "ns1:chair"),
        (
            "http://example.com/a#chair",
            False,
            ExceptionChecker(
                KeyError, "No known prefix for http://example.com/a# and generate=False"
            ),
        ),
        ("http://example.com/b#chair", None, "ns1:chair"),
        ("http://example.com/c", None, "ns1:c"),
        ("", None, ExceptionChecker(ValueError, "Can't split ''")),
        (
            "http://example.com/",
            None,
            ExceptionChecker(ValueError, "Can't split 'http://example.com/'"),
        ),
    ],
)
def test_generate_curie(
    test_nsm_function: NamespaceManager,
    uri: str,
    generate: Optional[bool],
    expected_result: OutcomePrimitive[str],
) -> None:
    """
    .. note::

        This is using the function scoped nsm fixture because curie has side
        effects and will modify the namespace manager.
    """
    nsm = test_nsm_function
    checker = OutcomeChecker[str].from_primitive(expected_result)
    with checker.context():
        if generate is None:
            actual_result = nsm.curie(uri)
        else:
            actual_result = nsm.curie(uri, generate=generate)
        checker.check(actual_result)
