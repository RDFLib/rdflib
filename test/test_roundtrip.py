import logging
import os.path
from json.decoder import JSONDecodeError
from pathlib import Path
from test.data import TEST_DATA_DIR
from test.testutils import GraphHelper
from typing import Callable, Collection, Iterable, List, Optional, Set, Tuple, Union
from xml.sax import SAXParseException

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

import rdflib
import rdflib.compare
from rdflib.namespace import XSD
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
    ("trig", "rdf11trig_eg2.trig"): pytest.mark.xfail(
        reason="""
    Something is going wrong here with blank node serialization. In the second
    graph below bob knows someone who does not exist, while in first he knows
    someone that does exist and has the name Alice.

    AssertionError: in both:
        (rdflib.term.BNode('cbb5eb12b5dcf688537b0298cce144c6dd68cf047530d0b4a455a8f31f314244fd'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/mbox'), rdflib.term.URIRef('mailto:alice@work.example.org'))
        (rdflib.term.BNode('cbb5eb12b5dcf688537b0298cce144c6dd68cf047530d0b4a455a8f31f314244fd'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/name'), rdflib.term.Literal('Alice'))
        (rdflib.term.URIRef('http://example.org/alice'), rdflib.term.URIRef('http://purl.org/dc/terms/publisher'), rdflib.term.Literal('Alice'))
        (rdflib.term.URIRef('http://example.org/bob'), rdflib.term.URIRef('http://purl.org/dc/terms/publisher'), rdflib.term.Literal('Bob'))
    only in first:
        (rdflib.term.BNode('cb0'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/knows'), rdflib.term.BNode('cbb5eb12b5dcf688537b0298cce144c6dd68cf047530d0b4a455a8f31f314244fd'))
        (rdflib.term.BNode('cb0'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/mbox'), rdflib.term.URIRef('mailto:bob@oldcorp.example.org'))
        (rdflib.term.BNode('cb0'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/name'), rdflib.term.Literal('Bob'))
    only in second:
        (rdflib.term.BNode('cb7be1d0397a49ddd4ae8aa96acc7b6135903c5f3fa5e47bf619c0e4b438aafcc1'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/knows'), rdflib.term.BNode('cb0'))
        (rdflib.term.BNode('cb7be1d0397a49ddd4ae8aa96acc7b6135903c5f3fa5e47bf619c0e4b438aafcc1'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/mbox'), rdflib.term.URIRef('mailto:bob@oldcorp.example.org'))
        (rdflib.term.BNode('cb7be1d0397a49ddd4ae8aa96acc7b6135903c5f3fa5e47bf619c0e4b438aafcc1'), rdflib.term.URIRef('http://xmlns.com/foaf/0.1/name'), rdflib.term.Literal('Bob'))
        """,
        raises=AssertionError,
    ),
}

# This is for files which can only be represented properly in one format
CONSTRAINED_FORMAT_MAP = {
    "example-lots_of_graphs.n3": {"n3"}  # only n3 can serialize QuotedGraph
}


def collect_files(
    directory: Path, exclude_names: Optional[Set[str]] = None
) -> List[Tuple[Path, str]]:
    result = []
    for path in directory.glob("**/*"):
        if not path.is_file():
            continue
        if exclude_names is not None and path.name in exclude_names:
            continue
        format = guess_format(path.name)
        if format is None:
            raise ValueError(f"could not determine format for {path}")
        result.append((path, format))
    return result


def roundtrip(infmt: str, testfmt: str, source: Path) -> None:
    g1 = rdflib.ConjunctiveGraph()

    g1.parse(source, format=infmt)

    s = g1.serialize(format=testfmt)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("serailized = \n%s", s)

    g2 = rdflib.ConjunctiveGraph()
    g2.parse(data=s, format=testfmt)

    if testfmt == "hext":
        # HexTuples always sets Literal("abc") -> Literal("abc", datatype=XSD.string)
        # and this prevents roundtripping since most other formats don't equate "" with
        # ""^^xsd:string, at least not in these tests
        #
        # So we have to scrub the literals' string datatype declarations...
        for c in g2.contexts():
            for s, p, o in c.triples((None, None, None)):
                if type(o) == rdflib.Literal and o.datatype == XSD.string:
                    c.remove((s, p, o))
                    c.add((s, p, rdflib.Literal(str(o))))

    if logger.isEnabledFor(logging.DEBUG):
        both, first, second = rdflib.compare.graph_diff(g1, g2)
        logger.debug("Items in both:\n%s", GraphHelper.format_graph_set(both))
        logger.debug("Items in G1 Only:\n%s", GraphHelper.format_graph_set(first))
        logger.debug("Items in G2 Only:\n%s", GraphHelper.format_graph_set(second))

    GraphHelper.assert_isomorphic(g1, g2)

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
    files: Collection[Tuple[Path, str]], hext_okay: bool = False
) -> Iterable[ParameterSet]:
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
            if xfail:
                marks.append(xfail)
            id = f"roundtrip_{os.path.basename(f)}_{infmt}_{testfmt}"
            values = (roundtrip, (infmt, testfmt, f))
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


EXTRA_FILES = [
    (TEST_DATA_DIR / "variants" / "special_chars.nt", "ntriples"),
    (TEST_DATA_DIR / "variants" / "xml_literal.rdf", "xml"),
    (TEST_DATA_DIR / "variants" / "rdf_prefix.jsonld", "json-ld"),
    (TEST_DATA_DIR / "variants" / "simple_quad.trig", "trig"),
    (TEST_DATA_DIR / "variants" / "rdf11trig_eg2.trig", "trig"),
    (TEST_DATA_DIR / "example-lots_of_graphs.n3", "n3"),
    (TEST_DATA_DIR / "issue156.n3", "n3"),
]


@pytest.mark.parametrize("checker, args", make_cases(EXTRA_FILES, hext_okay=True))
def test_extra(checker: Callable[[str, str, Path], None], args: Tuple[str, str, Path]):
    """
    Round tripping works correctly for selected extra files.
    """
    checker(*args)
