import pytest

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


def test_context(graph):

    # Now we have an empty graph, we can construct OWL classes in it
    # using the Python classes defined in this module

    a = Class(EXNS.Opera, graph=graph)

    # Now we can assert rdfs:subClassOf and owl:equivalentClass relationships
    # (in the underlying graph) with other classes using the 'subClassOf'
    # and 'equivalentClass' descriptors which can be set to a list
    # of objects for the corresponding predicates.

    a.subClassOf = [EXNS.MusicalWork]

    # We can then access the rdfs:subClassOf relationships

    assert str(list(a.subClassOf)) == "[Class: ex:MusicalWork ]"

    # This can also be used against already populated graphs:

    owlgraph = Graph().parse(str(OWL))

    assert (
        str(list(Class(OWL.Class, graph=owlgraph).subClassOf)) == "[Class: rdfs:Class ]"
    )

    # Operators are also available. For instance we can add ex:Opera to the extension
    # of the ex:CreativeWork class via the '+=' operator

    assert str(a) == "Class: ex:Opera SubClassOf: ex:MusicalWork"

    b = Class(EXNS.CreativeWork, graph=graph)

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

    c = a | b | Class(EXNS.Work, graph=graph)

    assert str(c) == "( ex:Opera OR ex:CreativeWork OR ex:Work )"

    # Boolean class expressions can also be operated as lists (using python list
    # operators)

    del c[c.index(Class(EXNS.Work, graph=graph))]

    assert str(c) == "( ex:Opera OR ex:CreativeWork )"

    # The '&' operator can be used to construct class intersection:

    woman = Class(EXNS.Female, graph=graph) & Class(EXNS.Human, graph=graph)
    woman.identifier = EXNS.Woman

    assert str(woman) == "( ex:Female AND ex:Human )"

    assert len(woman) == 2

    # Enumerated classes can also be manipulated

    contlist = [Class(EXNS.Africa, graph=graph), Class(EXNS.NorthAmerica, graph=graph)]

    ec = EnumeratedClass(members=contlist, graph=graph)

    assert str(ec) == "{ ex:Africa ex:NorthAmerica }"

    # owl:Restrictions can also be instantiated:

    r1 = Restriction(EXNS.hasParent, graph=graph, allValuesFrom=EXNS.Human)

    assert str(r1) == "( ex:hasParent ONLY ex:Human )"

    # Restrictions can also be created using Manchester OWL syntax in 'colloquial'
    # Python
    r2 = EXNS.hasParent @ some @ Class(EXNS.Physician, graph=graph)

    assert str(r2) == "( ex:hasParent SOME ex:Physician )"

    p = Property(EXNS.hasParent, graph=graph) @ max @ Literal(1)

    assert str(p) == "( ex:hasParent MAX 1 )"
