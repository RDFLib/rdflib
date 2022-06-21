from test.data import context0

from rdflib import OWL, Graph, Literal, Namespace
from rdflib.extras.infixowl import (
    Class,
    EnumeratedClass,
    Individual,
    Property,
    Restriction,
    max,
    some,
)

EXNS = Namespace("http://example.org/vocab/")


def test_lshift_rlshift_delimiters():
    g = Graph(identifier=context0)
    g.bind("ex", EXNS)

    Individual.factoryGraph = g

    classB = Class(EXNS.B)  # noqa: N806
    classC = Class(EXNS.C)  # noqa: N806
    classD = Class(EXNS.D)  # noqa: N806
    classE = Class(EXNS.E)  # noqa: N806
    classF = Class(EXNS.F)  # noqa: N806

    anonClass = EXNS.someProp << some >> classD  # noqa: N806
    classF += anonClass
    assert str(list(anonClass.subClassOf)) == "[Class: ex:F ]"

    classA = classE | classF | anonClass  # noqa: N806
    classB += classA
    classA.equivalentClass = [Class()]
    classB.subClassOf = [EXNS.someProp << some >> classC]
    assert str(classA) == "( ex:E OR ex:F OR ( ex:someProp SOME ex:D ) )"


def test_matmul_rmatmul_delimiters():
    g = Graph(identifier=context0)
    g.bind("ex", EXNS)

    Individual.factoryGraph = g

    classB = Class(EXNS.B)  # noqa: N806
    classC = Class(EXNS.C)  # noqa: N806
    classD = Class(EXNS.D)  # noqa: N806
    classE = Class(EXNS.E)  # noqa: N806
    classF = Class(EXNS.F)  # noqa: N806

    anonClass = EXNS.someProp @ some @ classD  # noqa: N806
    classF += anonClass
    assert str(list(anonClass.subClassOf)) == "[Class: ex:F ]"

    classA = classE | classF | anonClass  # noqa: N806
    classB += classA
    classA.equivalentClass = [Class()]
    classB.subClassOf = [EXNS.someProp @ some @ classC]
    assert str(classA) == "( ex:E OR ex:F OR ( ex:someProp SOME ex:D ) )"


def test_infixowl_serialization():
    # g1 = Graph()
    # g2 = Graph()

    # g1.bind("ex", EXNS)
    # g2.bind("ex", EXNS)

    prop = Property(EXNS.someProp, baseType=OWL.DatatypeProperty)

    restr1 = prop << some >> (Class(EXNS.Foo))

    assert str(restr1) == "( ex:someProp SOME ex:Foo )"

    assert (
        str(list(Property(EXNS.someProp, baseType=None).type))
        == "[rdflib.term.URIRef('http://www.w3.org/2002/07/owl#DatatypeProperty')]"
    )


def test_infix_owl_example1():

    g = Graph(identifier=context0)
    g.bind("ex", EXNS)

    Individual.factoryGraph = g
    classD = Class(EXNS.D)  # noqa: N806
    anonClass = EXNS.someProp << some >> classD  # noqa: N806

    assert str(anonClass) == "( ex:someProp SOME ex:D )"

    a = Class(EXNS.Opera, graph=g)

    # Now we can assert rdfs:subClassOf and owl:equivalentClass relationships
    # (in the underlying graph) with other classes using the 'subClassOf'
    # and 'equivalentClass' descriptors which can be set to a list
    # of objects for the corresponding predicates.

    a.subClassOf = [EXNS.MusicalWork]

    # We can then access the rdfs:subClassOf relationships

    assert str(list(a.subClassOf)) == "[Class: ex:MusicalWork ]"
    # [Class: ex:MusicalWork ]

    # This can also be used against already populated graphs:

    owlgraph = Graph().parse(str(OWL))
    owlgraph.bind("owl", OWL, override=False)

    assert (
        str(list(Class(OWL.Class, graph=owlgraph).subClassOf)) == "[Class: rdfs:Class ]"
    )

    # Operators are also available. For instance we can add ex:Opera to the extension
    # of the ex:CreativeWork class via the '+=' operator

    assert str(a) == "Class: ex:Opera SubClassOf: ex:MusicalWork"
    b = Class(EXNS.CreativeWork, graph=g)
    b += a
    assert (
        str(sorted(a.subClassOf, key=lambda c: c.identifier))
        == "[Class: ex:CreativeWork , Class: ex:MusicalWork ]"
    )

    # And we can then remove it from the extension as well

    b -= a
    assert str(a) == "Class: ex:Opera SubClassOf: ex:MusicalWork"

    # Boolean class constructions can also  be created with Python operators.
    # For example, The | operator can be used to construct a class consisting of a
    # owl:unionOf the operands:

    c = a | b | Class(EXNS.Work, graph=g)
    assert str(c) == "( ex:Opera OR ex:CreativeWork OR ex:Work )"

    # Boolean class expressions can also be operated as lists (using python list
    # operators)

    del c[c.index(Class(EXNS.Work, graph=g))]
    assert str(c) == "( ex:Opera OR ex:CreativeWork )"

    # The '&' operator can be used to construct class intersection:

    woman = Class(EXNS.Female, graph=g) & Class(EXNS.Human, graph=g)
    woman.identifier = EXNS.Woman
    assert str(woman) == "( ex:Female AND ex:Human )"
    assert len(woman) == 2

    # Enumerated classes can also be manipulated

    contlist = [Class(EXNS.Africa, graph=g), Class(EXNS.NorthAmerica, graph=g)]
    assert (
        str(EnumeratedClass(members=contlist, graph=g))
        == "{ ex:Africa ex:NorthAmerica }"
    )

    # owl:Restrictions can also be instantiated:

    assert (
        str(Restriction(EXNS.hasParent, graph=g, allValuesFrom=EXNS.Human))
        == "( ex:hasParent ONLY ex:Human )"
    )

    # Restrictions can also be created using Manchester OWL syntax in 'colloquial'
    # Python
    assert (
        str(EXNS.hasParent << some >> Class(EXNS.Physician, graph=g))
        == "( ex:hasParent SOME ex:Physician )"
    )

    Property(EXNS.hasParent, graph=g) << max >> Literal(1)
    assert (
        str(Property(EXNS.hasParent, graph=g) << max >> Literal(1))
        == "( ex:hasParent MAX 1 )"
    )
