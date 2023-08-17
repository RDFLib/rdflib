import importlib
import logging
import shutil
import subprocess
import sys
import warnings
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, cast

import rdflib.plugin
import rdflib.plugins.sparql
import rdflib.plugins.sparql.evaluate
from rdflib import Graph
from rdflib.parser import Parser
from rdflib.query import ResultRow

TEST_DIR = Path(__file__).parent.parent
TEST_PLUGINS_DIR = TEST_DIR / "plugins"


def del_key(d: Dict[Any, Any], key: Any) -> None:
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
def ctx_cleaners() -> Generator[List[Callable[[], None]], None, None]:
    cleaners: List[Callable[[], None]] = []
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
        ep_ns = f'{ep_name.replace(".", ":")}:'
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
        rows = cast(List[ResultRow], list(result))
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
        ep_ns = f'{ep_name.replace(".", ":")}:'
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
