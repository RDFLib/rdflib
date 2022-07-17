from test.data import context0, context1

import pytest

from rdflib import OWL, RDFS, BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.extras.infixowl import (
    ACE_NS,
    BooleanClass,
    Class,
    Individual,
    Property,
    max,
)
from rdflib.util import first

EXNS = Namespace("http://example.org/vocab/")
PZNS = Namespace(
    "http://www.co-ode.org/ontologies/pizza/2005/10/18/classified/pizza.owl#"
)


@pytest.fixture(scope="function")
def graph():
    g = Graph(identifier=EXNS.context0)
    g.bind("ex", EXNS)
    Individual.factoryGraph = g

    yield g

    del g


def test_class_instantiation(graph):

    name = EXNS.Man
    assert isinstance(name, URIRef)

    nounannotations = ("Man", "Men")
    nameannotation = Literal("Man")

    c = Class(
        identifier=name,
        subClassOf=None,
        equivalentClass=None,
        disjointWith=None,
        complementOf=None,
        graph=graph,
        skipOWLClassMembership=False,
        comment=Literal("This is a Man"),
        nounAnnotations=nounannotations,
        nameAnnotation=nameannotation,
        nameIsLabel=True,
    )
    c.serialize(graph)

    res = graph.serialize(format="ttl")

    assert res == (
        "@prefix ace: <http://attempto.ifi.uzh.ch/ace_lexicon#> .\n"
        "@prefix ex: <http://example.org/vocab/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "\n"
        "ace:CN_pl a owl:AnnotationProperty .\n"
        "\n"
        "ace:CN_sg a owl:AnnotationProperty .\n"
        "\n"
        "ace:PN_sg a owl:AnnotationProperty .\n"
        "\n"
        "ace:TV_pl a owl:AnnotationProperty .\n"
        "\n"
        "ace:TV_sg a owl:AnnotationProperty .\n"
        "\n"
        "ace:TV_vbg a owl:AnnotationProperty .\n"
        "\n"
        "ex:Man a owl:Class ;\n"
        '    rdfs:label "Man" ;\n'
        '    ace:CN_pl "Men" ;\n'
        '    ace:CN_sg "Man" ;\n'
        '    ace:PN_sg "Man" ;\n'
        '    rdfs:comment "This is a Man" .\n'
        "\n"
    )


def test_class_hash():
    b = Class(OWL.Restriction)
    c = Class(OWL.Restriction)
    assert len(set([b, c])) == 1


def test_class_and(graph):
    # Construct an anonymous class description consisting of the
    # intersection of this class and 'other' and return it

    # Chaining 3 intersections

    female = Class(EXNS.Female, graph=graph)
    human = Class(EXNS.Human, graph=graph)
    youngperson = Class(EXNS.YoungPerson, graph=graph)
    youngwoman = female & human & youngperson

    assert str(youngwoman) == "ex:YoungPerson THAT ( ex:Female AND ex:Human )"

    assert isinstance(youngwoman, BooleanClass) is True
    assert isinstance(youngwoman.identifier, BNode) is True


def test_class_getparents(graph):
    # computed attributes that returns a generator over taxonomic 'parents'
    # by disjunction, conjunction, and subsumption

    dad = Class(EXNS.Dad)

    brother = Class(EXNS.Brother)
    sister = Class(EXNS.Sister)
    sibling = brother | sister
    sibling.identifier = EXNS.Sibling

    assert len(sibling) == 2

    assert str(sibling) == "( ex:Brother OR ex:Sister )"

    assert (
        str(first(brother.parents))
        == "Class: ex:Sibling EquivalentTo: ( ex:Brother OR ex:Sister )"
    )

    parent = Class(EXNS.Parent)

    male = Class(EXNS.Male)
    father = parent & male
    father.identifier = EXNS.Father
    father.equivalentClass = [dad]

    female = Class(EXNS.Female)
    mother = parent & female
    mother.identifier = EXNS.Mother

    assert len(list(father.parents)) == 3
    assert (
        str(list(father.parents))
        == "[Class: ex:Dad , Class: ex:Parent , Class: ex:Male ]"
    )

    # Restriction(EXNS.isChild, graph=g, allValuesFrom=EXNS.Sibling)

    Property(EXNS.hasParent, graph=graph) << max >> Literal(1)

    assert male.isPrimitive() is True

    assert brother.isPrimitive() is True

    assert sibling.isPrimitive() is False

    assert list(sibling.subSumpteeIds()) == []

    assert str(brother.__repr__(full=True)) == "Class: ex:Brother "

    assert graph.serialize(format="ttl") == (
        "@prefix ex: <http://example.org/vocab/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "\n"
        "ex:Father a owl:Class ;\n"
        "    owl:equivalentClass ex:Dad ;\n"
        "    owl:intersectionOf ( ex:Parent ex:Male ) .\n"
        "\n"
        "ex:Mother a owl:Class ;\n"
        "    owl:intersectionOf ( ex:Parent ex:Female ) .\n"
        "\n"
        "ex:Sibling a owl:Class ;\n"
        "    owl:unionOf ( ex:Brother ex:Sister ) .\n"
        "\n"
        "ex:Brother a owl:Class .\n"
        "\n"
        "ex:Dad a owl:Class .\n"
        "\n"
        "ex:Female a owl:Class .\n"
        "\n"
        "ex:Male a owl:Class .\n"
        "\n"
        "ex:Sister a owl:Class .\n"
        "\n"
        "ex:hasParent a owl:ObjectProperty .\n"
        "\n"
        "ex:Parent a owl:Class .\n"
        "\n"
        "[] a owl:Restriction ;\n"
        "    owl:maxCardinality 1 ;\n"
        "    owl:onProperty ex:hasParent .\n"
        "\n"
    )


