"""
PYTEST_DONT_REWRITE
"""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    OrderedDict,
    Set,
    Tuple,
    TypeVar,
    cast,
)

import _pytest.config.argparsing
import pytest
from pytest import Item

from rdflib import RDF, BNode, Graph, Literal, URIRef
from rdflib.namespace import DC, DOAP, FOAF
from rdflib.plugins.stores.memory import Memory
from test.utils import GraphHelper
from test.utils.dawg_manifest import ManifestEntry
from test.utils.namespace import EARL, MF, RDFT

if TYPE_CHECKING:
    from _pytest.main import Session
    from _pytest.python import CallSpec2
    from _pytest.reports import TestReport
    from _pytest.runner import CallInfo
    from pluggy._result import _Result


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from rdflib.graph import _TripleType


TEST_REPORTS_DIR = Path(__file__).parent.parent.parent / "test_reports"

RDFLIB_PROJECT_IRI = URIRef("https://github.com/RDFLib/rdflib")


@dataclass(eq=False)
class EARLReport:
    """
    This is a helper class for building an EARL report graph.
    """

    reporter: EARLReporter
    output_file: Path
    assertions: List[Tuple[URIRef, Set[_TripleType]]] = field(
        init=False, default_factory=list, repr=False
    )

    def add_test_outcome(
        self, test_id: URIRef, outcome: URIRef, info: Optional[Literal] = None
    ):
        triples: Set[_TripleType] = set()
        assertion = BNode(f"{test_id}")
        triples.add((assertion, RDF.type, EARL.Assertion))
        triples.add((assertion, EARL.test, test_id))
        triples.add((assertion, EARL.subject, self.reporter.project_iri))
        triples.add((assertion, EARL.mode, EARL.automatic))
        triples.add((assertion, EARL.assertedBy, self.reporter.assertor_iri))
        result = BNode()
        triples.add((assertion, EARL.result, result))
        triples.add((result, RDF.type, EARL.TestResult))
        if self.reporter.add_datetime:
            triples.add((result, DC.date, self.reporter.asserted_at))
        triples.add((result, EARL.outcome, outcome))
        if info:
            triples.add((result, EARL.info, info))
        self.assertions.append((test_id, triples))

    def write(self) -> None:
        sorted_assertion = sorted(
            self.assertions, key=lambda assertion: f"{assertion[0]}"
        )
        if sorted_assertion:
            logger.debug("sorted_assertion[-1] = %r", sorted_assertion[-1])
        graph = self.reporter.make_report_graph()
        for assertion in sorted_assertion:
            for triple in assertion[1]:
                graph.add(triple)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        graph.serialize(format="turtle", destination=self.output_file)


def pytest_addoption(parser: _pytest.config.argparsing.Parser):
    group = parser.getgroup("terminal reporting")
    group.addoption(
        "--earl-output-dir",
        action="store",
        dest="earl_output_dir",
        metavar="dir",
        default=f"{TEST_REPORTS_DIR}",
        help="create EARL reports in the given directory.",
    )

    group.addoption(
        "--earl-output-file",
        action="store",
        dest="earl_output_file",
        metavar="path",
        default=None,
        help="write EARL report in the given file",
    )

    group.addoption(
        "--earl-output-suffix",
        action="store",
        dest="earl_output_suffix",
        metavar="path",
        default="-HEAD",
        help="suffix to use for prefix-defined test reports, defaults to '-HEAD'",
    )

    group.addoption(
        "--earl-assertor-iri",
        action="store",
        dest="earl_assertor_iri",
        metavar="iri",
        default=RDFLIB_PROJECT_IRI,
        help=f"Set the EARL assertor IRI, defaults to the assertor homepage if that is set, or to {RDFLIB_PROJECT_IRI} if no homepage is set.",
    )

    group.addoption(
        "--earl-assertor-homepage",
        action="store",
        dest="earl_assertor_homepage",
        metavar="URL",
        default=None,
        help="Set the EARL assertor homepage.",
    )

    group.addoption(
        "--earl-assertor-name",
        action="store",
        dest="earl_assertor_name",
        metavar="name",
        default=None,
        help="Set the EARL assertor name.",
    )

    group.addoption(
        "--earl-log-level",
        action="store",
        dest="earl_log_level",
        metavar="level",
        default=None,
        help="log level for EARL plugin itself",
    )

    group.addoption(
        "--earl-add-datetime",
        action="store_true",
        dest="earl_add_datetime",
        default=False,
        help="Don't write datetime to result",
    )


FromT = TypeVar("FromT")
ToT = TypeVar("ToT")


