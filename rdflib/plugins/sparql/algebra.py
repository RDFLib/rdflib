"""
Converting the 'parse-tree' output of pyparsing to a SPARQL Algebra expression

http://www.w3.org/TR/sparql11-query/#sparqlQuery

"""

import functools
import operator
import collections

from functools import reduce

from rdflib import Literal, Variable, URIRef, BNode

from rdflib.plugins.sparql.sparql import Prologue, Query
from rdflib.plugins.sparql.parserutils import CompValue, Expr
from rdflib.plugins.sparql.operators import (
    and_,
    TrueFilter,
    simplify as simplifyFilters,
)
from rdflib.paths import InvPath, AlternativePath, SequencePath, MulPath, NegatedPath

from pyparsing import ParseResults


# ---------------------------
# Some convenience methods
from rdflib.term import Identifier


def OrderBy(p, expr):
    return CompValue("OrderBy", p=p, expr=expr)


def ToMultiSet(p):
    return CompValue("ToMultiSet", p=p)


def Union(p1, p2):
    return CompValue("Union", p1=p1, p2=p2)


def Join(p1, p2):
    return CompValue("Join", p1=p1, p2=p2)


def Minus(p1, p2):
    return CompValue("Minus", p1=p1, p2=p2)


def Graph(term, graph):
    return CompValue("Graph", term=term, p=graph)


def BGP(triples=None):
    return CompValue("BGP", triples=triples or [])


def LeftJoin(p1, p2, expr):
    return CompValue("LeftJoin", p1=p1, p2=p2, expr=expr)


def Filter(expr, p):
    return CompValue("Filter", expr=expr, p=p)


def Extend(p, expr, var):
    return CompValue("Extend", p=p, expr=expr, var=var)


def Values(res):
    return CompValue("values", res=res)


def Project(p, PV):
    return CompValue("Project", p=p, PV=PV)


def Group(p, expr=None):
    return CompValue("Group", p=p, expr=expr)


def _knownTerms(triple, varsknown, varscount):
    return (
        len(
            [
                x
                for x in triple
                if x not in varsknown and isinstance(x, (Variable, BNode))
            ]
        ),
        -sum(varscount.get(x, 0) for x in triple),
        not isinstance(triple[2], Literal),
    )


def reorderTriples(l_):
    """
    Reorder triple patterns so that we execute the
    ones with most bindings first
    """

    def _addvar(term, varsknown):
        if isinstance(term, (Variable, BNode)):
            varsknown.add(term)

    l_ = [(None, x) for x in l_]
    varsknown = set()
    varscount = collections.defaultdict(int)
    for t in l_:
        for c in t[1]:
            if isinstance(c, (Variable, BNode)):
                varscount[c] += 1
    i = 0

    # Done in steps, sort by number of bound terms
    # the top block of patterns with the most bound terms is kept
    # the rest is resorted based on the vars bound after the first
    # block is evaluated

    # we sort by decorate/undecorate, since we need the value of the sort keys

    while i < len(l_):
        l_[i:] = sorted((_knownTerms(x[1], varsknown, varscount), x[1]) for x in l_[i:])
        t = l_[i][0][0]  # top block has this many terms bound
        j = 0
        while i + j < len(l_) and l_[i + j][0][0] == t:
            for c in l_[i + j][1]:
                _addvar(c, varsknown)
            j += 1
        i += 1

    return [x[1] for x in l_]


def triples(l):

    l = reduce(lambda x, y: x + y, l)
    if (len(l) % 3) != 0:
        raise Exception("these aint triples")
    return reorderTriples((l[x], l[x + 1], l[x + 2]) for x in range(0, len(l), 3))


def translatePName(p, prologue):
    """
    Expand prefixed/relative URIs
    """
    if isinstance(p, CompValue):
        if p.name == "pname":
            return prologue.absolutize(p)
        if p.name == "literal":
            return Literal(
                p.string, lang=p.lang, datatype=prologue.absolutize(p.datatype)
            )
    elif isinstance(p, URIRef):
        return prologue.absolutize(p)


def translatePath(p):
    """
    Translate PropertyPath expressions
    """

    if isinstance(p, CompValue):
        if p.name == "PathAlternative":
            if len(p.part) == 1:
                return p.part[0]
            else:
                return AlternativePath(*p.part)

        elif p.name == "PathSequence":
            if len(p.part) == 1:
                return p.part[0]
            else:
                return SequencePath(*p.part)

        elif p.name == "PathElt":
            if not p.mod:
                return p.part
            else:
                if isinstance(p.part, list):
                    if len(p.part) != 1:
                        raise Exception("Denkfehler!")

                    return MulPath(p.part[0], p.mod)
                else:
                    return MulPath(p.part, p.mod)

        elif p.name == "PathEltOrInverse":
            if isinstance(p.part, list):
                if len(p.part) != 1:
                    raise Exception("Denkfehler!")
                return InvPath(p.part[0])
            else:
                return InvPath(p.part)

        elif p.name == "PathNegatedPropertySet":
            if isinstance(p.part, list):
                return NegatedPath(AlternativePath(*p.part))
            else:
                return NegatedPath(p.part)


def translateExists(e):
    """
    Translate the graph pattern used by EXISTS and NOT EXISTS
    http://www.w3.org/TR/sparql11-query/#sparqlCollectFilters
    """

    def _c(n):
        if isinstance(n, CompValue):
            if n.name in ("Builtin_EXISTS", "Builtin_NOTEXISTS"):
                n.graph = translateGroupGraphPattern(n.graph)
                if n.graph.name == "Filter":
                    # filters inside (NOT) EXISTS can see vars bound outside
                    n.graph.no_isolated_scope = True

    e = traverse(e, visitPost=_c)

    return e


