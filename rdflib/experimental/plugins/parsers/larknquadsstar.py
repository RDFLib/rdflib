"""Parse RDF serialized as nquads files.

Usage::

If ``.parse()`` is called with a file-like object implementing ``readline``,
it will efficiently parse line by line rather than parsing the entire file.
"""
import hashlib
import os
from urllib.parse import urlparse

import lark_cython
from lark import Lark, Transformer

import rdflib
from rdflib.experimental.plugins.parsers.parserutil import (
    BaseParser,
    decode_literal,
    validate_iri,
)
from rdflib.experimental.term import RDFStarTriple


class NQuadsStarTransformer(BaseParser, Transformer):
    """Transform the tokenized ntriples into RDF primitives."""

    def __init__(self, base_iri=""):
        super().__init__()
        self.base_iri = base_iri
        self.prefixes = self.profile
        self.preserve_bnode_ids = True
        self.bidprefix = None
        self.context = None
        self.annotations = {}

    def blank_node_label(self, children):
        (bn_label,) = children
        return self.make_blank_node(bn_label.value)

    def decode_iriref(self, iriref):
        assert urlparse(iriref.value[1:-1]).scheme != ""
        return validate_iri(decode_literal(iriref.value[1:-1]))

    def iriref(self, children):
        (iriref_or_pname,) = children

        if iriref_or_pname.value.startswith("<"):
            assert " " not in iriref_or_pname.value, iriref_or_pname
            return rdflib.URIRef(self.decode_iriref(iriref_or_pname))

        return iriref_or_pname

    def literal(self, children):
        quoted_literal = children[0]

        quoted_literal = quoted_literal.value[1:-1]  # Remove ""s
        literal = decode_literal(quoted_literal)

        if len(children) == 2 and children[1].type == "IRIREF":
            datatype = children[1]
            return rdflib.Literal(literal, datatype=self.decode_iriref(datatype))

        elif len(children) == 2 and children[1].type == "LANGTAG":
            lang = children[1].value[1:]  # Remove @
            return rdflib.Literal(literal, lang=lang)
        else:
            return rdflib.Literal(literal, lang=None)

    def subject_or_object(self, children):
        # child[0] is a Triple if the subject is a quoted statement
        if isinstance(children[0], tuple):
            q = self.quotedstatement(children)
            self._call_state.graph.add(q)

        else:
            # Just an non-embedded term
            return children[0]

    def subject(self, children):
        return self.subject_or_object(children)

    def object(self, children):
        return self.subject_or_object(children)

    def quotedstatement(self, children):
        s, p, o = children
        hashid = hashlib.md5("-".join(children).encode("utf-8")).hexdigest()
        try:
            q = self.annotations[hashid]
        except KeyError:
            q = RDFStarTriple(hashid)
            q.setsubject(s)
            q.setpredicate(p)
            q.setobject(o)
            self.annotations[hashid] = q
        return q

    def statement(self, children):
        if len(children) == 3:
            subject, predicate, object_ = children
            graph = rdflib.graph.DATASET_DEFAULT_GRAPH_ID
        else:
            subject, predicate, object_, graph = children

        self.context = graph
        self._call_state.graph.addN([(subject, predicate, object_, graph)])
        return children

    def start(self, children):
        for child in children:
            yield child


nqstar_lark = Lark(
    open(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "grammar", "nquads-star.lark")
        ),
        "r",
    ).read(),
    parser="lalr",
    transformer=NQuadsStarTransformer(),
    _plugins=lark_cython.plugins,
)


class LarkNQuadsStarParser(rdflib.parser.Parser):
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

        # W3C test suite authors create tests for whitespace and
        # comment processing, unfortunately omitted from the
        # NTriples EBNF grammar specification.

        uncommented_input = "\n".join(
            [s.strip() for s in string.split("\n") if not s.startswith("#") and s != ""]
        )

        tf = nqstar_lark.options.transformer
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

        statements = nqstar_lark.parse(uncommented_input)

        tf._cleanup_parse()

        return graph

    def parse_string(self, string_or_bytes, graph=None, base=""):
        return self.parse(string_or_bytes, graph, base)
