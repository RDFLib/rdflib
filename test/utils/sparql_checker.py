"""This runs the nt tests for the W3C RDF Working Group's N-Quads
test suite."""
import enum
import logging
import pprint
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from io import BytesIO, StringIO
from pathlib import Path
from test.utils import BNodeHandling, GraphHelper
from test.utils.dawg_manifest import Manifest, ManifestEntry
from test.utils.iri import URIMapper
from test.utils.namespace import MF, QT, UT
from test.utils.result import ResultType, assert_bindings_collections_equal
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)
from urllib.parse import urljoin

import pytest
from pytest import MonkeyPatch

import rdflib
from rdflib.graph import Dataset, Graph
from rdflib.namespace import RDFS
from rdflib.plugins import sparql as rdflib_sparql_module
from rdflib.plugins.sparql.algebra import translateQuery, translateUpdate
from rdflib.plugins.sparql.parser import parseQuery, parseUpdate
from rdflib.plugins.sparql.results.rdfresults import RDFResultParser
from rdflib.plugins.sparql.sparql import QueryContext
from rdflib.query import Result
from rdflib.term import BNode, IdentifiedNode, Identifier, Literal, Node, URIRef
from rdflib.util import guess_format

logger = logging.getLogger(__name__)

# TESTS: https://www.w3.org/2009/sparql/docs/tests/
# Implementation Report: https://www.w3.org/2009/sparql/implementations/
# Summary: https://www.w3.org/2009/sparql/docs/tests/summary.html
# README: https://www.w3.org/2009/sparql/docs/tests/README.html


ENCODING = "utf-8"


class QueryType(enum.Enum):
    QUERY = enum.auto()
    UPDATE = enum.auto()


@dataclass
class TypeInfo:
    id: Identifier
    query_type: Optional[QueryType]
    syntax: bool = False
    skipped: bool = False
    negative: bool = False
    ns: Union[Type[QT], Type[UT], None] = field(init=False, default=None)
    query_property: Optional[URIRef] = field(init=False, default=None)
    graph_data_property: Optional[URIRef] = field(init=False, default=None)
    expected_outcome_property: Optional[URIRef] = field(init=False, default=None)

    def __post_init__(self) -> None:
        if self.query_type is QueryType.QUERY:
            self.ns = QT
            self.query_property = QT.query
            self.graph_data_property = QT.graphData
        elif self.query_type is QueryType.UPDATE:
            self.ns = UT
            self.query_property = UT.request
            self.graph_data_property = UT.graphData
            self.expected_outcome_property = UT.result

    @classmethod
    def make_dict(cls, *test_types: "TypeInfo") -> Dict[Identifier, "TypeInfo"]:
        return dict((test_type.id, test_type) for test_type in test_types)


type_info_dict = TypeInfo.make_dict(
    TypeInfo(MF.CSVResultFormatTest, QueryType.QUERY),
    TypeInfo(MF.NegativeSyntaxTest, QueryType.QUERY, syntax=True, negative=True),
    TypeInfo(MF.NegativeSyntaxTest11, QueryType.QUERY, syntax=True, negative=True),
    TypeInfo(MF.PositiveSyntaxTest, QueryType.QUERY, syntax=True),
    TypeInfo(MF.PositiveSyntaxTest11, QueryType.QUERY, syntax=True),
    TypeInfo(MF.QueryEvaluationTest, QueryType.QUERY),
    TypeInfo(UT.UpdateEvaluationTest, QueryType.UPDATE),
    TypeInfo(MF.UpdateEvaluationTest, QueryType.UPDATE),
    TypeInfo(MF.PositiveUpdateSyntaxTest11, QueryType.UPDATE, syntax=True),
    TypeInfo(
        MF.NegativeUpdateSyntaxTest11, QueryType.UPDATE, syntax=True, negative=True
    ),
    TypeInfo(MF.ServiceDescriptionTest, None, skipped=True),
    TypeInfo(MF.ProtocolTest, None, skipped=True),
)


