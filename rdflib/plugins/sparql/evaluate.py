"""
These method recursively evaluate the SPARQL Algebra

evalQuery is the entry-point, it will setup context and
return the SPARQLResult object

evalPart is called on each level and will delegate to the right method

A `rdflib.plugins.sparql.sparql.QueryContext` is passed along, keeping
information needed for evaluation

A list of dicts (solution mappings) is returned, apart from GroupBy which may
also return a dict of list of dicts
"""

from __future__ import annotations

import collections
import itertools
import logging
import re
from collections.abc import Generator, Iterable, Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    Union,
)
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from pyparsing import ParseException, ParseResults

from rdflib import __version__
from rdflib.graph import Graph
from rdflib.plugins.sparql import CUSTOM_EVALS, parser
from rdflib.plugins.sparql.aggregates import Aggregator
from rdflib.plugins.sparql.algebra import traverse
from rdflib.plugins.sparql.evalutils import (
    _ebv,
    _eval,
    _fillTemplate,
    _join,
    _minus,
    _val,
)
from rdflib.plugins.sparql.parserutils import CompValue, value
from rdflib.plugins.sparql.sparql import (
    AlreadyBound,
    FrozenBindings,
    FrozenDict,
    Prologue,
    Query,
    QueryContext,
    SPARQLError,
)
from rdflib.term import BNode, Identifier, Literal, URIRef, Variable

if TYPE_CHECKING:
    from rdflib.paths import Path

import json

try:
    import orjson

    _HAS_ORJSON = True
except ImportError:
    orjson = None  # type: ignore[assignment, unused-ignore]
    _HAS_ORJSON = False

_Triple = tuple[Identifier, Identifier, Identifier]

logger = logging.getLogger(__name__)


def evalBGP(
    ctx: QueryContext, bgp: list[_Triple]
) -> Generator[FrozenBindings, None, None]:
    """
    A basic graph pattern
    """

    if not bgp:
        yield ctx.solution()
        return

    s, p, o = bgp[0]

    _s = ctx[s]
    _p = ctx[p]
    _o = ctx[o]

    # type error: Item "None" of "Optional[Graph]" has no attribute "triples"
    # type Argument 1 to "triples" of "Graph" has incompatible type "tuple[Union[str, Path, None], Union[str, Path, None], Union[str, Path, None]]"; expected "tuple[Optional[Node], Optional[Node], Optional[Node]]"
    for ss, sp, so in ctx.graph.triples((_s, _p, _o)):  # type: ignore[union-attr, arg-type]
        if None in (_s, _p, _o):
            c = ctx.push()
        else:
            c = ctx

        if _s is None:
            # type error: Incompatible types in assignment (expression has type "Union[Node, Any]", target has type "Identifier")
            c[s] = ss  # type: ignore[assignment]

        try:
            if _p is None:
                # type error: Incompatible types in assignment (expression has type "Union[Node, Any]", target has type "Identifier")
                c[p] = sp  # type: ignore[assignment]
        except AlreadyBound:
            continue

        try:
            if _o is None:
                # type error: Incompatible types in assignment (expression has type "Union[Node, Any]", target has type "Identifier")
                c[o] = so  # type: ignore[assignment]
        except AlreadyBound:
            continue

        for x in evalBGP(c, bgp[1:]):
            yield x


def evalExtend(
    ctx: QueryContext, extend: CompValue
) -> Generator[FrozenBindings, None, None]:
    # TODO: Deal with dict returned from evalPart from GROUP BY

    for c in evalPart(ctx, extend.p):
        try:
            e = _eval(extend.expr, c.forget(ctx, _except=extend._vars))
            if isinstance(e, SPARQLError):
                raise e

            yield c.merge({extend.var: e})

        except SPARQLError:
            yield c


def evalLazyJoin(
    ctx: QueryContext, join: CompValue
) -> Generator[FrozenBindings, None, None]:
    """
    A lazy join will push the variables bound
    in the first part to the second part,
    essentially doing the join implicitly
    hopefully evaluating much fewer triples
    """
    for a in evalPart(ctx, join.p1):
        c = ctx.thaw(a)
        for b in evalPart(c, join.p2):
            yield b.merge(a)  # merge, as some bindings may have been forgotten


