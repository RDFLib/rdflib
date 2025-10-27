#!/usr/bin/env python
"""

A commandline tool for querying with sparql on local files with
custom serialization.

example usage:
    ```bash
    sparqlquery path/to/data.ttl -q "SELECT ?x WHERE {?x a foaf:Person. }"
    sparqlquery path/to/data.ttl -q "SELECT ?x WHERE {?x a foaf:Person. }" --format json
    sparqlquery path/to/data.ttl -q "SELECT ?x WHERE {?x a foaf:Person. }" --print "custom print: {x.value}" --only-first
    sparqlquery path/to/data.ttl --query-file query.spl
    sparqlquery data1.ttl data2.ttl --query-file query.spl
    sparqlquery http://example.com/sparqlendpoint --query-file query.spl
    sparqlquery http://example.com/sparqlendpoint --query-file query.spl --username user --password secret
    ```
"""
from __future__ import annotations

import argparse
import logging
from typing import Iterator, List, Optional, Tuple
from urllib.parse import urlparse

# from rdflib import plugin
from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.sparql import Query
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.query import Result, ResultRow

__all__ = ["sparqlquery", "PrettyTerm"]


class _ArgumentError(Exception):
    pass


class PrettyTerm:
    def __init__(self, term):
        self.term = term

    def __repr__(self):
        return self.term

    def __str__(self):
        return self.term.n3()

    @property
    def value(self):
        return str(self.term)


def sparqlquery(
    endpoints: List[str],
    query: str,
    custom_print_lines: Optional[List[str]] = None,
    only_first: bool = False,
    format: Optional[str] = None,
    auth: Optional[Tuple[str, str]] = None,
):
    g, search_only = _get_graph(endpoints, auth)
    q: Query = prepareQuery(
        query,
        # initNs = { "foaf": FOAF }
    )
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
    if format is not None:
        ret_bytes = results.serialize(format=format)
        if ret_bytes is not None:
            print(ret_bytes.decode())
        return
    elif q.algebra.name in ["SelectQuery"]:
        resultrows: Iterator[ResultRow] = iter(results)
        _serialize_query_results(resultrows, varlist, custom_print_lines, only_first)
    else:
        ret_bytes = results.serialize()
        if ret_bytes is not None:
            print(ret_bytes.decode())


def _table_print(**kwargs):
    print(list(kwargs.items()))


def _create_custom_print(custom_print_lines):
    mylines = list(custom_print_lines)

    def custom_print(**kwargs):
        for fmt in mylines:
            print(fmt.format(**kwargs))

    return custom_print


def _serialize_query_results(
    results: Iterator[ResultRow],
    varlist: List[str],
    custom_print_lines: Optional[List[str]],
    only_first: bool,
):
    if custom_print_lines is not None and len(custom_print_lines) > 0:
        print_function = _create_custom_print(custom_print_lines)
    else:
        print_function = _table_print
    for x in results:
        pretty_results = {label: PrettyTerm(x[label]) for label in x.labels}
        print_function(**pretty_results)
        if only_first:
            return


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
    parser.add_argument(
        "--only-first",
        action="store_true",
        default=False,
        help="Print only on first result. " "Only works togeter with --print",
    )
    parser.add_argument(
        "--print",
        nargs="*",
        type=str,
        help="custom print lines. Can be used multiple times."
        "If set ignores '--format'."
        "\nFormatting can use following extra methods:"
        "\n    x.value: print out only the string",
    )
    parser.add_argument("--format", type=str, help="Print result in given format.")
    parser.add_argument(
        "--username", type=str, help="Username used during authentication."
    )
    parser.add_argument(
        "--password", type=str, help="Password used during authentication."
    )

    args = parser.parse_args()
    opts = {}
    if args.print is not None:
        opts["custom_print_lines"] = args.print
        opts["only_first"] = args.only_first
    elif args.format is not None:
        opts["format"] = args.format

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
    return args.endpoint, query, args.warn, opts


def main():
    try:
        endpoints, query, warn, opts = parse_args()
    except _ArgumentError as err:
        print(err)
        exit()

    if warn:
        loglevel = logging.WARNING
    else:
        loglevel = logging.CRITICAL
    logging.basicConfig(level=loglevel)

    sparqlquery(endpoints, query, **opts)


if __name__ == "__main__":
    main()