@dataclass(frozen=True)
class GraphData:
    graph_id: URIRef
    label: Optional[Literal] = None

    @classmethod
    def from_graph(cls, graph: Graph, identifier: Identifier) -> "GraphData":
        if isinstance(identifier, URIRef):
            return cls(identifier)
        elif isinstance(identifier, BNode):
            po_list = list(graph.predicate_objects(identifier))
            assert len(po_list) == 2
            po_dict: Dict[Node, Node] = dict(po_list)
            graph_id = po_dict[UT.graph]
            assert isinstance(graph_id, URIRef)
            label = po_dict[RDFS.label]
            assert isinstance(label, Literal)
            return cls(graph_id, label)
        else:
            raise ValueError(f"invalid identifier {identifier!r}")

    def load_into(self, manifest: Manifest, dataset: Dataset) -> None:
        graph_local, graph_path = manifest.uri_mapper.to_local(self.graph_id)
        graph_text = graph_path.read_text(encoding=ENCODING)
        public_id = URIRef(f"{self.label}") if self.label is not None else self.graph_id
        logging.debug(
            "public_id = %s - graph = %s\n%s", public_id, graph_path, graph_text
        )
        dataset.parse(
            data=graph_text, publicID=public_id, format=guess_format(graph_path)
        )


@dataclass
class SPARQLEntry(ManifestEntry):
    type_info: TypeInfo = field(init=False)
    query: Optional[IdentifiedNode] = field(init=False, default=None)
    action_data: Optional[IdentifiedNode] = field(init=False, default=None)
    action_graph_data: Optional[Set[GraphData]] = field(init=False, default=None)
    result_data: Optional[IdentifiedNode] = field(init=False, default=None)
    result_graph_data: Optional[Set[GraphData]] = field(init=False, default=None)
    expected_outcome: Optional[URIRef] = field(init=False, default=None)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.type_info = type_info_dict[self.type]

        if self.type_info.syntax is True:
            assert self.result is None
            self.query = self.action
            assert isinstance(self.query, URIRef)
            return

        if self.type_info.query_type is not None:
            assert self.result is not None
            self.query = cast(
                Optional[IdentifiedNode],
                self.graph.value(self.action, self.type_info.query_property),
            )
            assert isinstance(self.query, URIRef)
            assert self.type_info.ns is not None
            self.action_data = cast(
                Optional[IdentifiedNode],
                self.graph.value(self.action, self.type_info.ns.data),
            )
            self.expected_outcome = cast(
                Optional[URIRef],
                self.graph.value(self.action, self.type_info.expected_outcome_property),
            )
            for action_graph_data_id in self.graph.objects(
                self.action, self.type_info.ns.graphData
            ):
                assert isinstance(action_graph_data_id, IdentifiedNode)
                graph_data = GraphData.from_graph(self.graph, action_graph_data_id)
                if self.action_graph_data is None:
                    self.action_graph_data = set()
                self.action_graph_data.add(graph_data)
            if isinstance(self.result, BNode):
                self.result_data = cast(
                    Optional[IdentifiedNode],
                    self.graph.value(self.result, self.type_info.ns.data),
                )
            else:
                self.result_data = self.result
                assert isinstance(self.result_data, URIRef)
            for result_graph_data_id in self.graph.objects(
                self.result, self.type_info.ns.graphData
            ):
                assert isinstance(result_graph_data_id, IdentifiedNode)
                graph_data = GraphData.from_graph(self.graph, result_graph_data_id)
                if self.result_graph_data is None:
                    self.result_graph_data = set()
                self.result_graph_data.add(graph_data)

    def load_dataset(
        self, data: Optional[IdentifiedNode], graph_data_set: Optional[Set[GraphData]]
    ) -> Dataset:
        dataset = Dataset()
        if data is not None:
            data_path = self.uri_mapper.to_local_path(data)
            data_text = data_path.read_text(encoding=ENCODING)
            logging.debug(
                "data (%s) = %s\n%s",
                data,
                data_path,
                data_text,
            )
            dataset.default_context.parse(
                data=data_text, format=guess_format(data_path)
            )
        if graph_data_set is not None:
            for graph_data in graph_data_set:
                graph_data.load_into(self.manifest, dataset)
        return dataset

    def action_dataset(self) -> Dataset:
        return self.load_dataset(self.action_data, self.action_graph_data)

    def result_dataset(self) -> Dataset:
        return self.load_dataset(self.result_data, self.result_graph_data)

    def query_text(self) -> str:
        assert self.query is not None
        query_path = self.uri_mapper.to_local_path(self.query)
        query_text = query_path.read_text(encoding=ENCODING)
        logging.debug("query = %s\n%s", query_path, query_text)
        return query_text

    def query_base(self) -> str:
        assert self.query is not None
        return urljoin(self.query, ".")


