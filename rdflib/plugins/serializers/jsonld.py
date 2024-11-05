"""
This serialiser will output an RDF Graph as a JSON-LD formatted document. See:

    http://json-ld.org/

Example usage::

    >>> from rdflib import Graph
    >>> testrdf = '''
    ... @prefix dc: <http://purl.org/dc/terms/> .
    ... <http://example.org/about>
    ...     dc:title "Someone's Homepage"@en .
    ... '''

    >>> g = Graph().parse(data=testrdf, format='n3')

    >>> print(g.serialize(format='json-ld', indent=2))
    [
      {
        "@id": "http://example.org/about",
        "http://purl.org/dc/terms/title": [
          {
            "@language": "en",
            "@value": "Someone's Homepage"
          }
        ]
      }
    ]

"""

# From: https://github.com/RDFLib/rdflib-jsonld/blob/feature/json-ld-1.1/rdflib_jsonld/serializer.py

# NOTE: This code writes the entire JSON object into memory before serialising,
# but we should consider streaming the output to deal with arbitrarily large
# graphs.

from __future__ import annotations

import warnings
from typing import IO, TYPE_CHECKING, Any, Union, cast

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Graph
from rdflib.namespace import RDF, XSD
from rdflib.serializer import Serializer
from rdflib.term import BNode, IdentifiedNode, Literal, URIRef

from ..shared.jsonld.context import UNDEF, Context
from ..shared.jsonld.keys import CONTEXT, GRAPH, ID, LANG, LIST, SET, VOCAB
from ..shared.jsonld.util import _HAS_ORJSON, json, orjson

if TYPE_CHECKING:
    from rdflib.graph import _ObjectType

    # In JSON-LD, a Literal cannot be Subject. So define a new type
    from ..shared.jsonld.context import JSONLDSubjectType, Term

__all__ = ["JsonLDSerializer", "from_rdf"]


PLAIN_LITERAL_TYPES = {XSD.boolean, XSD.integer, XSD.double, XSD.string}


class JsonLDSerializer(Serializer):
    def __init__(self, store: Graph):
        super(JsonLDSerializer, self).__init__(store)

    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        # TODO: docstring w. args and return value
        encoding = encoding or "utf-8"
        if encoding not in ("utf-8", "utf-16"):
            warnings.warn(
                "JSON should be encoded as unicode. " f"Given encoding was: {encoding}"
            )

        context_data = kwargs.get("context")
        use_native_types = (kwargs.get("use_native_types", False),)
        use_rdf_type = kwargs.get("use_rdf_type", False)
        auto_compact = kwargs.get("auto_compact", False)

        indent = kwargs.get("indent", 2)
        separators = kwargs.get("separators", (",", ": "))
        sort_keys = kwargs.get("sort_keys", True)
        ensure_ascii = kwargs.get("ensure_ascii", False)

        obj = from_rdf(
            self.store,
            context_data,
            base,
            use_native_types,
            use_rdf_type,
            auto_compact=auto_compact,
        )
        if _HAS_ORJSON:
            option: int = orjson.OPT_NON_STR_KEYS
            if indent is not None:
                option |= orjson.OPT_INDENT_2
            if sort_keys:
                option |= orjson.OPT_SORT_KEYS
            if ensure_ascii:
                warnings.warn("Cannot use ensure_ascii with orjson")
            data_bytes = orjson.dumps(obj, option=option)
            stream.write(data_bytes)
        else:
            data = json.dumps(
                obj,
                indent=indent,
                separators=separators,
                sort_keys=sort_keys,
                ensure_ascii=ensure_ascii,
            )
            stream.write(data.encode(encoding, "replace"))


def from_rdf(
    graph,
    context_data=None,
    base=None,
    use_native_types=False,
    use_rdf_type=False,
    auto_compact=False,
    startnode=None,
    index=False,
):
    # TODO: docstring w. args and return value
    # TODO: support for index and startnode

    if not context_data and auto_compact:
        context_data = dict(
            (pfx, str(ns))
            for (pfx, ns) in graph.namespaces()
            if pfx and str(ns) != "http://www.w3.org/XML/1998/namespace"
        )

    if isinstance(context_data, Context):
        context = context_data
        context_data = context.to_dict()
    else:
        context = Context(context_data, base=base)

    converter = Converter(context, use_native_types, use_rdf_type)
    result = converter.convert(graph)

    if converter.context.active:
        if isinstance(result, list):
            result = {context.get_key(GRAPH): result}
        result[CONTEXT] = context_data

    return result


