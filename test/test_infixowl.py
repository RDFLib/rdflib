from rdflib import BNode, Graph, Literal, Namespace, RDFS, OWL, XSD
from rdflib.namespace import NamespaceManager
from rdflib.util import first
from rdflib.extras.infixowl import (
    BooleanClass,
    Class,
    Collection,
    DeepClassClear,
    Individual,
    some,
    EnumeratedClass,
    Property,
    Restriction,
    max,
)


def test_infix_owl_example1():

    exNs = Namespace("http://example.com/")

    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind("ex", exNs, override=False)
    namespace_manager.bind("owl", OWL, override=False)
    g = Graph()
    g.namespace_manager = namespace_manager

    Individual.factoryGraph = g
    classD = Class(exNs.D)
    anonClass = exNs.someProp << some >> classD

    assert str(anonClass) == "( ex:someProp SOME ex:D )"

    a = Class(exNs.Opera, graph=g)

    # Now we can assert rdfs:subClassOf and owl:equivalentClass relationships
    # (in the underlying graph) with other classes using the 'subClassOf'
    # and 'equivalentClass' descriptors which can be set to a list
    # of objects for the corresponding predicates.

    a.subClassOf = [exNs.MusicalWork]

    # We can then access the rdfs:subClassOf relationships

    assert str(list(a.subClassOf)) == "[Class: ex:MusicalWork ]"
    # [Class: ex:MusicalWork ]

    # This can also be used against already populated graphs:

    owlGraph = Graph().parse(str(OWL))
    namespace_manager.bind("owl", OWL, override=False)
    owlGraph.namespace_manager = namespace_manager
    assert (
        str(list(Class(OWL.Class, graph=owlGraph).subClassOf))
        == "[Class: rdfs:Class ]"
    )

    # Operators are also available. For instance we can add ex:Opera to the extension
    # of the ex:CreativeWork class via the '+=' operator

    assert str(a) == "Class: ex:Opera SubClassOf: ex:MusicalWork"
    b = Class(exNs.CreativeWork, graph=g)
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

    c = a | b | Class(exNs.Work, graph=g)
    assert str(c) == "( ex:Opera OR ex:CreativeWork OR ex:Work )"

    # Boolean class expressions can also be operated as lists (using python list
    # operators)

    del c[c.index(Class(exNs.Work, graph=g))]
    assert str(c) == "( ex:Opera OR ex:CreativeWork )"

    # The '&' operator can be used to construct class intersection:

    woman = Class(exNs.Female, graph=g) & Class(exNs.Human, graph=g)
    woman.identifier = exNs.Woman
    assert str(woman) == "( ex:Female AND ex:Human )"
    assert len(woman) == 2

    # Enumerated classes can also be manipulated

    contList = [Class(exNs.Africa, graph=g), Class(exNs.NorthAmerica, graph=g)]
    assert (
        str(EnumeratedClass(members=contList, graph=g))
        == "{ ex:Africa ex:NorthAmerica }"
    )

    # owl:Restrictions can also be instantiated:

    assert (
        str(Restriction(exNs.hasParent, graph=g, allValuesFrom=exNs.Human))
        == "( ex:hasParent ONLY ex:Human )"
    )

    # Restrictions can also be created using Manchester OWL syntax in 'colloquial'
    # Python
    assert (
        str(exNs.hasParent << some >> Class(exNs.Physician, graph=g))
        == "( ex:hasParent SOME ex:Physician )"
    )

    Property(exNs.hasParent, graph=g) << max >> Literal(1)
    assert (
        str(Property(exNs.hasParent, graph=g) << max >> Literal(1))
        == "( ex:hasParent MAX 1 )"
    )


def test_infixowl_deepclassclear():
    EX = Namespace("http://example.com/")

    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind("ex", EX, override=False)
    namespace_manager.bind("owl", OWL, override=False)

    g = Graph()
    g.namespace_manager = namespace_manager
    Individual.factoryGraph = g

    classB = Class(EX.B)
    classC = Class(EX.C)
    classD = Class(EX.D)
    classE = Class(EX.E)
    classF = Class(EX.F)

    anonClass = EX.someProp << some >> classD

    assert str(anonClass) == "( ex:someProp SOME ex:D )"
    assert str(classF) == "Class: ex:F "

    classF += anonClass

    assert str(list(anonClass.subClassOf)) == "[Class: ex:F ]"

    classA = classE | classF | anonClass
    classB += classA
    classA.equivalentClass = [Class()]
    classB.subClassOf = [EX.someProp << some >> classC]

    assert str(classA) == "( ex:E OR ex:F OR ( ex:someProp SOME ex:D ) )"

    DeepClassClear(classA)
    assert str(classA) == "(  )"

    assert list(anonClass.subClassOf) == []

    assert str(classB) == "Class: ex:B SubClassOf: ( ex:someProp SOME ex:C )"

    otherClass = classD | anonClass

    assert str(otherClass) == "( ex:D OR ( ex:someProp SOME ex:D ) )"

    DeepClassClear(otherClass)
    assert str(otherClass) == "(  )"

    otherClass.delete()
    assert list(g.triples((otherClass.identifier, None, None))) == []


