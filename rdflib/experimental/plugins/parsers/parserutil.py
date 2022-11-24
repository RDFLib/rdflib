"""Utility functions used to support lark parsing."""

import collections
import hashlib
import logging
import re
from threading import local

import rdflib

__all__ = [
    "BaseParser",
    "decode_literal",
    "grouper",
    "smart_urljoin",
    "validate_iri",
]

log = logging.getLogger(__name__)


ESCAPE_MAP = {
    "t": "\t",
    "b": "\b",
    "n": "\n",
    "r": "\r",
    "f": "\f",
    '"': '"',
    "'": "'",
    "\\": "\\",
}


def process_escape(escape):

    escape = escape.group(0)[1:]

    if escape[0] in ("u", "U"):
        return chr(int(escape[1:], 16))
    else:
        return ESCAPE_MAP.get(escape[0], escape[0])


def decode_literal(literal):
    return re.sub(
        r"\\u[a-fA-F0-9]{4}|\\U[a-fA-F0-9]{8}|\\[^uU]", process_escape, literal
    )


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"

    from itertools import zip_longest

    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def smart_urljoin(base, url):
    """urljoin, only an empty fragment from the relative(?) URL will be
    preserved.
    """
    from urllib.parse import urljoin

    joined = urljoin(base, url)
    if url.endswith("#") and not joined.endswith("#"):
        joined += "#"
    return joined


LEGAL_IRI = re.compile(r'^[^\x00-\x20<>"{}|^`\\]*$')


def validate_iri(iri):
    if not LEGAL_IRI.match(iri):
        raise ValueError(f"Illegal characters in IRI: “{iri}”")
    return iri


class BaseParser:
    """Common base class for all parsers

    Provides shared utilities for creating RDF objects, handling IRIs, and
    tracking parser state.
    """

    def __init__(self, sink=None):
        self.sink = sink if sink is not None else rdflib.graph.Dataset()
        # self.profile = Profile()
        self.profile = {}
        self._call_state = local()

    def make_blank_node(self, label=None):
        if label:
            if label in self._call_state.bnodes:
                node = self._call_state.bnodes[label]
            else:
                if self.preserve_bnode_ids is True:
                    node = rdflib.BNode(label[2:])
                else:
                    if self.bidprefix is None:
                        node = rdflib.BNode()
                    else:
                        node = rdflib.BNode(
                            f"{self.bidprefix}{self._call_state.bidcounter:0}"
                        )
                        self._call_state.bidcounter += 1
                self._call_state.bnodes[label] = node
        else:
            if self.bidprefix is None:
                node = rdflib.BNode()
            else:
                node = rdflib.BNode(f"{self.bidprefix}{self._call_state.bidcounter:0}")
                self._call_state.bidcounter += 1
            self._call_state.bnodes[node.n3()] = node
        return node

    def make_quotedgraph(self, store=None):
        self._call_state.formulacounter += 1
        return rdflib.graph.QuotedGraph(
            store=self._call_state.graph.store if store is None else store,
            identifier=f"Formula{self._call_state.formulacounter}",
        )

    def make_rdfstartriple(self, subject, predicate, object):
        rdflib.logger.info(f"make_rdfstartriple: ({subject}, {predicate}, {object})")
        sid = str(
            hashlib.md5((subject + predicate + object).encode("utf-8")).hexdigest()
        )
        return rdflib.experimental.term.RDFStarTriple(sid, subject, predicate, object)

    def _prepare_parse(self, graph):
        self._call_state.bnodes = collections.defaultdict(rdflib.term.BNode)
        self._call_state.graph = graph
        self._call_state.bidcounter = 1
        self._call_state.formulacounter = 0

    def _cleanup_parse(self):
        del self._call_state.bnodes
        del self._call_state.graph
        del self._call_state.bidcounter
        del self._call_state.formulacounter

    def _make_graph(self):
        return rdflib.ConjunctiveGraph()
