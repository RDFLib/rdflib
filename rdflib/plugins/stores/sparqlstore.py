"""
This is an RDFLib store around Ivan Herman et al.'s SPARQL service wrapper.
This was first done in layer-cake, and then ported to RDFLib
"""

from __future__ import annotations

import collections
import re
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    Union,
    cast,
    overload,
)

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Graph
from rdflib.plugins.stores.regexmatching import NATIVE_REGEX
from rdflib.store import Store
from rdflib.term import (
    BNode,
    IdentifiedNode,
    Identifier,
    Literal,
    Node,
    URIRef,
    Variable,
)

if TYPE_CHECKING:
    import typing_extensions as te  # noqa: I001
    from collections.abc import Mapping, Iterator, Iterable, Generator
    from rdflib.graph import (
        _TripleType,
        _ContextType,
        _QuadType,
        _TriplePatternType,
        _SubjectType,
        _PredicateType,
        _ObjectType,
        _ContextIdentifierType,
    )
    from rdflib.plugins.sparql.sparql import Query, Update
    from rdflib.query import Result, ResultRow
    from .sparqlconnector import SUPPORTED_FORMATS, SUPPORTED_METHODS

from .sparqlconnector import SPARQLConnector

# Defines some SPARQL keywords
LIMIT = "LIMIT"
OFFSET = "OFFSET"
ORDERBY = "ORDER BY"

BNODE_IDENT_PATTERN = re.compile(r"(?P<label>_\:[^\s]+)")

_NodeToSparql: te.TypeAlias = Callable[["Node"], str]


def _node_to_sparql(node: Node) -> str:
    if isinstance(node, BNode):
        raise Exception(
            "SPARQLStore does not support BNodes! "
            "See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes"
        )
    return node.n3()