def test_infixowl_individual_type():
    g = Graph()
    b = Individual(OWL.Restriction, g)
    b.type = RDFS.Resource
    assert len(list(b.type)) == 1

    del b.type
    assert len(list(b.type)) == 0


def test_infixowl_individual_label():
    g = Graph()
    b = Individual(OWL.Restriction, g)
    b.label = Literal("boo")

    assert len(list(b.label)) == 3

    del b.label
    assert hasattr(b, "label") is False


def test_infixowl_class_hash():
    b = Class(OWL.Restriction)
    c = Class(OWL.Restriction)
    assert len(set([b, c])) == 1


def test_infixowl_class_and():
    # Construct an anonymous class description consisting of the
    # intersection of this class and 'other' and return it

    exNs = Namespace("http://example.com/")
    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind("ex", exNs, override=False)
    namespace_manager.bind("owl", OWL, override=False)
    g = Graph()
    g.namespace_manager = namespace_manager

    # Chaining 3 intersections

    female = Class(exNs.Female, graph=g)
    human = Class(exNs.Human, graph=g)
    youngPerson = Class(exNs.YoungPerson, graph=g)
    youngWoman = female & human & youngPerson

    assert str(youngWoman) == "ex:YoungPerson THAT ( ex:Female AND ex:Human )"

    assert isinstance(youngWoman, BooleanClass) is True
    assert isinstance(youngWoman.identifier, BNode) is True


def test_infix_owl_class_getparents():
    # computed attributes that returns a generator over taxonomic 'parents'
    # by disjunction, conjunction, and subsumption

    exNs = Namespace("http://example.com/")
    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind("ex", exNs, override=False)
    namespace_manager.bind("owl", OWL, override=False)
    g = Graph()
    g.namespace_manager = namespace_manager
    Individual.factoryGraph = g
    brother = Class(exNs.Brother)
    sister = Class(exNs.Sister)
    sibling = brother | sister
    sibling.identifier = exNs.Sibling
    assert len(sibling) == 2

    assert str(sibling) == "( ex:Brother OR ex:Sister )"

    assert (
        str(first(brother.parents))
        == "Class: ex:Sibling EquivalentTo: ( ex:Brother OR ex:Sister )"
    )
    parent = Class(exNs.Parent)
    male = Class(exNs.Male)
    father = parent & male
    father.identifier = exNs.Father
    assert len(list(father.parents)) == 2
    assert str(list(father.parents)) == "[Class: ex:Parent , Class: ex:Male ]"


def test_infixowl_enumeratedclass():
    exNs = Namespace("http://example.com/")
    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind("ex", exNs, override=False)
    namespace_manager.bind("owl", OWL, override=False)
    g = Graph()
    g.namespace_manager = namespace_manager
    Individual.factoryGraph = g

    ogbujiBros = EnumeratedClass(
        exNs.ogbujicBros, members=[exNs.chime, exNs.uche, exNs.ejike]
    )
    assert str(ogbujiBros) == "{ ex:chime ex:uche ex:ejike }"

    col = Collection(
        g, first(g.objects(predicate=OWL.oneOf, subject=ogbujiBros.identifier))
    )
    assert (
        str(sorted([g.qname(item) for item in col]))
        == "['ex:chime', 'ex:ejike', 'ex:uche']"
    )
    # logger.debug(g.serialize(format="pretty-xml"))

    assert str(g.serialize(format="n3")) == str(
        "@prefix ex: <http://example.com/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        "\n"
        "ex:ogbujicBros a owl:Class ;\n"
        "    owl:oneOf ( ex:chime ex:uche ex:ejike ) .\n"
        "\nex:chime a owl:Class .\n"
        "\nex:ejike a owl:Class .\n"
        "\nex:uche a owl:Class .\n"
        "\n"
    )