def evalJoin(ctx: QueryContext, join: CompValue) -> Generator[FrozenDict, None, None]:
    # TODO: Deal with dict returned from evalPart from GROUP BY
    # only ever for join.p1

    if join.lazy:
        return evalLazyJoin(ctx, join)
    else:
        a = evalPart(ctx, join.p1)
        b = set(evalPart(ctx, join.p2))
        return _join(a, b)


def evalUnion(ctx: QueryContext, union: CompValue) -> list[Any]:
    branch1_branch2 = []
    for x in evalPart(ctx, union.p1):
        branch1_branch2.append(x)
    for x in evalPart(ctx, union.p2):
        branch1_branch2.append(x)
    return branch1_branch2


def evalMinus(ctx: QueryContext, minus: CompValue) -> Generator[FrozenDict, None, None]:
    a = evalPart(ctx, minus.p1)
    b = set(evalPart(ctx, minus.p2))
    return _minus(a, b)


def evalLeftJoin(
    ctx: QueryContext, join: CompValue
) -> Generator[FrozenBindings, None, None]:
    # import pdb; pdb.set_trace()
    for a in evalPart(ctx, join.p1):
        ok = False
        c = ctx.thaw(a)
        for b in evalPart(c, join.p2):
            if _ebv(join.expr, b.forget(ctx)):
                ok = True
                yield b.merge(a)
        if not ok:
            # we've cheated, the ctx above may contain
            # vars bound outside our scope
            # before we yield a solution without the OPTIONAL part
            # check that we would have had no OPTIONAL matches
            # even without prior bindings...
            p1_vars = join.p1._vars
            if p1_vars is None or not any(
                _ebv(join.expr, b)
                for b in evalPart(ctx.thaw(a.remember(p1_vars)), join.p2)
            ):
                yield a


def evalFilter(
    ctx: QueryContext, part: CompValue
) -> Generator[FrozenBindings, None, None]:
    # TODO: Deal with dict returned from evalPart!
    for c in evalPart(ctx, part.p):
        if _ebv(
            part.expr,
            c.forget(ctx, _except=part._vars) if not part.no_isolated_scope else c,
        ):
            yield c


def evalGraph(
    ctx: QueryContext, part: CompValue
) -> Generator[FrozenBindings, None, None]:
    if ctx.dataset is None:
        raise Exception(
            "Non-conjunctive-graph doesn't know about "
            + "graphs. Try a query without GRAPH."
        )

    ctx = ctx.clone()
    graph: Union[str, Path, None, Graph] = ctx[part.term]
    prev_graph = ctx.graph
    if graph is None:
        for graph in ctx.dataset.contexts():
            # in SPARQL the default graph is NOT a named graph
            if graph == ctx.dataset.default_context:
                continue

            c = ctx.pushGraph(graph)
            c = c.push()
            graphSolution = [{part.term: graph.identifier}]
            for x in _join(evalPart(c, part.p), graphSolution):
                x.ctx.graph = prev_graph
                yield x

    else:
        if TYPE_CHECKING:
            assert not isinstance(graph, Graph)
        # type error: Argument 1 to "get_context" of "ConjunctiveGraph" has incompatible type "Union[str, Path]"; expected "Union[Node, str, None]"
        c = ctx.pushGraph(ctx.dataset.get_context(graph))  # type: ignore[arg-type]
        for x in evalPart(c, part.p):
            x.ctx.graph = prev_graph
            yield x


def evalValues(
    ctx: QueryContext, part: CompValue
) -> Generator[FrozenBindings, None, None]:
    for r in part.p.res:
        c = ctx.push()
        try:
            for k, v in r.items():
                if v != "UNDEF":
                    c[k] = v
        except AlreadyBound:
            continue

        yield c.solution()


def evalMultiset(ctx: QueryContext, part: CompValue):
    if part.p.name == "values":
        return evalValues(ctx, part)

    return evalPart(ctx, part.p)