def collectAndRemoveFilters(parts):
    """

    FILTER expressions apply to the whole group graph pattern in which
    they appear.

    http://www.w3.org/TR/sparql11-query/#sparqlCollectFilters
    """

    filters = []

    i = 0
    while i < len(parts):
        p = parts[i]
        if p.name == "Filter":
            filters.append(translateExists(p.expr))
            parts.pop(i)
        else:
            i += 1

    if filters:
        return and_(*filters)

    return None


def translateGroupOrUnionGraphPattern(graphPattern):
    A = None

    for g in graphPattern.graph:
        g = translateGroupGraphPattern(g)
        if not A:
            A = g
        else:
            A = Union(A, g)
    return A


def translateGraphGraphPattern(graphPattern):
    return Graph(graphPattern.term, translateGroupGraphPattern(graphPattern.graph))


def translateInlineData(graphPattern):
    return ToMultiSet(translateValues(graphPattern))


def translateGroupGraphPattern(graphPattern):
    """
    http://www.w3.org/TR/sparql11-query/#convertGraphPattern
    """

    if graphPattern.name == "SubSelect":
        return ToMultiSet(translate(graphPattern)[0])

    if not graphPattern.part:
        graphPattern.part = []  # empty { }

    filters = collectAndRemoveFilters(graphPattern.part)

    g = []
    for p in graphPattern.part:
        if p.name == "TriplesBlock":
            # merge adjacent TripleBlocks
            if not (g and g[-1].name == "BGP"):
                g.append(BGP())
            g[-1]["triples"] += triples(p.triples)
        else:
            g.append(p)

    G = BGP()
    for p in g:
        if p.name == "OptionalGraphPattern":
            A = translateGroupGraphPattern(p.graph)
            if A.name == "Filter":
                G = LeftJoin(G, A.p, A.expr)
            else:
                G = LeftJoin(G, A, TrueFilter)
        elif p.name == "MinusGraphPattern":
            G = Minus(p1=G, p2=translateGroupGraphPattern(p.graph))
        elif p.name == "GroupOrUnionGraphPattern":
            G = Join(p1=G, p2=translateGroupOrUnionGraphPattern(p))
        elif p.name == "GraphGraphPattern":
            G = Join(p1=G, p2=translateGraphGraphPattern(p))
        elif p.name == "InlineData":
            G = Join(p1=G, p2=translateInlineData(p))
        elif p.name == "ServiceGraphPattern":
            G = Join(p1=G, p2=p)
        elif p.name in ("BGP", "Extend"):
            G = Join(p1=G, p2=p)
        elif p.name == "Bind":
            G = Extend(G, p.expr, p.var)

        else:
            raise Exception(
                "Unknown part in GroupGraphPattern: %s - %s" % (type(p), p.name)
            )

    if filters:
        G = Filter(expr=filters, p=G)

    return G


class StopTraversal(Exception):
    def __init__(self, rv):
        self.rv = rv


def _traverse(e, visitPre=lambda n: None, visitPost=lambda n: None):
    """
    Traverse a parse-tree, visit each node

    if visit functions return a value, replace current node
    """
    _e = visitPre(e)
    if _e is not None:
        return _e

    if e is None:
        return None

    if isinstance(e, (list, ParseResults)):
        return [_traverse(x, visitPre, visitPost) for x in e]
    elif isinstance(e, tuple):
        return tuple([_traverse(x, visitPre, visitPost) for x in e])

    elif isinstance(e, CompValue):
        for k, val in e.items():
            e[k] = _traverse(val, visitPre, visitPost)

    _e = visitPost(e)
    if _e is not None:
        return _e

    return e


def _traverseAgg(e, visitor=lambda n, v: None):
    """
    Traverse a parse-tree, visit each node

    if visit functions return a value, replace current node
    """

    res = []

    if isinstance(e, (list, ParseResults, tuple)):
        res = [_traverseAgg(x, visitor) for x in e]

    elif isinstance(e, CompValue):
        for k, val in e.items():
            if val is not None:
                res.append(_traverseAgg(val, visitor))

    return visitor(e, res)


def traverse(tree, visitPre=lambda n: None, visitPost=lambda n: None, complete=None):
    """
    Traverse tree, visit each node with visit function
    visit function may raise StopTraversal to stop traversal
    if complete!=None, it is returned on complete traversal,
    otherwise the transformed tree is returned
    """
    try:
        r = _traverse(tree, visitPre, visitPost)
        if complete is not None:
            return complete
        return r
    except StopTraversal as st:
        return st.rv


def _hasAggregate(x):
    """
    Traverse parse(sub)Tree
    return true if any aggregates are used
    """

    if isinstance(x, CompValue):
        if x.name.startswith("Aggregate_"):
            raise StopTraversal(True)


def _aggs(e, A):
    """
    Collect Aggregates in A
    replaces aggregates with variable references
    """

    # TODO: nested Aggregates?

    if isinstance(e, CompValue) and e.name.startswith("Aggregate_"):
        A.append(e)
        aggvar = Variable("__agg_%d__" % len(A))
        e["res"] = aggvar
        return aggvar


def _findVars(x, res):
    """
    Find all variables in a tree
    """
    if isinstance(x, Variable):
        res.add(x)
    if isinstance(x, CompValue):
        if x.name == "Bind":
            res.add(x.var)
            return x  # stop recursion and finding vars in the expr
        elif x.name == "SubSelect":
            if x.projection:
                res.update(v.var or v.evar for v in x.projection)
            return x


