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
import re
import requests
from pyparsing import ParseException

from rdflib import Variable, Graph, BNode, URIRef, Literal
from six import iteritems, itervalues

from rdflib.plugins.sparql import CUSTOM_EVALS
from rdflib.plugins.sparql.parserutils import value
from rdflib.plugins.sparql.sparql import (
    QueryContext, AlreadyBound, FrozenBindings, Bindings, SPARQLError)
from rdflib.plugins.sparql.evalutils import (
    _filter, _eval, _join, _diff, _minus, _fillTemplate, _ebv, _val)

from rdflib.plugins.sparql.aggregates import Aggregator
from rdflib.plugins.sparql.algebra import Join, ToMultiSet, Values
from rdflib.plugins.sparql import parser


def evalBGP(ctx, bgp):
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

    for ss, sp, so in ctx.graph.triples((_s, _p, _o)):
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


def evalExtend(ctx, extend):
    # TODO: Deal with dict returned from evalPart from GROUP BY

    for c in evalPart(ctx, extend.p):
        try:
            e = _eval(extend.expr, c.forget(ctx, _except=extend._vars))
            if isinstance(e, SPARQLError):
                raise e

            yield c.merge({extend.var: e})

        except SPARQLError:
            yield c


def evalLazyJoin(ctx, join):
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


def evalJoin(ctx, join):

    # TODO: Deal with dict returned from evalPart from GROUP BY
    # only ever for join.p1

    if join.lazy:
        return evalLazyJoin(ctx, join)
    else:
        a = evalPart(ctx, join.p1)
        b = set(evalPart(ctx, join.p2))
        return _join(a, b)


def evalUnion(ctx, union):
    for x in evalPart(ctx, union.p1):
        yield x
    for x in evalPart(ctx, union.p2):
        yield x


def evalMinus(ctx, minus):
    a = evalPart(ctx, minus.p1)
    b = set(evalPart(ctx, minus.p2))
    return _minus(a, b)


def evalLeftJoin(ctx, join):
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
            if p1_vars is None \
                or not any(_ebv(join.expr, b) for b in
                           evalPart(ctx.thaw(a.remember(p1_vars)), join.p2)):

                yield a


def evalFilter(ctx, part):
    # TODO: Deal with dict returned from evalPart!
    for c in evalPart(ctx, part.p):
        if _ebv(part.expr, c.forget(ctx, _except=part._vars) if not part.no_isolated_scope else c):
            yield c


def evalGraph(ctx, part):

    if ctx.dataset is None:
        raise Exception(
            "Non-conjunctive-graph doesn't know about " +
            "graphs. Try a query without GRAPH.")

    ctx = ctx.clone()
    graph = ctx[part.term]
    if graph is None:

        for graph in ctx.dataset.contexts():

            # in SPARQL the default graph is NOT a named graph
            if graph == ctx.dataset.default_context:
                continue

            c = ctx.pushGraph(graph)
            c = c.push()
            graphSolution = [{part.term: graph.identifier}]
            for x in _join(evalPart(c, part.p), graphSolution):
                yield x

    else:
        c = ctx.pushGraph(ctx.dataset.get_context(graph))
        for x in evalPart(c, part.p):
            yield x


def evalValues(ctx, part):
    for r in part.p.res:
        c = ctx.push()
        try:
            for k, v in r.items():
                if v != 'UNDEF':
                    c[k] = v
        except AlreadyBound:
            continue

        yield c.solution()


def evalMultiset(ctx, part):

    if part.p.name == 'values':
        return evalValues(ctx, part)

    return evalPart(ctx, part.p)


