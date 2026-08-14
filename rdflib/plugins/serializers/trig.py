"""
Trig RDF graph serializer for RDFLib.
See <http://www.w3.org/TR/trig/> for syntax specification.
"""

from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from rdflib.graph import Dataset, Graph
from rdflib.plugins.serializers.turtle import TurtleSerializer
from rdflib.term import BNode, Node

if TYPE_CHECKING:
    from rdflib.graph import _ContextType, _SubjectType

__all__ = ["TrigSerializer"]


class TrigSerializer(TurtleSerializer):
    """TriG RDF graph serializer."""

    short_name = "trig"
    indentString = 4 * " "

    def __init__(self, store: Union[Graph, Dataset]):
        self.default_graph: Optional[Node]
        if store.context_aware:
            if TYPE_CHECKING:
                assert isinstance(store, Dataset)
            self.graphs = list(store.graphs())
            self.default_graph = store.default_graph.identifier
            if store.default_graph:
                self.graphs.append(store.default_graph)
        else:
            self.graphs = [store]
            self.default_graph = None

        super(TrigSerializer, self).__init__(store)

    def preprocess(self) -> None:
        for context in self.graphs:
            # do not write unnecessary prefix (ex: for an empty default graph)
            if len(context) == 0:
                continue
            self.store = context
            # Don't generate a new prefix for a graph URI if one already exists
            self.get_pname(context.identifier, False)
            self._subjects = {}

            for triple in context:
                self.preprocess_triple(triple)

            for subject in self._subjects.keys():
                self._references[subject] += 1

            self._graphs[context] = (self.order_subjects(), self._subjects)

    def reset(self) -> None:
        super(TrigSerializer, self).reset()
        self._graphs: Dict[
            _ContextType,
            Tuple[List[_SubjectType], Dict[_SubjectType, bool]],
        ] = {}

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = None,
        spacious: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        self.reset()
        self.stream = stream
        # if base is given here, use that, if not and a base is set for the graph use that
        if base is not None:
            self.base = base
        elif self.store.base is not None:
            self.base = self.store.base

        if spacious is not None:
            self._spacious = spacious

        self.preprocess()

        self.startDocument()

        firstTime = True
        for store, (ordered_subjects, subjects) in self._graphs.items():
            if not ordered_subjects:
                continue

            self._serialized = {}
            self.store = store
            self._subjects = subjects

            if self.default_graph and store.identifier == self.default_graph:
                self.write(self.indent() + "\n{")
            else:
                iri: Optional[str]
                if isinstance(store.identifier, BNode):
                    iri = store.identifier.n3()
                else:
                    # Show the full graph URI if a prefix for it doesn't already exist
                    iri = self.get_pname(store.identifier, False)
                    if iri is None:
                        iri = store.identifier.n3()
                self.write(self.indent() + "\n%s {" % iri)

            self.depth += 1
            for subject in ordered_subjects:
                if self.is_done(subject):
                    continue
                if firstTime:
                    firstTime = False
                if self.statement(subject) and not firstTime:
                    self.write("\n")
            self.depth -= 1
            self.write("}\n")

        self.endDocument()
        stream.write("\n".encode("latin-1"))
