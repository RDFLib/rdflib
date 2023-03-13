# -*- coding: utf-8 -*-
"""
This parser will interpret a JSON-LD document as an RDF Graph. See:

    http://json-ld.org/

Example usage::

    >>> from rdflib import Graph, URIRef, Literal
    >>> test_json = '''
    ... {
    ...     "@context": {
    ...         "dc": "http://purl.org/dc/terms/",
    ...         "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    ...         "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
    ...     },
    ...     "@id": "http://example.org/about",
    ...     "dc:title": {
    ...         "@language": "en",
    ...         "@value": "Someone's Homepage"
    ...     }
    ... }
    ... '''
    >>> g = Graph().parse(data=test_json, format='json-ld')
    >>> list(g) == [(URIRef('http://example.org/about'),
    ...     URIRef('http://purl.org/dc/terms/title'),
    ...     Literal("Someone's Homepage", lang='en'))]
    True

"""
# From: https://github.com/RDFLib/rdflib-jsonld/blob/feature/json-ld-1.1/rdflib_jsonld/parser.py

# NOTE: This code reads the entire JSON object into memory before parsing, but
# we should consider streaming the input to deal with arbitrarily large graphs.
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import rdflib.parser
from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.namespace import RDF, XSD
from rdflib.parser import InputSource, URLInputSource
from rdflib.term import BNode, IdentifiedNode, Literal, Node, URIRef

from ..shared.jsonld.context import UNDEF, Context, Term
from ..shared.jsonld.keys import (
    CONTEXT,
    GRAPH,
    ID,
    INCLUDED,
    INDEX,
    JSON,
    LANG,
    LIST,
    NEST,
    NONE,
    REV,
    SET,
    TYPE,
    VALUE,
    VOCAB,
)
from ..shared.jsonld.util import (
    VOCAB_DELIMS,
    context_from_urlinputsource,
    json,
    source_to_json,
)

__all__ = ["JsonLDParser", "to_rdf"]

TYPE_TERM = Term(str(RDF.type), TYPE, VOCAB)  # type: ignore[call-arg]

ALLOW_LISTS_OF_LISTS = True  # NOTE: Not allowed in JSON-LD 1.0


class JsonLDParser(rdflib.parser.Parser):
    def __init__(self):
        super(JsonLDParser, self).__init__()

    def parse(self, source: InputSource, sink: Graph, **kwargs: Any) -> None:
        # TODO: docstring w. args and return value
        encoding = kwargs.get("encoding") or "utf-8"
        if encoding not in ("utf-8", "utf-16"):
            warnings.warn(
                "JSON should be encoded as unicode. "
                "Given encoding was: %s" % encoding
            )

        base = kwargs.get("base") or sink.absolutize(
            source.getPublicId() or source.getSystemId() or ""
        )

        context_data = kwargs.get("context")
        if not context_data and hasattr(source, "url") and hasattr(source, "links"):
            if TYPE_CHECKING:
                assert isinstance(source, URLInputSource)
            context_data = context_from_urlinputsource(source)

        try:
            version = float(kwargs.get("version", "1.0"))
        except ValueError:
            version = None

        generalized_rdf = kwargs.get("generalized_rdf", False)

        data = source_to_json(source)

        # NOTE: A ConjunctiveGraph parses into a Graph sink, so no sink will be
        # context_aware. Keeping this check in case RDFLib is changed, or
        # someone passes something context_aware to this parser directly.
        conj_sink: Graph
        if not sink.context_aware:
            conj_sink = ConjunctiveGraph(store=sink.store, identifier=sink.identifier)
        else:
            conj_sink = sink

        to_rdf(data, conj_sink, base, context_data, version, generalized_rdf)


def to_rdf(
    data: Any,
    dataset: Graph,
    base: Optional[str] = None,
    context_data: Optional[bool] = None,
    version: Optional[float] = None,
    generalized_rdf: bool = False,
    allow_lists_of_lists: Optional[bool] = None,
):
    # TODO: docstring w. args and return value
    context = Context(base=base, version=version)
    if context_data:
        context.load(context_data)
    parser = Parser(
        generalized_rdf=generalized_rdf, allow_lists_of_lists=allow_lists_of_lists
    )
    return parser.parse(data, context, dataset)