def evalPart(ctx: QueryContext, part: CompValue) -> Any:
    # try custom evaluation functions
    for name, c in CUSTOM_EVALS.items():
        try:
            return c(ctx, part)
        except NotImplementedError:
            pass  # the given custome-function did not handle this part

    if part.name == "BGP":
        # Reorder triples patterns by number of bound nodes in the current ctx
        # Do patterns with more bound nodes first
        triples = sorted(
            part.triples, key=lambda t: len([n for n in t if ctx[n] is None])
        )

        return evalBGP(ctx, triples)
    elif part.name == "Filter":
        return evalFilter(ctx, part)
    elif part.name == "Join":
        return evalJoin(ctx, part)
    elif part.name == "LeftJoin":
        return evalLeftJoin(ctx, part)
    elif part.name == "Graph":
        return evalGraph(ctx, part)
    elif part.name == "Union":
        return evalUnion(ctx, part)
    elif part.name == "ToMultiSet":
        return evalMultiset(ctx, part)
    elif part.name == "Extend":
        return evalExtend(ctx, part)
    elif part.name == "Minus":
        return evalMinus(ctx, part)

    elif part.name == "Project":
        return evalProject(ctx, part)
    elif part.name == "Slice":
        return evalSlice(ctx, part)
    elif part.name == "Distinct":
        return evalDistinct(ctx, part)
    elif part.name == "Reduced":
        return evalReduced(ctx, part)

    elif part.name == "OrderBy":
        return evalOrderBy(ctx, part)
    elif part.name == "Group":
        return evalGroup(ctx, part)
    elif part.name == "AggregateJoin":
        return evalAggregateJoin(ctx, part)

    elif part.name == "SelectQuery":
        return evalSelectQuery(ctx, part)
    elif part.name == "AskQuery":
        return evalAskQuery(ctx, part)
    elif part.name == "ConstructQuery":
        return evalConstructQuery(ctx, part)

    elif part.name == "ServiceGraphPattern":
        return evalServiceQuery(ctx, part)

    elif part.name == "DescribeQuery":
        return evalDescribeQuery(ctx, part)

    else:
        raise Exception("I dont know: %s" % part.name)


# Everything in the text of a SERVICE pattern before its group graph pattern:
# the keywords, the endpoint, whitespace and comments. There, only a comment
# can hold a "{", and only an IRI, an escaped character in a prefixed name or a
# comment can hold a "#". A comment runs to the end of its line, which also
# stops the pattern backtracking through a run of comments.
_SERVICE_HEAD = re.compile(r"(?:<[^>]*>|\\.|#[^\n]*(?![^\n])|[^<\\#{])*{")


def _serviceGraphPatternText(part: CompValue) -> str:
    """Get the text inside the braces of a SERVICE pattern's group graph pattern."""
    service_string = part.service_string
    head = None
    if isinstance(service_string, str):
        service_string = service_string.rstrip()
        head = _SERVICE_HEAD.match(service_string)
    if head is None or not service_string.endswith("}"):
        raise ValueError(
            f"SERVICE pattern has no usable service_string: {service_string!r}"
        )
    return service_string[head.end() : -1]


def evalServiceQuery(ctx: QueryContext, part: CompValue):
    if not isinstance(part.term, URIRef):
        raise ValueError(
            f"SERVICE {part.term.n3()} is not supported, the endpoint must be an IRI"
        )
    service_url = str(part.term)
    service_query = _buildQueryStringForServiceCall(ctx, _serviceGraphPatternText(part))

    if not part.silent:
        yield from _callService(ctx, service_url, service_query)
        return
    try:
        # Convert every row before yielding any, so that a failure part way
        # through gives only the one solution below.
        solutions = list(_callService(ctx, service_url, service_query))
    except Exception as error:
        # The endpoint's userinfo and query, and the error's message, can hold
        # secrets, so the warning leaves them out. A failing endpoint can also
        # fail once for each solution it is joined with, so give the message
        # and traceback only when debugging.
        logger.warning(
            "Ignoring failed SERVICE SILENT call to %s: %s",
            _endpointWithoutSecrets(service_url),
            type(error).__name__,
            exc_info=logger.isEnabledFor(logging.DEBUG),
        )
        # A failed SERVICE SILENT pattern gives one solution with no bindings,
        # see https://www.w3.org/TR/sparql11-federated-query/#serviceFailure
        solutions = [FrozenBindings(ctx)]
    yield from solutions