class SPARQLStore(SPARQLConnector, Store):
    """An RDFLib store around a SPARQL endpoint.

    This is context-aware and should work as expected
    when a context is specified.

    ### Usage example

    ```python
    >>> from rdflib import Dataset
    >>> from rdflib.plugins.stores.sparqlstore import SPARQLStore
    >>>
    >>> g = Dataset(
    ...    SPARQLStore("https://query.wikidata.org/sparql", returnFormat="xml"),
    ...    default_union=True
    ... )
    >>>
    >>> res = g.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5")
    >>>
    >>> # Iterate the results
    >>> for row in res:
    ...     pass  # but really you'd do something like: print(row)
    >>>
    >>> # Or serialize the results
    >>> # something like: print(res.serialize(format="json").decode())
    ```

    !!! warning "Not all SPARQL endpoints support the same features"

        Checkout the `test suite on public endpoints <https://github.com/RDFLib/rdflib/blob/main/test/test_store/test_store_sparqlstore_public.py>`_
        for more details on how to successfully query different types of endpoints.

    For ConjunctiveGraphs, reading is done from the "default graph". Exactly
    what this means depends on your endpoint, because SPARQL does not offer a
    simple way to query the union of all graphs as it would be expected for a
    ConjuntiveGraph. This is why we recommend using Dataset instead, which is
    motivated by the SPARQL 1.1.

    Fuseki/TDB has a flag for specifying that the default graph
    is the union of all graphs (`tdb:unionDefaultGraph` in the Fuseki config).

    !!! warning "Blank nodes

        By default, the SPARQL Store does not support blank-nodes!

        As blank-nodes act as variables in SPARQL queries,
        there is no way to query for a particular blank node without
        using non-standard SPARQL extensions.

        See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes

    You can make use of such extensions through the `node_to_sparql`
    argument. For example if you want to transform BNode('0001') into
    "<bnode:b0001>", you can use a function like this:

    ```python
    >> def my_bnode_ext(node):
    ...     if isinstance(node, BNode):
    ...         return f"<bnode:b{node}>"
    ...     return _node_to_sparql(node)
    ...
    >> store = SPARQLStore(
    ...     "http://dbpedia.org/sparql",
    ...     node_to_sparql=my_bnode_ext
    ... )
    ```

    You can request a particular result serialization with the
    `returnFormat` parameter. This is a string that must have a
    matching plugin registered. Built in is support for `xml`,
    `json`, `csv`, `tsv` and `application/rdf+xml`.

    The underlying SPARQLConnector uses the urllib library.
    Any extra kwargs passed to the SPARQLStore connector are passed to
    urllib when doing HTTP calls. I.e. you have full control of
    cookies/auth/headers.

    HTTP basic auth is available with:

    ```python
    >> store = SPARQLStore('...my endpoint ...', auth=('user','pass'))
    ```
    """

    formula_aware = False
    transaction_aware = False
    graph_aware = True
    regex_matching = NATIVE_REGEX

    def __init__(
        self,
        query_endpoint: str | None = None,
        sparql11: bool = True,
        context_aware: bool = True,
        node_to_sparql: _NodeToSparql = _node_to_sparql,
        returnFormat: SUPPORTED_FORMATS = "xml",  # noqa: N803
        method: SUPPORTED_METHODS = "GET",
        auth: tuple[str, str] | None = None,
        **sparqlconnector_kwargs,
    ):
        super(SPARQLStore, self).__init__(
            query_endpoint=query_endpoint,
            returnFormat=returnFormat,
            method=method,
            auth=auth,
            **sparqlconnector_kwargs,
        )

        self.node_to_sparql = node_to_sparql
        self.nsBindings: dict[str, Any] = {}
        self.sparql11 = sparql11
        self.context_aware = context_aware
        self.graph_aware = context_aware
        self._queries = 0

    # type error: Missing return statement
    def open(self, configuration: str, create: bool = False) -> int | None:  # type: ignore[return]
        """This method is included so that calls to this Store via Graph, e.g. Graph("SPARQLStore"),
        can set the required parameters
        """
        if type(configuration) == str:  # noqa: E721
            self.query_endpoint = configuration
        else:
            raise Exception(
                "configuration must be a string (a single query endpoint URI)"
            )

    # Database Management Methods
    def create(self, configuration: str) -> None:
        raise TypeError(
            "The SPARQL Store is read only. Try SPARQLUpdateStore for read/write."
        )

    def destroy(self, configuration: str) -> None:
        raise TypeError("The SPARQL store is read only")

    # Transactional interfaces
    def commit(self) -> None:
        raise TypeError("The SPARQL store is read only")

    def rollback(self) -> None:
        raise TypeError("The SPARQL store is read only")

    def add(
        self, _: _TripleType, context: _ContextType = None, quoted: bool = False
    ) -> None:
        raise TypeError("The SPARQL store is read only")

    def addN(self, quads: Iterable[_QuadType]) -> None:  # noqa: N802
        raise TypeError("The SPARQL store is read only")

    # type error: Signature of "remove" incompatible with supertype "Store"
    def remove(  # type: ignore[override]
        self, _: _TriplePatternType, context: _ContextType | None
    ) -> None:
        raise TypeError("The SPARQL store is read only")

    # type error: Signature of "update" incompatible with supertype "SPARQLConnector"
    def update(  # type: ignore[override]
        self,
        query: Union[Update, str],
        initNs: dict[str, Any] = {},  # noqa: N803
        initBindings: dict[str, Identifier] = {},  # noqa: N803
        queryGraph: Identifier = None,  # noqa: N803
        DEBUG: bool = False,  # noqa: N803
    ) -> None:
        raise TypeError("The SPARQL store is read only")

    def _query(self, *args: Any, **kwargs: Any) -> Result:
        self._queries += 1

        return super(SPARQLStore, self).query(*args, **kwargs)

    def _inject_prefixes(self, query: str, extra_bindings: Mapping[str, Any]) -> str:
        bindings = set(list(self.nsBindings.items()) + list(extra_bindings.items()))
        if not bindings:
            return query
        return "\n".join(
            [
                "\n".join(["PREFIX %s: <%s>" % (k, v) for k, v in bindings]),
                "",  # separate ns_bindings from query with an empty line
                query,
            ]
        )

    # type error: Signature of "query" incompatible with supertype "SPARQLConnector"
    # type error: Signature of "query" incompatible with supertype "Store"
    def query(  # type: ignore[override]
        self,
        query: Union[Query, str],
        initNs: Mapping[str, Any] | None = None,  # noqa: N803
        initBindings: Mapping[str, Identifier] | None = None,  # noqa: N803
        queryGraph: str | None = None,  # noqa: N803
        DEBUG: bool = False,  # noqa: N803
    ) -> Result:
        self.debug = DEBUG
        assert isinstance(query, str)

        if initNs is not None and len(initNs) > 0:
            query = self._inject_prefixes(query, initNs)

        if initBindings:
            if not self.sparql11:
                raise Exception("initBindings not supported for SPARQL 1.0 Endpoints.")
            v = list(initBindings)

            # VALUES was added to SPARQL 1.1 on 2012/07/24
            query += "\nVALUES ( %s )\n{ ( %s ) }\n" % (
                " ".join("?" + str(x) for x in v),
                " ".join(self.node_to_sparql(initBindings[x]) for x in v),
            )

        return self._query(
            query, default_graph=queryGraph if self._is_contextual(queryGraph) else None
        )

    # type error: Return type "Iterator[tuple[tuple[Node, Node, Node], None]]" of "triples" incompatible with return type "Iterator[tuple[tuple[Node, Node, Node], Iterator[Optional[Graph]]]]"
    def triples(  # type: ignore[override]
        self, spo: _TriplePatternType, context: _ContextType | None = None
    ) -> Iterator[tuple[_TripleType, None]]:
        """
        - tuple **(s, o, p)**
          the triple used as filter for the SPARQL select.
          (None, None, None) means anything.
        - context **context**
          the graph effectively calling this method.

        Returns a tuple of triples executing essentially a SPARQL like
        SELECT ?subj ?pred ?obj WHERE { ?subj ?pred ?obj }

        **context** may include three parameter
        to refine the underlying query:

        * LIMIT: an integer to limit the number of results
        * OFFSET: an integer to enable paging of results
        * ORDERBY: an instance of Variable('s'), Variable('o') or Variable('p') or, by default, the first 'None' from the given triple

        !!! warning "Limit and offset

            - Using LIMIT or OFFSET automatically include ORDERBY otherwise this is
              because the results are retrieved in a not deterministic way (depends on
              the walking path on the graph)
            - Using OFFSET without defining LIMIT will discard the first OFFSET - 1 results

        ```python
        a_graph.LIMIT = limit
        a_graph.OFFSET = offset
        triple_generator = a_graph.triples(mytriple):
        # do something
        # Removes LIMIT and OFFSET if not required for the next triple() calls
        del a_graph.LIMIT
        del a_graph.OFFSET
        ```
        """

        p: IdentifiedNode | Variable
        s: IdentifiedNode | Literal | Variable
        o: IdentifiedNode | Literal | Variable
        _s, _p, _o = spo

        vars: list[Variable] = []
        if _s is None:
            s = Variable("s")
            vars.append(s)
        elif isinstance(_s, Variable):
            s = _s
            vars.append(s)
        # Technically we should check for QuotedGraph here, to make MyPy happy
        elif isinstance(_s, Graph):  # type: ignore[unreachable]
            raise ValueError("Cannot use a Graph as subject in SPARQLStore.")
        else:
            s = _s

        if _p is None:
            p = Variable("p")
            vars.append(p)
        else:
            p = _p

        if _o is None:
            o = Variable("o")
            vars.append(o)
        elif isinstance(_o, Variable):
            o = _o
            vars.append(o)
        # Technically we should check for QuotedGraph here, to make MyPy happy
        elif isinstance(_o, Graph):  # type: ignore[unreachable]
            raise ValueError("Cannot use a Graph as object in SPARQLStore.")
        else:
            o = _o
        if vars:
            v = " ".join([term.n3() for term in vars])
            verb = "SELECT %s " % v
        else:
            verb = "ASK"

        nts = self.node_to_sparql
        query = "%s { %s %s %s }" % (verb, nts(s), nts(p), nts(o))

        # The ORDER BY is necessary
        if (
            hasattr(context, LIMIT)
            or hasattr(context, OFFSET)
            or hasattr(context, ORDERBY)
        ):
            var = None
            if isinstance(s, Variable):
                var = s
            elif isinstance(p, Variable):
                var = p
            elif isinstance(o, Variable):
                var = o
            elif hasattr(context, ORDERBY) and isinstance(
                getattr(context, ORDERBY), Variable
            ):
                var = getattr(context, ORDERBY)
            # type error: Item "None" of "Optional[Variable]" has no attribute "n3"
            query = query + " %s %s" % (ORDERBY, var.n3())  # type: ignore[union-attr]

        try:
            query = query + " LIMIT %s" % int(getattr(context, LIMIT))
        except (ValueError, TypeError, AttributeError):
            pass
        try:
            query = query + " OFFSET %s" % int(getattr(context, OFFSET))
        except (ValueError, TypeError, AttributeError):
            pass

        result = self._query(
            query,
            # type error: Item "None" of "Optional[Graph]" has no attribute "identifier"
            default_graph=context.identifier if self._is_contextual(context) else None,  # type: ignore[union-attr]
        )

        if vars:
            if type(result) is tuple:
                if result[0] == 401:
                    raise ValueError(
                        "It looks like you need to authenticate with this SPARQL Store. HTTP unauthorized"
                    )
            for row in result:
                if TYPE_CHECKING:
                    # This will be a ResultRow because if vars is truthish then
                    # the query will be a SELECT query.
                    assert isinstance(row, ResultRow)
                yield (
                    (
                        row.get(s, URIRef(f"urn:undef:{s}"))
                        if isinstance(s, Variable)
                        else row.get(s, s)
                    ),
                    # TODO: getting value of ?p variable can return a Literal,
                    #  but literal cannot be yielded in the predicate slot.
                    cast(
                        IdentifiedNode,
                        (
                            row.get(p, URIRef(f"urn:undef:{p}"))
                            if isinstance(p, Variable)
                            else row.get(p, p)
                        ),
                    ),
                    (
                        row.get(o, URIRef(f"urn:undef:{o}"))
                        if isinstance(o, Variable)
                        else row.get(o, o)
                    ),
                ), None  # why is the context here not the passed in graph 'context'?
        else:
            if result.askAnswer:
                yield (s, cast(IdentifiedNode, p), o), None

    def triples_choices(
        self,
        _: (
            tuple[
                list[_SubjectType] | tuple[_SubjectType, ...],
                _PredicateType,
                _ObjectType | None,
            ]
            | tuple[
                _SubjectType | None,
                list[_PredicateType] | tuple[_PredicateType, ...],
                _ObjectType | None,
            ]
            | tuple[
                _SubjectType | None,
                _PredicateType,
                list[_ObjectType] | tuple[_ObjectType, ...],
            ]
        ),
        context: _ContextType | None = None,
    ) -> Generator[
        tuple[
            _TripleType,
            Iterator[_ContextType | None],
        ],
        None,
        None,
    ]:
        """
        A variant of triples that can take a list of terms instead of a
        single term in any slot.  Stores can implement this to optimize
        the response time from the import default 'fallback' implementation,
        which will iterate over each term in the list and dispatch to
        triples.
        """
        raise NotImplementedError("Triples choices currently not supported")

    def __len__(self, context: _ContextType | None = None) -> int:
        if not self.sparql11:
            raise NotImplementedError(
                "For performance reasons, this is not"
                + "supported for sparql1.0 endpoints"
            )
        else:
            q = "SELECT (count(*) as ?c) WHERE {?s ?p ?o .}"

            result = self._query(
                q,
                # type error: Item "None" of "Optional[Graph]" has no attribute "identifier"
                default_graph=(
                    context.identifier  # type: ignore[union-attr]
                    if self._is_contextual(context)
                    else None
                ),
            )
            # type error: Item "tuple[Node, ...]" of "Union[tuple[Node, Node, Node], bool, ResultRow]" has no attribute "c"
            return int(next(iter(result)).c)  # type: ignore[union-attr]

    # type error: Return type "Generator[Identifier, None, None]" of "contexts" incompatible with return type "Generator[Graph, None, None]" in supertype "Store"
    def contexts(  # type: ignore[override]
        self, triple: _TripleType | None = None
    ) -> Generator[_ContextIdentifierType, None, None]:
        """
        Iterates over results to `SELECT ?NAME { GRAPH ?NAME { ?s ?p ?o } }`
        or `SELECT ?NAME { GRAPH ?NAME {} }` if triple is `None`.

        Returns instances of this store with the SPARQL wrapper
        object updated via addNamedGraph(?NAME).

        This causes a named-graph-uri key / value  pair to be sent over
        the protocol.

        Please note that some SPARQL endpoints are not able to find empty named
        graphs.
        """

        if triple:
            nts = self.node_to_sparql
            s, p, o = triple
            params = (
                nts(s if s else Variable("s")),
                nts(p if p else Variable("p")),
                nts(o if o else Variable("o")),
            )
            q = "SELECT ?name WHERE { GRAPH ?name { %s %s %s }}" % params
        else:
            q = "SELECT ?name WHERE { GRAPH ?name {} }"

        result = self._query(q)
        # type error: Item "bool" of "Union[tuple[Node, Node, Node], bool, ResultRow]" has no attribute "name"
        # error: Generator has incompatible item type "Union[Any, Identifier]"; expected "IdentifiedNode"
        return (row.name for row in result)  # type: ignore[union-attr,misc]

    # Namespace persistence interface implementation
    def bind(self, prefix: str, namespace: URIRef, override: bool = True) -> None:
        bound_prefix = self.prefix(namespace)
        if override and bound_prefix:
            del self.nsBindings[bound_prefix]
        self.nsBindings[prefix] = namespace

    def prefix(self, namespace: URIRef) -> str | None:
        """ """
        return dict([(v, k) for k, v in self.nsBindings.items()]).get(namespace)

    def namespace(self, prefix: str) -> URIRef | None:
        return self.nsBindings.get(prefix)

    def namespaces(self) -> Iterator[tuple[str, URIRef]]:
        for prefix, ns in self.nsBindings.items():
            yield prefix, ns

    def add_graph(self, graph: Graph) -> None:
        raise TypeError("The SPARQL store is read only")

    def remove_graph(self, graph: Graph) -> None:
        raise TypeError("The SPARQL store is read only")

    @overload
    def _is_contextual(self, graph: None) -> te.Literal[False]: ...

    @overload
    def _is_contextual(self, graph: Graph | str | None) -> bool: ...

    def _is_contextual(self, graph: Graph | str | None) -> bool:
        """Returns `True` if the "GRAPH" keyword must appear
        in the final SPARQL query sent to the endpoint.
        """
        if (not self.context_aware) or (graph is None):
            return False
        if isinstance(graph, str):
            return graph != "__UNION__"
        else:
            return graph.identifier != DATASET_DEFAULT_GRAPH_ID

    def subjects(
        self,
        predicate: _PredicateType | None = None,
        object: _ObjectType | None = None,
    ) -> Generator[_SubjectType, None, None]:
        """A generator of subjects with the given predicate and object"""
        for t, c in self.triples((None, predicate, object)):
            yield t[0]

    def predicates(
        self,
        subject: _SubjectType | None = None,
        object: _ObjectType | None = None,
    ) -> Generator[_PredicateType, None, None]:
        """A generator of predicates with the given subject and object"""
        for t, c in self.triples((subject, None, object)):
            yield t[1]

    def objects(
        self,
        subject: _SubjectType | None = None,
        predicate: _PredicateType | None = None,
    ) -> Generator[_ObjectType, None, None]:
        """A generator of objects with the given subject and predicate"""
        for t, c in self.triples((subject, predicate, None)):
            yield t[2]

    def subject_predicates(
        self, object: _ObjectType | None = None
    ) -> Generator[tuple[_SubjectType, _PredicateType], None, None]:
        """A generator of (subject, predicate) tuples for the given object"""
        for t, c in self.triples((None, None, object)):
            yield t[0], t[1]

    def subject_objects(
        self, predicate: _PredicateType | None = None
    ) -> Generator[tuple[_SubjectType, _ObjectType], None, None]:
        """A generator of (subject, object) tuples for the given predicate"""
        for t, c in self.triples((None, predicate, None)):
            yield t[0], t[2]

    def predicate_objects(
        self, subject: _SubjectType | None = None
    ) -> Generator[tuple[_PredicateType, _ObjectType], None, None]:
        """A generator of (predicate, object) tuples for the given subject"""
        for t, c in self.triples((subject, None, None)):
            yield t[1], t[2]


