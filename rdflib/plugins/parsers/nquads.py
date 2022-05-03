"""
This is a rdflib plugin for parsing NQuad files into Conjunctive
graphs that can be used and queried. The store that backs the graph
*must* be able to handle contexts.

>>> from rdflib import ConjunctiveGraph, URIRef, Namespace
>>> g = ConjunctiveGraph()
>>> data = open("test/data/nquads.rdflib/example.nquads", "rb")
>>> g.parse(data, format="nquads") # doctest:+ELLIPSIS
<Graph identifier=... (<class 'rdflib.graph.Graph'>)>
>>> assert len(g.store) == 449
>>> # There should be 16 separate contexts
>>> assert len([x for x in g.store.contexts()]) == 16
>>> # is the name of entity E10009 "Arco Publications"?
>>> #   (in graph http://bibliographica.org/entity/E10009)
>>> # Looking for:
>>> # <http://bibliographica.org/entity/E10009>
>>> #   <http://xmlns.com/foaf/0.1/name>
>>> #   "Arco Publications"
>>> #   <http://bibliographica.org/entity/E10009>
>>> s = URIRef("http://bibliographica.org/entity/E10009")
>>> FOAF = Namespace("http://xmlns.com/foaf/0.1/")
>>> assert(g.value(s, FOAF.name).eq("Arco Publications"))
"""

from codecs import getreader

from rdflib import ConjunctiveGraph

# Build up from the NTriples parser:
from rdflib.plugins.parsers.ntriples import (
    ParseError,
    W3CNTriplesParser,
    r_tail,
    r_wspace,
)

__all__ = ["NQuadsParser"]


class NQuadsParser(W3CNTriplesParser):
    def parse(self, inputsource, sink, bnode_context=None, **kwargs):
        """
        Parse inputsource as an N-Quads file.

        :type inputsource: `rdflib.parser.InputSource`
        :param inputsource: the source of N-Quads-formatted data
        :type sink: `rdflib.graph.Graph`
        :param sink: where to send parsed triples
        :type bnode_context: `dict`, optional
        :param bnode_context: a dict mapping blank node identifiers to `~rdflib.term.BNode` instances.
                              See `.NTriplesParser.parse`
        """
        assert sink.store.context_aware, (
            "NQuadsParser must be given" " a context aware store."
        )
        self.sink = ConjunctiveGraph(store=sink.store, identifier=sink.identifier)

        source = inputsource.getCharacterStream()
        if not source:
            source = inputsource.getByteStream()
            source = getreader("utf-8")(source)

        if not hasattr(source, "read"):
            raise ParseError("Item to parse must be a file-like object.")

        self.file = source
        self.buffer = ""
        while True:
            self.line = __line = self.readline()
            if self.line is None:
                break
            try:
                self.parseline(bnode_context)
            except ParseError as msg:
                raise ParseError("Invalid line (%s):\n%r" % (msg, __line))

        return self.sink

    def parseline(self, bnode_context=None):
        self.eat(r_wspace)
        if (not self.line) or self.line.startswith(("#")):
            return  # The line is empty or a comment

        subject = self.subject(bnode_context)
        self.eat(r_wspace)

        predicate = self.predicate()
        self.eat(r_wspace)

        obj = self.object(bnode_context)
        self.eat(r_wspace)

        context = self.uriref() or self.nodeid(bnode_context) or self.sink.identifier
        self.eat(r_tail)

        if self.line:
            raise ParseError("Trailing garbage")
        # Must have a context aware store - add on a normal Graph
        # discards anything where the ctx != graph.identifier
        self.sink.get_context(context).add((subject, predicate, obj))