def _endpointWithoutSecrets(service_url: str) -> str:
    """Get an endpoint without its userinfo, query and fragment, which can hold
    secrets, for use in log and error messages."""
    try:
        parts = urlsplit(service_url)
    except ValueError:
        return "an endpoint with an invalid IRI"
    host = parts.netloc.rpartition("@")[2]
    return urlunsplit((parts.scheme, host, parts.path, "", ""))


def _callService(
    ctx: QueryContext, service_url: str, service_query: str
) -> Generator[FrozenBindings, None, None]:
    query_settings = {"query": service_query, "output": "json"}
    headers = {
        "accept": "application/sparql-results+json",
        "user-agent": f"rdflib/{__version__}",
    }
    # GET is easier to cache so prefer that if the query is not to long
    if len(service_query) < 600:
        # Keep the endpoint's own query string. A fragment is never sent, so
        # drop it rather than put the query in it.
        parts = urlsplit(service_url)
        query = "&".join(filter(None, [parts.query, urlencode(query_settings)]))
        request = Request(
            urlunsplit(parts._replace(query=query, fragment="")), headers=headers
        )
    else:
        request = Request(
            service_url,
            data=urlencode(query_settings).encode(),
            headers=headers,
        )
    with urlopen(request) as response:
        if response.status != 200:
            raise Exception(
                f"Service: {_endpointWithoutSecrets(service_url)}"
                f" responded with code: {response.status}"
            )
        body = response.read()
    if _HAS_ORJSON:
        json_dict = orjson.loads(body)
    else:
        json_dict = json.loads(body)
    variables = json_dict["head"]["vars"]
    for r in json_dict["results"]["bindings"]:
        yield from _yieldBindingsFromServiceCallResult(ctx, r, variables)


"""
    Build a query string to be used by the service call.
    It is supposed to pass in the existing bound solutions.
    Adds the prefixes and base it uses.
    Wraps it in select if needed.
"""


def _buildQueryStringForServiceCall(ctx: QueryContext, service_query: str) -> str:
    try:
        parse = parser.parseQuery(service_query)
    except ParseException:
        # This could be because we don't have a select around the service call.
        service_query = "SELECT REDUCED * WHERE {" + service_query + "}"
        parse = parser.parseQuery(service_query)
    if ctx.prologue is not None:
        service_query = _serviceQueryPrologue(ctx.prologue, parse) + service_query
    sol = [v for v in ctx.solution() if isinstance(v, Variable)]
    if len(sol) > 0:
        variables = " ".join([v.n3() for v in sol])
        variables_bound = " ".join([ctx.get(v).n3() for v in sol])
        service_query = (
            service_query + "VALUES (" + variables + ") {(" + variables_bound + ")}"
        )
    return service_query


def _serviceQueryPrologue(prologue: Prologue, parse: ParseResults) -> str:
    """Declare the base and prefixes that a query for an endpoint uses, so that
    its IRIs resolve there as they do here. Declaring only those keeps short
    queries short enough for GET."""
    prefixes: set[str] = set()
    relative = False

    def visit(node: Any) -> None:
        nonlocal relative
        if isinstance(node, CompValue) and node.name == "pname":
            prefixes.add(node.prefix or "")
        elif isinstance(node, URIRef) and prologue.absolutize(node) != node:
            relative = True

    traverse(parse, visitPost=visit)
    declarations = [f"BASE <{prologue.base}> "] if relative else []
    for prefix in sorted(prefixes):
        namespace = prologue.namespace_manager.store.namespace(prefix)
        if namespace is not None:
            declarations.append(f"PREFIX {prefix}: {namespace.n3()} ")
    return "".join(declarations)


