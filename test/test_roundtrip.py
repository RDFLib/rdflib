import enum
import logging
import os.path
from pathlib import Path
from test.data import TEST_DATA_DIR
from test.utils import BNodeHandling, GraphHelper
from typing import Callable, Iterable, List, Optional, Set, Tuple, Type, Union
from xml.sax import SAXParseException

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

import rdflib
import rdflib.compare
from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.namespace import XSD
from rdflib.parser import create_input_source
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib.util import guess_format

logger = logging.getLogger(__name__)

"""
Test round-tripping by all serializers/parser that are registered.
This means, you may test more than just core rdflib!

run with no arguments to test all formats + all files
run with a single argument, to test only that format, i.e. "n3"
run with three arguments to test round-tripping in a given format
and reading a single file in the given format, i.e.:

python test/test_roundtrip.py xml nt test/nt/literals-02.nt

tests roundtripping through rdf/xml with only the literals-02 file

HexTuples format, "hext", cannot be used in all roundtrips due to its
addition of xsd:string to literals of no declared type as this breaks
(rdflib) graph isomorphism, and given that its JSON serialization is
simple (lacking), so hext has been excluded from roundtripping here
but provides some roundtrip test functions of its own (see test_parser_hext.py
& test_serializer_hext.py)

"""

NT_DATA_DIR = Path(TEST_DATA_DIR) / "suites" / "nt_misc"
INVALID_NT_FILES = {
    # illegal literal as subject
    "literals-01.nt",
    "keywords-08.nt",
    "paths-04.nt",
    "numeric-01.nt",
    "numeric-02.nt",
    "numeric-03.nt",
    "numeric-04.nt",
    "numeric-05.nt",
    # illegal variables
    "formulae-01.nt",
    "formulae-02.nt",
    "formulae-03.nt",
    "formulae-05.nt",
    "formulae-06.nt",
    "formulae-10.nt",
    # illegal bnode as predicate
    "paths-06.nt",
    "anons-02.nt",
    "anons-03.nt",
    "qname-01.nt",
    "lists-06.nt",
}


N3_DATA_DIR = Path(TEST_DATA_DIR) / "suites" / "n3roundtrip"