def test_class_serialize(graph):

    father = Class(EXNS.Father)
    sister = Class(EXNS.Sister)
    parent = Class(EXNS.Parent)
    male = Class(EXNS.Male)

    nounannotations = ("Man", "Men")
    nameannotation = Literal("Man")

    owlc = Class(
        EXNS.test,
        subClassOf=[parent],
        equivalentClass=[male],
        disjointWith=[father],
        complementOf=sister,
        graph=graph,
        skipOWLClassMembership=False,
        comment=Literal("This is a Man"),
        nounAnnotations=nounannotations,
        nameAnnotation=nameannotation,
        nameIsLabel=True,
    )

    g1 = Graph(identifier=context1)

    owlc.serialize(g1)

    assert len(g1) > 0

    owlc.setupNounAnnotations(None)

    owlc.setupNounAnnotations(["Man", "Men"])

    owlc.extent = None

    owlc.extent = [context1]

    assert list(owlc.extent) == [context1]

    pred = RDFS.comment

    pred = ACE_NS.CN_pl

    tgt = (EXNS.test, pred, Literal("Men"))
    assert tgt in owlc.graph

    assert list(owlc._get_annotation(pred)) == [
        Literal("Men"),
        Literal("['Man', 'Men']"),
    ]

    assert owlc.extentQuery == (
        Variable("CLASS"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.org/vocab/test"),
    )

    assert str(owlc.__invert__()) == "Some Class DisjointWith ( NOT ex:Sister )\n"

    assert owlc.__repr__(full=True) == (
        "Class: ex:test \n"
        "    ## A Defined Class (Man) ##\n"
        "    This is a Man\n"
        "    SubClassOf: ex:Parent . \n"
        "    EquivalentTo: ex:Male . \n"
        "    DisjointWith ex:Father\n"
        "                 ex:Sister\n"
    )

    assert owlc.complementOf == sister

    owlc.complementOf = None

    owlc.complementOf = father

    with pytest.raises(Exception, match="2"):
        assert owlc.complementOf == sister


def test_class_nameislabel():
    g = Graph(identifier=context0)
    g.bind("ex", EXNS)

    Individual.factoryGraph = g
    nameannotation = Literal("Man")

    owlc = Class(
        EXNS.test,
        graph=g,
        comment=Literal("This is a Man"),
        nameAnnotation=nameannotation,
        nameIsLabel=True,
    )

    assert list(owlc.annotation) == [Literal("Man")]

    assert g.serialize(format="ttl") == (
        "@prefix ace: <http://attempto.ifi.uzh.ch/ace_lexicon#> .\n"
        "@prefix ex: <http://example.org/vocab/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "\n"
        "ace:CN_pl a owl:AnnotationProperty .\n"
        "\n"
        "ace:CN_sg a owl:AnnotationProperty .\n"
        "\n"
        "ace:PN_sg a owl:AnnotationProperty .\n"
        "\n"
        "ace:TV_pl a owl:AnnotationProperty .\n"
        "\n"
        "ace:TV_sg a owl:AnnotationProperty .\n"
        "\n"
        "ace:TV_vbg a owl:AnnotationProperty .\n"
        "\n"
        "ex:test a owl:Class ;\n"
        '    rdfs:label "Man" ;\n'
        '    ace:PN_sg "Man" ;\n'
        '    rdfs:comment "This is a Man" .\n'
        "\n"
    )


def test_class_nameisnotlabel():
    g = Graph(identifier=context0)
    g.bind("ex", EXNS)

    Individual.factoryGraph = g
    nameannotation = Literal("Man")

    owlc = Class(
        EXNS.test,
        graph=g,
        comment=Literal("This is a Man"),
        nameAnnotation=nameannotation,
    )

    assert list(owlc.annotation) == []

    assert g.serialize(format="ttl") == (
        "@prefix ace: <http://attempto.ifi.uzh.ch/ace_lexicon#> .\n"
        "@prefix ex: <http://example.org/vocab/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "\n"
        "ace:CN_pl a owl:AnnotationProperty .\n"
        "\n"
        "ace:CN_sg a owl:AnnotationProperty .\n"
        "\n"
        "ace:PN_sg a owl:AnnotationProperty .\n"
        "\n"
        "ace:TV_pl a owl:AnnotationProperty .\n"
        "\n"
        "ace:TV_sg a owl:AnnotationProperty .\n"
        "\n"
        "ace:TV_vbg a owl:AnnotationProperty .\n"
        "\n"
        "ex:test a owl:Class ;\n"
        '    ace:PN_sg "Man" ;\n'
        '    rdfs:comment "This is a Man" .\n'
        "\n"
    )

    assert (EXNS.test, RDFS.label, nameannotation) not in g
