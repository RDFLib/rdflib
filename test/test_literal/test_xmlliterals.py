import logging
import textwrap
import xml.dom.minidom
from typing import Callable, Sequence

import pytest

import rdflib
from rdflib import RDF, Literal


def testPythonRoundtrip():
    l1 = Literal("<msg>hello</msg>", datatype=RDF.XMLLiteral)
    assert l1.value is not None, "xml must have been parsed"
    assert l1.datatype == RDF.XMLLiteral, "literal must have right datatype"

    l2 = Literal("<msg>good morning</msg>", datatype=RDF.XMLLiteral)
    assert l2.value is not None, "xml must have been parsed"
    assert not l1.eq(l2), "literals must NOT be equal"

    l3 = Literal(l1.value)
    assert l1.eq(l3), "roundtripped literals must be equal"
    assert l3.datatype == RDF.XMLLiteral, "literal must have right datatype"

    l4 = Literal("<msg >hello</msg>", datatype=RDF.XMLLiteral)
    assert l1 == l4
    assert l1.eq(l4)

    rdflib.NORMALIZE_LITERALS = False
    try:
        l4 = Literal("<msg >hello</msg>", datatype=RDF.XMLLiteral)
        assert l1 != l4
        assert l1.eq(l4)
    finally:
        rdflib.NORMALIZE_LITERALS = True


def testRDFXMLParse():
    rdfxml = """\
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
>

<rdf:Description rdf:about="http://example.org/">
    <dc:description rdf:parseType="Literal">
        <p xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"></p>
    </dc:description>
</rdf:Description>

</rdf:RDF>"""

    g = rdflib.Graph()
    g.parse(data=rdfxml, format="xml")
    l1 = list(g)[0][2]
    assert l1.datatype == RDF.XMLLiteral


def graph():
    g = rdflib.Graph()
    g.add(
        (
            rdflib.URIRef("http://example.org/a"),
            rdflib.URIRef("http://example.org/p"),
            rdflib.Literal("<msg>hei</hei>", datatype=RDF.XMLLiteral),
        )
    )
    return g


def roundtrip(fmt):
    g1 = graph()
    l1 = list(g1)[0][2]
    g2 = rdflib.Graph()
    g2.parse(data=g1.serialize(format=fmt), format=fmt)
    l2 = list(g2)[0][2]
    assert l1.eq(l2)


def testRoundtrip():
    roundtrip("xml")
    roundtrip("n3")
    roundtrip("nt")


def testHTML():

    l1 = Literal("<msg>hello</msg>", datatype=RDF.XMLLiteral)
    assert l1.value is not None, "xml must have been parsed"
    assert l1.datatype == RDF.XMLLiteral, "literal must have right datatype"

    l2 = Literal("<msg>hello</msg>", datatype=RDF.HTML)
    assert l2.value is not None, "xml must have been parsed"
    assert l2.datatype == RDF.HTML, "literal must have right datatype"

    assert l1 != l2
    assert not l1.eq(l2)


@pytest.mark.parametrize(
    ("values", "equals"),
    [
        pytest.param(
            [
                lambda: Literal("<something />", datatype=RDF.XMLLiteral),
                lambda: Literal("<something/>", datatype=RDF.XMLLiteral),
            ],
            True,
        ),
        pytest.param(
            [
                lambda: Literal(
                    xml.dom.minidom.parseString(
                        textwrap.dedent(
                            """\
                    <!DOCTYPE example>
                    <something/>
                    """
                        )
                    ),
                    datatype=RDF.XMLLiteral,
                ),
                lambda: Literal(
                    xml.dom.minidom.parseString(
                        textwrap.dedent(
                            """\
                    <!DOCTYPE example>
                    <something />
                    """
                        )
                    ),
                    datatype=RDF.XMLLiteral,
                ),
            ],
            True,
        ),
    ],
)
def test_eq(values: Sequence[Callable[[], Literal]], equals: bool) -> None:
    first_value = values[0]()
    logging.debug("first_value = \n%r", first_value)
    for value in values[1:]:
        current_value = value()
        logging.debug("current_value = \n%r", current_value)
        if equals:
            assert first_value.eq(
                current_value
            ), f"{current_value} must be equal to {first_value}"
        else:
            assert not first_value.eq(
                current_value
            ), f"{current_value} must be not be equal to {first_value}"