XFAILS = {
    ("xml", "n3-writer-test-29.n3",): pytest.mark.xfail(
        reason="has predicates that cannot be shortened to strict qnames",
        raises=ValueError,
    ),
    ("xml", "qname-02.nt"): pytest.mark.xfail(
        reason="uses a property that cannot be qname'd",
        raises=ValueError,
    ),
    ("trix", "strquot.n3"): pytest.mark.xfail(
        reason="contains characters forbidden by the xml spec",
        raises=SAXParseException,
    ),
    ("xml", "strquot.n3"): pytest.mark.xfail(
        reason="contains characters forbidden by the xml spec",
        raises=SAXParseException,
    ),
    ("json-ld", "keywords-04.nt"): pytest.mark.xfail(
        reason="known NT->JSONLD problem",
        raises=AssertionError,
    ),
    ("json-ld", "example-misc.n3"): pytest.mark.xfail(
        reason="known N3->JSONLD problem",
        raises=AssertionError,
    ),
    ("json-ld", "rdf-test-11.n3"): pytest.mark.xfail(
        reason="known N3->JSONLD problem",
        raises=AssertionError,
    ),
    ("json-ld", "rdf-test-28.n3"): pytest.mark.xfail(
        reason="known N3->JSONLD problem",
        raises=AssertionError,
    ),
    ("json-ld", "n3-writer-test-26.n3"): pytest.mark.xfail(
        reason="known N3->JSONLD problem",
        raises=AssertionError,
    ),
    ("json-ld", "n3-writer-test-28.n3"): pytest.mark.xfail(
        reason="known N3->JSONLD problem",
        raises=AssertionError,
    ),
    ("json-ld", "n3-writer-test-22.n3"): pytest.mark.xfail(
        reason="known N3->JSONLD problem",
        raises=AssertionError,
    ),
    ("json-ld", "rdf-test-21.n3"): pytest.mark.xfail(
        reason="known N3->JSONLD problem",
        raises=AssertionError,
    ),
    ("n3", "example-lots_of_graphs.n3"): pytest.mark.xfail(
        reason="rdflib.compare.isomorphic does not work for quoted graphs.",
        raises=AssertionError,
    ),
    ("hext", "n3-writer-test-22.n3"): pytest.mark.xfail(
        reason='HexTuples conflates "" and ""^^xsd:string strings',
        raises=AssertionError,
    ),
    ("hext", "rdf-test-21.n3"): pytest.mark.xfail(
        reason='HexTuples conflates "" and ""^^xsd:string strings',
        raises=AssertionError,
    ),
    ("xml", "special_chars.nt"): pytest.mark.xfail(
        reason="missing escaping: PCDATA invalid Char value 12 and 8",
        raises=SAXParseException,
    ),
    ("trix", "special_chars.nt"): pytest.mark.xfail(
        reason="missing escaping: PCDATA invalid Char value 12 and 8",
        raises=SAXParseException,
    ),
    ("xml", "rdflibtest-pnamebrackets.nt"): pytest.mark.xfail(
        reason="results in invalid xml element name: <ns1:name(s)/>",
        raises=SAXParseException,
    ),
    ("json-ld", "diverse_quads.trig"): pytest.mark.xfail(
        reason="""
    jsonld serializer is dropping datatype:
        only in first:
            (rdflib.term.URIRef('example:subject'), rdflib.term.URIRef('http://example.com/predicate'), rdflib.term.Literal('XSD string', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')))
        only in second:
            (rdflib.term.URIRef('example:subject'), rdflib.term.URIRef('http://example.com/predicate'), rdflib.term.Literal('XSD string'))
    """,
        raises=AssertionError,
    ),
    ("hext", "diverse_quads.trig"): pytest.mark.xfail(
        reason="""
    hext serializer is dropping datatype:
        only in first:
            (rdflib.term.URIRef('example:subject'), rdflib.term.URIRef('http://example.com/predicate'), rdflib.term.Literal('XSD string', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')))
        only in second:
            (rdflib.term.URIRef('example:subject'), rdflib.term.URIRef('http://example.com/predicate'), rdflib.term.Literal('XSD string'))
    """,
        raises=AssertionError,
    ),
    ("n3", "data/suites/w3c/n3/N3Tests/cwm_syntax/decimal.n3"): pytest.mark.xfail(
        raises=AssertionError,
        reason="""double mismatch
    -            (rdflib.term.Literal('1.328435e+55', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#double')),
    +            (rdflib.term.Literal('1.3284347025749857e+55', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#double')),
    """,
    ),
    ("n3", "data/suites/w3c/n3/N3Tests/cwm_syntax/decimal-ref.n3"): pytest.mark.xfail(
        raises=AssertionError,
        reason="""double mismatch
    -            (rdflib.term.Literal('1.328435e+55', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#double')),
    +            (rdflib.term.Literal('1.32843470257e+55', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#double')),
    """,
    ),
    (
        "n3",
        "data/suites/w3c/n3/N3Tests/cwm_syntax/neg-single-quote.n3",
    ): pytest.mark.xfail(raises=BadSyntax, reason="no support for single quotes"),
    ("json-ld", "bnode_refs.trig"): pytest.mark.xfail(
        reason="a whole bunch of triples with bnode as subject is not in the reconstituted graph",
        raises=AssertionError,
    ),
}

# This is for files which can only be represented properly in one format
CONSTRAINED_FORMAT_MAP = {
    "example-lots_of_graphs.n3": {"n3"}  # only n3 can serialize QuotedGraph
}


def collect_files(
    directory: Path, exclude_names: Optional[Set[str]] = None, pattern: str = "**/*"
) -> List[Tuple[Path, str]]:
    result = []
    for path in directory.glob(pattern):
        if not path.is_file():
            continue
        if exclude_names is not None and path.name in exclude_names:
            continue
        format = guess_format(path.name)
        if format is None:
            raise ValueError(f"could not determine format for {path}")
        result.append((path, format))
    return result


class Check(enum.Enum):
    ISOMORPHIC = enum.auto()
    SET_EQUALS = enum.auto()
    SET_EQUALS_WITHOUT_BLANKS = enum.auto()


