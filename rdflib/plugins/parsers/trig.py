from __future__ import annotations

from typing import Any, MutableSequence

from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.parser import InputSource, Parser

from .notation3 import RDFSink, SinkParser


def becauseSubGraph(*args, **kwargs):
    pass


class TrigSinkParser(SinkParser):
    def directiveOrStatement(self, argstr: str, h: int) -> int:  # noqa: N802
        # import pdb; pdb.set_trace()

        i = self.skipSpace(argstr, h)
        if i < 0:
            return i  # EOF

        j = self.graph(argstr, i)
        if j >= 0:
            return j

        j = self.sparqlDirective(argstr, i)
        if j >= 0:
            return j

        j = self.directive(argstr, i)
        if j >= 0:
            return self.checkDot(argstr, j)

        j = self.statement(argstr, i)
        if j >= 0:
            return self.checkDot(argstr, j)

        return j

    def labelOrSubject(  # noqa: N802
        self, argstr: str, i: int, res: MutableSequence[Any]
    ) -> int:
        j = self.skipSpace(argstr, i)
        if j < 0:
            return j  # eof
        i = j

        j = self.uri_ref2(argstr, i, res)
        if j >= 0:
            return j

        if argstr[i] == "[":
            j = self.skipSpace(argstr, i + 1)
            if j < 0:
                self.BadSyntax(argstr, i, "Expected ] got EOF")
            if argstr[j] == "]":
                res.append(self.blankNode())
                return j + 1
        return -1

    def graph(self, argstr: str, i: int) -> int:
        """
        Parse trig graph, i.e.

           <urn:graphname> = { .. triples .. }

        return -1 if it doesn't look like a graph-decl
        raise Exception if it looks like a graph, but isn't.
        """

        # import pdb; pdb.set_trace()
        j = self.sparqlTok("GRAPH", argstr, i)  # optional GRAPH keyword
        if j >= 0:
            i = j

        r: MutableSequence[Any] = []
        j = self.labelOrSubject(argstr, i, r)
        if j >= 0:
            graph = r[0]
            i = j
        else:
            graph = self._store.graph.identifier  # hack

        j = self.skipSpace(argstr, i)
        if j < 0:
            self.BadSyntax(argstr, i, "EOF found when expected graph")

        if argstr[j : j + 1] == "=":  # optional = for legacy support
            i = self.skipSpace(argstr, j + 1)
            if i < 0:
                self.BadSyntax(argstr, i, "EOF found when expecting '{'")
        else:
            i = j

        if argstr[i : i + 1] != "{":
            return -1  # the node wasn't part of a graph

        j = i + 1

        oldParentContext = self._parentContext
        self._parentContext = self._context
        reason2 = self._reason2
        self._reason2 = becauseSubGraph
        # type error: Incompatible types in assignment (expression has type "Graph", variable has type "Optional[Formula]")
        self._context = self._store.newGraph(graph)  # type: ignore[assignment]

        while 1:
            i = self.skipSpace(argstr, j)
            if i < 0:
                self.BadSyntax(argstr, i, "needed '}', found end.")

            if argstr[i : i + 1] == "}":
                j = i + 1
                break

            j = self.directiveOrStatement(argstr, i)
            if j < 0:
                self.BadSyntax(argstr, i, "expected statement or '}'")

        self._context = self._parentContext
        self._reason2 = reason2
        self._parentContext = oldParentContext
        # res.append(subj.close())    # No use until closed
        return j


class TrigParser(Parser):
    """
    An RDFLib parser for TriG

    """

    def __init__(self):
        pass

    def parse(self, source: InputSource, graph: Graph, encoding: str = "utf-8") -> None:
        if encoding not in [None, "utf-8"]:
            raise Exception(
                # type error: Unsupported left operand type for % ("Tuple[str, str]")
                ("TriG files are always utf-8 encoded, ", "I was passed: %s")  # type: ignore[operator]
                % encoding
            )

        # we're currently being handed a Graph, not a ConjunctiveGraph
        assert graph.store.context_aware, "TriG Parser needs a context-aware store!"

        conj_graph = ConjunctiveGraph(store=graph.store, identifier=graph.identifier)
        conj_graph.default_context = graph  # TODO: CG __init__ should have a
        # default_context arg
        # TODO: update N3Processor so that it can use conj_graph as the sink
        conj_graph.namespace_manager = graph.namespace_manager

        sink = RDFSink(conj_graph)

        baseURI = conj_graph.absolutize(
            source.getPublicId() or source.getSystemId() or ""
        )
        p = TrigSinkParser(sink, baseURI=baseURI, turtle=True)

        stream = source.getCharacterStream()  # try to get str stream first
        if not stream:
            # fallback to get the bytes stream
            stream = source.getByteStream()
        p.loadStream(stream)

        for prefix, namespace in p._bindings.items():
            conj_graph.bind(prefix, namespace)

        # return ???
