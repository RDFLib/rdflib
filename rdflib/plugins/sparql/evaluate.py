"""
These method recursively evaluate the SPARQL Algebra

evalQuery is the entry-point, it will setup context and
return the SPARQLResult object

evalPart is called on each level and will delegate to the right method

A rdflib.plugins.sparql.sparql.QueryContext is passed along, keeping
information needed for evaluation

A list of dicts (solution mappings) is returned, apart from GroupBy which may
also return a dict of list of dicts

"""

import collections
import itertools
import json as j
import re
from typing import Any, Deque, Dict, Generator, Iterable, List, Tuple, Union
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pyparsing import ParseException

from rdflib.graph import Graph
from rdflib.plugins.sparql import CUSTOM_EVALS, parser
from rdflib.plugins.sparql.aggregates import Aggregator
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
    Query,
    QueryContext,
    SPARQLError,
)
from rdflib.term import BNode, Identifier, Literal, URIRef, Variable

_Triple = Tuple[Identifier, Identifier, Identifier]


def evalBGP(
    ctx: QueryContext, bgp: List[_Triple]
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
    for ss, sp, so in ctx.graph.triples((_s, _p, _o)):  # type: ignore[union-attr]
        if None in (_s, _p, _o):
            c = ctx.push()
        else:
            c = ctx

        if _s is None:
            c[s] = ss

        try:
            if _p is None:
                c[p] = sp
        except AlreadyBound:
            continue

        try:
            if _o is None:
                c[o] = so
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


def evalUnion(ctx: QueryContext, union: CompValue) -> Iterable[FrozenBindings]:
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
                yield b
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
    graph = ctx[part.term]
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
        c = ctx.pushGraph(ctx.dataset.get_context(graph))
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


def evalPart(ctx: QueryContext, part: CompValue):

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
        # raise Exception('ServiceGraphPattern not implemented')

    elif part.name == "DescribeQuery":
        raise Exception("DESCRIBE not implemented")

    else:
        raise Exception("I dont know: %s" % part.name)


def evalServiceQuery(ctx: QueryContext, part):
    res = {}
    match = re.match(
        "^service <(.*)>[ \n]*{(.*)}[ \n]*$",
        part.get("service_string", ""),
        re.DOTALL | re.I,
    )

    if match:
        service_url = match.group(1)
        service_query = _buildQueryStringForServiceCall(ctx, match)

        query_settings = {"query": service_query, "output": "json"}
        headers = {
            "accept": "application/sparql-results+json",
            "user-agent": "rdflibForAnUser",
        }
        # GET is easier to cache so prefer that if the query is not to long
        if len(service_query) < 600:
            response = urlopen(
                Request(service_url + "?" + urlencode(query_settings), headers=headers)
            )
        else:
            response = urlopen(
                Request(
                    service_url,
                    data=urlencode(query_settings).encode(),
                    headers=headers,
                )
            )
        if response.status == 200:
            json = j.loads(response.read())
            variables = res["vars_"] = json["head"]["vars"]
            # or just return the bindings?
            res = json["results"]["bindings"]
            if len(res) > 0:
                for r in res:
                    # type error: Argument 2 to "_yieldBindingsFromServiceCallResult" has incompatible type "str"; expected "Dict[str, Dict[str, str]]"
                    for bound in _yieldBindingsFromServiceCallResult(ctx, r, variables):  # type: ignore[arg-type]
                        yield bound
        else:
            raise Exception(
                "Service: %s responded with code: %s", service_url, response.status
            )


"""
    Build a query string to be used by the service call.
    It is supposed to pass in the existing bound solutions.
    Re-adds prefixes if added and sets the base.
    Wraps it in select if needed.
"""


def _buildQueryStringForServiceCall(ctx: QueryContext, match: re.Match) -> str:

    service_query = match.group(2)
    try:
        parser.parseQuery(service_query)
    except ParseException:
        # This could be because we don't have a select around the service call.
        service_query = "SELECT REDUCED * WHERE {" + service_query + "}"
        # type error: Item "None" of "Optional[Prologue]" has no attribute "namespace_manager"
        for p in ctx.prologue.namespace_manager.store.namespaces():  # type: ignore[union-attr]
            service_query = "PREFIX " + p[0] + ":" + p[1].n3() + " " + service_query
        # re add the base if one was defined
        # type error: Item "None" of "Optional[Prologue]" has no attribute "base"  [union-attr]
        base = ctx.prologue.base  # type: ignore[union-attr]
        if base is not None and len(base) > 0:
            service_query = "BASE <" + base + "> " + service_query
    sol = ctx.solution()
    if len(sol) > 0:
        variables = " ".join([v.n3() for v in sol])
        variables_bound = " ".join([ctx.get(v).n3() for v in sol])
        service_query = (
            service_query + "VALUES (" + variables + ") {(" + variables_bound + ")}"
        )
    return service_query


def _yieldBindingsFromServiceCallResult(
    ctx: QueryContext, r: Dict[str, Dict[str, str]], variables: List[str]
) -> Generator[FrozenBindings, None, None]:
    res_dict: Dict[Variable, Identifier] = {}
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
    res: Dict[Any, Any] = collections.defaultdict(
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


def evalOrderBy(
    ctx: QueryContext, part: CompValue
) -> Generator[FrozenBindings, None, None]:

    res = evalPart(ctx, part.p)

    for e in reversed(part.expr):

        reverse = bool(e.order and e.order == "DESC")
        res = sorted(
            res, key=lambda x: _val(value(x, e.expr, variables=True)), reverse=reverse
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
    mru_queue: Deque[Any] = collections.deque()

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


def evalSelectQuery(ctx: QueryContext, query: CompValue):

    res = {}
    res["type_"] = "SELECT"
    res["bindings"] = evalPart(ctx, query.p)
    res["vars_"] = query.PV
    return res


def evalAskQuery(ctx: QueryContext, query: CompValue):
    res: Dict[str, Union[bool, str]] = {}
    res["type_"] = "ASK"
    res["askAnswer"] = False
    for x in evalPart(ctx, query.p):
        res["askAnswer"] = True
        break

    return res


def evalConstructQuery(ctx: QueryContext, query) -> Dict[str, Union[str, Graph]]:
    template = query.template

    if not template:
        # a construct-where query
        template = query.p.p.triples  # query->project->bgp ...

    graph = Graph()

    for c in evalPart(ctx, query.p):
        graph += _fillTemplate(template, c)

    res: Dict[str, Union[str, Graph]] = {}
    res["type_"] = "CONSTRUCT"
    res["graph"] = graph

    return res


def evalQuery(graph: Graph, query: Query, initBindings, base=None):

    initBindings = dict((Variable(k), v) for k, v in initBindings.items())

    ctx = QueryContext(graph, initBindings=initBindings)

    ctx.prologue = query.prologue
    main = query.algebra

    if main.datasetClause:
        if ctx.dataset is None:
            raise Exception(
                "Non-conjunctive-graph doesn't know about "
                + "graphs! Try a query without FROM (NAMED)."
            )

        ctx = ctx.clone()  # or push/pop?

        firstDefault = False
        for d in main.datasetClause:
            if d.default:

                if firstDefault:
                    # replace current default graph
                    dg = ctx.dataset.get_context(BNode())
                    ctx = ctx.pushGraph(dg)
                    firstDefault = True

                ctx.load(d.default, default=True)

            elif d.named:
                g = d.named
                ctx.load(g, default=False)

    return evalPart(ctx, main)