def evalPart(ctx, part):

    # try custom evaluation functions
    for name, c in CUSTOM_EVALS.items():
        try:
            return c(ctx, part)
        except NotImplementedError:
            pass  # the given custome-function did not handle this part

    if part.name == 'BGP':
        # Reorder triples patterns by number of bound nodes in the current ctx
        # Do patterns with more bound nodes first
        triples = sorted(part.triples, key=lambda t: len([n for n in t if ctx[n] is None]))

        return evalBGP(ctx, triples)
    elif part.name == 'Filter':
        return evalFilter(ctx, part)
    elif part.name == 'Join':
        return evalJoin(ctx, part)
    elif part.name == 'LeftJoin':
        return evalLeftJoin(ctx, part)
    elif part.name == 'Graph':
        return evalGraph(ctx, part)
    elif part.name == 'Union':
        return evalUnion(ctx, part)
    elif part.name == 'ToMultiSet':
        return evalMultiset(ctx, part)
    elif part.name == 'Extend':
        return evalExtend(ctx, part)
    elif part.name == 'Minus':
        return evalMinus(ctx, part)

    elif part.name == 'Project':
        return evalProject(ctx, part)
    elif part.name == 'Slice':
        return evalSlice(ctx, part)
    elif part.name == 'Distinct':
        return evalDistinct(ctx, part)
    elif part.name == 'Reduced':
        return evalReduced(ctx, part)

    elif part.name == 'OrderBy':
        return evalOrderBy(ctx, part)
    elif part.name == 'Group':
        return evalGroup(ctx, part)
    elif part.name == 'AggregateJoin':
        return evalAggregateJoin(ctx, part)

    elif part.name == 'SelectQuery':
        return evalSelectQuery(ctx, part)
    elif part.name == 'AskQuery':
        return evalAskQuery(ctx, part)
    elif part.name == 'ConstructQuery':
        return evalConstructQuery(ctx, part)

    elif part.name == 'ServiceGraphPattern':
        return evalServiceQuery(ctx, part)
        #raise Exception('ServiceGraphPattern not implemented')

    elif part.name == 'DescribeQuery':
        raise Exception('DESCRIBE not implemented')

    else:
        raise Exception('I dont know: %s' % part.name)

def evalServiceQuery(ctx, part):
    res = {}
    match = re.match('^service <(.*)>[ \n]*{(.*)}[ \n]*$',
                     part.get('service_string', ''), re.DOTALL)

    if match:
        service_url = match.group(1)
        service_query = _buildQueryStringForServiceCall(ctx, match)

        query_settings = {'query': service_query,
                          'output': 'json'}
        headers = {'accept' : 'application/sparql-results+json',
                          'user-agent': 'rdflibForAnUser'}
        # GET is easier to cache so prefer that if the query is not to long
        if len(service_query) < 600:
            response = requests.get(service_url, params=query_settings, headers=headers)
        else:
            response = requests.post(service_url, params=query_settings, headers=headers)
        if response.status_code == 200:
            json = response.json();
            variables = res["vars_"] = json['head']['vars']
            # or just return the bindings?
            res = json['results']['bindings']
            if len(res) > 0:
                for r in res:
                    for bound in _yieldBindingsFromServiceCallResult(ctx, r, variables):
                        yield bound
        else:
            raise Exception("Service: %s responded with code: %s", service_url, response.status_code);


"""
    Build a query string to be used by the service call. 
    It is supposed to pass in the existing bound solutions.
    Re-adds prefixes if added and sets the base.
    Wraps it in select if needed.
"""
def _buildQueryStringForServiceCall(ctx, match):

    service_query = match.group(2)
    try:
        parser.parseQuery(service_query)
    except ParseException:
        # This could be because we don't have a select around the service call.
        service_query = 'SELECT REDUCED * WHERE {' + service_query + '}'
        for p in ctx.prologue.namespace_manager.store.namespaces():
            service_query = 'PREFIX ' + p[0] + ':' + p[1].n3() + ' ' + service_query
        # re add the base if one was defined
        base = ctx.prologue.base
        if base is not None and len(base) > 0:
            service_query = 'BASE <' + base + '> ' + service_query
    sol = ctx.solution();
    if len(sol) > 0:
        variables = ' '.join(map(lambda v:v.n3(), sol))
        variables_bound = ' '.join(map(lambda v: ctx.get(v).n3(), sol))
        service_query = service_query + 'VALUES (' + variables + ') {(' + variables_bound + ')}'
    return service_query


