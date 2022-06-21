from test.data import TEST_DATA_DIR, bob, michel, tarek

import pytest

from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.extras.infixowl import (
    AllClasses,
    AllProperties,
    BooleanClass,
    Class,
    ClassNamespaceFactory,
    CommonNSBindings,
    ComponentTerms,
    DeepClassClear,
    EnumeratedClass,
    GetIdentifiedClasses,
    Individual,
    Infix,
    MalformedClass,
    Property,
    Restriction,
    classOrTerm,
    exactly,
    generateQName,
    max,
    min,
    only,
    some,
    value,
)

EXNS = Namespace("http://example.org/vocab/")
PZNS = Namespace(
    "http://www.co-ode.org/ontologies/pizza/2005/10/18/classified/pizza.owl#"
)


@pytest.fixture(scope="function")
def graph():
    g = Graph()
    g.bind("ex", EXNS)
    Individual.factoryGraph = g

    yield g

    del g


def test_infix_operators_dunders():
    def fn(other, arg=""):
        return None

    i = Infix(fn)

    assert i.__ror__("foo") is not None
    assert i.__or__("foo") is None
    assert i.__rlshift__("foo") is not None
    assert i.__rshift__("foo") is None
    assert i.__rmatmul__("foo") is not None
    assert i.__matmul__("foo") is None
    assert i.__call__("foo", "baz") is None


@pytest.mark.xfail(reason="__or__/__ror__ operators broken for years")
def test_or_ror_operators(graph):

    with pytest.raises(Exception, match="Only URIRefs or Paths can be in paths!"):
        EXNS.hasParent | some | Class(EXNS.Physician, graph=graph)

    EXNS.hasParent | some | Class(EXNS.Physician, graph=graph)


@pytest.mark.xfail(
    reason="__lshift__/__rlshift__ operators expected to break when RDF Star work is merged in autumn 2022"
)
def test_lshift_rlshift_infix_operators(graph):

    res = EXNS.hasParent << some >> Class(EXNS.Physician, graph=graph)

    assert str(res) == "( ex:hasParent SOME ex:Physician )"


def test_matmul_infix_operators(graph):

    res = EXNS.hasParent @ some @ Class(EXNS.Physician, graph=graph)

    assert str(res) == "( ex:hasParent SOME ex:Physician )"


def test_common_ns_bindings():
    graph = Graph(bind_namespaces=None)
    exns1 = Namespace("http://example.com")

    CommonNSBindings(graph, additionalNS={"ex1": exns1})

    bound_namespaces = list(graph.namespace_manager.namespaces())

    assert ("ex1", URIRef(str(exns1))) in bound_namespaces
    assert ("owl", URIRef(str(OWL))) in bound_namespaces


def test_classorterm():
    term = URIRef("http://example.org/vocab/D")

    assert classOrTerm(Class(EXNS.D)) == term
    assert classOrTerm(term) == term


def test_generateqname(graph):

    assert (
        generateQName(graph, URIRef("http://example.org/vocab/ontology"))
        == "ex:ontology"
    )


def test_getidentifiedclasses(graph):

    graph.bind("ex", PZNS)
    graph.parse(TEST_DATA_DIR / "owl" / "pizza.owl", format="xml")

    assert len(list(GetIdentifiedClasses(graph))) == 97


def test_allclasses(graph):

    graph.bind("ex", PZNS)
    graph.parse(TEST_DATA_DIR / "owl" / "pizza.owl", format="xml")

    for c in AllClasses(graph):
        assert isinstance(c, Class)


def test_check_allclasses(graph):

    graph.bind("ex", PZNS)

    graph.add((tarek, RDF.type, OWL.Class))
    graph.add((michel, RDF.type, OWL.Class))
    graph.add((bob, RDF.type, OWL.Class))

    assert set(graph.subjects(predicate=RDF.type, object=OWL.Class)) == {
        URIRef("urn:example:bob"),
        URIRef("urn:example:michel"),
        URIRef("urn:example:tarek"),
    }


def test_check_allproperties(graph):

    graph.bind("ex", PZNS)
    graph.parse(TEST_DATA_DIR / "owl" / "pizza.owl", format="xml")

    for p in AllProperties(graph):
        assert isinstance(p, Property)


EXCL = ClassNamespaceFactory(EXNS)


def test_classnamespacefactory():

    leg = EXCL.Leg

    x = EXCL.__getitem__(leg.identifier)

    assert x is not None


def test_componentterms(graph):

    graph.bind("ex", PZNS)
    graph.parse(TEST_DATA_DIR / "owl" / "pizza.owl", format="xml")

    owlcls = list(AllClasses(graph))[-1]

    assert isinstance(owlcls, Class)

    for c in ComponentTerms(owlcls):
        assert isinstance(c, Class)


def test_componentterms_extended(graph):

    isPartOf = Property(EXNS.isPartOf)  # noqa: N806
    graph.add((isPartOf.identifier, RDF.type, OWL.TransitiveProperty))

    hasLocation = Property(EXNS.hasLocation, subPropertyOf=[isPartOf])  # noqa: N806
    graph.add((hasLocation.identifier, RDFS.subPropertyOf, isPartOf.identifier))

    leg = EXCL.Leg
    knee = EXCL.Knee
    joint = EXCL.Joint
    kneeJoint = EXCL.KneeJoint  # noqa: N806
    legStructure = EXCL.LegStructure  # noqa: N806

    kneeJoint.equivalentClass = [joint & (isPartOf @ some @ knee)]

    structure = EXCL.Structure

    legStructure.equivalentClass = [structure & (isPartOf @ some @ leg)]

    structure += leg
    structure += joint

    locatedInLeg = hasLocation @ some @ leg  # noqa: N806
    locatedInLeg += knee  # noqa: N806

    for c in ComponentTerms(knee):
        assert isinstance(c, Class)

    for c in ComponentTerms(legStructure):
        assert isinstance(c, Class)


