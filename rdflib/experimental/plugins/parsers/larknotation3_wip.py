# -*- coding: utf-8 -*-
"""Parse RDF serialized as turtle files.

Unlike the ntriples parser, this parser cannot efficiently parse turtle line
by line. If a file-like object is provided, the entire file will be read into
memory and parsed there.

"""
import os
from pprint import pformat
import re

import lark_cython
from lark import Lark, Transformer, Tree
from lark.lexer import Token

import rdflib

from rdflib.plugins.parsers.parserutil import (
    BaseParser,
    decode_literal,
    grouper,
    smart_urljoin,
    validate_iri,
)

RDF_TYPE = rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
RDF_NIL = rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#nil")
RDF_FIRST = rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#first")
RDF_REST = rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest")

XSD_DECIMAL = rdflib.URIRef("http://www.w3.org/2001/XMLSchema#decimal")
XSD_DOUBLE = rdflib.URIRef("http://www.w3.org/2001/XMLSchema#double")
XSD_INTEGER = rdflib.URIRef("http://www.w3.org/2001/XMLSchema#integer")
XSD_BOOLEAN = rdflib.URIRef("http://www.w3.org/2001/XMLSchema#boolean")
XSD_STRING = rdflib.URIRef("http://www.w3.org/2001/XMLSchema#string")

LOG_NS = rdflib.Namespace("http://www.w3.org/2000/10/swap/log#")

RDFLIB_OBJECTS = (
    rdflib.graph.QuotedGraph,
    rdflib.BNode,
    rdflib.Literal,
    rdflib.URIRef,
    rdflib.Variable,
)


def unpack_formulacontent(graph, content):
    rdflib.logger.info(f"graph = {graph.identifier} content = {content}")
    for triplesgenerator in content:
        if isinstance(triplesgenerator, list):
            graph = unpack_formulacontent(graph, triplesgenerator)
        else:
            for triple in triplesgenerator:
                graph.add(triple)
    return graph


def unpack_predicateobjectlist(subject, pol):
    rdflib.logger.info(f"subject = {subject} pol = {pol}")
    if not isinstance(subject, (rdflib.URIRef, rdflib.BNode)):
        rdflib.logger.info(f"UPOL SUBJECT {subject} ({type(subject)})")
    # if not isinstance(subject, RDFLIB_OBJECTS):
    if not isinstance(subject, (rdflib.URIRef, rdflib.BNode, rdflib.Variable)):
        for triple_or_node in subject:
            if isinstance(triple_or_node, tuple):
                rdflib.logger.info(f"AA UPOL YIELDING {triple_or_node}")
                yield triple_or_node
            else:
                rdflib.logger.info(f"AA UPOL SETTING subject from {triple_or_node}")
                subject = triple_or_node
                break

    for predicate, object_ in grouper(pol, 2):

        rdflib.logger.info(f"BB UPOL GROUPED: s={subject} p={predicate}, o={object_}")

        assert not isinstance(predicate, (lark_cython.Token, Token))
        # Maybe no longer neccessary with !rule
        # if isinstance(predicate, (lark_cython.Token, Token)):
        #     raise Exception(f"BB NEVER GETS TO HERE {predicate}")
        #     if predicate.value != "a":
        #         raise ValueError(predicate)
        #     predicate = RDF_TYPE

        assert not isinstance(object_, Tree)
        # if isinstance(object_, Tree):
        #     raise Exception(f"BB NEVER GETS TO HERE {predicate}")
        #     rdflib.logger.info(f"BB HAD TO DEAL WITH TREE: {object_}")
        #     object_ = object_.children

        for obj in object_:
            rdflib.logger.info(f"BB UPOL ITERATING OVER {object_}")

            for object_item in object_:

                rdflib.logger.info(
                    f"CC UPOL PROCESSING {object_item} ({type(object_item)})"
                )

                object_ = object_item
                rdflib.logger.info(
                    f"CC UPOL YIELDING triple ({subject} {predicate} {object_})"
                )
                yield (
                    subject,
                    predicate,
                    object_item,
                )