class ResultFileHelper:
    extentions = {
        "srx": "xml",
        "srj": "json",
        "csv": "csv",
        "tsv": "tsv",
    }

    @classmethod
    def load_result(cls, uri_mapper: URIMapper, result_uri: str) -> Tuple[Result, str]:
        result_path = uri_mapper.to_local_path(result_uri)
        ext = result_path.suffix[1:]
        format = cls.extentions.get(ext)
        result_text = result_path.read_text(encoding=ENCODING)
        logging.debug("result = %s (format=%s)\n%s", result_path, format, result_text)
        if format is not None:
            with StringIO(result_text) as tio:
                result: Result = Result.parse(tio, format=format)
            if logger.isEnabledFor(logging.DEBUG):
                logging.debug(
                    "result.bindings = \n%s",
                    pprint.pformat(result.bindings, indent=2, width=80),
                )
            return result, format
        graph = Graph()
        format = guess_format(f"{result_path}")
        assert format is not None
        graph.parse(data=result_text, format=format, publicID=result_uri)
        result = RDFResultParser().parse(graph)
        if logger.isEnabledFor(logging.DEBUG):
            logging.debug(
                "result.bindings = \n%s",
                pprint.pformat(result.bindings, indent=2, width=80),
            )
        return result, format


@contextmanager
def ctx_configure_rdflib() -> Generator[None, None, None]:
    # Several tests rely on lexical form of literals being kept!
    rdflib.NORMALIZE_LITERALS = False
    # We need an explicit default graph so tests with local graph references
    # work.
    rdflib_sparql_module.SPARQL_DEFAULT_GRAPH_UNION = False
    # TODO: Add comment explaining why this is being set.
    rdflib.DAWG_LITERAL_COLLATION = True
    yield
    rdflib.NORMALIZE_LITERALS = True
    rdflib_sparql_module.SPARQL_DEFAULT_GRAPH_UNION = True
    rdflib.DAWG_LITERAL_COLLATION = False


def check_syntax(monkeypatch: MonkeyPatch, entry: SPARQLEntry) -> None:
    assert entry.query is not None
    assert entry.type_info.query_type is not None
    query_text = entry.query_text()
    catcher: Optional[pytest.ExceptionInfo[Exception]] = None
    with ExitStack() as xstack:
        if entry.type_info.negative:
            catcher = xstack.enter_context(pytest.raises(Exception))
        if entry.type_info.query_type is QueryType.UPDATE:
            tree = parseUpdate(query_text)
            translateUpdate(tree)
        elif entry.type_info.query_type is QueryType.QUERY:
            tree = parseQuery(query_text)
            translateQuery(tree)
    if catcher is not None:
        assert catcher.value is not None
        logging.info("catcher.value = %s", catcher.value)


def check_update(monkeypatch: MonkeyPatch, entry: SPARQLEntry) -> None:
    try:
        rdflib_sparql_module.SPARQL_LOAD_GRAPHS = False
        assert isinstance(entry.action, BNode)
        assert isinstance(entry.result, BNode)
        assert entry.query is not None
        query_text = entry.query_text()
        dataset = entry.action_dataset()
        query_base = entry.query_base()
        logging.debug("query_base=%s", query_base)
        if logger.isEnabledFor(logging.DEBUG):
            logging.debug(
                "dataset before = \n%s",
                dataset.serialize(format="trig"),
            )
        dataset.update(query_text)

        if logger.isEnabledFor(logging.DEBUG):
            logging.debug(
                "dataset after = \n%s",
                dataset.serialize(format="trig"),
            )

        expected_result = entry.result_dataset()

        if logger.isEnabledFor(logging.DEBUG):
            logging.debug(
                "expected_result = \n%s",
                expected_result.serialize(format="trig"),
            )

        GraphHelper.assert_cgraph_isomorphic(
            expected_result, dataset, exclude_bnodes=True
        )
        GraphHelper.assert_sets_equals(expected_result, dataset, BNodeHandling.COLLAPSE)
    finally:
        rdflib_sparql_module.SPARQL_LOAD_GRAPHS = True


