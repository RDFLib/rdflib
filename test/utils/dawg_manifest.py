import logging
from dataclasses import dataclass, field
from test.utils import MarkListType, marks_to_list
from test.utils.graph import GraphSource, GraphSourceType
from test.utils.iri import URIMapper
from test.utils.namespace import MF
from typing import (
    Callable,
    Collection,
    Generator,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from urllib.parse import urljoin

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

from rdflib.graph import Graph
from rdflib.namespace import RDF
from rdflib.term import IdentifiedNode, Identifier, URIRef

POFilterType = Tuple[Optional[URIRef], Optional[URIRef]]
POFiltersType = Iterable[POFilterType]

MarkType = Union[MarkDecorator, Collection[Union[MarkDecorator, Mark]]]
MarksDictType = Mapping[
    str, Union[MarkDecorator, Collection[Union[MarkDecorator, Mark]]]
]
ManifestEntryMarkerType = Callable[["ManifestEntry"], Optional[MarkType]]
IdentifierT = TypeVar("IdentifierT", bound=Identifier)


@dataclass
class ManifestEntry:
    manifest: "Manifest"
    identifier: URIRef
    type: IdentifiedNode = field(init=False)
    action: Optional[IdentifiedNode] = field(init=False)
    result: Optional[IdentifiedNode] = field(init=False)
    result_cardinality: Optional[URIRef] = field(init=False)

    def __post_init__(self) -> None:
        type = self.value(RDF.type, IdentifiedNode)
        assert type is not None
        self.type = type

        self.action = self.value(MF.action, IdentifiedNode)
        self.result = self.value(MF.result, IdentifiedNode)
        self.result_cardinality = self.value(MF.resultCardinality, URIRef)
        if self.result_cardinality is not None:
            assert self.result_cardinality == MF.LaxCardinality

    @property
    def graph(self) -> Graph:
        return self.manifest.graph

    @property
    def uri_mapper(self) -> URIMapper:
        return self.manifest.uri_mapper

    def param(
        self,
        mark_dict: Optional[MarksDictType] = None,
        markers: Optional[Iterable[ManifestEntryMarkerType]] = None,
    ) -> ParameterSet:
        id = f"{self.identifier}"
        marks: MarkListType = []
        if mark_dict is not None:
            marks = marks_to_list(mark_dict.get(id, marks))
        if markers is not None:
            for marker in markers:
                opt_marks = marker(self)
                if opt_marks is not None:
                    opt_marks = marks_to_list(opt_marks)
                    marks.extend(opt_marks)
        return pytest.param(self, id=f"{self.identifier}", marks=marks)

    def value(
        self, predicate: Identifier, value_type: Type[IdentifierT]
    ) -> Optional[IdentifierT]:
        value = self.graph.value(self.identifier, predicate)
        if value is not None:
            assert isinstance(value, value_type)
        return value

    def check_filters(self, filters: POFiltersType) -> bool:
        for filter in filters:
            if (self.identifier, filter[0], filter[1]) in self.graph:
                return True
        return False


@dataclass
class Manifest:
    uri_mapper: URIMapper
    graph: Graph
    identifier: IdentifiedNode
    report_prefix: Optional[str] = None

    @classmethod
    def from_graph(
        cls,
        uri_mapper: URIMapper,
        graph: Graph,
        report_prefix: Optional[str] = None,
    ) -> Generator["Manifest", None, None]:
        for identifier in graph.subjects(RDF.type, MF.Manifest):
            assert isinstance(identifier, IdentifiedNode)
            manifest = Manifest(
                uri_mapper,
                graph,
                identifier,
                report_prefix,
            )
            yield manifest
            yield from manifest.included()

    @classmethod
    def from_sources(
        cls,
        uri_mapper: URIMapper,
        *sources: GraphSourceType,
        report_prefix: Optional[str] = None,
    ) -> Generator["Manifest", None, None]:
        for source in sources:
            logging.debug("source(%s) = %r", id(source), source)
            source = GraphSource.from_source(source)
            source_path_uri = source.path.absolute().as_uri()
            local_base = urljoin(source_path_uri, ".")
            public_id = uri_mapper.to_remote(local_base)
            logging.debug(
                "source = %s, source_path_uri = %s, local_base = %s, public_id = %s",
                source,
                source_path_uri,
                local_base,
                public_id,
            )
            graph = source.load(public_id=public_id)
            yield from cls.from_graph(
                uri_mapper,
                graph,
                report_prefix,
            )

    def included(self) -> Generator["Manifest", None, None]:
        for includes in self.graph.objects(self.identifier, MF.include):
            for include in self.graph.items(includes):
                assert isinstance(include, str)
                include_local_path = self.uri_mapper.to_local_path(include)
                yield from Manifest.from_sources(
                    self.uri_mapper,
                    include_local_path,
                    report_prefix=self.report_prefix,
                )

    def entires(
        self,
        entry_type: Type["ManifestEntryT"],
        exclude: Optional[POFiltersType] = None,
        include: Optional[POFiltersType] = None,
    ) -> Generator["ManifestEntryT", None, None]:
        for entries in self.graph.objects(self.identifier, MF.entries):
            for entry_iri in self.graph.items(entries):
                assert isinstance(entry_iri, URIRef)
                entry = entry_type(self, entry_iri)
                if exclude is not None and entry.check_filters(exclude):
                    continue
                if include is not None and not entry.check_filters(include):
                    continue
                yield entry

    def params(
        self,
        entry_type: Type["ManifestEntryT"],
        exclude: Optional[POFiltersType] = None,
        include: Optional[POFiltersType] = None,
        mark_dict: Optional[MarksDictType] = None,
        markers: Optional[Iterable[ManifestEntryMarkerType]] = None,
    ) -> Generator["ParameterSet", None, None]:
        for entry in self.entires(entry_type, exclude, include):
            yield entry.param(mark_dict, markers)


def params_from_sources(
    uri_mapper: URIMapper,
    entry_type: Type["ManifestEntryT"],
    *sources: GraphSourceType,
    exclude: Optional[POFiltersType] = None,
    include: Optional[POFiltersType] = None,
    mark_dict: Optional[MarksDictType] = None,
    markers: Optional[Iterable[ManifestEntryMarkerType]] = None,
    report_prefix: Optional[str] = None,
) -> Generator["ParameterSet", None, None]:
    for manifest in Manifest.from_sources(
        uri_mapper, *sources, report_prefix=report_prefix
    ):
        yield from manifest.params(entry_type, include, exclude, mark_dict, markers)


ManifestEntryT = TypeVar("ManifestEntryT", bound=ManifestEntry)