def test_raise_malformedclasserror():
    e = MalformedClass("Malformed owl:Restriction")

    assert str(repr(e)) == "Malformed owl:Restriction"

    with pytest.raises(MalformedClass, match="Malformed owl:Restriction"):
        raise e


def test_owlrdfproxylist(graph):

    ogbujiBros = EnumeratedClass(  # noqa: N806
        EXNS.ogbujiBros, members=[EXNS.chime, EXNS.uche, EXNS.ejike]
    )

    ogbujiSiblings = EnumeratedClass(  # noqa: N806
        EXNS.ogbujiBros, members=[EXNS.uche, EXNS.chime, EXNS.ejike]
    )

    assert ogbujiBros == ogbujiSiblings

    assert EXNS.chime in ogbujiBros

    fred = EXNS.fred

    bert = EXNS.bert

    assert fred not in ogbujiBros

    ogbujiBros.append(fred)

    ogbujiBros += bert

    assert ogbujiBros[1] == EXNS.uche

    assert len(ogbujiBros) == 5

    del ogbujiBros[4]

    assert len(ogbujiBros) == 4

    ogbujiBros[4] = fred

    assert len(ogbujiBros) == 5

    male = Class(EXNS.Male, graph=graph)
    female = Class(EXNS.Female, graph=graph)
    human = Class(EXNS.Human, graph=graph)

    youngPerson = Class(EXNS.YoungPerson, graph=graph)  # noqa: N806

    youngWoman = female & human & youngPerson  # noqa: N806
    assert isinstance(youngWoman, BooleanClass)

    res = ogbujiBros.__eq__(youngWoman)
    assert res is False

    youngMan = male & human & youngPerson  # noqa: N806

    res = youngMan.__eq__(youngWoman)
    assert res is False


def test_deepclassclear(graph):

    classB = Class(EXNS.B)  # noqa: N806
    classC = Class(EXNS.C)  # noqa: N806
    classD = Class(EXNS.D)  # noqa: N806
    classE = Class(EXNS.E)  # noqa: N806
    classF = Class(EXNS.F)  # noqa: N806

    anonClass = EXNS.someProp << some >> classD  # noqa: N806

    assert str(anonClass) == "( ex:someProp SOME ex:D )"
    assert str(classF) == "Class: ex:F "

    classF += anonClass  # noqa: N806
    assert str(list(anonClass.subClassOf)) == "[Class: ex:F ]"

    classA = classE | classF | anonClass  # noqa: N806
    classG = Class(EXNS.G, complementOf=classA)  # noqa: N806
    classB += classA
    classA.equivalentClass = [Class()]
    classA.complementOf = classG
    classB.subClassOf = [EXNS.someProp << some >> classC]

    assert str(classA) == "( ex:E OR ex:F OR ( ex:someProp SOME ex:D ) )"

    DeepClassClear(classA)
    assert str(classA) == "(  )"

    assert list(anonClass.subClassOf) == []

    assert str(classB) == "Class: ex:B SubClassOf: ( ex:someProp SOME ex:C )"

    otherClass = classD | anonClass  # noqa: N806

    assert str(otherClass) == "( ex:D OR ( ex:someProp SOME ex:D ) )"

    DeepClassClear(otherClass)
    assert str(otherClass) == "(  )"

    otherClass.delete()
    assert list(graph.triples((otherClass.identifier, None, None))) == []


def test_booleanclassextenthelper(graph):

    fire = Class(EXNS.Fire)
    water = Class(EXNS.Water)

    tc1 = BooleanClass(members=[fire, water])
    assert str(tc1) == "( ex:Fire AND ex:Water )"

    tc2 = BooleanClass(operator=OWL.unionOf, members=[fire, water])
    assert str(tc2) == "( ex:Fire OR ex:Water )"


def test_changeoperator(graph):
    # Converts a unionOf / intersectionOf class expression into one
    # that instead uses the given operator

    fire = Class(EXNS.Fire)
    water = Class(EXNS.Water)

    testclass = BooleanClass(members=[fire, water])

    assert str(testclass) == "( ex:Fire AND ex:Water )"

    testclass.changeOperator(OWL.unionOf)
    assert repr(testclass) == "( ex:Fire OR ex:Water )"

    try:
        testclass.changeOperator(OWL.unionOf)
    except Exception as e:
        assert str(e) == "The new operator is already being used!"


def test_cardinality_zero(graph):

    prop = Property(EXNS.someProp, baseType=OWL.DatatypeProperty)
    r = Restriction(
        prop, graph=graph, cardinality=Literal(0, datatype=XSD.nonNegativeInteger)
    )

    assert str(r) == "( ex:someProp EQUALS 0 )"


def test_textual_infix_operators(graph):

    isPartOf = Property(EXNS.isPartOf)  # noqa: N806
    graph.add((isPartOf.identifier, RDF.type, OWL.TransitiveProperty))

    knee = EXCL.Knee

    x = isPartOf @ some @ knee

    assert x is not None

    y = isPartOf @ only @ knee

    assert y is not None

    y = isPartOf @ exactly @ Literal("1", datatype=XSD.integer)

    y = isPartOf @ min @ Literal("1", datatype=XSD.integer)

    y = isPartOf @ max @ Literal("1", datatype=XSD.integer)

    y = isPartOf @ value @ Literal("1", datatype=XSD.integer)
