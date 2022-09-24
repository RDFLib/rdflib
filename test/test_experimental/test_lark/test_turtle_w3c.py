"""This runs the turtle tests for the W3C RDF Working Group's Turtle
test suite."""

import logging
from contextlib import ExitStack
from test.data import TEST_DATA_DIR
from test.utils import BNodeHandling, GraphHelper, ensure_suffix
from test.utils.dawg_manifest import ManifestEntry, params_from_sources
from test.utils.iri import URIMapper
from test.utils.namespace import RDFT
from typing import Optional

import pytest

import rdflib
from rdflib.graph import Graph

logger = logging.getLogger(__name__)

rdflib.plugin.register(
    "larkttl",
    rdflib.parser.Parser,
    "rdflib.experimental.plugins.parsers.larkturtle",
    "LarkTurtleParser",
)


REMOTE_BASE_IRI = "http://www.w3.org/2013/TurtleTests/"
LOCAL_BASE_DIR = TEST_DATA_DIR / "suites/w3c/turtle/"
ENCODING = "utf-8"
MAPPER = URIMapper.from_mappings(
    (REMOTE_BASE_IRI, ensure_suffix(LOCAL_BASE_DIR.as_uri(), "/"))
)
VALID_TYPES = {
    RDFT.TestTurtlePositiveSyntax,
    RDFT.TestTurtleNegativeSyntax,
    RDFT.TestTurtleEval,
    RDFT.TestTurtleNegativeEval,
}

MARK_DICT = {
    f"{REMOTE_BASE_IRI}#bareword_double": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#double_lower_case_e": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#positive_numeric": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#numeric_with_leading_0": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-number-03": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-number-05": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-number-07": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-number-09": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-number-10": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#turtle-syntax-number-11": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#turtle-subm-11": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#turtle-subm-19": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
    f"{REMOTE_BASE_IRI}#turtle-subm-20": pytest.mark.xfail(
        reason="Difference in Lark Cython Numeric serialization"
    ),
}


def check_entry(entry: ManifestEntry) -> None:
    assert entry.action is not None
    assert entry.type in VALID_TYPES

    action_path = entry.uri_mapper.to_local_path(entry.action)

    if logger.isEnabledFor(logging.DEBUG):
        logger.info(
            "action = %s\n%s", action_path, action_path.read_text(encoding=ENCODING)
        )

    catcher: Optional[pytest.ExceptionInfo[Exception]] = None

    graph = Graph()

    with ExitStack() as xstack:
        if entry.type in (RDFT.TestTurtleNegativeSyntax, RDFT.TestTurtleNegativeEval):
            catcher = xstack.enter_context(pytest.raises(Exception))

        graph.parse(
            action_path,
            publicID=entry.action,
            format="larkttl",
            base=REMOTE_BASE_IRI + str(action_path).split("/")[-1],
        )
        GraphHelper.assert_isomorphic(
            graph,
            Graph().parse(
                action_path,
                publicID=entry.action,
                format="ttl",
            ),
        )

    if catcher is not None:
        assert catcher.value is not None

    if entry.type == RDFT.TestTurtleEval:
        assert entry.result is not None
        result_source = entry.uri_mapper.to_local_path(entry.result)
        result_graph = Graph()
        result_graph.parse(
            result_source,
            publicID=entry.action,
            format="ntriples",
        )
        GraphHelper.assert_isomorphic(graph, result_graph)
        GraphHelper.assert_sets_equals(
            graph, result_graph, bnode_handling=BNodeHandling.COLLAPSE
        )


@pytest.mark.parametrize(
    ["manifest_entry"],
    params_from_sources(
        MAPPER,
        ManifestEntry,
        LOCAL_BASE_DIR / "manifest.ttl",
        mark_dict=MARK_DICT,
        report_prefix="rdflib_w3c_turtle",
    ),
)
def test_entry(manifest_entry: ManifestEntry) -> None:
    check_entry(manifest_entry)
