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
from __future__ import annotations

from codecs import getreader
from typing import Any, MutableMapping, Optional

from rdflib.exceptions import ParserError as ParseError
from rdflib.graph import ConjunctiveGraph
from rdflib.parser import InputSource

# Build up from the NTriples parser:
from rdflib.plugins.parsers.ntriples import W3CNTriplesParser, r_tail, r_wspace
from rdflib.term import BNode

__all__ = ["NQuadsParser"]

_BNodeContextType = MutableMapping[str, BNode]


class NQuadsParser(W3CNTriplesParser):
    # type error: Signature of "parse" incompatible with supertype "W3CNTriplesParser"
    def parse(  # type: ignore[override]
        self,
        inputsource: InputSource,
        sink: ConjunctiveGraph,
        bnode_context: Optional[_BNodeContextType] = None,
        **kwargs: Any,
    ) -> ConjunctiveGraph:
        """
        Parse inputsource as an N-Quads file.

        :type inputsource: `rdflib.parser.InputSource`
        :param inputsource: the source of N-Quads-formatted data
        :type sink: `rdflib.graph.Graph`
        :param sink: where to send parsed triples
        :type bnode_context: `dict`, optional
        :param bnode_context: a dict mapping blank node identifiers to `~rdflib.term.BNode` instances.
                              See `.W3CNTriplesParser.parse`
        """
        assert sink.store.context_aware, (
            "NQuadsParser must be given" " a context aware store."
        )
        # type error: Incompatible types in assignment (expression has type "ConjunctiveGraph", base class "W3CNTriplesParser" defined the type as "Union[DummySink, NTGraphSink]")
        self.sink: ConjunctiveGraph = ConjunctiveGraph(  # type: ignore[assignment]
            store=sink.store, identifier=sink.identifier
        )

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

    def parseline(self, bnode_context: Optional[_BNodeContextType] = None) -> None:
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