def _yieldBindingsFromServiceCallResult(
    ctx: QueryContext, r: dict[str, dict[str, str]], variables: list[str]
) -> Generator[FrozenBindings, None, None]:
    res_dict: dict[Variable, Identifier] = {}
    for var in variables:
        if var in r and r[var]:
            var_binding = r[var]
            var_type = var_binding["type"]
            if var_type == "uri":
                res_dict[Variable(var)] = URIRef(var_binding["value"])
            elif var_type == "literal":
                res_dict[Variable(var)] = Literal(
                    var_binding["value"],
                    datatype=var_binding.get("datatype"),
                    lang=var_binding.get("xml:lang"),
                )
            # This is here because of
            # https://www.w3.org/TR/2006/NOTE-rdf-sparql-json-res-20061004/#variable-binding-results
            elif var_type == "typed-literal":
                res_dict[Variable(var)] = Literal(
                    var_binding["value"], datatype=URIRef(var_binding["datatype"])
                )
            elif var_type == "bnode":
                res_dict[Variable(var)] = BNode(var_binding["value"])
            else:
                raise ValueError(f"invalid type {var_type!r} for variable {var!r}")
    yield FrozenBindings(ctx, res_dict)


def evalGroup(ctx: QueryContext, group: CompValue):
    """
    http://www.w3.org/TR/sparql11-query/#defn_algGroup
    """
    # grouping should be implemented by evalAggregateJoin
    return evalPart(ctx, group.p)


def evalAggregateJoin(
    ctx: QueryContext, agg: CompValue
) -> Generator[FrozenBindings, None, None]:
    # import pdb ; pdb.set_trace()
    p = evalPart(ctx, agg.p)
    # p is always a Group, we always get a dict back

    group_expr = agg.p.expr
    res: dict[Any, Any] = collections.defaultdict(
        lambda: Aggregator(aggregations=agg.A)
    )

    if group_expr is None:
        # no grouping, just COUNT in SELECT clause
        # get 1 aggregator for counting
        aggregator = res[True]
        for row in p:
            aggregator.update(row)
    else:
        for row in p:
            # determine right group aggregator for row
            k = tuple(_eval(e, row, False) for e in group_expr)
            res[k].update(row)

    # all rows are done; yield aggregated values
    for aggregator in res.values():
        yield FrozenBindings(ctx, aggregator.get_bindings())

    # there were no matches
    if len(res) == 0:
        yield FrozenBindings(ctx)


def _order_key(v: Any) -> tuple[Any, ...]:
    """Sort key for an ORDER BY condition.

    An expression that errors has no value, which SPARQL 1.1 section 15.1 orders
    lowest. `(0,)` sorts before every key from `_val`, so errors come first in
    ascending order and last with DESC.
    """
    if isinstance(v, SPARQLError):
        return (0,)
    return _val(v)


def evalOrderBy(
    ctx: QueryContext, part: CompValue
) -> Generator[FrozenBindings, None, None]:
    res = evalPart(ctx, part.p)

    for e in reversed(part.expr):
        reverse = bool(e.order and e.order == "DESC")
        res = sorted(
            res,
            key=lambda x: _order_key(value(x, e.expr, variables=True)),
            reverse=reverse,
        )

    return res


def evalSlice(ctx: QueryContext, slice: CompValue):
    res = evalPart(ctx, slice.p)

    return itertools.islice(
        res,
        slice.start,
        slice.start + slice.length if slice.length is not None else None,
    )


def evalReduced(
    ctx: QueryContext, part: CompValue
) -> Generator[FrozenBindings, None, None]:
    """apply REDUCED to result

    REDUCED is not as strict as DISTINCT, but if the incoming rows were sorted
    it should produce the same result with limited extra memory and time per
    incoming row.
    """

    # This implementation uses a most recently used strategy and a limited
    # buffer size. It relates to a LRU caching algorithm:
    # https://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used_.28LRU.29
    MAX = 1
    # TODO: add configuration or determine "best" size for most use cases
    # 0: No reduction
    # 1: compare only with the last row, almost no reduction with
    #    unordered incoming rows
    # N: The greater the buffer size the greater the reduction but more
    #    memory and time are needed

    # mixed data structure: set for lookup, deque for append/pop/remove
    mru_set = set()
    mru_queue: collections.deque[Any] = collections.deque()

    for row in evalPart(ctx, part.p):
        if row in mru_set:
            # forget last position of row
            mru_queue.remove(row)
        else:
            # row seems to be new
            yield row
            mru_set.add(row)
            if len(mru_set) > MAX:
                # drop the least recently used row from buffer
                mru_set.remove(mru_queue.pop())
        # put row to the front
        mru_queue.appendleft(row)


