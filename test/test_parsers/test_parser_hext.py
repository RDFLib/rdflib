import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from rdflib import ConjunctiveGraph, Dataset, Literal
from rdflib.namespace import XSD


def test_small_string():
    s = """
        ["http://example.com/s01", "http://example.com/a", "http://example.com/Type1", "globalId", "", ""]
        ["http://example.com/s01", "http://example.com/label", "This is a Label", "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString", "en", ""]
        ["http://example.com/s01", "http://example.com/comment", "This is a comment", "http://www.w3.org/2001/XMLSchema#string", "", ""]
        ["http://example.com/s01", "http://example.com/creationDate", "2021-12-01", "http://www.w3.org/2001/XMLSchema#date", "", ""]
        ["http://example.com/s01", "http://example.com/creationTime", "2021-12-01T12:13:00", "http://www.w3.org/2001/XMLSchema#dateTime", "", ""]
        ["http://example.com/s01", "http://example.com/age", "42", "http://www.w3.org/2001/XMLSchema#integer", "", ""]
        ["http://example.com/s01", "http://example.com/trueFalse", "false", ",http://www.w3.org/2001/XMLSchema#boolean", "", ""]
        ["http://example.com/s01", "http://example.com/op1", "http://example.com/o1", "globalId", "", ""]
        ["http://example.com/s01", "http://example.com/op1", "http://example.com/o2", "globalId", "", ""]
        ["http://example.com/s01", "http://example.com/op2", "http://example.com/o3", "globalId", "", ""]
        """
    d = Dataset().parse(data=s, format="hext")
    assert len(d) == 10


def test_small_string_cg():
    s = """
        ["http://example.com/s01", "http://example.com/a", "http://example.com/Type1", "globalId", "", ""]
        ["http://example.com/s01", "http://example.com/label", "This is a Label", "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString", "en", ""]
        ["http://example.com/s01", "http://example.com/comment", "This is a comment", "http://www.w3.org/2001/XMLSchema#string", "", ""]
        ["http://example.com/s01", "http://example.com/creationDate", "2021-12-01", "http://www.w3.org/2001/XMLSchema#date", "", ""]
        ["http://example.com/s01", "http://example.com/creationTime", "2021-12-01T12:13:00", "http://www.w3.org/2001/XMLSchema#dateTime", "", ""]
        ["http://example.com/s01", "http://example.com/age", "42", "http://www.w3.org/2001/XMLSchema#integer", "", ""]
        ["http://example.com/s01", "http://example.com/trueFalse", "false", ",http://www.w3.org/2001/XMLSchema#boolean", "", ""]
        ["http://example.com/s01", "http://example.com/op1", "http://example.com/o1", "globalId", "", ""]
        ["http://example.com/s01", "http://example.com/op1", "http://example.com/o2", "globalId", "", ""]
        ["http://example.com/s01", "http://example.com/op2", "http://example.com/o3", "globalId", "", ""]
        """
    d = ConjunctiveGraph().parse(data=s, format="hext")
    assert len(d) == 10


def test_small_file_singlegraph():
    d = Dataset().parse(
        Path(__file__).parent.parent / "data/test_parser_hext_singlegraph.ndjson",
        format="hext",
    )
    assert len(d) == 10


def test_small_file_multigraph():
    d = Dataset()
    assert len(d) == 0
    d.parse(
        Path(__file__).parent.parent / "data/test_parser_hext_multigraph.ndjson",
        format="hext",
        publicID=d.default_context.identifier,
    )

    """There are 22 lines in the file test_parser_hext_multigraph.ndjson. When loaded
    into a Dataset, we get only 18 quads since the the dataset can contextualise
    the triples and thus deduplicate 4."""
    total_triples = 0
    # count all the triples in the Dataset
    for context in d.contexts():
        for triple in context.triples((None, None, None)):
            total_triples += 1
    assert total_triples == 18


def test_small_file_multigraph_cg():
    d = ConjunctiveGraph()
    assert len(d) == 0
    d.parse(
        Path(__file__).parent.parent / "data/test_parser_hext_multigraph.ndjson",
        format="hext",
        publicID=d.default_context.identifier,
    )

    """There are 22 lines in the file test_parser_hext_multigraph.ndjson. When loaded
    into a CG, we get only 18 quads since the the CG can contextualise
    the triples and thus deduplicate 4."""
    total_triples = 0
    # count all the triples in the Dataset
    for context in d.contexts():
        for triple in context.triples((None, None, None)):
            total_triples += 1
    assert total_triples == 18


def test_roundtrip():
    # these are some RDF files that HexT can round-trip since the have no
    # literals with no datatype declared:
    TEST_DIR = Path(__file__).parent.absolute() / "nt"
    files_to_skip = {
        "paths-04.nt": "subject literal",
        "even_more_literals.nt": "JSON decoding error",
        "literals-02.nt": "JSON decoding error",
        "more_literals.nt": "JSON decoding error",
        "test.nt": "JSON decoding error",
        "literals-05.nt": "JSON decoding error",
        "i18n-01.nt": "JSON decoding error",
        "literals-04.nt": "JSON decoding error",
        "rdflibtest01.nt": "JSON decoding error",
        "rdflibtest05.nt": "JSON decoding error",
    }
    tests = 0
    skipped = 0
    skip = False
    print()
    p = TEST_DIR.glob("**/*")
    for f in [x for x in p if x.is_file()]:
        tests += 1
        print(f"Test {tests}: {f}")
        if f.name not in files_to_skip.keys():
            try:
                cg = ConjunctiveGraph().parse(f, format="nt")
                # print(cg.serialize(format="n3"))
            except:
                print(f"Skipping: could not NT parse")
                skipped += 1
                skip = True
            if not skip:
                cg2 = ConjunctiveGraph()
                cg2.parse(
                    data=cg.serialize(format="hext"),
                    format="hext",
                    publicID=cg2.default_context.identifier,
                )
                if cg2.context_aware:
                    for context in cg2.contexts():
                        for triple in context.triples((None, None, None)):
                            if type(triple[2]) == Literal:
                                if triple[2].datatype == XSD.string:
                                    context.remove((triple[0], triple[1], triple[2]))
                                    context.add(
                                        (triple[0], triple[1], Literal(str(triple[2])))
                                    )
                else:
                    for triple in cg2.triples((None, None, None)):
                        if type(triple[2]) == Literal:
                            if triple[2].datatype == XSD.string:
                                cg2.remove((triple[0], triple[1], triple[2]))
                                cg2.add((triple[0], triple[1], Literal(str(triple[2]))))

                # print(cg2.serialize(format="trig"))
                assert cg.isomorphic(cg2)
            skip = False
        else:
            print(f"Skipping: {files_to_skip[f.name]}")

    print(f"No. tests: {tests}")
    print(f"No. tests skipped: {skipped}")


if __name__ == "__main__":
    test_small_file_multigraph()
