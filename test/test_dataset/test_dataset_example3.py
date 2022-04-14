import os
from test.data import CONSISTENT_DATA_DIR

import pytest

import rdflib
from rdflib import logger
from rdflib.compare import (
    graph_diff,
    isomorphic,
    similar,
    to_canonical_graph,
    to_isomorphic,
)
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph
from rdflib.namespace import DC, DCTERMS, FOAF, RDF, SKOS, XSD, Namespace
from rdflib.term import BNode, Literal, URIRef

example3_root = os.path.join(CONSISTENT_DATA_DIR, "example-3-three-named-graphs.")

EX = Namespace("http://www.example.org/vocabulary#")
EXDOC = Namespace("http://www.example.org/exampleDocument#")
SWP = Namespace("http://www.w3.org/2004/03/trix/swp-1/")


@pytest.fixture
def example3(request):
    d = Dataset()

    d.bind("ex", EX)
    d.bind("", EXDOC)
    d.bind("swp", SWP)

    G1 = d.graph(EXDOC.G1)
    G2 = d.graph(EXDOC.G2)
    G3 = d.graph(EXDOC.G3)

    monica = EXDOC.Monica
    G1.add((monica, EX.name, Literal("Monica Murphy")))
    G1.add((monica, EX.homepage, URIRef("http://www.monicamurphy.org")))
    G1.add((monica, EX.email, URIRef("mailto:monica@monicamurphy.org")))
    G1.add((monica, EX.hasSkill, EX.management))

    G2.add((monica, RDF.type, EX.Person))
    G2.add((monica, EX.hasSkill, EX.Programming))

    w1 = BNode()
    w2 = BNode()

    G3.add((EXDOC.G1, SWP.assertedBy, w1))
    G3.add((w1, SWP.authority, EXDOC.Chris))
    G3.add((w1, DC.date, Literal("2003-10-02", datatype=XSD.date)))

    G3.add((EXDOC.G2, SWP.quotedBy, w2))
    G3.add((EXDOC.G3, SWP.assertedBy, w2))
    G3.add((w2, DC.date, Literal("2003-09-03", datatype=XSD.date)))
    G3.add((w2, SWP.authority, EXDOC.Chris))
    G3.add((EXDOC.Chris, RDF.type, EX.Person))
    G3.add((EXDOC.Chris, EX.email, URIRef("mailto:chris@bizer.de")))

    yield d


context_formats = [
    "json-ld",
    "trix",
    "nquads",
    "trig",
    "hext",
]


@pytest.fixture
def xfail_selected_context_parse_data_formats(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        "json-ld",
        "trix",
        "nquads",
        "trig",
        "hext",
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", context_formats)
@pytest.mark.usefixtures("xfail_selected_context_parse_data_formats")
def test_parse_example3_from_data(fmt, example3):
    d1 = example3

    d2 = Dataset()
    with open(example3_root + fmt, "r") as fp:
        d2.parse(data=fp.read(), format=fmt)

    assert len(list(d2.contexts())) == 3
    assert len(list(d2.graphs())) == 3
    assert len(d2) == 0

    assert len(list(d1.quads((None, None, None, None)))) == len(
        list(d2.quads((None, None, None, None)))
    )

    assert len(d1.store) == len(d2.store)

    assert isomorphic(d1, d2)

    assert EXDOC.G1 in list(d2.contexts())
    assert EXDOC.G2 in list(d2.contexts())
    assert EXDOC.G3 in list(d2.contexts())
    assert (EXDOC.Chris, RDF.type, EX.Person) in d2.graph(EXDOC.G3)


@pytest.fixture
def xfail_selected_context_parse_file_formats(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        "json-ld",
        "hext",
        "trig",
        "trix",
        "nquads",
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", context_formats)
@pytest.mark.usefixtures("xfail_selected_context_parse_file_formats")
def test_parse_example3_from_file(fmt, example3):
    d1 = example3

    d2 = Dataset()
    with open(example3_root + fmt, "r") as fp:
        d2.parse(file=fp, format=fmt)

    assert len(list(d2.contexts())) == 3
    assert len(list(d2.graphs())) == 3
    assert len(d2) == 0

    assert len(list(d1.quads((None, None, None, None)))) == len(
        list(d2.quads((None, None, None, None)))
    )

    assert len(d1.store) == len(d2.store)

    assert isomorphic(d1, d2)

    assert len(list(d2.contexts())) == 3
    assert len(list(d2.graphs())) == 3
    assert len(d2) == 0
    assert EXDOC.G1 in list(d2.contexts())
    assert EXDOC.G2 in list(d2.contexts())
    assert EXDOC.G3 in list(d2.contexts())
    assert (EXDOC.Chris, RDF.type, EX.Person) in d2.graph(EXDOC.G3)

    assert isomorphic(d1, d2)


@pytest.fixture
def xfail_selected_context_parse_location_formats(request):
    fmt = request.getfixturevalue("fmt")

    expected_failures = [
        "trix",
        "hext",
        "nquads",
        "json-ld",
        "hext",
        "trig",
    ]

    if fmt in expected_failures:
        request.node.add_marker(
            pytest.mark.xfail(reason=f"Expected failure with {fmt}")
        )


@pytest.mark.parametrize("fmt", context_formats)
@pytest.mark.usefixtures("xfail_selected_context_parse_location_formats")
def test_parse_example3_from_location(fmt, example3):
    d1 = example3

    d2 = Dataset()
    loc = example3_root + fmt
    d2.parse(location=loc, format=fmt)

    assert len(list(d2.contexts())) == 3
    assert len(list(d2.graphs())) == 3
    assert len(d2) == 0

    assert len(list(d1.quads((None, None, None, None)))) == len(
        list(d2.quads((None, None, None, None)))
    )

    assert len(d1.store) == len(d2.store)

    assert len(list(d2.contexts())) == 3
    assert len(list(d2.graphs())) == 3
    assert len(d2) == 0
    assert EXDOC.G1 in list(d2.contexts())
    assert EXDOC.G2 in list(d2.contexts())
    assert EXDOC.G3 in list(d2.contexts())
    assert (EXDOC.Chris, RDF.type, EX.Person) in d2.graph(EXDOC.G3)

    assert isomorphic(d1, d2)
