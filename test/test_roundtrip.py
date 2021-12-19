import pytest

import rdflib
import rdflib.compare

try:
    from .test_nt_suite import all_nt_files
    assert all_nt_files

    from .test_n3_suite import all_n3_files
    assert all_n3_files
except:
    from test.test_nt_suite import all_nt_files
    from test.test_n3_suite import all_n3_files

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


SKIP = [
    ("xml", "test/n3/n3-writer-test-29.n3"),
    # has predicates that cannot be shortened to strict qnames
    ("xml", "test/nt/qname-02.nt"),  # uses a property that cannot be qname'd
    ("trix", "test/n3/strquot.n3"),  # contains characters forbidden by the xml spec
    ("xml", "test/n3/strquot.n3"),  # contains characters forbidden by the xml spec
    ("json-ld", "test/nt/keywords-04.nt"),  # known NT->JSONLD problem
    ("json-ld", "test/n3/example-misc.n3"),  # known N3->JSONLD problem
    ("json-ld", "test/n3/n3-writer-test-16.n3"),  # known N3->JSONLD problem
    ("json-ld", "test/n3/rdf-test-11.n3"),  # known N3->JSONLD problem
    ("json-ld", "test/n3/rdf-test-28.n3"),  # known N3->JSONLD problem
    ("json-ld", "test/n3/n3-writer-test-26.n3"),  # known N3->JSONLD problem
    ("json-ld", "test/n3/n3-writer-test-28.n3"),  # known N3->JSONLD problem
    ("json-ld", "test/n3/n3-writer-test-22.n3"),  # known N3->JSONLD problem
    ("json-ld", "test/n3/rdf-test-21.n3"),  # known N3->JSONLD problem
]


def roundtrip(e, verbose=False):
    infmt, testfmt, source = e

    g1 = rdflib.ConjunctiveGraph()

    g1.parse(source, format=infmt)

    s = g1.serialize(format=testfmt)

    if verbose:
        print("S:")
        print(s, flush=True)

    g2 = rdflib.ConjunctiveGraph()
    g2.parse(data=s, format=testfmt)

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


formats = None


def get_cases():
    global formats
    if not formats:
        serializers = set(
            x.name for x in rdflib.plugin.plugins(None, rdflib.plugin.Serializer)
        )
        parsers = set(x.name for x in rdflib.plugin.plugins(None, rdflib.plugin.Parser))
        formats = parsers.intersection(serializers)

    for testfmt in formats:
        if testfmt != "hext":
            if "/" in testfmt:
                continue  # skip double testing
            for f, infmt in all_nt_files():
                if (testfmt, f) not in SKIP:
                    yield roundtrip, (infmt, testfmt, f)


@pytest.mark.parametrize("checker, args", get_cases())
def test_cases(checker, args):
    checker(args)


def get_n3_test():
    global formats
    if not formats:
        serializers = set(
            x.name for x in rdflib.plugin.plugins(None, rdflib.plugin.Serializer)
        )
        parsers = set(x.name for x in rdflib.plugin.plugins(None, rdflib.plugin.Parser))
        formats = parsers.intersection(serializers)

    for testfmt in formats:
        if testfmt != "hext":
            if "/" in testfmt:
                continue  # skip double testing
            for f, infmt in all_n3_files():
                if (testfmt, f) not in SKIP:
                    yield roundtrip, (infmt, testfmt, f)


@pytest.mark.parametrize("checker, args", get_n3_test())
def test_n3(checker, args):
    checker(args)


if __name__ == "__main__":
    print("hi")
