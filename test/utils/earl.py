"""
PYTEST_DONT_REWRITE
"""
import enum
import logging
from datetime import datetime
from pathlib import Path
from test.utils.namespace import EARL, RDFT
from typing import TYPE_CHECKING, Generator, Optional, Tuple, cast

import pytest
from pytest import Item

from rdflib import RDF, BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DOAP, FOAF, DefinedNamespace
from rdflib.term import Node

if TYPE_CHECKING:
    from _pytest.main import Session
    from _pytest.python import CallSpec2
    from _pytest.reports import TestReport
    from _pytest.runner import CallInfo
    from pluggy._result import _Result


class EarlReport:
    """
    This is a helper class for building an EARL report graph.
    """

    def __init__(
        self,
        asserter_uri: Optional[str] = None,
        asserter_homepage: Optional[str] = None,
        asserter_name: Optional[str] = None,
    ) -> None:
        self.graph = graph = Graph()
        graph.bind("foaf", FOAF)
        graph.bind("earl", EARL)
        graph.bind("doap", DOAP)
        graph.bind("dc", DC)

        self.asserter: Node
        asserter: Node
        if asserter_uri is not None or asserter_homepage is not None:
            # cast to remove Optional because mypy is not smart enough to
            # figure out that it won't be optional.
            asserter_ref = cast(
                str, asserter_homepage if asserter_uri is None else asserter_uri
            )
            self.asserter = asserter = URIRef(asserter_ref)
            graph.add((asserter, RDF.type, FOAF.Person))
        else:
            self.asserter = asserter = BNode()
            graph.add((asserter, RDF.type, FOAF.Person))
        if asserter_name:
            graph.add((asserter, FOAF.name, Literal(asserter_name)))
        if asserter_homepage:
            graph.add((asserter, FOAF.homepage, URIRef(asserter_homepage)))

        self.project = project = URIRef("https://github.com/RDFLib/rdflib")

        graph.add((project, DOAP.homepage, project))
        graph.add((project, DOAP.name, Literal("RDFLib")))
        graph.add((project, RDF.type, DOAP.Project))
        graph.add((project, DOAP["programming-language"], Literal("Python")))
        graph.add(
            (
                project,
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

        self.now = Literal(datetime.now())

    def add_test_outcome(
        self, test_id: URIRef, outcome: URIRef, info: Optional[Literal] = None
    ) -> Tuple[Node, Node]:
        graph = self.graph
        assertion = BNode()
        graph.add((assertion, RDF.type, EARL.Assertion))
        graph.add((assertion, EARL.test, test_id))
        graph.add((assertion, EARL.subject, self.project))
        graph.add((assertion, EARL.mode, EARL.automatic))
        if self.asserter:
            graph.add((assertion, EARL.assertedBy, self.asserter))

        result = BNode()
        graph.add((assertion, EARL.result, result))
        graph.add((result, RDF.type, EARL.TestResult))
        graph.add((result, DC.date, self.now))
        graph.add((result, EARL.outcome, outcome))
        if info:
            graph.add((result, EARL.info, info))

        return graph, result


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting")
    group.addoption(
        "--earl-report",
        action="store",
        dest="earl_path",
        metavar="path",
        default=None,
        help="create EARL report file at given path.",
    )

    group.addoption(
        "--earl-asserter-uri",
        action="store",
        dest="earl_asserter_uri",
        metavar="uri",
        default=None,
        help="Set the EARL asserter URI, defaults to the asserter homepage if not set.",
    )

    group.addoption(
        "--earl-asserter-homepage",
        action="store",
        dest="earl_asserter_homepage",
        metavar="URL",
        default=None,
        help="Set the EARL asserter homepage.",
    )

    group.addoption(
        "--earl-asserter-name",
        action="store",
        dest="earl_asserter_name",
        metavar="name",
        default=None,
        help="Set the EARL asserter name.",
    )


def pytest_configure(config):
    earl_path = config.option.earl_path
    if earl_path:
        config._earl = EarlReporter(
            Path(earl_path),
            EarlReport(
                asserter_uri=config.option.earl_asserter_uri,
                asserter_name=config.option.earl_asserter_name,
                asserter_homepage=config.option.earl_asserter_homepage,
            ),
        )
        config.pluginmanager.register(config._earl)


def pytest_unconfigure(config):
    earl = getattr(config, "_excel", None)
    if earl:
        del config._earl
        config.pluginmanager.unregister(earl)


# https://docs.pytest.org/en/latest/reference.html#pytest.hookspec.pytest_runtest_protocol


class TestResult(enum.Enum):
    PASS = enum.auto()
    FAIL = enum.auto()
    ERROR = enum.auto()
    SKIP = enum.auto()


class TestReportHelper:
    @classmethod
    def get_rdf_test_uri(cls, report: "TestReport") -> Optional[URIRef]:
        return next(
            (
                cast(URIRef, item[1])
                for item in report.user_properties
                if item[0] == RDFT.Test
            ),
            None,
        )


class EarlReporter:
    """
    This class is a pytest plugin that will write a EARL report with results for
    every pytest which has a rdf_test_uri parameter that is a string or an
    URIRef.
    """

    def __init__(self, output_path: Path, report: Optional[EarlReport] = None) -> None:
        self.report = report if report is not None else EarlReport()
        self.output_path = output_path

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(
        self, item: Item, call: "CallInfo[None]"
    ) -> Generator[None, "_Result", None]:
        result = yield

        report: "TestReport" = result.get_result()

        if not hasattr(item, "callspec"):
            return
        callspec: "CallSpec2" = getattr(item, "callspec")
        rdf_test_uri = callspec.params.get("rdf_test_uri")
        if rdf_test_uri is None:
            return
        if not isinstance(rdf_test_uri, URIRef) and not isinstance(rdf_test_uri, str):
            logging.warning("rdf_test_uri parameter is not a URIRef or a str")
            return
        if not isinstance(rdf_test_uri, URIRef):
            rdf_test_uri = URIRef(rdf_test_uri)

        report.user_properties.append((RDFT.Test, rdf_test_uri))

    def append_result(self, report: "TestReport", test_result: TestResult) -> None:
        rdf_test_uri = TestReportHelper.get_rdf_test_uri(report)
        if rdf_test_uri is None:
            # No RDF test
            return
        if test_result is TestResult.PASS:
            self.report.add_test_outcome(rdf_test_uri, EARL.passed)
        elif test_result is TestResult.FAIL:
            self.report.add_test_outcome(rdf_test_uri, EARL.failed)
        elif (test_result) is TestResult.SKIP:
            self.report.add_test_outcome(rdf_test_uri, EARL.untested)
        else:
            self.report.add_test_outcome(rdf_test_uri, EARL.cantTell)

    def pytest_runtest_logreport(self, report: "TestReport") -> None:
        if report.passed:
            if report.when == "call":  # ignore setup/teardown
                self.append_result(report, TestResult.PASS)
        elif report.failed:
            if report.when == "call":  # ignore setup/teardown
                self.append_result(report, TestResult.FAIL)
            else:
                self.append_result(report, TestResult.ERROR)
        elif report.skipped:
            self.append_result(report, TestResult.SKIP)

    def pytest_sessionfinish(self, session: "Session"):
        self.report.graph.serialize(format="turtle", destination=self.output_path)