def test_infixowl_booleanclassextenthelper():
    testGraph = Graph()
    Individual.factoryGraph = testGraph
    EX = Namespace("http://example.com/")
    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind("ex", EX, override=False)
    testGraph.namespace_manager = namespace_manager

    fire = Class(EX.Fire)
    water = Class(EX.Water)

    testClass = BooleanClass(members=[fire, water])
    assert str(testClass) == "( ex:Fire AND ex:Water )"

    testClass2 = BooleanClass(operator=OWL.unionOf, members=[fire, water])
    assert str(testClass2) == "( ex:Fire OR ex:Water )"


def test_infixowl_changeoperator():
    # Converts a unionOf / intersectionOf class expression into one
    # that instead uses the given operator

    testGraph = Graph()
    Individual.factoryGraph = testGraph
    EX = Namespace("http://example.com/")
    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind("ex", EX, override=False)
    testGraph.namespace_manager = namespace_manager
    fire = Class(EX.Fire)
    water = Class(EX.Water)
    testClass = BooleanClass(members=[fire, water])

    assert str(testClass) == "( ex:Fire AND ex:Water )"

    testClass.changeOperator(OWL.unionOf)
    assert repr(testClass) == "( ex:Fire OR ex:Water )"

    try:
        testClass.changeOperator(OWL.unionOf)
    except Exception as e:
        assert str(e) == "The new operator is already being used!"


def test_infixowl_serialization():
    g1 = Graph()
    g2 = Graph()

    EX = Namespace("http://example.com/")
    namespace_manager = NamespaceManager(g1)
    namespace_manager.bind("ex", EX, override=False)
    namespace_manager = NamespaceManager(g2)
    namespace_manager.bind("ex", EX, override=False)

    # Individual.factoryGraph = g1

    prop = Property(EX.someProp, baseType=OWL.DatatypeProperty)

    restr1 = prop << some >> (Class(EX.Foo))

    assert str(restr1) == "( ex:someProp SOME ex:Foo )"

    assert (
        str(list(Property(EX.someProp, baseType=None).type))
        == "[rdflib.term.URIRef('http://www.w3.org/2002/07/owl#DatatypeProperty')]"
    )


def test_cardinality_zero():

    graph = Graph()
    EX = Namespace("http://example.com/")
    namespace_manager = NamespaceManager(graph)
    namespace_manager.bind("ex", EX, override=False)
    prop = Property(EX.someProp, baseType=OWL.DatatypeProperty)
    Restriction(
        prop, graph=graph, cardinality=Literal(0, datatype=XSD.nonNegativeInteger)
    )


def test_lshift_rlshift_delimiters():
    EX = Namespace("http://example.com/")
    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind("ex", EX, override=False)
    namespace_manager.bind("owl", OWL, override=False)
    g = Graph()
    g.namespace_manager = namespace_manager
    Individual.factoryGraph = g
    classB = Class(EX.B)
    classC = Class(EX.C)
    classD = Class(EX.D)
    classE = Class(EX.E)
    classF = Class(EX.F)

    anonClass = EX.someProp << some >> classD
    classF += anonClass
    assert str(list(anonClass.subClassOf)) == "[Class: ex:F ]"

    classA = classE | classF | anonClass
    classB += classA
    classA.equivalentClass = [Class()]
    classB.subClassOf = [EX.someProp << some >> classC]
    assert str(classA) == "( ex:E OR ex:F OR ( ex:someProp SOME ex:D ) )"


def test_matmul_rmatmul_delimiters():
    EX = Namespace("http://example.com/")
    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind("ex", EX, override=False)
    namespace_manager.bind("owl", OWL, override=False)
    g = Graph()
    g.namespace_manager = namespace_manager
    Individual.factoryGraph = g
    classB = Class(EX.B)
    classC = Class(EX.C)
    classD = Class(EX.D)
    classE = Class(EX.E)
    classF = Class(EX.F)

    anonClass = EX.someProp @ some @ classD
    classF += anonClass
    assert str(list(anonClass.subClassOf)) == "[Class: ex:F ]"

    classA = classE | classF | anonClass
    classB += classA
    classA.equivalentClass = [Class()]
    classB.subClassOf = [EX.someProp @ some @ classC]
    assert str(classA) == "( ex:E OR ex:F OR ( ex:someProp SOME ex:D ) )"