def _addVars(x, children):
    """
    find which variables may be bound by this part of the query
    """
    if isinstance(x, Variable):
        return set([x])
    elif isinstance(x, CompValue):
        if x.name == "RelationalExpression":
            x["_vars"] = set()
        elif x.name == "Extend":
            # vars only used in the expr for a bind should not be included
            x["_vars"] = reduce(
                operator.or_,
                [child for child, part in zip(children, x) if part != "expr"],
                set(),
            )

        else:
            x["_vars"] = set(reduce(operator.or_, children, set()))

            if x.name == "SubSelect":
                if x.projection:
                    s = set(v.var or v.evar for v in x.projection)
                else:
                    s = set()

                return s

        return x["_vars"]

    return reduce(operator.or_, children, set())


def _sample(e, v=None):
    """
    For each unaggregated variable V in expr
    Replace V with Sample(V)
    """
    if isinstance(e, CompValue) and e.name.startswith("Aggregate_"):
        return e  # do not replace vars in aggregates
    if isinstance(e, Variable) and v != e:
        return CompValue("Aggregate_Sample", vars=e)


def _simplifyFilters(e):
    if isinstance(e, Expr):
        return simplifyFilters(e)


def translateAggregates(q, M):
    E = []
    A = []

    # collect/replace aggs in :
    #    select expr as ?var
    if q.projection:
        for v in q.projection:
            if v.evar:
                v.expr = traverse(v.expr, functools.partial(_sample, v=v.evar))
                v.expr = traverse(v.expr, functools.partial(_aggs, A=A))

    # having clause
    if traverse(q.having, _hasAggregate, complete=False):
        q.having = traverse(q.having, _sample)
        traverse(q.having, functools.partial(_aggs, A=A))

    # order by
    if traverse(q.orderby, _hasAggregate, complete=False):
        q.orderby = traverse(q.orderby, _sample)
        traverse(q.orderby, functools.partial(_aggs, A=A))

    # sample all other select vars
    # TODO: only allowed for vars in group-by?
    if q.projection:
        for v in q.projection:
            if v.var:
                rv = Variable("__agg_%d__" % (len(A) + 1))
                A.append(CompValue("Aggregate_Sample", vars=v.var, res=rv))
                E.append((rv, v.var))

    return CompValue("AggregateJoin", A=A, p=M), E


def translateValues(v):
    # if len(v.var)!=len(v.value):
    #     raise Exception("Unmatched vars and values in ValueClause: "+str(v))

    res = []
    if not v.var:
        return res
    if not v.value:
        return res
    if not isinstance(v.value[0], list):

        for val in v.value:
            res.append({v.var[0]: val})
    else:
        for vals in v.value:
            res.append(dict(zip(v.var, vals)))

    return Values(res)


def translate(q):
    """
    http://www.w3.org/TR/sparql11-query/#convertSolMod

    """

    _traverse(q, _simplifyFilters)

    q.where = traverse(q.where, visitPost=translatePath)

    # TODO: Var scope test
    VS = set()
    traverse(q.where, functools.partial(_findVars, res=VS))

    # all query types have a where part
    M = translateGroupGraphPattern(q.where)

    aggregate = False
    if q.groupby:
        conditions = []
        # convert "GROUP BY (?expr as ?var)" to an Extend
        for c in q.groupby.condition:
            if isinstance(c, CompValue) and c.name == "GroupAs":
                M = Extend(M, c.expr, c.var)
                c = c.var
            conditions.append(c)

        M = Group(p=M, expr=conditions)
        aggregate = True
    elif (
        traverse(q.having, _hasAggregate, complete=False)
        or traverse(q.orderby, _hasAggregate, complete=False)
        or any(
            traverse(x.expr, _hasAggregate, complete=False)
            for x in q.projection or []
            if x.evar
        )
    ):
        # if any aggregate is used, implicit group by
        M = Group(p=M)
        aggregate = True

    if aggregate:
        M, E = translateAggregates(q, M)
    else:
        E = []

    # HAVING
    if q.having:
        M = Filter(expr=and_(*q.having.condition), p=M)

    # VALUES
    if q.valuesClause:
        M = Join(p1=M, p2=ToMultiSet(translateValues(q.valuesClause)))

    if not q.projection:
        # select *
        PV = list(VS)
    else:
        PV = list()
        for v in q.projection:
            if v.var:
                if v not in PV:
                    PV.append(v.var)
            elif v.evar:
                if v not in PV:
                    PV.append(v.evar)

                E.append((v.expr, v.evar))
            else:
                raise Exception("I expected a var or evar here!")

    for e, v in E:
        M = Extend(M, e, v)

    # ORDER BY
    if q.orderby:
        M = OrderBy(
            M,
            [
                CompValue("OrderCondition", expr=c.expr, order=c.order)
                for c in q.orderby.condition
            ],
        )

    # PROJECT
    M = Project(M, PV)

    if q.modifier:
        if q.modifier == "DISTINCT":
            M = CompValue("Distinct", p=M)
        elif q.modifier == "REDUCED":
            M = CompValue("Reduced", p=M)

    if q.limitoffset:
        offset = 0
        if q.limitoffset.offset is not None:
            offset = q.limitoffset.offset.toPython()

        if q.limitoffset.limit is not None:
            M = CompValue(
                "Slice", p=M, start=offset, length=q.limitoffset.limit.toPython()
            )
        else:
            M = CompValue("Slice", p=M, start=offset)

    return M, PV


def simplify(n):
    """Remove joins to empty BGPs"""
    if isinstance(n, CompValue):
        if n.name == "Join":
            if n.p1.name == "BGP" and len(n.p1.triples) == 0:
                return n.p2
            if n.p2.name == "BGP" and len(n.p2.triples) == 0:
                return n.p1
        elif n.name == "BGP":
            n["triples"] = reorderTriples(n.triples)
            return n


