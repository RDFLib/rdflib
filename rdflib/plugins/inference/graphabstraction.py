from __future__ import annotations

try:
    from pyoxigraph import BlankNode as ox_BlankNode
    from pyoxigraph import DefaultGraph as ox_DefaultGraph
    from pyoxigraph import Literal as ox_Literal
    from pyoxigraph import NamedNode as ox_NamedNode
    from pyoxigraph import Quad as ox_Quad
    from pyoxigraph import Store as ox_Store

    has_oxigraph = True
except ImportError:
    has_oxigraph = False
    ox_Store = None
    ox_DefaultGraph = None
    ox_Quad = None
    ox_Literal = None
    ox_BlankNode = None
    ox_NamedNode = None

import warnings
from collections.abc import Generator
from typing import Any, Tuple, Union

from rdflib import Dataset as rdf_Dataset
from rdflib import Graph as rdf_Graph
from rdflib.namespace import RDF
from rdflib.term import BNode as rdf_BNode
from rdflib.term import IdentifiedNode as rdf_IdentifiedNode
from rdflib.term import Literal as rdf_Literal
from rdflib.term import URIRef as rdf_URIRef

ALLOWED_GRAPH_TYPES = Union[rdf_Graph, rdf_Dataset, ox_Store]

# ruff: noqa: N806 N816

# mypy: disable_error_code = "attr-defined, assignment, no-redef, misc"


