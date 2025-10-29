#!/usr/bin/env python
"""

A commandline tool for querying with sparql on local files with
custom serialization.

example usage:
    ```bash
    sparqlquery path/to/data.ttl -q "SELECT ?x WHERE {?x a foaf:Person. }"
    sparqlquery path/to/data.ttl -q "SELECT ?x WHERE {?x a foaf:Person. }" --format json
    #sparqlquery - -q "SELECT ?x WHERE {?x a foaf:Person}" << rdfpipe info.ttl
    rdfpipe test.ttl | sparqlquery - -q "SELECT ?x WHERE {?x a foaf:Person}"
    sparqlquery path/to/data.ttl --query-file query.spl
    sparqlquery data1.ttl data2.ttl --query-file query.spl
    sparqlquery http://example.com/sparqlendpoint --query-file query.spl
    sparqlquery http://example.com/sparqlendpoint --query-file query.spl --username user --password secret
    ```
"""
from __future__ import annotations

import argparse
import inspect
from inspect import Parameter
import logging
import sys
from typing import Iterator, List, Optional, Tuple, Dict
from urllib.parse import urlparse

from .rdfpipe import _format_and_kws

from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.plugin import ResultSerializer, PluginException
from rdflib.plugin import get as get_plugin
from rdflib.plugin import plugins as get_plugins
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.sparql import Query
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.query import Result, ResultRow

__all__ = ["sparqlquery"]


class _ArgumentError(Exception):
    pass

class _PrintHelpExit(Exception):
    pass


def sparqlquery(
    endpoints: List[str],
    query: str,
    result_format: Optional[str] = None,
    result_keywords: Dict[str, str] = {},
    auth: Optional[Tuple[str, str]] = None,
    use_stdin: bool = False,
    use_remote: bool = False,
):
    if use_stdin:
        search_only = True
        g = Graph().parse(sys.stdin)
        raise NotImplementedError()
    else:
        g, search_only = _get_graph(endpoints, auth, use_remote)
    q: Query = prepareQuery(query)
    if search_only and q.algebra.name not in [
        "SelectQuery",
        "DescribeQuery",
        "AskQuery",
    ]:
        raise NotImplementedError(
            "Queries on local files or STDIN can only use SELECT, DESCRIBE or ASK."
        )

    results: Result = g.query(q)
    ret_bytes = results.serialize(format=result_format, **result_keywords)
    if ret_bytes is not None:
        print(ret_bytes.decode())


def _dest_is_local(dest: str):
    q = urlparse(dest)
    return q.scheme in ["", "file"]

def _dest_is_internet_addr(dest: str):
    q = urlparse(dest)
    return q.scheme in ["http", "https"]


def _get_graph(endpoints, auth, use_remote: bool) -> Tuple[Graph, bool]:
    graph: Graph
    search_only = True
    if use_remote:
        # store = plugin.get("SPARQLStore", Store)(auth=auth)
        # store.open(endpoints[0])
        store = SPARQLStore(endpoints[0], auth=auth)
        graph = ConjunctiveGraph(store)
        search_only = False
    else:
        graph = Graph()
        for x in endpoints:
            graph.parse(location=x)
        search_only = True
    return graph, search_only

def parse_args():
    parser = argparse.ArgumentParser(prog="sparqlquery",
                                     description=__doc__, add_help=False)
    parser.add_argument(
        "endpoint",
        nargs="+",
        type=str,
        help="Endpoints for sparql query. "
        "If  multiple use a conjunctive graph instead. "
        "Reads from stdin if '-' is given.",
    )
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        help="Sparql query. Cannot be set together with --queryfile",
    )
    parser.add_argument(
        "--queryfile",
        type=str,
        help="File from where the sparql query is read."
        "Canot be set together with -q/--query",
    )
    parser.add_argument(
        "-w",
        "--warn",
        action="store_true",
        default=False,
        help="Output warnings to stderr " "(by default only critical errors).",
    )
    parser.add_argument("--format", type=str, default="csv",
                        help="Print sparql result in given format. "
                        "Keywords as described in epilog can be given "
                        "after format like: "
                        "FORMAT:(+)KW1,-KW2,KW3=VALUE.")
    parser.add_argument(
        "--help",
        action="store_true",
        default=False,
        help="show help message and exit. "
        "Also prints information about given format.",
    )
    parser.add_argument(
        "--username", type=str, help="Username used during authentication."
    )
    parser.add_argument(
        "--password", type=str, help="Password used during authentication."
    )

    args = parser.parse_args()
    opts = {}

    format_, format_keywords = _format_and_kws(args.format)
    if args.help:
        parser.epilog = _create_epilog_from_format(format_)
        parser.print_help()
        raise _PrintHelpExit()

    if args.query and args.queryfile is None:
        query = args.query
    elif args.queryfile and args.query is None:
        with open(args.queryfile, "r") as f:
            query = f.read()
    else:
        parser.print_help()
        raise _ArgumentError("Either -q/--query or --queryfile must be provided")

    if args.username is not None and args.password is not None:
        opts["auth"] = (args.username, args.password)
    elif args.username is None and args.password is None:
        pass
    else:
        parser.print_help()
        raise _ArgumentError("User only provided one of password and username")

    if len(args.endpoint) == 1:
        if args.endpoint[0] == "-":
            endpoints = []
            opts["use_stdin"] = True
        elif _dest_is_internet_addr(args.endpoint[0]):
            endpoints = args.endpoint
            opts["use_remote"] = True
        else:
            endpoints = args.endpoint
    else:
        endpoints = list(args.endpoint)
        if any(not(_dest_is_local(x)) for x in args.endpoint):
            raise NotImplementedError(
                    "If multiple endpoints are given, all must be local files."
                    )

    return endpoints, query, format_, format_keywords, args.warn, opts


def _create_epilog_from_format(format_) -> str:
    try:
        plugin = get_plugin(format_, ResultSerializer)
    except PluginException as err:
        available_plugins = [x.name for x in get_plugins(None, ResultSerializer)]
        return f"No plugin registered for sparql result in format '{format_}'. "\
                f"available plugins: {available_plugins}"
    serializer_function = plugin.serialize
    module = inspect.getmodule(plugin.serialize)
    pydoc_target = ".".join([module.__name__, plugin.serialize.__qualname__])
    sig = inspect.signature(plugin.serialize)
    available_keywords = [
            x for x, y in sig.parameters.items()
            if y.kind in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
            ]
    available_keywords.pop(0) # pop self
    epilog = f"For more customization for format '{format_}' "\
            f"use `pydoc {pydoc_target}`. "\
            f"Known keywords are {available_keywords}."
    if any(y.kind == Parameter.VAR_KEYWORD for x, y in sig.parameters.items()):
        epilog += " Further keywords might be valid."
    return epilog



def main():
    try:
        endpoints, query, result_format, format_keywords, warn, opts = parse_args()
    except _PrintHelpExit:
        exit()
    except _ArgumentError as err:
        print(err)
        exit()

    if warn:
        loglevel = logging.WARNING
    else:
        loglevel = logging.CRITICAL
    logging.basicConfig(level=loglevel)

    sparqlquery(endpoints, query, result_format=result_format,
                result_keywords=format_keywords, **opts)


if __name__ == "__main__":
    main()
