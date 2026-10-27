from __future__ import annotations

import importlib
import logging
import shutil
import subprocess
import sys
import warnings
from collections.abc import Callable, Generator
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, cast

import pytest

import rdflib.plugin
import rdflib.plugins.sparql
import rdflib.plugins.sparql.evaluate
from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.parser import Parser
from rdflib.query import ResultRow
from rdflib.serializer import Serializer

TEST_DIR = Path(__file__).parent.parent
TEST_PLUGINS_DIR = TEST_DIR / "plugins"


def del_key(d: dict[Any, Any], key: Any) -> None:
    del d[key]


@contextmanager
def ctx_plugin(tmp_path: Path, plugin_src: Path) -> Generator[None, None, None]:
    base = tmp_path / f"{hash(plugin_src)}"
    pypath = (base / "pypath").absolute()
    plugpath = (base / "plugin").absolute()
    shutil.copytree(plugin_src, plugpath)
    logging.debug("Installing %s into %s", plugin_src, pypath)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--isolated",
            "--no-input",
            "--no-clean",
            "--no-index",
            "--no-build-isolation",
            "--disable-pip-version-check",
            "--target",
            f"{pypath}",
            f"{plugpath}",
        ],
        check=True,
    )

    sys.path.append(f"{pypath}")

    yield None

    sys.path.remove(f"{pypath}")


@contextmanager
def ctx_cleaners() -> Generator[list[Callable[[], None]], None, None]:
    cleaners: list[Callable[[], None]] = []
    yield cleaners
    for cleaner in cleaners:
        logging.debug("running cleaner %s", cleaner)
        cleaner()


# Using no_cover as coverage freaks out and crashes because of what is happening here.
def test_sparqleval(tmp_path: Path, no_cover: None) -> None:
    with ExitStack() as stack:
        stack.enter_context(ctx_plugin(tmp_path, TEST_PLUGINS_DIR / "sparqleval"))
        warnings_record = stack.enter_context(warnings.catch_warnings(record=True))
        cleaners = stack.enter_context(ctx_cleaners())

        ep_name = "example.rdflib.plugin.sparqleval"
        ep_ns = f"{ep_name.replace('.', ':')}:"
        plugin_module = importlib.import_module(ep_name)
        assert plugin_module.namespace == ep_ns

        importlib.reload(rdflib.plugins.sparql)
        importlib.reload(rdflib.plugins.sparql.evaluate)

        cleaners.insert(0, lambda: del_key(rdflib.plugins.sparql.CUSTOM_EVALS, ep_name))

        logging.debug(
            "rdflib.plugins.sparql.CUSTOM_EVALS = %s",
            rdflib.plugins.sparql.CUSTOM_EVALS,
        )

        graph = Graph()
        query_string = (
            "SELECT ?output1 WHERE { BIND(<" + ep_ns + "function>() AS ?output1) }"
        )
        logging.debug("query_string = %s", query_string)
        result = graph.query(query_string)
        assert result.type == "SELECT"
        rows = cast(list[ResultRow], list(result))
        logging.debug("rows = %s", rows)
        assert len(rows) == 1
        assert len(rows[0]) == 1
        assert rows[0][0] == plugin_module.function_result
        assert [str(msg) for msg in warnings_record] == []


# Using no_cover as coverage freaks out and crashes because of what is happening here.
def test_parser(tmp_path: Path, no_cover: None) -> None:
    with ExitStack() as stack:
        stack.enter_context(ctx_plugin(tmp_path, TEST_PLUGINS_DIR / "parser"))
        warnings_record = stack.enter_context(warnings.catch_warnings(record=True))
        cleaners = stack.enter_context(ctx_cleaners())

        ep_name = "example.rdflib.plugin.parser"
        ep_ns = f"{ep_name.replace('.', ':')}:"
        plugin_module = importlib.import_module(ep_name)
        assert plugin_module.ExampleParser.namespace() == ep_ns

        importlib.reload(rdflib.plugin)
        cleaners.insert(0, lambda: del_key(rdflib.plugin._plugins, (ep_name, Parser)))

        graph = Graph()
        assert len(graph) == 0
        graph.parse(format=ep_name, data="")

        assert len(graph) > 0
        triples = set(graph.triples((None, None, None)))
        logging.debug("triples = %s", triples)
        assert triples == plugin_module.ExampleParser.constant_output()
        assert [str(msg) for msg in warnings_record] == []


@pytest.mark.parametrize("kind", [Parser, Serializer])
@pytest.mark.parametrize("name", ["nq", "application/n-quads"])
def test_nquads_aliases(name: str, kind: type[Parser] | type[Serializer]) -> None:
    """The short and media type names resolve to the same plugin as `nquads`."""
    assert rdflib.plugin.get(name, kind) is rdflib.plugin.get("nquads", kind)


def test_nq_format_parse_and_serialize() -> None:
    """`nq` can be used as a format name to both serialize and parse N-Quads."""
    dataset = Dataset()
    dataset.graph(URIRef("urn:example:graph")).add(
        (URIRef("urn:example:s"), URIRef("urn:example:p"), Literal("o"))
    )

    data = dataset.serialize(format="nq")
    assert data == dataset.serialize(format="nquads")

    parsed = Dataset()
    parsed.parse(data=data, format="nq")
    assert set(parsed.quads()) == set(dataset.quads())
    assert len(set(parsed.quads())) == 1
