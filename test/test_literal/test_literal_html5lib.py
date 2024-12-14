import xml.dom.minidom
from typing import Callable

import pytest

import rdflib.term
from rdflib.namespace import RDF
from rdflib.term import Literal
from test.utils.literal import LiteralChecker
from test.utils.outcome import OutcomeChecker, OutcomePrimitives

try:
    import html5rdf as _  # noqa: F401
except ImportError:
    pytest.skip("html5rdf not installed", allow_module_level=True)


def test_has_html5rdf() -> None:
    assert rdflib.term._HAS_HTML5RDF is True
    assert RDF.HTML in rdflib.term.XSDToPython
    rule = next(
        (
            item
            for item in rdflib.term._GenericPythonToXSDRules
            if item[0] is xml.dom.minidom.DocumentFragment
        ),
        None,
    )
    assert rule is not None
    assert rule[1][1] == RDF.HTML


@pytest.mark.parametrize(
    ["factory", "outcome"],
    [
        # Ill-typed literals, these have lexical forms that result in
        # errors when parsed as HTML by html5rdf.
        (
            lambda: Literal("<body><h1>Hello, World!</h1></body>", datatype=RDF.HTML),
            LiteralChecker(
                ..., None, RDF.HTML, True, "<body><h1>Hello, World!</h1></body>"
            ),
        ),
        (
            lambda: Literal("<body></body>", datatype=RDF.HTML),
            LiteralChecker(..., None, RDF.HTML, True, "<body></body>"),
        ),
        (
            lambda: Literal("<tr><td>THE TEXT IS IN HERE</td></tr>", datatype=RDF.HTML),
            LiteralChecker(
                ..., None, RDF.HTML, True, "<tr><td>THE TEXT IS IN HERE</td></tr>"
            ),
        ),
        # Well-typed literals, these have lexical forms that parse
        # without errors with html5rdf.
        (
            lambda: Literal("<table></table>", datatype=RDF.HTML),
            LiteralChecker(..., None, RDF.HTML, False, "<table></table>"),
        ),
        (
            lambda: Literal("  <table>  </table>  ", datatype=RDF.HTML, normalize=True),
            LiteralChecker(..., None, RDF.HTML, False, "  <table>  </table>  "),
        ),
        (
            lambda: Literal(
                "  <table>  </table>  ", datatype=RDF.HTML, normalize=False
            ),
            LiteralChecker(..., None, RDF.HTML, False, "  <table>  </table>  "),
        ),
    ],
)
def test_literal_construction(
    factory: Callable[[], Literal],
    outcome: OutcomePrimitives[Literal],
) -> None:
    checker = OutcomeChecker[Literal].from_primitives(outcome)
    with checker.context():
        actual_outcome = factory()
        checker.check(actual_outcome)