def analyse(n, children):
    """
    Some things can be lazily joined.
    This propegates whether they can up the tree
    and sets lazy flags for all joins
    """

    if isinstance(n, CompValue):
        if n.name == "Join":
            n["lazy"] = all(children)
            return False
        elif n.name in ("Slice", "Distinct"):
            return False
        else:
            return all(children)
    else:
        return True


def translatePrologue(p, base, initNs=None, prologue=None):

    if prologue is None:
        prologue = Prologue()
        prologue.base = ""
    if base:
        prologue.base = base
    if initNs:
        for k, v in initNs.items():
            prologue.bind(k, v)

    for x in p:
        if x.name == "Base":
            prologue.base = x.iri
        elif x.name == "PrefixDecl":
            prologue.bind(x.prefix, prologue.absolutize(x.iri))

    return prologue


def translateQuads(quads):
    if quads.triples:
        alltriples = triples(quads.triples)
    else:
        alltriples = []

    allquads = collections.defaultdict(list)

    if quads.quadsNotTriples:
        for q in quads.quadsNotTriples:
            if q.triples:
                allquads[q.term] += triples(q.triples)

    return alltriples, allquads


def translateUpdate1(u, prologue):
    if u.name in ("Load", "Clear", "Drop", "Create"):
        pass  # no translation needed
    elif u.name in ("Add", "Move", "Copy"):
        pass
    elif u.name in ("InsertData", "DeleteData", "DeleteWhere"):
        t, q = translateQuads(u.quads)
        u["quads"] = q
        u["triples"] = t
        if u.name in ("DeleteWhere", "DeleteData"):
            pass  # TODO: check for bnodes in triples
    elif u.name == "Modify":
        if u.delete:
            u.delete["triples"], u.delete["quads"] = translateQuads(u.delete.quads)
        if u.insert:
            u.insert["triples"], u.insert["quads"] = translateQuads(u.insert.quads)
        u["where"] = translateGroupGraphPattern(u.where)
    else:
        raise Exception("Unknown type of update operation: %s" % u)

    u.prologue = prologue
    return u


def translateUpdate(q, base=None, initNs=None):
    """
    Returns a list of SPARQL Update Algebra expressions
    """

    res = []
    prologue = None
    if not q.request:
        return res
    for p, u in zip(q.prologue, q.request):
        prologue = translatePrologue(p, base, initNs, prologue)

        # absolutize/resolve prefixes
        u = traverse(u, visitPost=functools.partial(translatePName, prologue=prologue))
        u = _traverse(u, _simplifyFilters)

        u = traverse(u, visitPost=translatePath)

        res.append(translateUpdate1(u, prologue))

    return res


def translateQuery(q, base=None, initNs=None):
    """
    Translate a query-parsetree to a SPARQL Algebra Expression

    Return a rdflib.plugins.sparql.sparql.Query object
    """

    # We get in: (prologue, query)

    prologue = translatePrologue(q[0], base, initNs)

    # absolutize/resolve prefixes
    q[1] = traverse(
        q[1], visitPost=functools.partial(translatePName, prologue=prologue)
    )

    P, PV = translate(q[1])
    datasetClause = q[1].datasetClause
    if q[1].name == "ConstructQuery":

        template = triples(q[1].template) if q[1].template else None

        res = CompValue(q[1].name, p=P, template=template, datasetClause=datasetClause)
    else:
        res = CompValue(q[1].name, p=P, datasetClause=datasetClause, PV=PV)

    res = traverse(res, visitPost=simplify)
    _traverseAgg(res, visitor=analyse)
    _traverseAgg(res, _addVars)

    return Query(prologue, res)


class ExpressionNotCoveredException(Exception):
    pass