def convert_optional(
    optional: Optional[FromT], converter: Callable[[FromT], ToT]
) -> Optional[ToT]:
    if optional is not None:
        return converter(optional)
    return None


PYTEST_PLUGIN_NAME = "rdflib_earl_reporter"


def pytest_configure(config: pytest.Config):
    if config.option.earl_log_level is not None:
        log_level = config.option.earl_log_level
        logger.setLevel(log_level)

    earl_reporter = EARLReporter(
        assertor_iri=URIRef(config.option.earl_assertor_iri),
        output_dir=Path(config.option.earl_output_dir),
        output_suffix=config.option.earl_output_suffix,
        output_file=convert_optional(config.option.earl_output_file, Path),
        assertor_homepage=convert_optional(
            config.option.earl_assertor_homepage, URIRef
        ),
        assertor_name=convert_optional(config.option.earl_assertor_name, Literal),
        add_datetime=config.option.earl_add_datetime,
    )
    logger.debug("registering earl_reporter = %s", earl_reporter)
    config.pluginmanager.register(earl_reporter, PYTEST_PLUGIN_NAME)


def pytest_unconfigure(config: pytest.Config):
    earl_reporter: Optional[EARLReporter] = config.pluginmanager.get_plugin(
        PYTEST_PLUGIN_NAME
    )
    logger.debug("earl_reporter = %s", earl_reporter)
    if earl_reporter:
        config.pluginmanager.unregister(earl_reporter, PYTEST_PLUGIN_NAME)


# https://docs.pytest.org/en/latest/reference.html#pytest.hookspec.pytest_runtest_protocol


class TestResult(enum.Enum):
    PASS = enum.auto()
    FAIL = enum.auto()
    ERROR = enum.auto()
    SKIP = enum.auto()


class TestReportHelper:
    @classmethod
    def get_rdf_test_uri(cls, report: TestReport) -> Optional[URIRef]:
        return next(
            (
                cast(URIRef, item[1])
                for item in report.user_properties
                if item[0] == RDFT.Test
            ),
            None,
        )

    @classmethod
    def get_manifest_entry(cls, report: TestReport) -> Optional[ManifestEntry]:
        return next(
            (
                cast(ManifestEntry, item[1])
                for item in report.user_properties
                if item[0] == MF.ManifestEntry
            ),
            None,
        )