def _yieldBindingsFromServiceCallResult(ctx, r, variables):
    res_dict = {}
    for var in variables:
        if var in r and r[var]:
            if r[var]['type'] == "uri":
                res_dict[Variable(var)] = URIRef(r[var]["value"])
            elif r[var]['type'] == "bnode":
                res_dict[Variable(var)] = BNode(r[var]["value"])
            elif r[var]['type'] == "literal" and 'datatype' in r[var]:
                res_dict[Variable(var)] = Literal(r[var]["value"], datatype=r[var]['datatype'])
            elif r[var]['type'] == "literal" and 'xml:lang' in r[var]:
                res_dict[Variable(var)] = Literal(r[var]["value"], lang=r[var]['xml:lang'])
    yield FrozenBindings(ctx, res_dict)


def evalGroup(ctx, group):
    """
    http://www.w3.org/TR/sparql11-query/#defn_algGroup
    """
    # grouping should be implemented by evalAggregateJoin
    return evalPart(ctx, group.p)


def evalAggregateJoin(ctx, agg):
    # import pdb ; pdb.set_trace()
    p = evalPart(ctx, agg.p)
    # p is always a Group, we always get a dict back

    group_expr = agg.p.expr
    res = collections.defaultdict(lambda: Aggregator(aggregations=agg.A))

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
    for aggregator in itervalues(res):
        yield FrozenBindings(ctx, aggregator.get_bindings())

    # there were no matches
    if len(res) == 0:
        yield FrozenBindings(ctx)


def evalOrderBy(ctx, part):

    res = evalPart(ctx, part.p)

    for e in reversed(part.expr):

        reverse = bool(e.order and e.order == 'DESC')
        res = sorted(res, key=lambda x: _val(value(x, e.expr, variables=True)), reverse=reverse)

    return res


def evalSlice(ctx, slice):
    res = evalPart(ctx, slice.p)

    return itertools.islice(res, slice.start, slice.start + slice.length if slice.length is not None else None)


def evalReduced(ctx, part):
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
    mru_queue = collections.deque()

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


def evalDistinct(ctx, part):
    res = evalPart(ctx, part.p)

    done = set()
    for x in res:
        if x not in done:
            yield x
            done.add(x)


def evalProject(ctx, project):
    res = evalPart(ctx, project.p)

    return (row.project(project.PV) for row in res)


def evalSelectQuery(ctx, query):

    res = {}
    res["type_"] = "SELECT"
    res["bindings"] = evalPart(ctx, query.p)
    res["vars_"] = query.PV
    return res


def evalAskQuery(ctx, query):
    res = {}
    res["type_"] = "ASK"
    res["askAnswer"] = False
    for x in evalPart(ctx, query.p):
        res["askAnswer"] = True
        break

    return res


def evalConstructQuery(ctx, query):
    template = query.template

    if not template:
        # a construct-where query
        template = query.p.p.triples  # query->project->bgp ...

    graph = Graph()

    for c in evalPart(ctx, query.p):
        graph += _fillTemplate(template, c)

    res = {}
    res["type_"] = "CONSTRUCT"
    res["graph"] = graph

    return res


def evalQuery(graph, query, initBindings, base=None):

    initBindings = dict((Variable(k), v) for k, v in iteritems(initBindings))

    ctx = QueryContext(graph, initBindings=initBindings)

    ctx.prologue = query.prologue
    main = query.algebra

    if main.datasetClause:
        if ctx.dataset is None:
            raise Exception(
                "Non-conjunctive-graph doesn't know about " +
                "graphs! Try a query without FROM (NAMED).")

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
