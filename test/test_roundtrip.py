import logging
import os.path
from pathlib import Path
from test.testutils import GraphHelper
from typing import Callable, Collection, Iterable, List, Optional, Set, Tuple, Union
from xml.sax import SAXParseException

import pytest
from _pytest.mark.structures import Mark, MarkDecorator, ParameterSet

import rdflib
import rdflib.compare
from rdflib.util import guess_format
from rdflib.namespace import XSD

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

NT_DATA_DIR = Path(__file__).parent / "nt"
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


N3_DATA_DIR = Path(__file__).parent / "n3"

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


def roundtrip(infmt: str, testfmt: str, source: Path, verbose: bool = False) -> None:

    g1 = rdflib.ConjunctiveGraph()

    g1.parse(source, format=infmt)

    s = g1.serialize(format=testfmt)

    if verbose:
        print("S:")
        print(s, flush=True)

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

    if verbose:
        both, first, second = rdflib.compare.graph_diff(g1, g2)
        print("Diff:")
        print("%d triples in both" % len(both))
        print("G1 Only:")
        for t in sorted(first):
            print(t)

        print("--------------------")
        print("G2 Only")
        for t in sorted(second):
            print(t)

    assert rdflib.compare.isomorphic(g1, g2)

    if verbose:
        print("Ok!")


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


def make_cases(files: Collection[Tuple[Path, str]]) -> Iterable[ParameterSet]:
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