def patched_query_context_load(uri_mapper: URIMapper) -> Callable[..., Any]:
    def _patched_load(
        self: QueryContext, source: URIRef, default: bool = False, **kwargs
    ) -> None:
        public_id = None
        use_source: Union[URIRef, Path] = source
        format = guess_format(use_source)
        if f"{source}".startswith(("https://", "http://")):
            use_source = uri_mapper.to_local_path(source)
            public_id = source
        if default:
            assert self.graph is not None
            self.graph.parse(use_source, format=format, publicID=public_id)
        else:
            self.dataset.parse(use_source, format=format, publicID=public_id)

    return _patched_load


def check_query(monkeypatch: MonkeyPatch, entry: SPARQLEntry) -> None:
    assert entry.query is not None
    assert isinstance(entry.result, URIRef)

    monkeypatch.setattr(
        QueryContext, "load", patched_query_context_load(entry.uri_mapper)
    )

    query_text = entry.query_text()
    dataset = entry.action_dataset()
    query_base = entry.query_base()

    logging.debug("query_base=%s", query_base)
    result = dataset.query(query_text, base=query_base)

    if logger.isEnabledFor(logging.DEBUG):
        logging.debug(
            "dataset = \n%s",
            dataset.serialize(format="trig"),
        )

    logging.debug("result.type = %s", result.type)
    expected_result, expected_result_format = ResultFileHelper.load_result(
        entry.uri_mapper, entry.result
    )

    assert expected_result.type == result.type

    if result.type == ResultType.SELECT:
        if logger.isEnabledFor(logging.DEBUG):
            logging.debug(
                "entry.result_cardinality = %s, result.bindings = \n%s",
                entry.result_cardinality,
                pprint.pformat(result.bindings, indent=2, width=80),
            )
        if expected_result_format == "csv":
            with BytesIO() as bio:
                result.serialize(bio, format="csv")
                bio.seek(0)
                logging.debug(
                    "result.bindings csv = \n%s",
                    bio.getvalue().decode("utf-8"),
                )
                result = Result.parse(bio, format="csv")
        lax_cardinality = entry.result_cardinality == MF.LaxCardinality
        assert_bindings_collections_equal(
            expected_result.bindings,
            result.bindings,
            skip_duplicates=lax_cardinality,
        )
    elif result.type == ResultType.ASK:
        assert expected_result.askAnswer == result.askAnswer
    else:
        assert expected_result.graph is not None
        assert result.graph is not None
        logging.debug(
            "expected_result.graph = %s, result.graph = %s\n%s",
            expected_result.graph,
            result.graph,
            result.graph.serialize(format=expected_result_format),
        )
        GraphHelper.assert_isomorphic(expected_result.graph, result.graph)


SKIP_TYPES = {
    MF.ServiceDescriptionTest,
    MF.ProtocolTest,
}


def check_entry(monkeypatch: MonkeyPatch, entry: SPARQLEntry) -> None:
    if logger.isEnabledFor(logging.DEBUG):
        logging.debug(
            "entry = \n%s",
            pprint.pformat(entry, indent=0, width=80),
        )
    if entry.type_info.syntax is True:
        return check_syntax(monkeypatch, entry)
    if entry.type_info.query_type is QueryType.UPDATE:
        return check_update(monkeypatch, entry)
    elif entry.type_info.query_type is QueryType.QUERY:
        return check_query(monkeypatch, entry)
    raise ValueError(f"unsupported test {entry.type}")