def roundtrip(
    infmt: str,
    testfmt: str,
    source: Path,
    graph_type: Type[Graph] = ConjunctiveGraph,
    checks: Optional[Set[Check]] = None,
    same_public_id: bool = False,
) -> None:
    g1 = graph_type()

    if same_public_id:
        input_source = create_input_source(source)
        g1.parse(input_source, format=infmt)
    else:
        g1.parse(source, format=infmt)

    s = g1.serialize(format=testfmt)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "infmt = %s, testfmt = %s, source = %s, serialized = \n%s",
            infmt,
            testfmt,
            source,
            s,
        )

    g2 = graph_type()
    if same_public_id:
        g2.parse(data=s, publicID=input_source.getPublicId(), format=testfmt)
    else:
        g2.parse(data=s, format=testfmt)

    if testfmt == "hext" and isinstance(g2, ConjunctiveGraph):
        # HexTuples always sets Literal("abc") -> Literal("abc", datatype=XSD.string)
        # and this prevents roundtripping since most other formats don't equate "" with
        # ""^^xsd:string, at least not in these tests
        #
        # So we have to scrub the literals' string datatype declarations...
        for c in g2.contexts():
            # type error: Incompatible types in assignment (expression has type "Node", variable has type "str")
            for s, p, o in c.triples((None, None, None)):  # type: ignore[assignment]
                if type(o) == rdflib.Literal and o.datatype == XSD.string:
                    # type error: Argument 1 to "remove" of "Graph" has incompatible type "Tuple[str, Node, Literal]"; expected "Tuple[Optional[Node], Optional[Node], Optional[Node]]"
                    c.remove((s, p, o))  # type: ignore[arg-type]
                    # type error: Argument 1 to "add" of "Graph" has incompatible type "Tuple[str, Node, Literal]"; expected "Tuple[Node, Node, Node]"
                    c.add((s, p, rdflib.Literal(str(o))))  # type: ignore[arg-type]

    if logger.isEnabledFor(logging.DEBUG):
        both, first, second = rdflib.compare.graph_diff(g1, g2)
        logger.debug("Items in both:\n%s", GraphHelper.format_graph_set(both))
        logger.debug("Items in G1 Only:\n%s", GraphHelper.format_graph_set(first))
        logger.debug("Items in G2 Only:\n%s", GraphHelper.format_graph_set(second))

    if checks is None or Check.ISOMORPHIC in checks:
        GraphHelper.assert_isomorphic(g1, g2)
    if checks is not None:
        if Check.SET_EQUALS in checks:
            GraphHelper.assert_sets_equals(
                g1, g2, bnode_handling=BNodeHandling.COLLAPSE
            )
        if Check.SET_EQUALS_WITHOUT_BLANKS in checks:
            GraphHelper.assert_sets_equals(
                g1, g2, bnode_handling=BNodeHandling.COLLAPSE
            )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("OK")


_formats: Optional[Set[str]] = None


def get_formats() -> Set[str]:
    global _formats
    if not _formats:
        serializers = set(
            x.name for x in rdflib.plugin.plugins(None, rdflib.plugin.Serializer)
        )
        parsers = set(x.name for x in rdflib.plugin.plugins(None, rdflib.plugin.Parser))
        _formats = {
            format for format in parsers.intersection(serializers) if "/" not in format
        }
    return _formats


def make_cases(
    files: Iterable[Tuple[Path, str]],
    formats: Optional[Set[str]] = None,
    hext_okay: bool = False,
    checks: Optional[Set[Check]] = None,
    graph_type: Type[Graph] = ConjunctiveGraph,
    same_public_id: bool = False,
) -> Iterable[ParameterSet]:
    if formats is None:
        formats = get_formats()
    for testfmt in formats:
        # if testfmt == "hext":
        #     continue
        logging.debug("testfmt = %s", testfmt)
        for f, infmt in files:
            constrained_formats = CONSTRAINED_FORMAT_MAP.get(f.name, None)
            if constrained_formats is not None and testfmt not in constrained_formats:
                logging.debug(
                    f"skipping format {testfmt} as it is not in the list of constrained formats for {f} which is {constrained_formats}"
                )
                continue
            marks: List[Union[MarkDecorator, Mark]] = []
            xfail = XFAILS.get((testfmt, f.name))
            if xfail is None:
                xfail = XFAILS.get(
                    (testfmt, f"{f.relative_to(TEST_DATA_DIR.parent).as_posix()}")
                )
            if xfail is not None:
                marks.append(xfail)
            id = f"roundtrip_{os.path.basename(f)}_{infmt}_{testfmt}"
            values = (
                lambda infmt, testfmt, f: roundtrip(
                    infmt,
                    testfmt,
                    f,
                    checks=checks,
                    graph_type=graph_type,
                    same_public_id=same_public_id,
                ),
                (infmt, testfmt, f),
            )
            logging.debug("values = %s", values)
            yield pytest.param(*values, marks=marks, id=id)


def test_formats() -> None:
    formats = get_formats()
    logging.debug("formats = %s", formats)
    assert formats is not None
    assert len(formats) > 4


@pytest.mark.parametrize(
    "checker, args", make_cases(collect_files(NT_DATA_DIR, INVALID_NT_FILES))
)
def test_nt(checker: Callable[[str, str, Path], None], args: Tuple[str, str, Path]):
    checker(*args)


@pytest.mark.parametrize("checker, args", make_cases(collect_files(N3_DATA_DIR)))
def test_n3(checker: Callable[[str, str, Path], None], args: Tuple[str, str, Path]):
    checker(*args)


N3_W3C_SUITE_DIR = Path(TEST_DATA_DIR) / "suites" / "w3c" / "n3"