def translateAlgebra(query_algebra: Query):
    """

    :param query_algebra: An algebra returned by the function call algebra.translateQuery(parse_tree).
    :return: The query form generated from the SPARQL 1.1 algebra tree for select queries.

    """

    def overwrite(text):
        file = open("query.txt", "w+")
        file.write(text)
        file.close()

    def replace(
        old,
        new,
        search_from_match: str = None,
        search_from_match_occurrence: int = None,
        count: int = 1,
    ):
        # Read in the file
        with open("query.txt", "r") as file:
            filedata = file.read()

        def find_nth(haystack, needle, n):
            start = haystack.lower().find(needle)
            while start >= 0 and n > 1:
                start = haystack.lower().find(needle, start + len(needle))
                n -= 1
            return start

        if search_from_match and search_from_match_occurrence:
            position = find_nth(
                filedata, search_from_match, search_from_match_occurrence
            )
            filedata_pre = filedata[:position]
            filedata_post = filedata[position:].replace(old, new, count)
            filedata = filedata_pre + filedata_post
        else:
            filedata = filedata.replace(old, new, count)

        # Write the file out again
        with open("query.txt", "w") as file:
            file.write(filedata)

    def convert_node_arg(node_arg):
        if isinstance(node_arg, Identifier):
            return node_arg.n3()
        elif isinstance(node_arg, CompValue):
            return "{" + node_arg.name + "}"
        elif isinstance(node_arg, Expr):
            return "{" + node_arg.name + "}"
        elif isinstance(node_arg, str):
            return node_arg
        else:
            raise ExpressionNotCoveredException(
                "The expression {0} might not be covered yet.".format(node_arg)
            )

    def sparql_query_text(node):
        """
         https://www.w3.org/TR/sparql11-query/#sparqlSyntax

        :param node:
        :return:
        """

        if isinstance(node, CompValue):
            # 18.2 Query Forms
            if node.name == "SelectQuery":
                overwrite("-*-SELECT-*- " + "{" + node.p.name + "}")

            # 18.2 Graph Patterns
            elif node.name == "BGP":
                # Identifiers or Paths
                # Negated path throws a type error. Probably n3() method of negated paths should be fixed
                triples = "".join(
                    triple[0].n3() + " " + triple[1].n3() + " " + triple[2].n3() + "."
                    for triple in node.triples
                )
                replace("{BGP}", triples)
                # The dummy -*-SELECT-*- is placed during a SelectQuery or Multiset pattern in order to be able
                # to match extended variables in a specific Select-clause (see "Extend" below)
                replace("-*-SELECT-*-", "SELECT", count=-1)
                # If there is no "Group By" clause the placeholder will simply be deleted. Otherwise there will be
                # no matching {GroupBy} placeholder because it has already been replaced by "group by variables"
                replace("{GroupBy}", "", count=-1)
                replace("{Having}", "", count=-1)
            elif node.name == "Join":
                replace("{Join}", "{" + node.p1.name + "}{" + node.p2.name + "}")  #
            elif node.name == "LeftJoin":
                replace(
                    "{LeftJoin}",
                    "{" + node.p1.name + "}OPTIONAL{{" + node.p2.name + "}}",
                )
            elif node.name == "Filter":
                if isinstance(node.expr, CompValue):
                    expr = node.expr.name
                else:
                    raise ExpressionNotCoveredException(
                        "This expression might not be covered yet."
                    )
                if node.p:
                    # Filter with p=AggregateJoin = Having
                    if node.p.name == "AggregateJoin":
                        replace("{Filter}", "{" + node.p.name + "}")
                        replace("{Having}", "HAVING({" + expr + "})")
                    else:
                        replace(
                            "{Filter}", "FILTER({" + expr + "}) {" + node.p.name + "}"
                        )
                else:
                    replace("{Filter}", "FILTER({" + expr + "})")

            elif node.name == "Union":
                replace(
                    "{Union}", "{{" + node.p1.name + "}}UNION{{" + node.p2.name + "}}"
                )
            elif node.name == "Graph":
                expr = "GRAPH " + node.term.n3() + " {{" + node.p.name + "}}"
                replace("{Graph}", expr)
            elif node.name == "Extend":
                query_string = open("query.txt", "r").read().lower()
                select_occurrences = query_string.count("-*-select-*-")
                replace(
                    node.var.n3(),
                    "(" + convert_node_arg(node.expr) + " as " + node.var.n3() + ")",
                    search_from_match="-*-select-*-",
                    search_from_match_occurrence=select_occurrences,
                )
                replace("{Extend}", "{" + node.p.name + "}")
            elif node.name == "Minus":
                expr = "{" + node.p1.name + "}MINUS{{" + node.p2.name + "}}"
                replace("{Minus}", expr)
            elif node.name == "Group":
                group_by_vars = []
                if node.expr:
                    for var in node.expr:
                        if isinstance(var, Identifier):
                            group_by_vars.append(var.n3())
                        else:
                            raise ExpressionNotCoveredException(
                                "This expression might not be covered yet."
                            )
                    replace("{Group}", "{" + node.p.name + "}")
                    replace("{GroupBy}", "GROUP BY " + " ".join(group_by_vars) + " ")
                else:
                    replace("{Group}", "{" + node.p.name + "}")
            elif node.name == "AggregateJoin":
                replace("{AggregateJoin}", "{" + node.p.name + "}")
                for agg_func in node.A:
                    if isinstance(agg_func.res, Identifier):
                        identifier = agg_func.res.n3()
                    else:
                        raise ExpressionNotCoveredException(
                            "This expression might not be covered yet."
                        )
                    agg_func_name = agg_func.name.split("_")[1]
                    distinct = ""
                    if agg_func.distinct:
                        distinct = agg_func.distinct + " "
                    if agg_func_name == "GroupConcat":
                        replace(
                            identifier,
                            "GROUP_CONCAT"
                            + "("
                            + distinct
                            + agg_func.vars.n3()
                            + ";SEPARATOR="
                            + agg_func.separator.n3()
                            + ")",
                        )
                    else:
                        replace(
                            identifier,
                            agg_func_name.upper()
                            + "("
                            + distinct
                            + convert_node_arg(agg_func.vars)
                            + ")",
                        )
                    # For non-aggregated variables the aggregation function "sample" is automatically assigned.
                    # However, we do not want to have "sample" wrapped around non-aggregated variables. That is
                    # why we replace it. If "sample" is used on purpose it will not be replaced as the alias
                    # must be different from the variable in this case.
                    replace(
                        "(SAMPLE({0}) as {0})".format(convert_node_arg(agg_func.vars)),
                        convert_node_arg(agg_func.vars),
                    )
            elif node.name == "GroupGraphPatternSub":
                replace(
                    "GroupGraphPatternSub",
                    " ".join([convert_node_arg(pattern) for pattern in node.part]),
                )
            elif node.name == "TriplesBlock":
                print("triplesblock")
                replace(
                    "{TriplesBlock}",
                    "".join(
                        triple[0].n3()
                        + " "
                        + triple[1].n3()
                        + " "
                        + triple[2].n3()
                        + "."
                        for triple in node.triples
                    ),
                )

            # 18.2 Solution modifiers
            elif node.name == "ToList":
                raise ExpressionNotCoveredException(
                    "This expression might not be covered yet."
                )
            elif node.name == "OrderBy":
                order_conditions = []
                for c in node.expr:
                    if isinstance(c.expr, Identifier):
                        var = c.expr.n3()
                        if c.order is not None:
                            cond = var + "(" + c.order + ")"
                        else:
                            cond = var
                        order_conditions.append(cond)
                    else:
                        raise ExpressionNotCoveredException(
                            "This expression might not be covered yet."
                        )
                replace("{OrderBy}", "{" + node.p.name + "}")
                replace("{OrderConditions}", " ".join(order_conditions) + " ")
            elif node.name == "Project":
                project_variables = []
                for var in node.PV:
                    if isinstance(var, Identifier):
                        project_variables.append(var.n3())
                    else:
                        raise ExpressionNotCoveredException(
                            "This expression might not be covered yet."
                        )
                order_by_pattern = ""
                if node.p.name == "OrderBy":
                    order_by_pattern = "ORDER BY {OrderConditions}"
                replace(
                    "{Project}",
                    " ".join(project_variables)
                    + "{{"
                    + node.p.name
                    + "}}"
                    + "{GroupBy}"
                    + order_by_pattern
                    + "{Having}",
                )
            elif node.name == "Distinct":
                replace("{Distinct}", "DISTINCT {" + node.p.name + "}")
            elif node.name == "Reduced":
                replace("{Reduced}", "REDUCED {" + node.p.name + "}")
            elif node.name == "Slice":
                slice = "OFFSET " + str(node.start) + " LIMIT " + str(node.length)
                replace("{Slice}", "{" + node.p.name + "}" + slice)
            elif node.name == "ToMultiSet":
                if node.p.name == "values":
                    replace("{ToMultiSet}", "{{" + node.p.name + "}}")
                else:
                    replace(
                        "{ToMultiSet}", "{-*-SELECT-*- " + "{" + node.p.name + "}" + "}"
                    )

            # 18.2 Property Path

            # 17 Expressions and Testing Values
            # # 17.3 Operator Mapping
            elif node.name == "RelationalExpression":
                expr = convert_node_arg(node.expr)
                op = node.op
                if isinstance(list, type(node.other)):
                    other = (
                        "("
                        + ", ".join(convert_node_arg(expr) for expr in node.other)
                        + ")"
                    )
                else:
                    other = convert_node_arg(node.other)
                condition = "{left} {operator} {right}".format(
                    left=expr, operator=op, right=other
                )
                replace("{RelationalExpression}", condition)
            elif node.name == "ConditionalAndExpression":
                inner_nodes = " && ".join(
                    [convert_node_arg(expr) for expr in node.other]
                )
                replace(
                    "{ConditionalAndExpression}",
                    convert_node_arg(node.expr) + " && " + inner_nodes,
                )
            elif node.name == "ConditionalOrExpression":
                inner_nodes = " || ".join(
                    [convert_node_arg(expr) for expr in node.other]
                )
                replace(
                    "{ConditionalOrExpression}",
                    "(" + convert_node_arg(node.expr) + " || " + inner_nodes + ")",
                )
            elif node.name == "MultiplicativeExpression":
                left_side = convert_node_arg(node.expr)
                multiplication = left_side
                for i, operator in enumerate(node.op):
                    multiplication += (
                        operator + " " + convert_node_arg(node.other[i]) + " "
                    )
                replace("{MultiplicativeExpression}", multiplication)
            elif node.name == "AdditiveExpression":
                left_side = convert_node_arg(node.expr)
                addition = left_side
                for i, operator in enumerate(node.op):
                    addition += operator + " " + convert_node_arg(node.other[i]) + " "
                replace("{AdditiveExpression}", addition)
            elif node.name == "UnaryNot":
                replace("{UnaryNot}", "!" + convert_node_arg(node.expr))

            # # 17.4 Function Definitions
            # # # 17.4.1 Functional Forms
            elif node.name.endswith("BOUND"):
                bound_var = convert_node_arg(node.arg)
                replace("{Builtin_BOUND}", "bound(" + bound_var + ")")
            elif node.name.endswith("IF"):
                arg2 = convert_node_arg(node.arg2)
                arg3 = convert_node_arg(node.arg3)

                if_expression = (
                    "IF(" + "{" + node.arg1.name + "}, " + arg2 + ", " + arg3 + ")"
                )
                replace("{Builtin_IF}", if_expression)
            elif node.name.endswith("COALESCE"):
                replace(
                    "{Builtin_COALESCE}",
                    "COALESCE("
                    + ", ".join(convert_node_arg(arg) for arg in node.arg)
                    + ")",
                )
            elif node.name.endswith("Builtin_EXISTS"):
                # The node's name which we get with node.graph.name returns "Join" instead of GroupGraphPatternSub
                # According to https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#rExistsFunc
                # ExistsFunc can only have a GroupGraphPattern as parameter. However, when we print the query algebra
                # we get a GroupGraphPatternSub
                replace("{Builtin_EXISTS}", "EXISTS " + "{{" + node.graph.name + "}}")
                traverse(node.graph, visitPre=sparql_query_text)
                return node.graph
            elif node.name.endswith("Builtin_NOTEXISTS"):
                # The node's name which we get with node.graph.name returns "Join" instead of GroupGraphPatternSub
                # According to https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#rNotExistsFunc
                # NotExistsFunc can only have a GroupGraphPattern as parameter. However, when we print the query algebra
                # we get a GroupGraphPatternSub
                print(node.graph.name)
                replace(
                    "{Builtin_NOTEXISTS}", "NOT EXISTS " + "{{" + node.graph.name + "}}"
                )
                traverse(node.graph, visitPre=sparql_query_text)
                return node.graph
            # # # # 17.4.1.5 logical-or: Covered in "RelationalExpression"
            # # # # 17.4.1.6 logical-and: Covered in "RelationalExpression"
            # # # # 17.4.1.7 RDFterm-equal: Covered in "RelationalExpression"
            elif node.name.endswith("sameTerm"):
                replace(
                    "{Builtin_sameTerm}",
                    "SAMETERM("
                    + convert_node_arg(node.arg1)
                    + ", "
                    + convert_node_arg(node.arg2)
                    + ")",
                )
            # # # # IN: Covered in "RelationalExpression"
            # # # # NOT IN: Covered in "RelationalExpression"

            # # # 17.4.2 Functions on RDF Terms
            elif node.name.endswith("Builtin_isIRI"):
                replace("{Builtin_isIRI}", "isIRI(" + convert_node_arg(node.arg) + ")")
            elif node.name.endswith("Builtin_isBLANK"):
                replace(
                    "{Builtin_isBLANK}", "isBLANK(" + convert_node_arg(node.arg) + ")"
                )
            elif node.name.endswith("Builtin_isLITERAL"):
                replace(
                    "{Builtin_isLITERAL}",
                    "isLITERAL(" + convert_node_arg(node.arg) + ")",
                )
            elif node.name.endswith("Builtin_isNUMERIC"):
                replace(
                    "{Builtin_isNUMERIC}",
                    "isNUMERIC(" + convert_node_arg(node.arg) + ")",
                )
            elif node.name.endswith("Builtin_STR"):
                replace("{Builtin_STR}", "STR(" + convert_node_arg(node.arg) + ")")
            elif node.name.endswith("Builtin_LANG"):
                replace("{Builtin_LANG}", "LANG(" + convert_node_arg(node.arg) + ")")
            elif node.name.endswith("Builtin_DATATYPE"):
                replace(
                    "{Builtin_DATATYPE}", "DATATYPE(" + convert_node_arg(node.arg) + ")"
                )
            elif node.name.endswith("Builtin_IRI"):
                replace("{Builtin_IRI}", "IRI(" + convert_node_arg(node.arg) + ")")
            elif node.name.endswith("Builtin_BNODE"):
                replace("{Builtin_BNODE}", "BNODE(" + convert_node_arg(node.arg) + ")")
            elif node.name.endswith("STRDT"):
                replace(
                    "{Builtin_STRDT}",
                    "STRDT("
                    + convert_node_arg(node.arg1)
                    + ", "
                    + convert_node_arg(node.arg2)
                    + ")",
                )
            elif node.name.endswith("Builtin_STRLANG"):
                replace(
                    "{Builtin_STRLANG}",
                    "STRLANG("
                    + convert_node_arg(node.arg1)
                    + ", "
                    + convert_node_arg(node.arg2)
                    + ")",
                )
            elif node.name.endswith("Builtin_UUID"):
                replace("{Builtin_UUID}", "UUID()")
            elif node.name.endswith("Builtin_STRUUID"):
                replace("{Builtin_STRUUID}", "STRUUID()")

            # # # 17.4.3 Functions on Strings
            elif node.name.endswith("Builtin_STRLEN"):
                replace(
                    "{Builtin_STRLEN}", "STRLEN(" + convert_node_arg(node.arg) + ")"
                )
            elif node.name.endswith("Builtin_SUBSTR"):
                args = [node.arg.n3(), node.start]
                if node.length:
                    args.append(node.length)
                expr = "SUBSTR(" + ", ".join(args) + ")"
                replace("{Builtin_SUBSTR}", expr)
            elif node.name.endswith("Builtin_UCASE"):
                replace("{Builtin_UCASE}", "UCASE(" + convert_node_arg(node.arg) + ")")
            elif node.name.endswith("Builtin_LCASE"):
                replace("{Builtin_LCASE}", "LCASE(" + convert_node_arg(node.arg) + ")")
            elif node.name.endswith("Builtin_STRSTARTS"):
                replace(
                    "{Builtin_STRSTARTS}",
                    "STRSTARTS("
                    + convert_node_arg(node.arg1)
                    + ", "
                    + convert_node_arg(node.arg2)
                    + ")",
                )
            elif node.name.endswith("Builtin_STRENDS"):
                replace(
                    "{Builtin_STRENDS}",
                    "STRENDS("
                    + convert_node_arg(node.arg1)
                    + ", "
                    + convert_node_arg(node.arg2)
                    + ")",
                )
            elif node.name.endswith("Builtin_CONTAINS"):
                replace(
                    "{Builtin_CONTAINS}",
                    "CONTAINS("
                    + convert_node_arg(node.arg1)
                    + ", "
                    + convert_node_arg(node.arg2)
                    + ")",
                )
            elif node.name.endswith("Builtin_STRBEFORE"):
                replace(
                    "{Builtin_STRBEFORE}",
                    "STRBEFORE("
                    + convert_node_arg(node.arg1)
                    + ", "
                    + convert_node_arg(node.arg2)
                    + ")",
                )
            elif node.name.endswith("Builtin_STRAFTER"):
                replace(
                    "{Builtin_STRAFTER}",
                    "STRAFTER("
                    + convert_node_arg(node.arg1)
                    + ", "
                    + convert_node_arg(node.arg2)
                    + ")",
                )
            elif node.name.endswith("Builtin_ENCODE_FOR_URI"):
                replace(
                    "{Builtin_ENCODE_FOR_URI}",
                    "ENCODE_FOR_URI(" + convert_node_arg(node.arg) + ")",
                )
            elif node.name.endswith("Builtin_CONCAT"):
                expr = "CONCAT({vars})".format(
                    vars=", ".join(elem.n3() for elem in node.arg)
                )
                replace("{Builtin_CONCAT}", expr)
            elif node.name.endswith("Builtin_LANGMATCHES"):
                replace(
                    "{Builtin_LANGMATCHES}",
                    "LANGMATCHES("
                    + convert_node_arg(node.arg1)
                    + ", "
                    + convert_node_arg(node.arg2)
                    + ")",
                )
            elif node.name.endswith("REGEX"):
                args = [convert_node_arg(node.text), convert_node_arg(node.pattern)]
                expr = "REGEX(" + ", ".join(args) + ")"
                replace("{Builtin_REGEX}", expr)
            elif node.name.endswith("REPLACE"):
                replace(
                    "{Builtin_REPLACE}",
                    "REPLACE("
                    + convert_node_arg(node.arg)
                    + ", "
                    + convert_node_arg(node.pattern)
                    + ", "
                    + convert_node_arg(node.replacement)
                    + ")",
                )

            # # # 17.4.4 Functions on Numerics
            elif node.name == "Builtin_ABS":
                replace("{Builtin_ABS}", "ABS(" + convert_node_arg(node.arg) + ")")
            elif node.name == "Builtin_ROUND":
                replace("{Builtin_ROUND}", "ROUND(" + convert_node_arg(node.arg) + ")")
            elif node.name == "Builtin_CEIL":
                replace("{Builtin_CEIL}", "CEIL(" + convert_node_arg(node.arg) + ")")
            elif node.name == "Builtin_FLOOR":
                replace("{Builtin_FLOOR}", "FLOOR(" + convert_node_arg(node.arg) + ")")
            elif node.name == "Builtin_RAND":
                replace("{Builtin_RAND}", "RAND()")

            # # # 17.4.5 Functions on Dates and Times
            elif node.name == "Builtin_NOW":
                replace("{Builtin_NOW}", "NOW()")
            elif node.name == "Builtin_YEAR":
                replace("{Builtin_YEAR}", "YEAR(" + convert_node_arg(node.arg) + ")")
            elif node.name == "Builtin_MONTH":
                replace("{Builtin_MONTH}", "MONTH(" + convert_node_arg(node.arg) + ")")
            elif node.name == "Builtin_DAY":
                replace("{Builtin_DAY}", "DAY(" + convert_node_arg(node.arg) + ")")
            elif node.name == "Builtin_HOURS":
                replace("{Builtin_HOURS}", "HOURS(" + convert_node_arg(node.arg) + ")")
            elif node.name == "Builtin_MINUTES":
                replace(
                    "{Builtin_MINUTES}", "MINUTES(" + convert_node_arg(node.arg) + ")"
                )
            elif node.name == "Builtin_SECONDS":
                replace(
                    "{Builtin_SECONDS}", "SECONDS(" + convert_node_arg(node.arg) + ")"
                )
            elif node.name == "Builtin_TIMEZONE":
                replace(
                    "{Builtin_TIMEZONE}", "TIMEZONE(" + convert_node_arg(node.arg) + ")"
                )
            elif node.name == "Builtin_TZ":
                replace("{Builtin_TZ}", "TZ(" + convert_node_arg(node.arg) + ")")

            # # # 17.4.6 Hash functions
            elif node.name == "Builtin_MD5":
                replace("{Builtin_MD5}", "MD5(" + convert_node_arg(node.arg) + ")")
            elif node.name == "Builtin_SHA1":
                replace("{Builtin_SHA1}", "SHA1(" + convert_node_arg(node.arg) + ")")
            elif node.name == "Builtin_SHA256":
                replace(
                    "{Builtin_SHA256}", "SHA256(" + convert_node_arg(node.arg) + ")"
                )
            elif node.name == "Builtin_SHA384":
                replace(
                    "{Builtin_SHA384}", "SHA384(" + convert_node_arg(node.arg) + ")"
                )
            elif node.name == "Builtin_SHA512":
                replace(
                    "{Builtin_SHA512}", "SHA512(" + convert_node_arg(node.arg) + ")"
                )

            # Other
            elif node.name == "values":
                columns = []
                for key in node.res[0].keys():
                    if isinstance(key, Identifier):
                        columns.append(key.n3())
                    else:
                        raise ExpressionNotCoveredException(
                            "The expression {0} might not be covered yet.".format(key)
                        )
                values = "VALUES (" + " ".join(columns) + ")"

                rows = ""
                for elem in node.res:
                    row = []
                    for term in elem.values():
                        if isinstance(term, Identifier):
                            row.append(
                                term.n3()
                            )  # n3() is not part of Identifier class but every subclass has it
                        elif isinstance(term, str):
                            row.append(term)
                        else:
                            raise ExpressionNotCoveredException(
                                "The expression {0} might not be covered yet.".format(
                                    term
                                )
                            )
                    rows += "(" + " ".join(row) + ")"

                replace("values", values + "{" + rows + "}")
            elif node.name == "ServiceGraphPattern":
                replace(
                    "{ServiceGraphPattern}",
                    "SERVICE "
                    + convert_node_arg(node.term)
                    + "{"
                    + node.graph.name
                    + "}",
                )
                traverse(node.graph, visitPre=sparql_query_text)
                return node.graph
            # else:
            #     raise ExpressionNotCoveredException("The expression {0} might not be covered yet.".format(node.name))

    traverse(query_algebra.algebra, visitPre=sparql_query_text)
    query_from_algebra = open("query.txt", "r").read()
    os.remove("query.txt")

    return query_from_algebra


def pprintAlgebra(q):
    def pp(p, ind="    "):
        # if isinstance(p, list):
        #     print "[ "
        #     for x in p: pp(x,ind)
        #     print "%s ]"%ind
        #     return
        if not isinstance(p, CompValue):
            print(p)
            return
        print("%s(" % (p.name,))
        for k in p:
            print(
                "%s%s ="
                % (
                    ind,
                    k,
                ),
                end=" ",
            )
            pp(p[k], ind + "    ")
        print("%s)" % ind)

    try:
        pp(q.algebra)
    except AttributeError:
        # it's update, just a list
        for x in q:
            pp(x)


if __name__ == "__main__":
    import sys
    from rdflib.plugins.sparql import parser
    import os.path

    if os.path.exists(sys.argv[1]):
        q = open(sys.argv[1]).read()
    else:
        q = sys.argv[1]

    pq = parser.parseQuery(q)
    print(pq)
    print("--------")
    tq = translateQuery(pq)
    pprintAlgebra(tq)