@dataclass(eq=False)
class EARLReporter:
    """
    This class is a pytest plugin that will write a EARL report with results for
    every pytest which has a rdf_test_uri parameter that is a string or an
    URIRef.
    """

    assertor_iri: URIRef
    output_dir: Path
    output_suffix: str
    output_file: Optional[Path] = None
    assertor_name: Optional[Literal] = None
    assertor_homepage: Optional[URIRef] = None
    add_datetime: bool = True
    extra_triples: Set[_TripleType] = field(default_factory=set)
    prefix_reports: Dict[str, EARLReport] = field(init=True, default_factory=dict)
    report: Optional[EARLReport] = field(init=True, default=None)

    def __post_init__(self) -> None:
        if self.assertor_homepage is not None:
            self.assertor_iri = self.assertor_homepage

        if self.assertor_name:
            self.extra_triples.add((self.assertor_iri, FOAF.name, self.assertor_name))
        if self.assertor_homepage:
            self.extra_triples.add(
                (self.assertor_iri, FOAF.homepage, URIRef(self.assertor_homepage))
            )

        self.project_iri = RDFLIB_PROJECT_IRI

        self.extra_triples.add((self.project_iri, DOAP.homepage, self.project_iri))
        self.extra_triples.add((self.project_iri, DOAP.name, Literal("RDFLib")))
        self.extra_triples.add((self.project_iri, RDF.type, DOAP.Project))
        self.extra_triples.add(
            (self.project_iri, DOAP["programming-language"], Literal("Python"))
        )
        self.extra_triples.add(
            (
                self.project_iri,
                DOAP.description,
                Literal(
                    (
                        "RDFLib is a Python library for working with RDF, "
                        "a simple yet powerful language for representing information."
                    ),
                    lang="en",
                ),
            )
        )

        self.asserted_at = Literal(datetime.now())

        if self.output_file:
            self.report = EARLReport(self, self.output_file)

    def setup_report_graph(self, graph: Graph) -> None:
        GraphHelper.add_triples(graph, self.extra_triples)
        graph.bind("foaf", FOAF)
        graph.bind("earl", EARL)
        graph.bind("doap", DOAP)
        graph.bind("dc", DC)

    def make_report_graph(self) -> Graph:
        graph = Graph(store=OrderedMemory())
        self.setup_report_graph(graph)
        return graph

    def make_report_with_prefix(self, report_prefix: str) -> EARLReport:
        output_file = self.output_dir / f"{report_prefix}{self.output_suffix}.ttl"
        return EARLReport(self, output_file)

    def get_report_for(self, entry: Optional[ManifestEntry]) -> Optional[EARLReport]:
        if self.report:
            return self.report
        if entry is None:
            return None
        manifest = entry.manifest
        logger.debug("manifest = %s", manifest)
        if manifest.report_prefix is None:
            return None
        report = self.prefix_reports.get(manifest.report_prefix)
        if report is None:
            report = self.prefix_reports[manifest.report_prefix] = (
                self.make_report_with_prefix(manifest.report_prefix)
            )
        return report

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(
        self, item: Item, call: CallInfo[None]
    ) -> Generator[None, _Result, None]:
        result = yield

        report: TestReport = result.get_result()

        if not hasattr(item, "callspec"):
            return
        callspec: CallSpec2 = getattr(item, "callspec")
        rdf_test_uri = callspec.params.get("rdf_test_uri")
        if rdf_test_uri is not None:
            if isinstance(rdf_test_uri, str):
                rdf_test_uri = URIRef(rdf_test_uri)
            if isinstance(rdf_test_uri, URIRef):
                report.user_properties.append((RDFT.Test, rdf_test_uri))
            else:
                logger.warning(
                    "rdf_test_uri parameter is not a URIRef or a str, ignoring it"
                )

        manifest_entry = callspec.params.get("manifest_entry")
        if manifest_entry is not None:
            report.user_properties.append((MF.ManifestEntry, manifest_entry))

    @classmethod
    def get_rdf_test_uri(
        cls, rdf_test_uri: Optional[URIRef], manifest_entry: Optional[ManifestEntry]
    ) -> Optional[URIRef]:
        if rdf_test_uri is not None:
            return rdf_test_uri
        if manifest_entry is not None:
            return manifest_entry.identifier
        return None

    def append_result(self, report: TestReport, test_result: TestResult) -> None:
        rdf_test_uri = TestReportHelper.get_rdf_test_uri(report)
        manifest_entry = TestReportHelper.get_manifest_entry(report)
        rdf_test_uri = self.get_rdf_test_uri(rdf_test_uri, manifest_entry)
        logger.debug(
            "rdf_test_uri = %s, manifest_entry = %s", rdf_test_uri, manifest_entry
        )
        if rdf_test_uri is None:
            # nothing to report with
            return
        earl_report = self.get_report_for(manifest_entry)
        logger.debug("earl_report = %s, test_result = %s", earl_report, test_result)
        if earl_report is None:
            return
        if test_result is TestResult.PASS:
            earl_report.add_test_outcome(rdf_test_uri, EARL.passed)
        elif test_result is TestResult.FAIL:
            earl_report.add_test_outcome(rdf_test_uri, EARL.failed)
        elif test_result is TestResult.SKIP:
            earl_report.add_test_outcome(rdf_test_uri, EARL.untested)
        else:
            earl_report.add_test_outcome(rdf_test_uri, EARL.cantTell)

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        logger.debug(
            "report: passed = %s, failed = %s, skipped = %s, when = %s, outcome = %s, keywords = %s",
            report.passed,
            report.failed,
            report.skipped,
            report.when,
            report.outcome,
            report.keywords,
        )
        if report.passed:
            if report.when == "call":  # ignore setup/teardown
                self.append_result(report, TestResult.PASS)
        elif report.failed:
            if report.when == "call":  # ignore setup/teardown
                self.append_result(report, TestResult.FAIL)
            else:
                self.append_result(report, TestResult.ERROR)
        elif report.skipped:
            if "skip" in report.keywords:
                self.append_result(report, TestResult.SKIP)
            elif "xfail" in report.keywords:
                self.append_result(report, TestResult.FAIL)
            else:
                self.append_result(report, TestResult.ERROR)

    def pytest_sessionfinish(self, session: Session):
        if self.report is not None:
            self.report.write()
        for report in self.prefix_reports.values():
            report.write()

    def make_report(self, output_file: Path) -> EARLReport:
        return EARLReport(self, output_file)


class OrderedMemory(Memory):
    def __init__(self, configuration=None, identifier=None):
        super().__init__(configuration, identifier)
        self.__spo = OrderedDict()
        self.__pos = OrderedDict()
        self.__osp = OrderedDict()
        self.__namespace = OrderedDict()
        self.__prefix = OrderedDict()
        self.__context_obj_map = OrderedDict()
