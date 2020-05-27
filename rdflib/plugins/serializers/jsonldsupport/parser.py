# -*- coding: utf-8 -*-
"""
This parser will interpret a JSON-LD document as an RDF Graph. See:

    http://json-ld.org/

Example usage::

    >>> from rdflib.plugin import register, Parser
    >>> register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')

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
# NOTE: This code reads the entire JSON object into memory before parsing, but
# we should consider streaming the input to deal with arbitrarily large graphs.

import warnings
from rdflib.graph import ConjunctiveGraph
from rdflib.parser import Parser, URLInputSource
from rdflib.namespace import RDF, XSD
from rdflib.term import URIRef, BNode, Literal

from ._compat import str, str
from .context import Context, Term, UNDEF
from .util import source_to_json, VOCAB_DELIMS, context_from_urlinputsource
from .keys import CONTEXT, GRAPH, ID, INDEX, LANG, LIST, REV, SET, TYPE, VALUE, VOCAB

__all__ = ['JsonLDParser', 'to_rdf']


# Add jsonld suffix so RDFLib can guess format from file name
try:
    from rdflib.util import SUFFIX_FORMAT_MAP
    if 'jsonld' not in SUFFIX_FORMAT_MAP:
        SUFFIX_FORMAT_MAP['jsonld'] = 'application/ld+json'
except ImportError:
    pass


TYPE_TERM = Term(str(RDF.type), TYPE, VOCAB)

ALLOW_LISTS_OF_LISTS = True # NOTE: Not allowed in JSON-LD 1.0


class JsonLDParser(Parser):
    def __init__(self):
        super(JsonLDParser, self).__init__()

    def parse(self, source, sink, **kwargs):
        # TODO: docstring w. args and return value
        encoding = kwargs.get('encoding') or 'utf-8'
        if encoding not in ('utf-8', 'utf-16'):
            warnings.warn("JSON should be encoded as unicode. " +
                          "Given encoding was: %s" % encoding)

        base = kwargs.get('base') or sink.absolutize(
            source.getPublicId() or source.getSystemId() or "")
        context_data = kwargs.get('context')
        if not context_data and isinstance(source, URLInputSource):
            context_data = context_from_urlinputsource(source)
        produce_generalized_rdf = kwargs.get('produce_generalized_rdf', False)

        data = source_to_json(source)

        # NOTE: A ConjunctiveGraph parses into a Graph sink, so no sink will be
        # context_aware. Keeping this check in case RDFLib is changed, or
        # someone passes something context_aware to this parser directly.
        if not sink.context_aware:
            conj_sink = ConjunctiveGraph(
                store=sink.store,
                identifier=sink.identifier)
        else:
            conj_sink = sink

        to_rdf(data, conj_sink, base, context_data)


def to_rdf(data, dataset, base=None, context_data=None,
        produce_generalized_rdf=False,
        allow_lists_of_lists=None):
    # TODO: docstring w. args and return value
    context=Context(base=base)
    if context_data:
        context.load(context_data)
    parser = Parser(generalized_rdf=produce_generalized_rdf,
            allow_lists_of_lists=allow_lists_of_lists)
    return parser.parse(data, context, dataset)


class Parser(object):

    def __init__(self, generalized_rdf=False, allow_lists_of_lists=None):
        self.generalized_rdf = generalized_rdf
        self.allow_lists_of_lists = (allow_lists_of_lists
                if allow_lists_of_lists is not None else ALLOW_LISTS_OF_LISTS)

    def parse(self, data, context, dataset):
        topcontext = False

        if isinstance(data, list):
            resources = data
        elif isinstance(data, dict):
            l_ctx = data.get(CONTEXT)
            if l_ctx:
                context.load(l_ctx, context.base)
                topcontext = True
            resources = data
            if not isinstance(resources, list):
                resources = [resources]

        if context.vocab:
            dataset.bind(None, context.vocab)
        for name, term in list(context.terms.items()):
            if term.id and term.id.endswith(VOCAB_DELIMS):
                dataset.bind(name, term.id)

        graph = dataset.default_context if dataset.context_aware else dataset

        for node in resources:
            self._add_to_graph(dataset, graph, context, node, topcontext)

        return graph


    def _add_to_graph(self, dataset, graph, context, node, topcontext=False):
        if not isinstance(node, dict) or context.get_value(node):
            return

        if CONTEXT in node and not topcontext:
            l_ctx = node.get(CONTEXT)
            if l_ctx:
                context = context.subcontext(l_ctx)
            else:
                context = Context(base=context.doc_base)

        id_val = context.get_id(node)
        if isinstance(id_val, str):
            subj = self._to_rdf_id(context, id_val)
        else:
            subj = BNode()

        if subj is None:
            return None

        # NOTE: crude way to signify that this node might represent a named graph
        no_id = id_val is None

        for key, obj in list(node.items()):
            if key in (CONTEXT, ID) or key in context.get_keys(ID):
                continue
            if key == REV or key in context.get_keys(REV):
                for rkey, robj in list(obj.items()):
                    self._key_to_graph(dataset, graph, context, subj, rkey, robj,
                            reverse=True, no_id=no_id)
            else:
                self._key_to_graph(dataset, graph, context, subj, key, obj,
                        no_id=no_id)

        return subj


    def _key_to_graph(self, dataset, graph, context, subj, key, obj,
            reverse=False, no_id=False):

        if isinstance(obj, list):
            obj_nodes = obj
        else:
            obj_nodes = [obj]

        term = context.terms.get(key)
        if term:
            term_id = term.id
            if term.container == LIST:
                obj_nodes = [{LIST: obj_nodes}]
            elif isinstance(obj, dict):
                if term.container == INDEX:
                    obj_nodes = []
                    for values in list(obj.values()):
                        if not isinstance(values, list):
                            obj_nodes.append(values)
                        else:
                            obj_nodes += values
                elif term.container == LANG:
                    obj_nodes = []
                    for lang, values in list(obj.items()):
                        if not isinstance(values, list):
                            values = [values]
                        for v in values:
                            obj_nodes.append((v, lang))
        else:
            term_id = None

        if TYPE in (key, term_id):
            term = TYPE_TERM
        elif GRAPH in (key, term_id):
            if dataset.context_aware and not no_id:
                subgraph = dataset.get_context(subj)
            else:
                subgraph = graph
            for onode in obj_nodes:
                self._add_to_graph(dataset, subgraph, context, onode)
            return
        elif SET in (key, term_id):
            for onode in obj_nodes:
                self._add_to_graph(dataset, graph, context, onode)
            return

        pred_uri = term.id if term else context.expand(key)

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


    def _to_object(self, dataset, graph, context, term, node, inlist=False):

        if node is None:
            return

        if isinstance(node, tuple):
            value, lang = node
            if value is None:
                return
            return Literal(value, lang=lang)

        if isinstance(node, dict):
            node_list = context.get_list(node)
            if node_list is not None:
                if inlist and not self.allow_lists_of_lists:
                    return
                listref = self._add_list(dataset, graph, context, term, node_list)
                if listref:
                    return listref

        else: # expand..
            if not term or not term.type:
                if isinstance(node, float):
                    return Literal(node, datatype=XSD.double)
                if term and term.language is not UNDEF:
                    lang = term.language
                else:
                    lang = context.language
                return Literal(node, lang=lang)
            else:
                if term.type == ID:
                    node = {ID: context.resolve(node)}
                elif term.type == VOCAB:
                    node = {ID: context.expand(node) or context.resolve_iri(node)}
                else:
                    node = {TYPE: term.type,
                            VALUE: node}

        lang = context.get_language(node)
        if lang or context.get_key(VALUE) in node or VALUE in node:
            value = context.get_value(node)
            if value is None:
                return None
            datatype = not lang and context.get_type(node) or None
            if lang:
                return Literal(value, lang=lang)
            elif datatype:
                return Literal(value, datatype=context.expand(datatype))
            else:
                return Literal(value)
        else:
            return self._add_to_graph(dataset, graph, context, node)


    def _to_rdf_id(self, context, id_val):
        bid = self._get_bnodeid(id_val)
        if bid:
            return BNode(bid)
        else:
            uri = context.resolve(id_val)
            if not self.generalized_rdf and ':' not in uri:
                return None
            return URIRef(uri)


    def _get_bnodeid(self, ref):
        if not ref.startswith('_:'):
            return
        bid = ref.split('_:', 1)[-1]
        return bid or None


    def _add_list(self, dataset, graph, context, term, node_list):
        if not isinstance(node_list, list):
            node_list = [node_list]
        first_subj = BNode()
        subj, rest = first_subj, None
        for node in node_list:
            if node is None:
                continue
            if rest:
                graph.add((subj, RDF.rest, rest))
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