class Notation3Transformer(BaseParser, Transformer):
    def __init__(self, base_iri=""):
        super().__init__()
        self.base_iri = base_iri
        self.prefixes = self.profile
        self.preserve_bnode_ids = True
        self.bidprefix = None

    def blank_node_label(self, children):
        (bn_label,) = children
        return self.make_blank_node(bn_label.value)

    def inneroperator(self, children):
        (child,) = children
        ops = {"=>": LOG_NS.implies, "=": rdflib.OWL.sameAs, "<=": LOG_NS.implies}
        op = ops.get(child, None)
        if op is not None:
            return rdflib.term.URIRef(op)
        else:
            return child

    def decode_iriref(self, iriref):
        iriref = (
            iriref.value
            if isinstance(iriref, lark_cython.lark_cython.Token)
            else iriref
        )
        return validate_iri(decode_literal(iriref[1:-1]))

    def iri(self, children):
        # rdflib.logger.info(f"{children}")
        (iriref_or_pname,) = children
        iriref_or_pname = (
            iriref_or_pname
            if isinstance(iriref_or_pname, rdflib.URIRef)
            else iriref_or_pname.value
        )
        if iriref_or_pname.startswith("<"):
            return rdflib.URIRef(
                smart_urljoin(self.base_iri, self.decode_iriref(iriref_or_pname))
            )

        return iriref_or_pname

    def irilist(self, children):
        rdflib.logger.info(f"{children}")
        return children

    def predicateobjectlist(self, children):
        # rdflib.logger.info(f"{children}")
        return children

    def formula(self, children):
        # rdflib.logger.info(f"{children}")
        formulagraph = unpack_formulacontent(self.make_quotedgraph(), children)
        # rdflib.logger.info(f"{formulagraph}")
        return formulagraph

    def triples(self, children):
        rdflib.logger.info(f"{children}")
        if len(children) == 1:
            rdflib.logger.info(f"UNPACKING CHILD TRIPLES")
            for triple_or_node in children[0]:
                if isinstance(triple_or_node, tuple):
                    rdflib.logger.info(f"TRIPLES YIELDING {triple_or_node}")
                    self._call_state.graph.add(triple_or_node)
                    yield triple_or_node

        elif len(children) == 2:
            subject = children[0]
            rdflib.logger.info(f"CALLING UPOL WITH {subject} {children[1]}")
            for triple in unpack_predicateobjectlist(subject, children[1]):
                rdflib.logger.info(f"PROCESSING UPOL YIELD {triple} AS TRIPLE")
                self._call_state.graph.add(triple)
                yield triple

    def objectlist(self, children):
        # rdflib.logger.info(f"{children}")
        return children

    def formulacontent(self, children):
        # rdflib.logger.info(f"{children}")
        return children

    def forall(self, children):
        rdflib.logger.info(f"{children}")
        return children

    def forsome(self, children):
        rdflib.logger.info(f"{children}")
        return children

    def n3statement(self, children):
        # rdflib.logger.info(f"{children} -> {children[0]}")
        return children[0]

    def verb(self, children):
        # rdflib.logger.info(f"{children} -> {children[0]}")
        if len(children) == 1:
            return children[0]
        else:
            rdflib.logger.info(f"VERB PASSTHROUGH {children[0]}")
            return children

    def subject(self, children):
        # rdflib.logger.info(f"{children} -> {children[0]}")
        return children[0]

    def predicate(self, children):
        # rdflib.logger.info(f"{children} -> {children[0]}")
        return children[0]

    def object(self, children):
        # rdflib.logger.info(f"{children} -> {children[0]}")
        return children[0]

    def expression(self, children):
        # rdflib.logger.info(f"{children} -> {children[0]}")
        return children[0]

    def path(self, children):
        # rdflib.logger.info(f"{children} -> {children[0]}")
        return children[0]

    def pathitem(self, children):
        # rdflib.logger.info(f"{children} -> {children[0]}")
        return children[0]

    def literal(self, children):
        # rdflib.logger.info(f"{children} -> {children[0]}")
        return children[0]

    def quickvar(self, children):
        # rdflib.logger.info(f"{children} -> {children[0].value}")
        return rdflib.term.Variable(children[0].value)

    def n3directive(self, children):
        # rdflib.logger.info(f"{children} BYCHILD")
        for child in children:
            yield child

    def sparql_directive(self, children):
        # rdflib.logger.info(f"{children} BYCHILD")
        for child in children:
            yield child

    def prefixedname(self, children):
        # rdflib.logger.info(f"{children}")
        (pname,) = children
        ns, _, ln = pname.value.partition(":")
        return rdflib.URIRef(self.prefixes[ns] + decode_literal(ln))

    def prefixid(self, children):
        # rdflib.logger.info(f"{children}")
        ns, iriref = children
        iri = smart_urljoin(self.base_iri, self.decode_iriref(iriref))
        ns = ns.value[:-1]  # Drop trailing : from namespace
        self.prefixes[ns] = iri

        return []

    def sparqlprefix(self, children):
        rdflib.logger.info(f"{children}")
        return self.prefixid(children[1:])

    def base(self, children):
        rdflib.logger.info(f"{children}")
        base_directive, base_iriref = children

        self.base_iri = smart_urljoin(
            self.base_iri, self.decode_iriref(base_iriref.value)
        )

        return []

    def sparqlbase(self, children):
        rdflib.logger.info(f"{children}")
        return self.base(children)

    def blanknode(self, children):
        # rdflib.logger.info(f"{children}")
        (bn,) = children

        if bn.type == "ANON":
            return self.make_blank_node()
        elif bn.type == "BLANK_NODE_LABEL":
            return self.make_blank_node(bn.value)
        else:
            raise NotImplementedError()

    def blanknodepropertylist(self, children):
        rdflib.logger.info(f"{children}")
        pl_root = self.make_blank_node()
        for pl_item in unpack_predicateobjectlist(pl_root, children[0]):
            rdflib.logger.info(f"BNPL YIELDING plitem {pl_item}")
            yield pl_item
        yield pl_root

    def collection(self, children):
        rdflib.logger.info(f"{children}")
        prev_node = RDF_NIL
        for value in reversed(children):
            this_bn = self.make_blank_node()
            if not isinstance(value, (rdflib.URIRef, rdflib.Literal, rdflib.BNode)):
                rdflib.logger.info(f"COLLECTION0 {repr(value)}")
                for triple_or_node in value:
                    if isinstance(triple_or_node, tuple):
                        rdflib.logger.info(
                            f"COLLECTION YIELDING {repr(triple_or_node)}"
                        )
                        yield triple_or_node
                    else:
                        rdflib.logger.info(
                            f"COLLECTION SETTING value to {repr(triple_or_node)}"
                        )
                        value = triple_or_node
                        break
            rdflib.logger.info(f"COLLECTION2 {repr(value)}")
            if not isinstance(value, (rdflib.URIRef, rdflib.Literal, rdflib.BNode)):
                yield (
                    this_bn,
                    RDF_FIRST,
                    this_bn,
                )
            else:
                yield (
                    this_bn,
                    RDF_FIRST,
                    value,
                )
            yield (
                this_bn,
                RDF_REST,
                prev_node,
            )
            prev_node = this_bn

        yield prev_node

    def numericliteral(self, children):
        # rdflib.logger.info(f"{children}")
        (numeric,) = children

        if numeric.type == "DECIMAL":
            return rdflib.Literal(numeric, datatype=XSD_DECIMAL)
        elif numeric.type == "DOUBLE":
            return rdflib.Literal(numeric, datatype=XSD_DOUBLE)
        elif numeric.type == "INTEGER":
            return rdflib.Literal(numeric, datatype=XSD_INTEGER)
        else:
            raise NotImplementedError(f"{numeric} {type(numeric)} {repr(numeric)}")

    def rdfliteral(self, children):
        # rdflib.logger.info(f"{children}")
        literal_string = children[0]
        lang = None
        type_ = None
        if len(children) == 2 and isinstance(children[1], rdflib.URIRef):
            type_ = children[1]
            return rdflib.Literal(literal_string, datatype=type_)
        elif len(children) == 2 and children[1].type == "LANGTAG":
            lang = children[1].value[1:]  # Remove @
            return rdflib.Literal(literal_string, lang=lang)
        else:
            return rdflib.Literal(literal_string, datatype=None)

    def booleanliteral(self, children):
        # rdflib.logger.info(f"{children}")
        (boolean,) = children
        return rdflib.Literal(boolean, datatype=XSD_BOOLEAN)

    def astring(self, children):
        # rdflib.logger.info(f"{children}")
        (literal,) = children
        if literal.type in (
            "STRING_LITERAL_QUOTE",
            "STRING_LITERAL_SINGLE_QUOTE",
        ):
            string = decode_literal(literal.value[1:-1])
        if literal.type in (
            "STRING_LITERAL_LONG_SINGLE_QUOTE",
            "STRING_LITERAL_LONG_QUOTE",
        ):
            string = decode_literal(literal.value[3:-3])

        return string

    def start(self, children):
        rdflib.logger.info(f"{children}")
        for child in children:
            if not isinstance(child, Tree):
                for triple in child:
                    # rdflib.logger.info(f"YIELDING {triple}")
                    yield triple


