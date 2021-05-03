"""
This is a rdflib plugin for parsing NQuad files into Conjunctive
graphs that can be used and queried. The store that backs the graph
*must* be able to handle contexts.

>>> from rdflib import ConjunctiveGraph, URIRef, Namespace
>>> g = ConjunctiveGraph()
>>> data = open("test/nquads.rdflib/example.nquads", "rb")
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
import re

from rdflib import ConjunctiveGraph

# Build up from the NTriples parser:
from rdflib.plugins.parsers.ntriples import W3CNTriplesParser
from rdflib.plugins.parsers.ntriples import ParseError
from rdflib.plugins.parsers.ntriples import tail
from rdflib.plugins.parsers.ntriples import wspace
from rdflib.plugins.parsers.ntriples import wspaces
from rdflib.plugins.parsers.ntriples import r_comment_or_empty

__all__ = ["NQuadsParser"]


r_uriref_predicate_object_context = re.compile(wspace + r"([<_][^ ]+)"
                                               + wspaces + r"(<[^ ]+)"
                                               + wspaces + r'(".*[^\\]"[^ \t]*|<[^>]*>|_[^ ]*)'
                                               + wspaces + r"([^ ]+)?"
                                               + tail)

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
        return self.processing_loop(bnode_context)

    def parseline(self, the_line, bnode_context=None):
        # This splits the line into four component because this is a quad.
        # The logic is similar for triples, except the context as fourth component.
        m = r_uriref_predicate_object_context.match(the_line)
        if not m:
            # Very rare case, so performances are less important.
            if r_comment_or_empty.match(the_line):
                return  # The line is a comment
            raise ParseError("Not a quad")

        first_token, second_token, third_token, fourth_token, _ = m.groups()

        subject = self.uriref(first_token) or self.nodeid(first_token, bnode_context)
        if not subject:
            raise ParseError("Subject must be uriref or nodeID")

        predicate = self.uriref(second_token)
        if not predicate:
            raise ParseError("Predicate must be uriref")

        obj = self.uriref(third_token) or self.nodeid(third_token, bnode_context) or self.literal(third_token)
        if obj is False:
            raise ParseError("Unrecognised object type")

        if fourth_token:
            context = self.uriref(fourth_token) or self.nodeid(fourth_token, bnode_context)
        else:
            context = self.sink.identifier

        # Must have a context aware store - add on a normal Graph
        # discards anything where the ctx != graph.identifier
        self.sink.get_context(context).add((subject, predicate, obj))