r"""
List generated with:

sparql --base '.' --query <(echo '
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdft:  <http://www.w3.org/ns/rdftest#>
PREFIX mf:    <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#>
PREFIX test:  <https://w3c.github.io/N3/tests/test.n3#>
SELECT DISTINCT ?file WHERE {
    ?test a test:TestN3PositiveSyntax.
    ?test mf:action ?file
}
') --data test/data/suites/w3c/n3/N3Tests/manifest-parser.ttl --results=TSV \
  | sed 1d \
  | sed -E 's,^.*(test/data/suites/.*)>$,\1,g' \
  | grep -v '/new_syntax/' \
  | xargs -I{} find {} -printf '%p:%s\n' \
  | gawk -F: '($2 <= 1024){ print $1 }' \
  | xargs egrep -c '[?]\S+' | sort \
  | sed -E -n 's|^test/data/suites/w3c/n3/(.*):0|    (N3_W3C_SUITE_DIR / "\1", "n3"),|gp'
"""

N3_W3C_SUITE_FILES = [
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_andy/D-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_i18n/hiragana.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_i18n/i18n.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_i18n/umlaut.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_includes/bnode-conclude-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_includes/builtins.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_includes/concat-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_includes/conjunction-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_includes/foo.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_includes/list-in-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_includes/t10a.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_includes/t1.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_includes/t2.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_includes/t3.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/append-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/bnode_in_list_in_list.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/builtin_generated_match-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/construct.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/list-bug1-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/list-bug2-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/r1-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/unify2-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/unify3-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/unify4-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_list/unify5-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_math/long.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/anon-prop.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/anonymous_loop.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/classes.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/contexts.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/daml-pref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/equiv-syntax.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/filter-bnodes.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/invalid-ex.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/kb1.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/lists.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/lists-simple.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/reluri-1.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/t00-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/t01-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_other/underbarscope.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/double-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/socrates-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t1.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t1-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t2.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t2-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t3.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t3-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t4-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t5-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t6-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t8-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t9.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/t9-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_reason/timbl.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_string/endsWith-out.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_supports/simple.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_supports/simple-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/a1.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/bad-preds-formula.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/bad-preds-literal.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/base.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/base-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/BnodeAcrossFormulae.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/boolean.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/boolean-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/colon-no-qname.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/decimal.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/decimal-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/embedded-dot-in-qname.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/formula_bnode.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/formula-simple-1.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/formula-subject.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/graph-as-object.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/neg-formula-predicate.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/neg-literal-predicate.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/neg-single-quote.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/nested.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/one-bnode.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/qvars3.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/sep-term.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/sib.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/space-in-uri-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/this-rules-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/trailing-semicolon-ref.nt", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/zero-length-lname.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_syntax/zero-predicates.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_unify/reflexive-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_unify/unify1-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_unify/unify2.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/cwm_unify/unify2-ref.n3", "n3"),
    (N3_W3C_SUITE_DIR / "N3Tests/extra/good_prefix.n3", "n3"),
]


@pytest.mark.parametrize(
    "checker, args",
    make_cases(
        N3_W3C_SUITE_FILES,
        formats={"n3"},
        # NOTE: Isomomorphic check does not work on Quoted Graphs
        checks={Check.SET_EQUALS_WITHOUT_BLANKS},
        graph_type=Graph,
        same_public_id=True,
    ),
)
def test_n3_suite(
    checker: Callable[[str, str, Path], None], args: Tuple[str, str, Path]
):
    checker(*args)


EXTRA_FILES = [
    (TEST_DATA_DIR / "variants" / "special_chars.nt", "ntriples"),
    (TEST_DATA_DIR / "variants" / "xml_literal.rdf", "xml"),
    (TEST_DATA_DIR / "variants" / "rdf_prefix.jsonld", "json-ld"),
    (TEST_DATA_DIR / "variants" / "simple_quad.trig", "trig"),
    (TEST_DATA_DIR / "variants" / "rdf11trig_eg2.trig", "trig"),
    (TEST_DATA_DIR / "variants" / "diverse_triples.nt", "ntriples"),
    (TEST_DATA_DIR / "variants" / "diverse_quads.nq", "nquads"),
    (TEST_DATA_DIR / "variants" / "diverse_quads.trig", "trig"),
    (TEST_DATA_DIR / "roundtrip" / "bnode_refs.trig", "trig"),
    (TEST_DATA_DIR / "example-lots_of_graphs.n3", "n3"),
    (TEST_DATA_DIR / "issue156.n3", "n3"),
]


@pytest.mark.parametrize("checker, args", make_cases(EXTRA_FILES, hext_okay=True))
def test_extra(checker: Callable[[str, str, Path], None], args: Tuple[str, str, Path]):
    """
    Round tripping works correctly for selected extra files.
    """
    checker(*args)