def evalDistinct(
    ctx: QueryContext, part: CompValue
) -> Generator[FrozenBindings, None, None]:
    res = evalPart(ctx, part.p)

    done = set()
    for x in res:
        if x not in done:
            yield x
            done.add(x)


def evalProject(ctx: QueryContext, project: CompValue):
    res = evalPart(ctx, project.p)
    return (row.project(project.PV) for row in res)


def evalSelectQuery(
    ctx: QueryContext, query: CompValue
) -> Mapping[str, Union[str, list[Variable], Iterable[FrozenDict]]]:
    res: dict[str, Union[str, list[Variable], Iterable[FrozenDict]]] = {}
    res["type_"] = "SELECT"
    res["bindings"] = evalPart(ctx, query.p)
    res["vars_"] = query.PV
    return res


def evalAskQuery(ctx: QueryContext, query: CompValue) -> Mapping[str, Union[str, bool]]:
    res: dict[str, Union[bool, str]] = {}
    res["type_"] = "ASK"
    res["askAnswer"] = False
    for x in evalPart(ctx, query.p):
        res["askAnswer"] = True
        break

    return res


def evalConstructQuery(
    ctx: QueryContext, query: CompValue
) -> Mapping[str, Union[str, Graph]]:
    template = query.template

    if not template:
        # a construct-where query
        template = query.p.p.triples  # query->project->bgp ...

    graph = Graph()

    for c in evalPart(ctx, query.p):
        graph += _fillTemplate(template, c)

    res: dict[str, Union[str, Graph]] = {}
    res["type_"] = "CONSTRUCT"
    res["graph"] = graph

    return res


def evalDescribeQuery(ctx: QueryContext, query) -> dict[str, Union[str, Graph]]:
    # Create a result graph and bind namespaces from the graph being queried
    graph = Graph()
    # type error: Item "None" of "Optional[Graph]" has no attribute "namespaces"
    for pfx, ns in ctx.graph.namespaces():  # type: ignore[union-attr]
        graph.bind(pfx, ns)

    to_describe = set()

    # Explicit IRIs may be provided to a DESCRIBE query.
    # If there is a WHERE clause, explicit IRIs may be provided in
    # addition to projected variables. Find those explicit IRIs and
    # prepare to describe them.
    for iri in query.PV:
        if isinstance(iri, URIRef):
            to_describe.add(iri)

    # If there is a WHERE clause, evaluate it then find the unique set of
    # resources to describe across all bindings and projected variables
    if query.p is not None:
        bindings = evalPart(ctx, query.p)
        to_describe.update(*(set(binding.values()) for binding in bindings))

    # Get a CBD for all resources identified to describe
    for resource in to_describe:
        # type error: Item "None" of "Optional[Graph]" has no attribute "cbd"
        ctx.graph.cbd(resource, target_graph=graph)  # type: ignore[union-attr]

    res: dict[str, Union[str, Graph]] = {}
    res["type_"] = "DESCRIBE"
    res["graph"] = graph

    return res


def evalQuery(
    graph: Graph,
    query: Query,
    initBindings: Mapping[str, Identifier] | None = None,
    base: str | None = None,
) -> Mapping[Any, Any]:
    """Evaluate a SPARQL query against a graph.

    !!! warning "Caution"

        This method can access indirectly requested network endpoints, for
        example, query processing will attempt to access network endpoints
        specified in `SERVICE` directives.

        When processing untrusted or potentially malicious queries, measures
        should be taken to restrict network and file access.

        For information on available security measures, see the RDFLib
        [Security Considerations](../security_considerations.md)
        documentation.
    """
    main = query.algebra

    initBindings = dict((Variable(k), v) for k, v in (initBindings or {}).items())

    ctx = QueryContext(
        graph, initBindings=initBindings, datasetClause=main.datasetClause
    )

    ctx.prologue = query.prologue

    return evalPart(ctx, main)
