#!/usr/bin/env python
"""

A commandline tool for querying with sparql on local files with
custom serialization.

example usage:
    ```bash
    sparqlquery path/to/data.ttl -q "SELECT ?x WHERE {?x a foaf:Person. }"
    sparqlquery path/to/data.ttl -q "SELECT ?x WHERE {?x a foaf:Person. }" --format json
    sparqlquery path/to/data.ttl --query-file query.spl
    sparqlquery data1.ttl data2.ttl --query-file query.spl
    sparqlquery http://example.com/sparqlendpoint --query-file query.spl
    sparqlquery http://example.com/sparqlendpoint --query-file query.spl --username user --password secret
    ```
"""
from __future__ import annotations

import argparse
import logging
from typing import Iterator, List, Optional, Tuple, Dict
from urllib.parse import urlparse

# from rdflib import plugin
from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.plugin import ResultSerializer
from rdflib.plugin import get as get_plugin
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.sparql import Query
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.query import Result, ResultRow

__all__ = ["sparqlquery", "PrettyTerm"]


class _ArgumentError(Exception):
    pass


def sparqlquery(
    endpoints: List[str],
    query: str,
    fmt: Optional[str] = None,
    auth: Optional[Tuple[str, str]] = None,
    format_opt: Dict[str, str] = {},
):
    g, search_only = _get_graph(endpoints, auth)
    q: Query = prepareQuery(query)
    if search_only and q.algebra.name not in [
        "SelectQuery",
        "DescribeQuery",
        "AskQuery",
    ]:
        raise NotImplementedError(
            "Queries on local files can only " "use SELECT, DESCRIBE or ASK."
        )
    varlist = [str(v) for v in q.algebra._vars]

    results: Result = g.query(q)
    ret_bytes = results.serialize(format=fmt, **format_opt)
    if ret_bytes is not None:
        print(ret_bytes.decode())


def _dest_is_local(dest: str):
    q = urlparse(dest)
    return q.scheme in ["", "file"]


def _get_graph(endpoints, auth) -> Tuple[Graph, bool]:
    graph: Graph
    search_only = True
    if len(endpoints) == 1 and not _dest_is_local(endpoints[0]):
        # store = plugin.get("SPARQLStore", Store)(auth=auth)
        # store.open(endpoints[0])
        store = SPARQLStore(endpoints[0], auth=auth)
        graph = ConjunctiveGraph(store)
        search_only = False
    elif all(not (_dest_is_local(x)) for x in endpoints):
        raise NotImplementedError("Cant use multiple remote locations.")
    else:
        if not all(_dest_is_local(x) for x in endpoints):
            raise NotImplementedError("Cant mix local and remote locations.")
        graph = Graph()
        for x in endpoints:
            graph.parse(location=x)
        search_only = True
    return graph, search_only


def parse_args():
    parser = argparse.ArgumentParser(prog="sparqlquery", description=__doc__)
    parser.add_argument(
        "endpoint",
        nargs="+",
        type=str,
        help="Endpoints for sparql query. "
        "If  multiple use a conjunctive graph instead.",
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
    parser.add_argument("--format", type=str, default="csv", dest="fmt",
                        help="Print result in given format.")
    parser.add_argument(
        "--help-format", dest="helpformat",
        action="store_true",
        default=False,
        help="Prints out help for controlling the result formatting.",
    )
    parser.add_argument(
        "--username", type=str, help="Username used during authentication."
    )
    parser.add_argument(
        "--password", type=str, help="Password used during authentication."
    )

    args = parser.parse_args()
    opts = {}

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
    return args.endpoint, query, args.fmt, args.warn, args.helpformat, opts


def main():
    try:
        endpoints, query, serialize_fmt, warn, helpformat, opts = parse_args()
    except _ArgumentError as err:
        print(err)
        exit()

    if warn:
        loglevel = logging.WARNING
    else:
        loglevel = logging.CRITICAL
    logging.basicConfig(level=loglevel)

    if helpformat:
        plgn = get_plugin(serialize_fmt, ResultSerializer)
        help(plgn)
        exit()

    sparqlquery(endpoints, query, fmt=serialize_fmt, **opts)


if __name__ == "__main__":
    main()