class DataGraph:

    is_oxigraph: bool
    _default_union: bool

    def __new__(
        cls,
        store: ALLOWED_GRAPH_TYPES,
        locked_context: Union[rdf_Graph, str, None] = None,
    ):
        self = super().__new__(cls)
        self.is_oxigraph = has_oxigraph and isinstance(store, ox_Store)
        self.impl = store

        self._default_union = False
        if self.is_oxigraph:
            self.triples = self.triples_in_oxigraph
            self.add = self.add_to_oxigraph
            self.remove = self.remove_from_oxigraph
            self.subject_objects = self.subject_objects_in_oxigraph
            self.subjects = self.subjects_in_oxigraph
            self.objects = self.objects_in_oxigraph
            self.predicate_objects = self.predicate_objects_in_oxigraph
            self.subject_predicates = self.subject_predicates_in_oxigraph
            if isinstance(locked_context, rdf_Graph):
                self.locked_context = ox_NamedNode(locked_context.identifier)
            elif isinstance(locked_context, str):
                self.locked_context = ox_NamedNode(locked_context)
            else:
                self.locked_context = None
        else:
            self.triples = self.triples_in_rdflib
            self.add = self.add_to_rdflib
            self.remove = self.remove_from_rdflib
            self.subject_objects = self.subject_objects_in_rdflib
            self.subjects = self.subjects_in_rdflib
            self.objects = self.objects_in_rdflib
            self.predicate_objects = self.predicate_objects_in_rdflib
            self.subject_predicates = self.subject_predicates_in_rdflib
            if isinstance(locked_context, rdf_Graph):
                self.locked_context = locked_context
            elif isinstance(locked_context, str):
                self.locked_context = self.impl.get_context(rdf_URIRef(locked_context))  # type: ignore[union-attr]
            else:
                self.locked_context = None
        return self

    @classmethod
    def convert_triple_to_oxigraph(
        cls,
        triple: Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal, None],
            Union[rdf_IdentifiedNode, None],
            Union[rdf_Literal, rdf_IdentifiedNode, None],
        ],
    ):
        in_s, in_p, in_o = triple

        if in_s is None:
            out_s = None
        elif isinstance(in_s, rdf_BNode):
            out_s = ox_BlankNode(str(in_s))
        elif isinstance(in_s, rdf_Literal):
            if in_s.language is not None:
                out_s = ox_Literal(str(in_s), language=in_s.language)
            else:
                data_type = in_s.datatype
                if data_type is not None:
                    data_type = ox_NamedNode(str(data_type))
                out_s = ox_Literal(str(in_s), datatype=data_type)
        else:
            out_s = ox_NamedNode(str(in_s))
        if in_p is None:
            out_p = None
        elif isinstance(in_p, rdf_BNode):
            out_p = ox_BlankNode(str(in_p))
        else:
            out_p = ox_NamedNode(str(in_p))
        if in_o is None:
            out_o = None
        elif isinstance(in_o, rdf_BNode):
            out_o = ox_BlankNode(str(in_o))
        elif isinstance(in_o, rdf_Literal):
            if in_o.language is not None:
                out_o = ox_Literal(str(in_o), language=in_o.language)
            else:
                data_type = in_o.datatype
                if data_type is not None:
                    data_type = ox_NamedNode(str(data_type))
                out_o = ox_Literal(str(in_o), datatype=data_type)
        else:
            out_o = ox_NamedNode(str(in_o))
        return out_s, out_p, out_o

    @classmethod
    def to_ox(
        cls, term: Union[rdf_IdentifiedNode, rdf_Literal, None]
    ) -> Union[ox_NamedNode, ox_BlankNode, ox_Literal, None]:
        if term is None:
            return None
        elif isinstance(term, rdf_BNode):
            return ox_BlankNode(str(term))
        elif isinstance(term, rdf_Literal):
            if term.language is not None:
                return ox_Literal(str(term), language=term.language)
            else:
                data_type = term.datatype
                if data_type is not None:
                    data_type = ox_NamedNode(str(data_type))
                return ox_Literal(str(term), datatype=data_type)
        else:
            return ox_NamedNode(str(term))

    @classmethod
    def to_rdf(
        cls, term: Union[ox_NamedNode, ox_BlankNode, ox_Literal, None]
    ) -> Union[rdf_IdentifiedNode, rdf_Literal, None]:
        if term is None:
            return None
        elif isinstance(term, ox_BlankNode):
            return rdf_BNode(term.value)
        elif isinstance(term, ox_Literal):
            if term.language is not None:
                return rdf_Literal(term.value, lang=term.language)
            data_type = term.datatype
            if data_type is not None:
                data_type = rdf_URIRef(data_type.value)
            return rdf_Literal(term.value, datatype=data_type)
        else:
            return rdf_URIRef(term.value)

    @classmethod
    def convert_quad_to_rdflib(cls, quad: ox_Quad):
        s, p, o, g = quad
        if s is None:
            out_s = None
        elif isinstance(s, ox_BlankNode):
            out_s = rdf_BNode(s.value)
        elif isinstance(s, ox_Literal):
            # Technically a subject can never be a Literal
            # in Oxigraph, but this is here for completeness
            if s.language is not None:
                out_s = rdf_Literal(s.value, lang=s.language)  # type: ignore[assignment]
            else:
                data_type = s.datatype
                if data_type is not None:
                    data_type = rdf_URIRef(data_type.value)
                out_s = rdf_Literal(s.value, datatype=data_type)  # type: ignore[assignment]
        else:
            out_s = rdf_URIRef(s.value)  # type: ignore[assignment]
        if p is None:
            out_p = None
        elif isinstance(p, ox_BlankNode):
            out_p = rdf_BNode(p.value)
        else:
            out_p = rdf_URIRef(p.value)  # type: ignore[assignment]
        if o is None:
            out_o = None
        elif isinstance(o, ox_Literal):
            if o.language is not None:
                out_o = rdf_Literal(o.value, lang=o.language)
            else:
                data_type = o.datatype
                if data_type is not None:
                    data_type = rdf_URIRef(data_type.value)
                out_o = rdf_Literal(o.value, datatype=data_type)
        elif isinstance(o, ox_BlankNode):
            out_o = rdf_BNode(o.value)  # type: ignore[assignment]
        else:
            out_o = rdf_URIRef(o.value)  # type: ignore[assignment]
        if g is None:
            out_g = None
        elif isinstance(g, ox_DefaultGraph):
            out_g = None
        else:
            out_g = rdf_URIRef(g.value)
        return out_s, out_p, out_o, out_g

    @property
    def default_union(self) -> bool:
        return self._default_union

    @property
    def store(self) -> Any:
        if self.is_oxigraph:
            return self.impl
        else:
            return self.impl.store

    @default_union.setter
    def default_union(self, value: bool):
        self._default_union = value
        if self.is_oxigraph:
            pass
        elif isinstance(self.impl, rdf_Dataset):
            self.impl.default_union = value

    def add_to_oxigraph(
        self,
        triple: Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal],
            rdf_IdentifiedNode,
            Union[rdf_Literal, rdf_IdentifiedNode],
        ],
    ):
        if isinstance(triple[0], rdf_Literal):
            # Oxigraph does not support Literal in the subject position
            # So this cannot be added to the store.
            warnings.warn(
                "OWL-RL inferencer tried to add a triple with a Literal in the subject position",
            )
            return
        if isinstance(triple[1], rdf_BNode) or isinstance(triple[1], rdf_Literal):
            # Oxigraph does not support BNode or Literal in the predicate position
            # Cannot add the triple
            warnings.warn(
                "OWL-RL inferencer tried to add a triple with a BNode or Literal in the predicate position",
            )
            return
        ox_s, ox_p, ox_o = self.convert_triple_to_oxigraph(triple)
        if self.locked_context is not None:
            ox_g = self.locked_context
        else:
            ox_g = None
        return self.impl.add(ox_Quad(ox_s, ox_p, ox_o, ox_g))

    def remove_from_oxigraph(
        self,
        triple: Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal],
            rdf_IdentifiedNode,
            Union[rdf_Literal, rdf_IdentifiedNode],
        ],
    ):
        if triple[0] is not None and isinstance(triple[0], rdf_Literal):
            # Oxigraph does not support Literal in the subject position
            # So this can never match any triples in the Store.
            return
        ox_triples = self.convert_triple_to_oxigraph(triple)
        if isinstance(ox_triples[1], ox_BlankNode) or isinstance(
            ox_triples[1], ox_Literal
        ):
            return
        if isinstance(ox_triples[0], ox_Literal):
            return
        if self.locked_context is not None:
            to_remove = list(
                self.impl.quads_for_pattern(
                    ox_triples[0], ox_triples[1], ox_triples[2], self.locked_context
                )
            )
        elif self._default_union:
            to_remove = list(
                self.impl.quads_for_pattern(
                    ox_triples[0], ox_triples[1], ox_triples[2], None
                )
            )
        else:
            to_remove = list(
                self.impl.quads_for_pattern(
                    ox_triples[0], ox_triples[1], ox_triples[2], ox_DefaultGraph()
                )
            )
        for q in to_remove:
            self.impl.remove(q)

    def triples_in_oxigraph(
        self,
        triple: Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal, None],
            Union[rdf_IdentifiedNode, None],
            Union[rdf_IdentifiedNode, rdf_Literal, None],
        ],
    ) -> Generator[
        Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal],
            rdf_IdentifiedNode,
            Union[rdf_IdentifiedNode, rdf_Literal],
        ],
        None,
        None,
    ]:
        if triple[0] is not None and isinstance(triple[0], rdf_Literal):
            # Oxigraph does not support Literal in the subject position
            # So this can never match any triples in the Store.
            return
        ox_triples = self.convert_triple_to_oxigraph(triple)
        if isinstance(ox_triples[1], ox_BlankNode) or isinstance(
            ox_triples[1], ox_Literal
        ):
            # Oxigraph does not support BNode or Literal in the predicate position
            # Cannot yield any results
            return
        if isinstance(ox_triples[0], ox_Literal):
            # Oxigraph does not support Literal in the subject position
            # Cannot yield any results
            return
        if self.locked_context is not None:
            for q in self.impl.quads_for_pattern(
                ox_triples[0], ox_triples[1], ox_triples[2], self.locked_context
            ):
                yield self.convert_quad_to_rdflib(q)[:3]
        elif self._default_union:
            for q in self.impl.quads_for_pattern(
                ox_triples[0], ox_triples[1], ox_triples[2], None
            ):
                yield self.convert_quad_to_rdflib(q)[:3]
        else:
            default_graph = ox_DefaultGraph()
            for q in self.impl.quads_for_pattern(
                ox_triples[0], ox_triples[1], ox_triples[2], default_graph
            ):
                yield self.convert_quad_to_rdflib(q)[:3]

    def subject_objects_in_oxigraph(
        self, predicate: Union[rdf_IdentifiedNode, None]
    ) -> Generator[
        Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal],
            Union[rdf_IdentifiedNode, rdf_Literal],
        ],
        None,
        None,
    ]:
        if isinstance(predicate, rdf_BNode) or isinstance(predicate, rdf_Literal):
            # Oxigraph does not support BNode or Literal in the predicate position
            # Cannot yield any results
            return
        _p = self.to_ox(predicate)
        if self.locked_context is not None:
            for q in self.impl.quads_for_pattern(None, _p, None, self.locked_context):
                s, _, o, _ = self.convert_quad_to_rdflib(q)
                yield s, o
        elif self._default_union:
            for q in self.impl.quads_for_pattern(None, _p, None, None):
                s, _, o, _ = self.convert_quad_to_rdflib(q)
                yield s, o
        else:
            for q in self.impl.quads_for_pattern(None, _p, None, ox_DefaultGraph()):
                s, _, o, _ = self.convert_quad_to_rdflib(q)
                yield s, o

    def subject_predicates_in_oxigraph(
        self, object_: Union[rdf_IdentifiedNode, rdf_Literal, None]
    ) -> Generator[
        Tuple[Union[rdf_IdentifiedNode, rdf_Literal], rdf_IdentifiedNode], None, None
    ]:
        _o = self.to_ox(object_)
        if self.locked_context is not None:
            for q in self.impl.quads_for_pattern(None, None, _o, self.locked_context):
                s, p, _, _ = self.convert_quad_to_rdflib(q)
                yield s, p
        elif self._default_union:
            for q in self.impl.quads_for_pattern(None, None, _o, None):
                s, p, _, _ = self.convert_quad_to_rdflib(q)
                yield s, p
        else:
            for q in self.impl.quads_for_pattern(None, None, _o, ox_DefaultGraph()):
                s, p, _, _ = self.convert_quad_to_rdflib(q)
                yield s, p

    def predicate_objects_in_oxigraph(
        self, subject: Union[rdf_IdentifiedNode, rdf_Literal, None]
    ) -> Generator[
        Tuple[rdf_IdentifiedNode, Union[rdf_IdentifiedNode, rdf_Literal]], None, None
    ]:
        if subject is not None and isinstance(subject, rdf_Literal):
            # Oxigraph does not support literal subjects
            # So no predicate-object pairs can be returned
            return
        _s = self.to_ox(subject)
        if self.locked_context is not None:
            for q in self.impl.quads_for_pattern(_s, None, None, self.locked_context):
                _, p, o, _ = self.convert_quad_to_rdflib(q)
                yield p, o
        elif self._default_union:
            for q in self.impl.quads_for_pattern(_s, None, None, None):
                _, p, o, _ = self.convert_quad_to_rdflib(q)
                yield p, o
        else:
            for q in self.impl.quads_for_pattern(_s, None, None, ox_DefaultGraph()):
                _, p, o, _ = self.convert_quad_to_rdflib(q)
                yield p, o

    def subjects_in_oxigraph(
        self,
        predicate: rdf_IdentifiedNode,
        object_: Union[rdf_IdentifiedNode, rdf_Literal, None],
    ) -> Generator[Union[rdf_IdentifiedNode, rdf_Literal], None, None]:
        _p = self.to_ox(predicate)
        _o = self.to_ox(object_)
        if self.locked_context is not None:
            for s, _, _, _ in self.impl.quads_for_pattern(
                None, _p, _o, self.locked_context
            ):
                yield self.to_rdf(s)
        elif self._default_union:
            for s, _, _, _ in self.impl.quads_for_pattern(None, _p, _o, None):
                yield self.to_rdf(s)
        else:
            for s, _, _, _ in self.impl.quads_for_pattern(
                None, _p, _o, ox_DefaultGraph()
            ):
                yield self.to_rdf(s)

    def objects_in_oxigraph(
        self,
        subject: Union[rdf_IdentifiedNode, rdf_Literal, None],
        predicate: Union[rdf_IdentifiedNode, None],
    ) -> Generator[Union[rdf_IdentifiedNode, rdf_Literal], None, None]:
        if subject is not None and isinstance(subject, rdf_Literal):
            # Oxigraph does not support literal subjects
            # So no objects can be returned
            return
        _s = self.to_ox(subject)
        _p = self.to_ox(predicate)
        if self.locked_context is not None:
            for _, _, o, _ in self.impl.quads_for_pattern(
                _s, _p, None, self.locked_context
            ):
                yield self.to_rdf(o)
        elif self._default_union:
            for _, _, o, _ in self.impl.quads_for_pattern(_s, _p, None, None):
                yield self.to_rdf(o)
        else:
            for _, _, o, _ in self.impl.quads_for_pattern(
                _s, _p, None, ox_DefaultGraph()
            ):
                yield self.to_rdf(o)

    def add_to_rdflib(
        self,
        triple: Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal],
            rdf_IdentifiedNode,
            Union[rdf_Literal, rdf_IdentifiedNode],
        ],
    ):
        if self.locked_context is not None:
            return self.impl.add((triple[0], triple[1], triple[2], self.locked_context))
        else:
            return self.impl.add((triple[0], triple[1], triple[2]))

    def remove_from_rdflib(
        self,
        triple: Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal],
            rdf_IdentifiedNode,
            Union[rdf_Literal, rdf_IdentifiedNode],
        ],
    ):
        if self.locked_context is not None:
            return self.impl.remove(
                (triple[0], triple[1], triple[2], self.locked_context)
            )
        else:
            return self.impl.remove((triple[0], triple[1], triple[2]))

    def triples_in_rdflib(
        self,
        triple: Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal, None],
            Union[rdf_IdentifiedNode, None],
            Union[rdf_IdentifiedNode, rdf_Literal, None],
        ],
    ) -> Generator[
        Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal],
            rdf_IdentifiedNode,
            Union[rdf_IdentifiedNode, rdf_Literal],
        ],
        None,
        None,
    ]:
        if self.locked_context is not None:
            for t in self.impl.triples(triple, context=self.locked_context):
                yield t
        else:
            for t in self.impl.triples(triple):
                yield t

    def subject_objects_in_rdflib(
        self, predicate: Union[rdf_IdentifiedNode, None]
    ) -> Generator[tuple, None, None]:
        if self.locked_context is not None:
            for t in self.impl.subject_objects(predicate, context=self.locked_context):
                yield t
        else:
            for t in self.impl.subject_objects(predicate):
                yield t

    def subject_predicates_in_rdflib(
        self, object_: Union[rdf_IdentifiedNode, rdf_Literal, None]
    ) -> Generator[Any, None, None]:
        if self.locked_context is not None:
            for t in self.impl.subject_predicates(object_, context=self.locked_context):
                yield t
        else:
            for t in self.impl.subject_predicates(object_):
                yield t

    def predicate_objects_in_rdflib(
        self, subject: Union[rdf_IdentifiedNode, rdf_Literal, None]
    ) -> Generator[tuple, None, None]:
        if self.locked_context is not None:
            for t in self.impl.predicate_objects(subject, context=self.locked_context):
                yield t
        else:
            for t in self.impl.predicate_objects(subject):
                yield t

    def subjects_in_rdflib(
        self,
        predicate: rdf_IdentifiedNode,
        object_: Union[rdf_IdentifiedNode, rdf_Literal, None],
    ) -> Generator[rdf_IdentifiedNode, None, None]:
        if self.locked_context is not None:
            for t in self.impl.subjects(
                predicate, object_, context=self.locked_context
            ):
                yield t
        else:
            for t in self.impl.subjects(predicate, object_):
                yield t

    def objects_in_rdflib(
        self,
        subject: Union[rdf_IdentifiedNode, rdf_Literal],
        predicate: Union[rdf_IdentifiedNode, None],
    ) -> Generator[Union[rdf_IdentifiedNode, rdf_Literal], None, None]:
        if self.locked_context is not None:
            for t in self.impl.objects(subject, predicate, context=self.locked_context):
                yield t
        else:
            for t in self.impl.objects(subject, predicate):
                yield t

    def get_context(self, identifier: Union[rdf_URIRef, str]) -> DataGraph:
        if self.is_oxigraph:
            return DataGraph(self.impl, str(identifier))
        else:
            return DataGraph(self.impl, self.impl.get_context(rdf_URIRef(identifier)))

    def __contains__(
        self,
        triple: Tuple[
            Union[rdf_IdentifiedNode, rdf_Literal, None],
            Union[rdf_IdentifiedNode, None],
            Union[rdf_IdentifiedNode, rdf_Literal, None],
        ],
    ) -> bool:
        if self.is_oxigraph:
            if triple[0] is not None and isinstance(triple[0], rdf_Literal):
                # an Oxigraph store cannot have a Literal in the subject position
                # so this triple cannot exist in the store
                return False
            triple_ = self.convert_triple_to_oxigraph(triple)
            if self.locked_context is not None:
                quad = ox_Quad(triple_[0], triple_[1], triple_[2], self.locked_context)
            elif self._default_union:
                quad = ox_Quad(triple_[0], triple_[1], triple_[2], None)
            else:
                quad = ox_Quad(triple_[0], triple_[1], triple_[2], ox_DefaultGraph())
            return quad in self.impl
        else:
            if self.locked_context is not None:
                quad = (triple[0], triple[1], triple[2], self.locked_context)
                return quad in self.impl
            else:
                return triple in self.impl

    def items(
        self, list_: rdf_IdentifiedNode
    ) -> Generator[Union[rdf_IdentifiedNode, rdf_Literal], None, None]:
        """Generator over all items in the resource specified by list

        Args:
            list: An RDF collection.
        """
        if not self.is_oxigraph:
            for i in self.impl.items(list_):
                yield i
            return
        if isinstance(list_, rdf_URIRef):
            next_list = ox_NamedNode(str(list_))
        elif isinstance(list_, rdf_BNode):
            next_list = ox_BlankNode(str(list_))
        else:
            raise ValueError("List must be a URIRef, or BNode")
        chain: set[Any] = {next_list}
        FIRST = ox_NamedNode(RDF.first)
        REST = ox_NamedNode(RDF.rest)
        while next_list:
            firsts = list(self.impl.quads_for_pattern(next_list, FIRST, None, None))
            if len(firsts) == 0:
                item = None
            else:
                item = firsts[0][2]
            if item is not None:
                yield self.to_rdf(item)
            rests = list(self.impl.quads_for_pattern(next_list, REST, None, None))
            if len(rests) == 0:
                next_list = None
            else:
                next_list = rests[0][2]
            if next_list in chain:
                raise ValueError("List contains a recursive rdf:rest reference")
            chain.add(next_list)

    def bind(self, prefix: str, namespace: str, **kwargs) -> None:
        if self.is_oxigraph:
            pass
        else:
            self.impl.bind(prefix, namespace, **kwargs)