class Converter:
    def __init__(self, context: Context, use_native_types: bool, use_rdf_type: bool):
        self.context = context
        self.use_native_types = context.active or use_native_types
        self.use_rdf_type = use_rdf_type

    def convert(self, graph: Graph):
        # TODO: bug in rdflib dataset parsing (nquads et al):
        # plain triples end up in separate unnamed graphs (rdflib issue #436)
        if graph.context_aware:
            # type error: "Graph" has no attribute "contexts"
            all_contexts = list(graph.contexts())  # type: ignore[attr-defined]
            has_dataset_default_id = any(
                c.identifier == DATASET_DEFAULT_GRAPH_ID for c in all_contexts
            )
            if (
                has_dataset_default_id
                # # type error: "Graph" has no attribute "contexts"
                and graph.default_context.identifier == DATASET_DEFAULT_GRAPH_ID  # type: ignore[attr-defined]
            ):
                default_graph = graph.default_context  # type: ignore[attr-defined]
            else:
                default_graph = Graph()
            graphs = [default_graph]
            default_graph_id = default_graph.identifier

            for g in all_contexts:
                if g in graphs:
                    continue
                if isinstance(g.identifier, URIRef):
                    graphs.append(g)
                else:
                    default_graph += g
        else:
            graphs = [graph]
            default_graph_id = graph.identifier

        context = self.context

        objs: list[Any] = []
        for g in graphs:
            obj = {}
            graphname = None

            if isinstance(g.identifier, URIRef):
                if g.identifier != default_graph_id:
                    graphname = context.shrink_iri(g.identifier)
                    obj[context.id_key] = graphname

            nodes = self.from_graph(g)

            if not graphname and len(nodes) == 1:
                obj.update(nodes[0])
            else:
                if not nodes:
                    continue
                obj[context.graph_key] = nodes

            if objs and objs[0].get(context.get_key(ID)) == graphname:
                objs[0].update(obj)
            else:
                objs.append(obj)

        if len(graphs) == 1 and len(objs) == 1 and not self.context.active:
            default = objs[0]
            items = default.get(context.graph_key)
            if len(default) == 1 and items:
                objs = items
        elif len(objs) == 1 and self.context.active:
            objs = objs[0]

        return objs

    def from_graph(self, graph: Graph):
        nodemap: dict[Any, Any] = {}

        for s in set(graph.subjects()):
            ## only iri:s and unreferenced (rest will be promoted to top if needed)
            if isinstance(s, URIRef) or (
                isinstance(s, BNode) and not any(graph.subjects(None, s))
            ):
                self.process_subject(graph, s, nodemap)

        return list(nodemap.values())

    def process_subject(self, graph: Graph, s: IdentifiedNode, nodemap):
        if isinstance(s, URIRef):
            node_id = self.context.shrink_iri(s)
        elif isinstance(s, BNode):
            node_id = s.n3()
        else:
            # This does not seem right, this probably should be an error.
            node_id = None

        # used_as_object = any(graph.subjects(None, s))
        if node_id in nodemap:
            return None

        node = {}
        node[self.context.id_key] = node_id
        nodemap[node_id] = node

        for p, o in graph.predicate_objects(s):
            # predicate_objects can return a lot of different types,
            # but we only need to consider it to be a JSON-compatible type.
            object_val = cast(Union[IdentifiedNode, Literal], o)
            pred_val = cast(IdentifiedNode, p)
            self.add_to_node(graph, s, pred_val, object_val, node, nodemap)

        return node

    def add_to_node(
        self,
        graph: Graph,
        s: IdentifiedNode,
        p: IdentifiedNode,
        o: IdentifiedNode | Literal,
        s_node: dict[str, Any],
        nodemap,
    ):
        context = self.context
        term: Term | None = None
        if isinstance(o, Literal):
            _datatype = str(o.datatype) if o.datatype else None
            language = o.language
            term = context.find_term(str(p), _datatype, language=language)
        else:
            containers = [LIST, None] if graph.value(o, RDF.first) else [None]
            for container in containers:
                for coercion in (ID, VOCAB, UNDEF):
                    term = context.find_term(str(p), coercion, container)
                    if term:
                        break
                if term:
                    break
            language = None if term is None else term.language

        node: str | list[Any] | dict[str, Any] | None = None
        use_set = not context.active

        if term is not None:
            p_key = term.name

            if term.type:
                node = self.type_coerce(o, term.type)
            elif (
                term.language and isinstance(o, Literal) and o.language == term.language
            ):
                node = str(o)
            elif context.language:
                # TODO: MyPy thinks this is unreachable?
                if isinstance(o, Literal) and (  # type: ignore[unreachable]
                    term.language is None and o.language is None
                ):
                    node = str(o)

            if LIST in term.container:
                assert isinstance(
                    o, IdentifiedNode
                ), "Subject of a @list container must an a URI or BNode"
                _col = self.to_collection(graph, o)
                if _col is not None:
                    node = []
                    for v in _col:
                        if isinstance(v, (IdentifiedNode, Literal)):
                            coerced = self.type_coerce(v, term.type)
                        else:
                            coerced = None
                        if coerced is not None:
                            node.append(coerced)
                        else:
                            node.append(self.to_raw_value(graph, s, v, nodemap))
            elif LANG in term.container and language:
                value = s_node.setdefault(p_key, {})
                values = value.get(language)
                node = str(o)
                if values or SET in term.container:
                    if not isinstance(values, list):
                        value[language] = values = [values]
                    values.append(node)
                else:
                    value[language] = node
                return
            elif SET in term.container:
                use_set = True

        else:
            p_key = context.to_symbol(p)
            # TODO: for coercing curies - quite clumsy; unify to_symbol and find_term?
            key_term = context.terms.get(p_key)
            if key_term and (key_term.type or key_term.container):
                p_key = p
            if not term and p == RDF.type and not self.use_rdf_type:
                if isinstance(o, URIRef):
                    node = context.to_symbol(o)
                p_key = context.type_key

        if node is None:
            node = self.to_raw_value(graph, s, o, nodemap)

        value = s_node.get(p_key)
        if value:
            if not isinstance(value, list):
                value = [value]
            value.append(node)
        elif use_set:
            value = [node]
        else:
            value = node
        s_node[p_key] = value

    def type_coerce(
        self, o: IdentifiedNode | Literal, coerce_type: str
    ) -> str | IdentifiedNode | Literal | None:
        if coerce_type == ID:
            if isinstance(o, URIRef):
                return self.context.shrink_iri(o)
            elif isinstance(o, BNode):
                return o.n3()
            else:
                return o
        elif coerce_type == VOCAB and isinstance(o, URIRef):
            return self.context.to_symbol(o)
        elif isinstance(o, Literal) and str(o.datatype) == coerce_type:
            return o
        else:
            return None

    def to_raw_value(
        self,
        graph: Graph,
        s: JSONLDSubjectType,
        o: _ObjectType,
        nodemap: dict[str, Any],
    ):
        context = self.context
        if isinstance(o, (URIRef, BNode)):
            coll: list[Any] | None = self.to_collection(graph, o)
        else:
            coll = None
        if coll is not None:
            coll = [self.to_raw_value(graph, s, lo, nodemap) for lo in coll]
            return {context.list_key: coll}
        elif isinstance(o, BNode):
            embed = (
                False  # TODO: self.context.active or using startnode and only one ref
            )
            onode = self.process_subject(graph, o, nodemap)
            if onode:
                if embed and not any(s2 for s2 in graph.subjects(None, o) if s2 != s):
                    return onode
                else:
                    nodemap[onode[context.id_key]] = onode
            return {context.id_key: o.n3()}
        elif isinstance(o, URIRef):
            # TODO: embed if o != startnode (else reverse)
            return {context.id_key: context.shrink_iri(o)}
        elif isinstance(o, Literal):
            # TODO: if compact
            native = self.use_native_types and o.datatype in PLAIN_LITERAL_TYPES
            if native:
                v = o.toPython()
            else:
                v = str(o)
            if o.datatype:
                if native and self.context.active:
                    return v
                return {
                    context.type_key: context.to_symbol(o.datatype),
                    context.value_key: v,
                }
            elif o.language and o.language != context.language:
                return {context.lang_key: o.language, context.value_key: v}
            # type error: Right operand of "and" is never evaluated
            elif not context.active or context.language and not o.language:  # type: ignore[unreachable]
                return {context.value_key: v}
            else:
                return v

    def to_collection(
        self, graph: Graph, l_: JSONLDSubjectType
    ) -> list[_ObjectType] | None:
        if l_ != RDF.nil and not graph.value(l_, RDF.first):
            return None
        list_nodes: list[_ObjectType] = []
        chain: set[_ObjectType] = set([l_])
        list_head: _ObjectType | None = l_
        while list_head:
            if list_head == RDF.nil:
                # The only way to return a real result is to reach
                # a rdf:nil node at the end of a rdf list.
                return list_nodes
            if isinstance(list_head, URIRef):
                return None
            first, rest = None, None
            for p, o in graph.predicate_objects(list_head):
                if not first and p == RDF.first:
                    first = o
                elif not rest and p == RDF.rest:
                    rest = o
                elif p != RDF.type or o != RDF.List:
                    return None
            if first is not None:
                list_nodes.append(first)
            if rest is None:
                # TODO: If no rdf:rest is found, should we return the current list_nodes?
                return None
            list_head = rest
            if list_head in chain:
                return None  # TODO: Should this just return the current list_nodes?
            chain.add(list_head)
        return None