class Parser(object):
    def __init__(
        self, generalized_rdf: bool = False, allow_lists_of_lists: Optional[bool] = None
    ):
        self.generalized_rdf = generalized_rdf
        self.allow_lists_of_lists = (
            allow_lists_of_lists
            if allow_lists_of_lists is not None
            else ALLOW_LISTS_OF_LISTS
        )

    def parse(self, data: Any, context: Context, dataset: Graph) -> Graph:
        topcontext = False
        resources: Union[Dict[str, Any], List[Any]]
        if isinstance(data, list):
            resources = data
        elif isinstance(data, dict):
            local_context = data.get(CONTEXT)
            if local_context:
                context.load(local_context, context.base)
                topcontext = True
            resources = data
            # type error: Subclass of "Dict[str, Any]" and "List[Any]" cannot exist: would have incompatible method signatures
            if not isinstance(resources, list):  # type: ignore[unreachable]
                resources = [resources]

        if context.vocab:
            dataset.bind(None, context.vocab)
        for name, term in context.terms.items():
            if term.id and term.id.endswith(VOCAB_DELIMS):
                dataset.bind(name, term.id)

        # type error: "Graph" has no attribute "default_context"
        graph = dataset.default_context if dataset.context_aware else dataset  # type: ignore[attr-defined]

        for node in resources:
            self._add_to_graph(dataset, graph, context, node, topcontext)

        return graph

    def _add_to_graph(
        self,
        dataset: Graph,
        graph: Graph,
        context: Context,
        node: Any,
        topcontext: bool = False,
    ) -> Optional[Node]:
        if not isinstance(node, dict) or context.get_value(node):
            # type error: Return value expected
            return  # type: ignore[return-value]

        if CONTEXT in node and not topcontext:
            local_context = node[CONTEXT]
            if local_context:
                context = context.subcontext(local_context)
            else:
                context = Context(base=context.doc_base)

        # type error: Incompatible types in assignment (expression has type "Optional[Context]", variable has type "Context")
        context = context.get_context_for_type(node)  # type: ignore[assignment]

        id_val = context.get_id(node)

        if id_val is None:
            nested_id = self._get_nested_id(context, node)
            if nested_id is not None and len(nested_id) > 0:
                id_val = nested_id

        if isinstance(id_val, str):
            subj = self._to_rdf_id(context, id_val)
        else:
            subj = BNode()

        if subj is None:
            return None

        # NOTE: crude way to signify that this node might represent a named graph
        no_id = id_val is None

        for key, obj in node.items():
            if key == CONTEXT or key in context.get_keys(ID):
                continue

            if key == REV or key in context.get_keys(REV):
                for rkey, robj in obj.items():
                    self._key_to_graph(
                        dataset,
                        graph,
                        context,
                        subj,
                        rkey,
                        robj,
                        reverse=True,
                        no_id=no_id,
                    )
            else:
                self._key_to_graph(dataset, graph, context, subj, key, obj, no_id=no_id)

        return subj

    # type error: Missing return statement
    def _get_nested_id(self, context: Context, node: Dict[str, Any]) -> Optional[str]:  # type: ignore[return]
        for key, obj in node.items():
            if context.version >= 1.1 and key in context.get_keys(NEST):
                term = context.terms.get(key)
                if term and term.id is None:
                    continue
                objs = obj if isinstance(obj, list) else [obj]
                for obj in objs:
                    if not isinstance(obj, dict):
                        continue
                    id_val = context.get_id(obj)
                    if not id_val:
                        subcontext = context.get_context_for_term(
                            context.terms.get(key)
                        )
                        id_val = self._get_nested_id(subcontext, obj)
                    if isinstance(id_val, str):
                        return id_val

    def _key_to_graph(
        self,
        dataset: Graph,
        graph: Graph,
        context: Context,
        subj: Node,
        key: str,
        obj: Any,
        reverse: bool = False,
        no_id: bool = False,
    ) -> None:
        if isinstance(obj, list):
            obj_nodes = obj
        else:
            obj_nodes = [obj]

        term = context.terms.get(key)
        if term:
            term_id = term.id
            if term.type == JSON:
                obj_nodes = [self._to_typed_json_value(obj)]
            elif LIST in term.container:
                obj_nodes = [{LIST: obj_nodes}]
            elif isinstance(obj, dict):
                obj_nodes = self._parse_container(context, term, obj)
        else:
            term_id = None

        if TYPE in (key, term_id):
            term = TYPE_TERM

        if GRAPH in (key, term_id):
            if dataset.context_aware and not no_id:
                if TYPE_CHECKING:
                    assert isinstance(dataset, ConjunctiveGraph)
                # type error: Argument 1 to "get_context" of "ConjunctiveGraph" has incompatible type "Node"; expected "Union[IdentifiedNode, str, None]"
                subgraph = dataset.get_context(subj)  # type: ignore[arg-type]
            else:
                subgraph = graph
            for onode in obj_nodes:
                self._add_to_graph(dataset, subgraph, context, onode)
            return

        if SET in (key, term_id):
            for onode in obj_nodes:
                self._add_to_graph(dataset, graph, context, onode)
            return

        if INCLUDED in (key, term_id):
            for onode in obj_nodes:
                self._add_to_graph(dataset, graph, context, onode)
            return

        if context.version >= 1.1 and key in context.get_keys(NEST):
            term = context.terms.get(key)
            if term and term.id is None:
                return
            objs = obj if isinstance(obj, list) else [obj]
            for obj in objs:
                if not isinstance(obj, dict):
                    continue
                for nkey, nobj in obj.items():
                    # NOTE: we've already captured subject
                    if nkey in context.get_keys(ID):
                        continue
                    subcontext = context.get_context_for_type(obj)
                    # type error: Argument 3 to "_key_to_graph" of "Parser" has incompatible type "Optional[Context]"; expected "Context"
                    self._key_to_graph(dataset, graph, subcontext, subj, nkey, nobj)  # type: ignore[arg-type]
            return

        pred_uri = term.id if term else context.expand(key)

        context = context.get_context_for_term(term)

        flattened = []
        for obj in obj_nodes:
            if isinstance(obj, dict):
                objs = context.get_set(obj)
                if objs is not None:
                    obj = objs
            if isinstance(obj, list):
                flattened += obj
                continue
            flattened.append(obj)
        obj_nodes = flattened

        if not pred_uri:
            return

        if term and term.reverse:
            reverse = not reverse

        pred: IdentifiedNode
        bid = self._get_bnodeid(pred_uri)
        if bid:
            if not self.generalized_rdf:
                return
            pred = BNode(bid)
        else:
            pred = URIRef(pred_uri)

        for obj_node in obj_nodes:
            obj = self._to_object(dataset, graph, context, term, obj_node)
            if obj is None:
                continue
            if reverse:
                graph.add((obj, pred, subj))
            else:
                graph.add((subj, pred, obj))

    def _parse_container(
        self, context: Context, term: Term, obj: Dict[str, Any]
    ) -> List[Any]:
        if LANG in term.container:
            obj_nodes = []
            for lang, values in obj.items():
                if not isinstance(values, list):
                    values = [values]
                if lang in context.get_keys(NONE):
                    obj_nodes += values
                else:
                    for v in values:
                        obj_nodes.append((v, lang))
            return obj_nodes

        v11 = context.version >= 1.1

        if v11 and GRAPH in term.container and ID in term.container:
            return [
                dict({GRAPH: o})
                if k in context.get_keys(NONE)
                else dict({ID: k, GRAPH: o})
                if isinstance(o, dict)
                else o
                for k, o in obj.items()
            ]

        elif v11 and GRAPH in term.container and INDEX in term.container:
            return [dict({GRAPH: o}) for k, o in obj.items()]

        elif v11 and GRAPH in term.container:
            return [dict({GRAPH: obj})]

        elif v11 and ID in term.container:
            return [
                dict({ID: k}, **o)
                if isinstance(o, dict) and k not in context.get_keys(NONE)
                else o
                for k, o in obj.items()
            ]

        elif v11 and TYPE in term.container:
            return [
                self._add_type(
                    context,
                    {ID: context.expand(o) if term.type == VOCAB else o}
                    if isinstance(o, str)
                    else o,
                    k,
                )
                if isinstance(o, (dict, str)) and k not in context.get_keys(NONE)
                else o
                for k, o in obj.items()
            ]

        elif INDEX in term.container:
            obj_nodes = []
            for key, nodes in obj.items():
                if not isinstance(nodes, list):
                    nodes = [nodes]
                for node in nodes:
                    if v11 and term.index and key not in context.get_keys(NONE):
                        if not isinstance(node, dict):
                            node = {ID: node}
                        values = node.get(term.index, [])
                        if not isinstance(values, list):
                            values = [values]
                        values.append(key)
                        node[term.index] = values
                    obj_nodes.append(node)
            return obj_nodes

        return [obj]

    @staticmethod
    def _add_type(context: Context, o: Dict[str, Any], k: str) -> Dict[str, Any]:
        otype = context.get_type(o) or []
        if otype and not isinstance(otype, list):
            otype = [otype]
        otype.append(k)
        o[TYPE] = otype
        return o

    def _to_object(
        self,
        dataset: Graph,
        graph: Graph,
        context: Context,
        term: Optional[Term],
        node: Any,
        inlist: bool = False,
    ) -> Optional[Node]:
        if isinstance(node, tuple):
            value, lang = node
            if value is None:
                # type error: Return value expected
                return  # type: ignore[return-value]
            if lang and " " in lang:
                # type error: Return value expected
                return  # type: ignore[return-value]
            return Literal(value, lang=lang)

        if isinstance(node, dict):
            node_list = context.get_list(node)
            if node_list is not None:
                if inlist and not self.allow_lists_of_lists:
                    # type error: Return value expected
                    return  # type: ignore[return-value]
                listref = self._add_list(dataset, graph, context, term, node_list)
                if listref:
                    return listref

        else:  # expand compacted value
            if term and term.type:
                if term.type == JSON:
                    node = self._to_typed_json_value(node)
                elif node is None:
                    # type error: Return value expected
                    return  # type: ignore[return-value]
                elif term.type == ID and isinstance(node, str):
                    node = {ID: context.resolve(node)}
                elif term.type == VOCAB and isinstance(node, str):
                    node = {ID: context.expand(node) or context.resolve_iri(node)}
                else:
                    node = {TYPE: term.type, VALUE: node}
            else:
                if node is None:
                    # type error: Return value expected
                    return  # type: ignore[return-value]
                if isinstance(node, float):
                    return Literal(node, datatype=XSD.double)

                if term and term.language is not UNDEF:
                    lang = term.language
                else:
                    lang = context.language
                return Literal(node, lang=lang)

        lang = context.get_language(node)
        datatype = not lang and context.get_type(node) or None
        value = context.get_value(node)
        # type error: Unsupported operand types for in ("Optional[Any]" and "Generator[str, None, None]")
        if datatype in context.get_keys(JSON):  # type: ignore[operator]
            node = self._to_typed_json_value(value)
            datatype = context.get_type(node)
            value = context.get_value(node)

        if lang or context.get_key(VALUE) in node or VALUE in node:
            if value is None:
                return None
            if lang:
                if " " in lang:
                    # type error: Return value expected
                    return  # type: ignore[return-value]
                return Literal(value, lang=lang)
            elif datatype:
                return Literal(value, datatype=context.expand(datatype))
            else:
                return Literal(value)
        else:
            return self._add_to_graph(dataset, graph, context, node)

    def _to_rdf_id(self, context: Context, id_val: str) -> Optional[IdentifiedNode]:
        bid = self._get_bnodeid(id_val)
        if bid:
            return BNode(bid)
        else:
            uri = context.resolve(id_val)
            if not self.generalized_rdf and ":" not in uri:
                return None
            return URIRef(uri)

    def _get_bnodeid(self, ref: str) -> Optional[str]:
        if not ref.startswith("_:"):
            # type error: Return value expected
            return  # type: ignore[return-value]
        bid = ref.split("_:", 1)[-1]
        return bid or None

    def _add_list(
        self,
        dataset: Graph,
        graph: Graph,
        context: Context,
        term: Optional[Term],
        node_list: Any,
    ) -> IdentifiedNode:
        if not isinstance(node_list, list):
            node_list = [node_list]

        first_subj = BNode()
        subj, rest = first_subj, None

        for node in node_list:
            if node is None:
                continue

            if rest:
                # type error: Statement is unreachable
                graph.add((subj, RDF.rest, rest))  # type: ignore[unreachable]
                subj = rest

            obj = self._to_object(dataset, graph, context, term, node, inlist=True)

            if obj is None:
                continue

            graph.add((subj, RDF.first, obj))
            rest = BNode()

        if rest:
            graph.add((subj, RDF.rest, RDF.nil))
            return first_subj
        else:
            return RDF.nil

    @staticmethod
    def _to_typed_json_value(value: Any) -> Dict[str, str]:
        return {
            TYPE: URIRef("%sJSON" % str(RDF)),
            VALUE: json.dumps(
                value, separators=(",", ":"), sort_keys=True, ensure_ascii=False
            ),
        }
