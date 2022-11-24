# -*- coding: utf-8 -*-
"""Parse RDF serialized as turtle files.

Unlike the ntriples parser, this parser cannot efficiently parse turtle line
by line. If a file-like object is provided, the entire file will be read into
memory and parsed there.

"""
import os

import lark_cython
from lark import Lark, Transformer, Tree
from lark.lexer import Token

import rdflib
from rdflib.experimental.plugins.parsers.parserutil import (
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


def unpack_predicateobjectlist(subject, pol):
    if not isinstance(subject, (rdflib.URIRef, rdflib.BNode)):
        for triple_or_node in subject:
            if isinstance(triple_or_node, tuple):
                yield triple_or_node
            else:
                subject = triple_or_node
                break

    for predicate, object_ in grouper(pol, 2):
        if isinstance(predicate, (lark_cython.Token, Token)):
            if predicate.value != "a":
                raise ValueError(predicate)
            predicate = RDF_TYPE

        if not isinstance(object_, (rdflib.URIRef, rdflib.Literal, rdflib.BNode)):
            if isinstance(object_, Tree):
                object_ = object_.children
            for triple_or_node in object_:
                if isinstance(triple_or_node, tuple):
                    yield triple_or_node
                else:
                    object_ = triple_or_node
                    yield (
                        subject,
                        predicate,
                        object_,
                    )
        else:
            yield (
                subject,
                predicate,
                object_,
            )


class TurtleTransformer(BaseParser, Transformer):
    def __init__(self, base_iri=""):
        super().__init__()
        self.base_iri = base_iri
        self.prefixes = self.profile
        self.preserve_bnode_ids = True
        self.bidprefix = None

    def decode_iriref(self, iriref):
        return validate_iri(decode_literal(iriref[1:-1]))

    def iri(self, children):
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

    def predicateobjectlist(self, children):
        return children

    def triples(self, children):
        if len(children) == 2:
            subject = children[0]
            for triple in unpack_predicateobjectlist(subject, children[1]):
                yield triple
        elif len(children) == 1:
            for triple_or_node in children[0]:
                if isinstance(triple_or_node, tuple):
                    yield triple_or_node

    def prefixedname(self, children):
        (pname,) = children
        ns, _, ln = pname.value.partition(":")
        return rdflib.URIRef(self.prefixes[ns] + decode_literal(ln))

    def prefixid(self, children):
        ns, iriref = children
        iri = smart_urljoin(self.base_iri, self.decode_iriref(iriref))
        ns = ns.value[:-1]  # Drop trailing : from namespace
        self.prefixes[ns] = iri

        return []

    def sparqlprefix(self, children):
        return self.prefixid(children[1:])

    def base(self, children):
        base_directive, base_iriref = children

        self.base_iri = smart_urljoin(
            self.base_iri, self.decode_iriref(base_iriref.value)
        )

        return []

    def sparqlbase(self, children):
        return self.base(children)

    def blanknode(self, children):
        (bn,) = children

        if bn.type == "ANON":
            return self.make_blank_node()
        elif bn.type == "BLANK_NODE_LABEL":
            return self.make_blank_node(bn.value)
        else:
            raise NotImplementedError()

    def blanknodepropertylist(self, children):
        pl_root = self.make_blank_node()
        for pl_item in unpack_predicateobjectlist(pl_root, children[0]):
            yield pl_item
        yield pl_root

    def collection(self, children):
        prev_node = RDF_NIL
        for value in reversed(children):
            this_bn = self.make_blank_node()
            if not isinstance(value, (rdflib.URIRef, rdflib.Literal, rdflib.BNode)):
                for triple_or_node in value:
                    if isinstance(triple_or_node, tuple):
                        yield triple_or_node
                    else:
                        value = triple_or_node
                        break
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
        (boolean,) = children
        return rdflib.Literal(boolean, datatype=XSD_BOOLEAN)

    def astring(self, children):
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
        for child in children:
            if not isinstance(child, Tree):
                for triple in child:
                    yield triple


turtle_lark = Lark(
    open(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "grammar", "turtle.lark")
        ),
        "r",
    ).read(),
    parser="lalr",
    debug=False,
    import_paths=[os.path.abspath(os.path.join(os.path.dirname(__file__), "grammar"))],
)


class LarkTurtleParser(rdflib.parser.Parser):
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

        tree = turtle_lark.parse(string)

        tf = TurtleTransformer(base_iri=base)
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

        for triple in tf.transform(tree):
            graph.add(triple)

        tf._cleanup_parse()

        return graph

    def parse_string(self, string_or_bytes, graph=None, base=""):
        return self.parse(string_or_bytes, graph, base)