notation3_lark = Lark(
    open(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "grammar", "notation3speedup.lark")
        ),
        "r",
    ).read(),
    parser="lalr",
    # transformer=TurtleTransformer(ds = rdflib.Dataset(identifier=rdflib.URIRef("urn:example:context0"))),
    transformer=Notation3Transformer(),
    debug=False,
    _plugins=lark_cython.plugins,
)


class LarkN3Parser(rdflib.parser.Parser):
    format = None

    def parse(self, string_or_stream, graph=None, base="", **kwargs):

        if not isinstance(string_or_stream, str) and not isinstance(
            string_or_stream, rdflib.parser.InputSource
        ):
            string_or_stream = rdflib.parser.create_input_source(string_or_stream)
        elif isinstance(string_or_stream, str):
            try:
                validate_iri(string_or_stream)
                string_or_stream = rdflib.parser.create_input_source(string_or_stream)
            except Exception:
                # Is probably data
                pass

        if hasattr(string_or_stream, "readline"):
            string = string_or_stream.read()
        else:
            # Presume string.
            string = string_or_stream

        if isinstance(string_or_stream, bytes):
            string = string_or_stream.decode("utf-8")
        else:
            string = string_or_stream

        # TODO: stringify the remaining input sources
        if isinstance(string, rdflib.parser.FileInputSource):
            string = string.file.read().decode()
        elif isinstance(string, rdflib.parser.StringInputSource):
            string = string.getCharacterStream().read()

        tf = notation3_lark.options.transformer
        tf.base_iri = base
        tf.preserve_bnode_ids = kwargs.get("preserve_bnode_ids", False)
        tf.bidprefix = kwargs.get("bidprefix", None)
        bindings = kwargs.get("bindings", dict())

        if graph is None:
            graph = tf._make_graph()

        for p, n in rdflib.namespace._NAMESPACE_PREFIXES_CORE.items():
            if p not in tf.prefixes:
                tf.prefixes[p] = n

        for p, n in bindings.items():
            if p not in tf.prefixes:
                tf.prefixes[p] = n

        for p, n in tf.prefixes.items():
            graph.bind(p, n)

        tf._prepare_parse(graph)

        list(notation3_lark.parse(string))

        # Nononono BUT, illuminates the issue
        for (f1, f2) in graph.subject_objects(LOG_NS.implies):
            for triple in f1:
                rdflib.logger.info(f"TRIPLE {triple}")
                graph.store.remove(triple, context=graph.identifier)

        tf._cleanup_parse()

        return graph

    def parse_string(self, string_or_bytes, graph=None, base=""):
        return self.parse(string_or_bytes, graph, base)
