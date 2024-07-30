from __future__ import annotations

from codecs import getreader
from enum import Enum
from typing import Any, MutableMapping, Optional

from rdflib.exceptions import ParserError as ParseError
from rdflib.graph import Dataset
from rdflib.parser import InputSource
from rdflib.plugins.parsers.nquads import NQuadsParser
# Build up from the NTriples parser:
from rdflib.plugins.parsers.ntriples import r_wspace
from rdflib.term import BNode

__all__ = ["RDFPatchParser"]

_BNodeContextType = MutableMapping[str, BNode]


class Operation(Enum):
    AddTripleOrQuad = 'A'
    DeleteTripleOrQuad = 'D'
    AddPrefix = 'PA'
    DeletePrefix = 'PD'
    TransactionStart = 'TX'
    TransactionCommit = 'TC'
    TransactionAbort = 'TA'
    Header = 'H'


class RDFPatchParser(NQuadsParser):
    def parse(  # type: ignore[override]
        self,
        inputsource: InputSource,
        sink: Dataset,
        bnode_context: Optional[_BNodeContextType] = None,
        skolemize: bool = False,
        **kwargs: Any,
    ) -> Dataset:
        """
        Parse inputsource as an RDF Patch file.

        :type inputsource: `rdflib.parser.InputSource`
        :param inputsource: the source of RDF Patch formatted data
        :type sink: `rdflib.graph.Graph`
        :param sink: where to send parsed data
        :type bnode_context: `dict`, optional
        :param bnode_context: a dict mapping blank node identifiers to `~rdflib.term.BNode` instances.
                              See `.W3CNTriplesParser.parse`
        """
        assert sink.store.context_aware, (
            "RDFPatchParser must be given" " a context aware store."
        )
        # type error: Incompatible types in assignment (expression has type "ConjunctiveGraph", base class "W3CNTriplesParser" defined the type as "Union[DummySink, NTGraphSink]")
        self.sink: Dataset = Dataset(  # type: ignore[assignment]
            store=sink.store
        )
        self.skolemize = skolemize

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
                self.parsepatch(bnode_context)
            except ParseError as msg:
                raise ParseError("Invalid line (%s):\n%r" % (msg, __line))

        if self.skolemize:
            return self.sink
        else:
            self.sink = self.sink.de_skolemize()
            return self.sink  # Dataset is skolemized as part of adding/removing triples
            # , so de skolemize before returning. NB this is broken by the parent class
            # (ConjunctiveGraph) which re-skolemizes the dataset.

    def parsepatch(self, bnode_context: Optional[_BNodeContextType] = None) -> None:
        self.eat(r_wspace)
        #  From spec: "No comments should be included (comments start # and run to end
        #  of line)."
        if (not self.line) or self.line.startswith("#"):
            return  # The line is empty or a comment

        # if header, transaction, skip
        operation = self.operation()
        self.eat(r_wspace)

        if operation == Operation.AddTripleOrQuad:
            self.add_triple_or_quad()
        elif operation == Operation.DeleteTripleOrQuad:
            self.delete_triple_or_quad()
        elif operation == Operation.AddPrefix:
            self.add_prefix()
        elif operation == Operation.DeletePrefix:
            self.delete_prefix()

    def add_triple_or_quad(self):
        self.sink.parse(data=self.line, format='nquads', skolemize=True)

    def delete_triple_or_quad(self):
        removal_ds = Dataset()
        removal_ds.parse(data=self.line, format='nquads', skolemize=True)
        triple_or_quad = next(iter(removal_ds))
        self.sink.remove(triple_or_quad)

    def add_prefix(self):
        # Extract prefix and URI from the line
        prefix, ns, _ = self.line.replace('"', "").replace("'", "").split(" ")
        ns_stripped = ns.strip("<>")
        self.sink.bind(prefix, ns_stripped)

    def delete_prefix(self):
        prefix, _, _ = self.line.replace('"', "").replace("'", "").split(" ")
        self.sink.namespace_manager.bind(prefix, None, replace=True)

    def operation(self) -> Operation:
        for op in Operation:
            if self.line.startswith(op.value):
                self.eat_op(op.value)
                return op
        raise ValueError(
            f"Invalid or no Operation found in line: \"{self.line}\". Valid Operations "
            f"codes are {', '.join([op.value for op in Operation])}")

    def eat_op(self, op: str) -> None:
        self.line = self.line.lstrip(op)