class SPARQLUpdateStore(SPARQLStore):
    """A store using SPARQL queries for reading and SPARQL Update for changes.

    This can be context-aware, if so, any changes will be to the given named
    graph only.

    In favor of the SPARQL 1.1 motivated Dataset, we advise against using this
    with ConjunctiveGraphs, as it reads and writes from and to the
    "default graph". Exactly what this means depends on the endpoint and can
    result in confusion.

    For Graph objects, everything works as expected.

    See the [`SPARQLStore`][rdflib.plugins.stores.sparqlstore.SPARQLStore] base class for more information.
    """

    where_pattern = re.compile(r"""(?P<where>WHERE\s*\{)""", re.IGNORECASE)

    ##############################################################
    # Regex for injecting GRAPH blocks into updates on a context #
    ##############################################################

    # Observations on the SPARQL grammar (http://www.w3.org/TR/2013/REC-sparql11-query-20130321/):
    # 1. Only the terminals STRING_LITERAL1, STRING_LITERAL2,
    #    STRING_LITERAL_LONG1, STRING_LITERAL_LONG2, and comments can contain
    #    curly braces.
    # 2. The non-terminals introduce curly braces in pairs only.
    # 3. Unescaped " can occur only in strings and comments.
    # 3. Unescaped ' can occur only in strings, comments, and IRIRefs.
    # 4. \ always escapes the following character, especially \", \', and
    #    \\ denote literal ", ', and \ respectively.
    # 5. # always starts a comment outside of string and IRI
    # 6. A comment ends at the next newline
    # 7. IRIREFs need to be detected, as they may contain # without starting a comment
    # 8. PrefixedNames do not contain a #
    # As a consequence, it should be rather easy to detect strings and comments
    # in order to avoid unbalanced curly braces.

    # From the SPARQL grammar
    STRING_LITERAL1 = "'([^'\\\\]|\\\\.)*'"
    STRING_LITERAL2 = '"([^"\\\\]|\\\\.)*"'
    STRING_LITERAL_LONG1 = "'''(('|'')?([^'\\\\]|\\\\.))*'''"
    STRING_LITERAL_LONG2 = '"""(("|"")?([^"\\\\]|\\\\.))*"""'
    String = "(%s)|(%s)|(%s)|(%s)" % (
        STRING_LITERAL1,
        STRING_LITERAL2,
        STRING_LITERAL_LONG1,
        STRING_LITERAL_LONG2,
    )
    IRIREF = '<([^<>"{}|^`\\]\\\\[\\x00-\\x20])*>'
    COMMENT = "#[^\\x0D\\x0A]*([\\x0D\\x0A]|\\Z)"

    # Simplified grammar to find { at beginning and } at end of blocks
    BLOCK_START = "{"
    BLOCK_END = "}"
    ESCAPED = "\\\\."

    # Match anything that doesn't start or end a block:
    BlockContent = "(%s)|(%s)|(%s)|(%s)" % (String, IRIREF, COMMENT, ESCAPED)
    BlockFinding = "(?P<block_start>%s)|(?P<block_end>%s)|(?P<block_content>%s)" % (
        BLOCK_START,
        BLOCK_END,
        BlockContent,
    )
    BLOCK_FINDING_PATTERN = re.compile(BlockFinding)

    # Note that BLOCK_FINDING_PATTERN.finditer() will not cover the whole
    # string with matches. Everything that is not matched will have to be
    # part of the modified query as is.

    ##################################################################

    def __init__(
        self,
        query_endpoint: str | None = None,
        update_endpoint: str | None = None,
        sparql11: bool = True,
        context_aware: bool = True,
        postAsEncoded: bool = True,  # noqa: N803
        autocommit: bool = True,
        dirty_reads: bool = False,
        **kwds,
    ):
        """
        Args:
            autocommit: if set, the store will commit after every
                writing operations. If False, we only make queries on the
                server once commit is called.
            dirty_reads if set, we do not commit before reading. So you
                cannot read what you wrote before manually calling commit.
        """

        SPARQLStore.__init__(
            self,
            query_endpoint,
            sparql11,
            context_aware,
            update_endpoint=update_endpoint,
            **kwds,
        )

        self.postAsEncoded = postAsEncoded
        self.autocommit = autocommit
        self.dirty_reads = dirty_reads
        self._edits: list[str] | None = None
        self._updates = 0

    def query(self, *args: Any, **kwargs: Any) -> Result:
        if not self.autocommit and not self.dirty_reads:
            self.commit()
        return SPARQLStore.query(self, *args, **kwargs)

    # type error: Signature of "triples" incompatible with supertype "Store"
    def triples(  # type: ignore[override]
        self, *args: Any, **kwargs: Any
    ) -> Iterator[tuple[_TripleType, None]]:
        if not self.autocommit and not self.dirty_reads:
            self.commit()
        return SPARQLStore.triples(self, *args, **kwargs)

    # type error: Signature of "contexts" incompatible with supertype "Store"
    def contexts(  # type: ignore[override]
        self, *args: Any, **kwargs: Any
    ) -> Generator[_ContextIdentifierType, None, None]:
        if not self.autocommit and not self.dirty_reads:
            self.commit()
        return SPARQLStore.contexts(self, *args, **kwargs)

    def __len__(self, *args: Any, **kwargs: Any) -> int:
        if not self.autocommit and not self.dirty_reads:
            self.commit()
        return SPARQLStore.__len__(self, *args, **kwargs)

    def open(
        self, configuration: Union[str, tuple[str, str]], create: bool = False
    ) -> None:
        """Sets the endpoint URLs for this `SPARQLStore`

        Args:
            configuration: either a tuple of (query_endpoint, update_endpoint),
                or a string with the endpoint which is configured as query and update endpoint
            create: if True an exception is thrown.
        """

        if create:
            raise Exception("Cannot create a SPARQL Endpoint")

        if isinstance(configuration, tuple):
            self.query_endpoint = configuration[0]
            if len(configuration) > 1:
                self.update_endpoint = configuration[1]
        else:
            self.query_endpoint = configuration
            self.update_endpoint = configuration

    def _transaction(self) -> list[str]:
        if self._edits is None:
            self._edits = []
        return self._edits

    # Transactional interfaces
    def commit(self) -> None:
        """`add()`, `addN()`, and `remove()` are transactional to reduce overhead of many small edits.
        Read and update() calls will automatically commit any outstanding edits.
        This should behave as expected most of the time, except that alternating writes
        and reads can degenerate to the original call-per-triple situation that originally existed.
        """
        if self._edits and len(self._edits) > 0:
            self._update("\n;\n".join(self._edits))
            self._edits = None

    def rollback(self) -> None:
        self._edits = None

    def add(
        self,
        spo: _TripleType,
        context: _ContextType | None = None,
        quoted: bool = False,
    ) -> None:
        """Add a triple to the store of triples."""

        if not self.update_endpoint:
            raise Exception("UpdateEndpoint is not set")

        assert not quoted
        (subject, predicate, obj) = spo

        nts = self.node_to_sparql
        triple = "%s %s %s ." % (nts(subject), nts(predicate), nts(obj))
        if self._is_contextual(context):
            if TYPE_CHECKING:
                # _is_contextual will never return true if context is None
                assert context is not None
            q = "INSERT DATA { GRAPH %s { %s } }" % (nts(context.identifier), triple)
        else:
            q = "INSERT DATA { %s }" % triple
        self._transaction().append(q)
        if self.autocommit:
            self.commit()

    def addN(self, quads: Iterable[_QuadType]) -> None:  # noqa: N802
        """Add a list of quads to the store."""
        if not self.update_endpoint:
            raise Exception("UpdateEndpoint is not set - call 'open'")

        contexts = collections.defaultdict(list)
        for subject, predicate, obj, context in quads:
            contexts[context].append((subject, predicate, obj))
        data: list[str] = []
        nts = self.node_to_sparql
        for context in contexts:
            triples = [
                "%s %s %s ." % (nts(subject), nts(predicate), nts(obj))
                for subject, predicate, obj in contexts[context]
            ]
            data.append(
                "INSERT DATA { GRAPH %s { %s } }\n"
                % (nts(context.identifier), "\n".join(triples))
            )
        self._transaction().extend(data)
        if self.autocommit:
            self.commit()

    # type error: Signature of "remove" incompatible with supertype "Store"
    def remove(  # type: ignore[override]
        self, spo: _TriplePatternType, context: _ContextType | None
    ) -> None:
        """Remove a triple from the store"""
        if not self.update_endpoint:
            raise Exception("UpdateEndpoint is not set - call 'open'")

        subject: _SubjectType
        predicate: _PredicateType
        obj: _ObjectType
        (_subject, _predicate, _obj) = spo
        if _subject is None:
            subject = Variable("S")
        else:
            subject = _subject
        if _predicate is None:
            predicate = Variable("P")
        else:
            predicate = _predicate
        if _obj is None:
            obj = Variable("O")
        else:
            obj = _obj

        nts = self.node_to_sparql
        triple = "%s %s %s ." % (nts(subject), nts(predicate), nts(obj))
        if self._is_contextual(context):
            if TYPE_CHECKING:
                # _is_contextual will never return true if context is None
                assert context is not None
            cid = nts(context.identifier)
            q = "WITH %(graph)s DELETE { %(triple)s } WHERE { %(triple)s }" % {
                "graph": cid,
                "triple": triple,
            }
        else:
            q = "DELETE { %s } WHERE { %s } " % (triple, triple)
        self._transaction().append(q)
        if self.autocommit:
            self.commit()

    def setTimeout(self, timeout) -> None:  # noqa: N802
        self._timeout = int(timeout)

    def _update(self, update):
        self._updates += 1

        SPARQLConnector.update(self, update)

    # type error: Signature of "update" incompatible with supertype "SPARQLConnector"
    # type error: Signature of "update" incompatible with supertype "Store"
    def update(  # type: ignore[override]
        self,
        query: Update | str,
        initNs: dict[str, Any] = {},  # noqa: N803
        initBindings: dict[str, Identifier] = {},  # noqa: N803
        queryGraph: str | None = None,  # noqa: N803
        DEBUG: bool = False,  # noqa: N803
    ):
        """Perform a SPARQL Update Query against the endpoint, INSERT, LOAD, DELETE etc.

        Setting initNs adds PREFIX declarations to the beginning of
        the update. Setting initBindings adds inline VALUEs to the
        beginning of every WHERE clause. By the SPARQL grammar, all
        operations that support variables (namely INSERT and DELETE)
        require a WHERE clause.
        Important: initBindings fails if the update contains the
        substring 'WHERE {' which does not denote a WHERE clause, e.g.
        if it is part of a literal.

        !!! info "Context-aware query rewriting"

            - **When:**  If context-awareness is enabled and the graph is not the default graph of the store.
            - **Why:** To ensure consistency with the [`Memory`][rdflib.plugins.stores.memory.Memory] store.
                The graph must accept "local" SPARQL requests (requests with no GRAPH keyword)
                as if it was the default graph.
            - **What is done:** These "local" queries are rewritten by this store.
                The content of each block of a SPARQL Update operation is wrapped in a GRAPH block
                except if the block is empty.
                This basically causes INSERT, INSERT DATA, DELETE, DELETE DATA and WHERE to operate
                only on the context.
            - **Example:** `"INSERT DATA { <urn:michel> <urn:likes> <urn:pizza> }"` is converted into
                `"INSERT DATA { GRAPH <urn:graph> { <urn:michel> <urn:likes> <urn:pizza> } }"`.
            - **Warning:** Queries are presumed to be "local" but this assumption is **not checked**.
                For instance, if the query already contains GRAPH blocks, the latter will be wrapped in new GRAPH blocks.
            - **Warning:** A simplified grammar is used that should tolerate
                extensions of the SPARQL grammar. Still, the process may fail in
                uncommon situations and produce invalid output.
        """
        if not self.update_endpoint:
            raise Exception("Update endpoint is not set!")

        self.debug = DEBUG
        assert isinstance(query, str)
        query = self._inject_prefixes(query, initNs)

        if self._is_contextual(queryGraph):
            if TYPE_CHECKING:
                # _is_contextual will never return true if context is None
                assert queryGraph is not None
            query = self._insert_named_graph(query, queryGraph)

        if initBindings:
            # For INSERT and DELETE the WHERE clause is obligatory
            # (http://www.w3.org/TR/2013/REC-sparql11-query-20130321/#rModify)
            # Other query types do not allow variables and don't
            # have a WHERE clause.  This also works for updates with
            # more than one INSERT/DELETE.
            v = list(initBindings)
            values = "\nVALUES ( %s )\n{ ( %s ) }\n" % (
                " ".join("?" + str(x) for x in v),
                " ".join(self.node_to_sparql(initBindings[x]) for x in v),
            )

            query = self.where_pattern.sub("WHERE { " + values, query)

        self._transaction().append(query)
        if self.autocommit:
            self.commit()

    def _insert_named_graph(self, query: str, query_graph: str) -> str:
        """Inserts GRAPH <query_graph> {} into blocks of SPARQL Update operations

        For instance,  `INSERT DATA { <urn:michel> <urn:likes> <urn:pizza> }`
        is converted into
        `INSERT DATA { GRAPH <urn:graph> { <urn:michel> <urn:likes> <urn:pizza> } }`
        """
        if isinstance(query_graph, Node):
            query_graph = self.node_to_sparql(query_graph)
        else:
            query_graph = "<%s>" % query_graph
        graph_block_open = " GRAPH %s {" % query_graph
        graph_block_close = "} "

        # SPARQL Update supports the following operations:
        # LOAD, CLEAR, DROP, ADD, MOVE, COPY, CREATE, INSERT DATA, DELETE DATA, DELETE/INSERT, DELETE WHERE
        # LOAD, CLEAR, DROP, ADD, MOVE, COPY, CREATE do not make much sense in a context.
        # INSERT DATA, DELETE DATA, and DELETE WHERE require the contents of their block to be wrapped in a GRAPH <?> { }.
        # DELETE/INSERT supports the WITH keyword, which sets the graph to be
        # used for all following DELETE/INSERT instruction including the
        # non-optional WHERE block. Equivalently, a GRAPH block can be added to
        # all blocks.
        #
        # Strategy employed here: Wrap the contents of every top-level block into a `GRAPH <?> { }`.

        level = 0
        modified_query = []
        pos = 0
        for match in self.BLOCK_FINDING_PATTERN.finditer(query):
            if match.group("block_start") is not None:
                level += 1
                if level == 1:
                    modified_query.append(query[pos : match.end()])
                    modified_query.append(graph_block_open)
                    pos = match.end()
            elif match.group("block_end") is not None:
                if level == 1:
                    since_previous_pos = query[pos : match.start()]
                    if modified_query[-1] is graph_block_open and (
                        since_previous_pos == "" or since_previous_pos.isspace()
                    ):
                        # In this case, adding graph_block_start and
                        # graph_block_end results in an empty GRAPH block. Some
                        # endpoints (e.g. TDB) can not handle this. Therefore
                        # remove the previously added block_start.
                        modified_query.pop()
                        modified_query.append(since_previous_pos)
                    else:
                        modified_query.append(since_previous_pos)
                        modified_query.append(graph_block_close)
                    pos = match.start()
                level -= 1
        modified_query.append(query[pos:])

        return "".join(modified_query)

    def add_graph(self, graph: Graph) -> None:
        if not self.graph_aware:
            Store.add_graph(self, graph)
        elif graph.identifier != DATASET_DEFAULT_GRAPH_ID:
            self.update("CREATE GRAPH %s" % self.node_to_sparql(graph.identifier))

    def remove_graph(self, graph: Graph) -> None:
        if not self.graph_aware:
            Store.remove_graph(self, graph)
        elif graph.identifier == DATASET_DEFAULT_GRAPH_ID:
            self.update("DROP DEFAULT")
        else:
            self.update("DROP GRAPH %s" % self.node_to_sparql(graph.identifier))

    def subjects(
        self,
        predicate: _PredicateType | None = None,
        object: _ObjectType | None = None,
    ) -> Generator[_SubjectType, None, None]:
        """A generator of subjects with the given predicate and object"""
        for t, c in self.triples((None, predicate, object)):
            yield t[0]

    def predicates(
        self,
        subject: _SubjectType | None = None,
        object: _ObjectType | None = None,
    ) -> Generator[_PredicateType, None, None]:
        """A generator of predicates with the given subject and object"""
        for t, c in self.triples((subject, None, object)):
            yield t[1]

    def objects(
        self,
        subject: _SubjectType | None = None,
        predicate: _PredicateType | None = None,
    ) -> Generator[_ObjectType, None, None]:
        """A generator of objects with the given subject and predicate"""
        for t, c in self.triples((subject, predicate, None)):
            yield t[2]

    def subject_predicates(
        self, object: _ObjectType | None = None
    ) -> Generator[tuple[_SubjectType, _PredicateType], None, None]:
        """A generator of (subject, predicate) tuples for the given object"""
        for t, c in self.triples((None, None, object)):
            yield t[0], t[1]

    def subject_objects(
        self, predicate: _PredicateType | None = None
    ) -> Generator[tuple[_SubjectType, _ObjectType], None, None]:
        """A generator of (subject, object) tuples for the given predicate"""
        for t, c in self.triples((None, predicate, None)):
            yield t[0], t[2]

    def predicate_objects(
        self, subject: _SubjectType | None = None
    ) -> Generator[tuple[_PredicateType, _ObjectType], None, None]:
        """A generator of (predicate, object) tuples for the given subject"""
        for t, c in self.triples((subject, None, None)):
            yield t[1], t[2]


__all__ = ["SPARQLUpdateStore", "SPARQLStore"]
