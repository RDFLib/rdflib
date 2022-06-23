import pytest

from rdflib import OWL, XSD, Graph, Literal, Namespace, URIRef
from rdflib.extras.infixowl import Property

EXNS = Namespace("http://example.org/vocab/")
PZNS = Namespace(
    "http://www.co-ode.org/ontologies/pizza/2005/10/18/classified/pizza.owl#"
)


@pytest.fixture(scope="function")
def graph():
    g = Graph(identifier=EXNS.context0)
    g.bind("ex", EXNS)

    yield g

    del g


def test_property(graph):

    comment = Literal("This is a woman")
    verbannotations = ("woman", "Women", "Womens")
    nameannotation = Literal("Woman")
    iswoman = Property(
        identifier=EXNS.iswoman,
        graph=graph,
        baseType=OWL.DatatypeProperty,
        subPropertyOf=None,
        domain=None,
        range=None,
        inverseOf=None,
        otherType=None,
        equivalentProperty=None,
        comment=comment,
        verbAnnotations=verbannotations,
        nameAnnotation=nameannotation,
        nameIsLabel=True,
    )

    comment = Literal("This is a man")
    verbannotations = ("Man", "Men", "Mens")
    nameannotation = Literal("Man")

    isman = Property(
        identifier=EXNS.isman,
        graph=graph,
        subPropertyOf=[EXNS.nosuchproperty],
        domain=EXNS.Parent,
        range=XSD.integer,
        inverseOf=iswoman,
        otherType=None,
        equivalentProperty=[EXNS.nosuchequivalentproperty],
        comment=comment,
        verbAnnotations=verbannotations,
        nameAnnotation=nameannotation,
        nameIsLabel=True,
    )

    isman.setupVerbAnnotations(None)

    assert str(repr(isman)) == (
        "ObjectProperty( ex:isman annotation(This is a man)\n"
        "  inverseOf( DatatypeProperty( ex:iswoman This is a woman\n"
        ") )\n"
        "   super( ex:nosuchproperty )\n"
        "   domain( ex:Parent )\n"
        "   range( Class: xsd:integer  )\n"
        ")"
    )

    assert str(repr(iswoman)) == "DatatypeProperty( ex:iswoman This is a woman\n)"

    isman.extent = None

    isman.extent = [(EXNS.aclass, EXNS.somextent)]

    assert list(isman.extent) == [
        (
            URIRef("http://example.org/vocab/aclass"),
            URIRef("http://example.org/vocab/isman"),
            URIRef("http://example.org/vocab/somextent"),
        )
    ]

    sg = Graph()

    isman.serialize(sg)

    assert len(sg) > 0

    iswoman.domain = None

    iswoman.domain = EXNS.Parent

    iswoman.domain = [EXNS.Parent, EXNS.Mother]

    iswoman.range = None

    iswoman.range = XSD.decimal

    iswoman.range = [XSD.decimal, XSD.float]

    assert list(isman.extent) == [
        (
            URIRef("http://example.org/vocab/aclass"),
            URIRef("http://example.org/vocab/isman"),
            URIRef("http://example.org/vocab/somextent"),
        )
    ]

    # TODO, this deletes but does replace?
    isman.replace(EXNS.someotherextent)

    assert list(isman.extent) == []

    assert sg.serialize(format="ttl") == (
        "@prefix ns1: <http://attempto.ifi.uzh.ch/ace_lexicon#> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "\n"
        "<http://example.org/vocab/isman> a owl:ObjectProperty ;\n"
        '    rdfs:label "Man" ;\n'
        '    ns1:PN_sg "Man" ;\n'
        '    ns1:TV_pl "Men" ;\n'
        '    ns1:TV_sg "Man" ;\n'
        '    ns1:TV_vbg "Mens" ;\n'
        '    rdfs:comment "This is a man" ;\n'
        "    rdfs:domain <http://example.org/vocab/Parent> ;\n"
        "    rdfs:range xsd:integer ;\n"
        "    rdfs:subPropertyOf <http://example.org/vocab/nosuchproperty> ;\n"
        "    owl:inverseOf <http://example.org/vocab/iswoman> .\n"
        "\n"
        "<http://example.org/vocab/Parent> a owl:Class .\n"
        "\n"
        "<http://example.org/vocab/iswoman> a owl:DatatypeProperty ;\n"
        '    rdfs:label "Woman" ;\n'
        '    ns1:PN_sg "Woman" ;\n'
        '    ns1:TV_pl "Women" ;\n'
        '    ns1:TV_sg "woman" ;\n'
        '    ns1:TV_vbg "Womens" ;\n'
        '    rdfs:comment "This is a woman" .\n'
        "\n"
        "xsd:integer a owl:Class .\n"
        "\n"
    )
