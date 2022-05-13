import enum
import itertools
import logging
from dataclasses import dataclass, field
from pathlib import Path
from test.utils import pytest_mark_filter
from typing import Any, Callable, Dict, Set, Union

import pytest

from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.plugins.stores.berkeleydb import has_bsddb
from rdflib.store import Store
from rdflib.term import IdentifiedNode, URIRef


class StoreTrait(enum.Enum):
    WRAPPER = enum.auto()
    DISK_BACKED = enum.auto()


@dataclass
class StoreInfo:
    name: str
    traits: Set[StoreTrait] = field(default_factory=set)

    def make_graph(
        self, tmp_path: Path, identifier: Union[IdentifiedNode, str, None] = None
    ) -> Graph:
        graph = Graph(store=self.name, bind_namespaces="none", identifier=identifier)
        if StoreTrait.DISK_BACKED in self.traits:
            use_path = tmp_path / f"{self.name}.storedata"
            use_path.mkdir(exist_ok=True, parents=True)
            logging.debug("use_path = %s", use_path)
            graph.open(f"{use_path}", create=True)
        return graph


def make_store_info_dict(*result_format: StoreInfo) -> Dict[str, StoreInfo]:
    result = {}
    for item in result_format:
        result[item.name] = item
    return result


store_info_dict = make_store_info_dict(
    StoreInfo("Memory"),
    StoreInfo("SimpleMemory"),
    StoreInfo("SPARQLStore"),
    StoreInfo("SPARQLUpdateStore"),
    *((StoreInfo("BerkeleyDB", {StoreTrait.DISK_BACKED}),) if has_bsddb else ()),
)


@pytest.fixture(
    scope="module",
    params=store_info_dict.keys(),
)
def store_name(request) -> str:
    assert isinstance(request.param, str)
    return request.param


GraphMutator = Callable[[Graph], Any]

EGNSSUB = Namespace("http://example.com/sub/")
EGNSSUB_V0 = EGNSSUB["v0"]
EGNSSUB_V1 = EGNSSUB["v1"]
EGNSSUB_V2 = EGNSSUB["v2"]

NamespaceBindings = Dict[str, URIRef]


def make_graph(tmp_path: Path, store_name: str) -> Graph:
    logging.info("store_info_dict.keys() = %s", store_info_dict.keys())
    store_info = store_info_dict[store_name]
    return store_info.make_graph(tmp_path)


def check_ns(graph: Graph, expected_bindings: NamespaceBindings) -> None:
    actual_graph_bindings = list(graph.namespaces())
    logging.info("actual_bindings = %s", actual_graph_bindings)
    assert list(expected_bindings.items()) == actual_graph_bindings
    store: Store = graph.store
    actual_store_bindings = list(store.namespaces())
    assert list(expected_bindings.items()) == actual_store_bindings
    for prefix, uri in expected_bindings.items():
        assert store.prefix(uri) == prefix
        assert store.namespace(prefix) == uri


@pytest.mark.parametrize(
    ["override", "replace"], itertools.product([True, False], [True, False])
)
def test_simple_bind(
    tmp_path: Path, store_name: str, override: bool, replace: bool
) -> None:
    """
    URI binds to a prefix regardless of override and replace values.
    """
    graph = make_graph(tmp_path, store_name)
    graph.bind("egsub", EGNSSUB_V0, override=override, replace=replace)
    check_ns(graph, {"egsub": EGNSSUB_V0})


@pytest.mark.parametrize(
    ["override", "replace"], itertools.product([True, False], [True, False])
)
def test_bind_two_bind(
    tmp_path: Path, store_name: str, override: bool, replace: bool
) -> None:
    """
    A second prefix with a different URI binds correctly regardless of override
    and replace values.
    """
    graph = make_graph(tmp_path, store_name)
    graph.bind("egsub", EGNSSUB_V0)
    graph.bind("egsubv1", EGNSSUB_V1, override=override, replace=replace)
    check_ns(graph, {"egsub": EGNSSUB_V0, "egsubv1": EGNSSUB_V1})


@pytest.mark.parametrize("replace", [True, False])
def test_rebind_uri_override(tmp_path: Path, store_name: str, replace: bool) -> None:
    """
    URI binds to new prefix if override is `True` regardless of the value of `replace`.
    """
    graph = make_graph(tmp_path, store_name)
    graph.bind("egsub", EGNSSUB_V0)
    graph.bind("egsubv0", EGNSSUB_V0, override=True, replace=replace)
    check_ns(graph, {"egsubv0": EGNSSUB_V0})


@pytest.mark.parametrize("replace", [True, False])
def test_rebind_uri_no_override(tmp_path: Path, store_name: str, replace: bool) -> None:
    """
    URI does not bind to new prefix if override is `False` regardless of the value of `replace`.
    """
    graph = make_graph(tmp_path, store_name)
    graph.bind("egsub", EGNSSUB_V0)
    graph.bind("egsubv0", EGNSSUB_V0, override=False, replace=replace)
    check_ns(graph, {"egsub": EGNSSUB_V0})


@pytest.mark.parametrize(
    ["store_name", "override"],
    pytest_mark_filter(
        itertools.product(store_info_dict.keys(), [True, False]),
        {
            ("SPARQLStore", False): (
                pytest.mark.xfail(
                    raises=AssertionError,
                    reason="""
    SPARQLStore's namespace bindings work on a fundementally different way than
    the other stores, which is both simpler, but requires some additional work
    to make it behave like the other stores.
    """,
                ),
            ),
            ("SPARQLUpdateStore", False): (
                pytest.mark.xfail(
                    raises=AssertionError,
                    reason="""
    SPARQLStore's namespace bindings work on a fundementally different way than
    the other stores, which is both simpler, but requires some additional work
    to make it behave like the other stores.
    """,
                ),
            ),
        },
    ),
)
def test_rebind_prefix_replace(tmp_path: Path, store_name: str, override: bool) -> None:
    """
    If `replace` is `True`,
        Prefix binds to a new URI and `override` is `True`,
        but does not bind to a new URI if `override` is `False`.

    NOTE re logic, this is mainly just taking what most stores does and saying
    that is the right thing, not sure it really makes sense. This method is
    quite complicated and it is unlcear which of replace and override should
    take precedence in this case, once we sorted it out we should clarify in
    the documentation.
    """
    graph = make_graph(tmp_path, store_name)
    graph.bind("egsub", EGNSSUB_V0)
    if override:
        graph.bind("egsub", EGNSSUB_V1, override=override, replace=True)
        check_ns(graph, {"egsub": EGNSSUB_V1})
    else:
        graph.bind("egsub", EGNSSUB_V1, override=override, replace=True)
        check_ns(graph, {"egsub": EGNSSUB_V0})


@pytest.mark.parametrize(
    ["reuse_override", "reuse_replace"], itertools.product([True, False], [True, False])
)
def test_rebind_prefix_reuse_uri_replace(
    tmp_path: Path, store_name: str, reuse_override: bool, reuse_replace: bool
) -> None:
    """
    Prefix binds to a new URI and the old URI can be reused with a new prefix
    regardless of the value of override or replace used when reusing the old
    URI.
    """
    graph = make_graph(tmp_path, store_name)
    graph.bind("egsub", EGNSSUB_V0)
    graph.bind("egsub", EGNSSUB_V1, override=True, replace=True)
    graph.bind("egsubv0", EGNSSUB_V0, override=reuse_override, replace=reuse_replace)
    check_ns(graph, {"egsub": EGNSSUB_V1, "egsubv0": EGNSSUB_V0})
