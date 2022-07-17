from rdflib import BNode, ConjunctiveGraph, Dataset, Graph, Literal, Namespace, URIRef
from rdflib.extras.infixowl import Class, Property, classOrTerm
from rdflib.extras.infixowl import generateQName as generate_qname  # noqa: N813
from rdflib.extras.infixowl import propertyOrIdentifier

EXNS = Namespace("http://example.org/vocab/")
PZNS = Namespace(
    "http://www.co-ode.org/ontologies/pizza/2005/10/18/classified/pizza.owl#"
)

mansyn = """
    Prefix: : <http://ex.com/owl/families#>
    Prefix: g: <http://ex.com/owl2/families#>

    Ontology: <http://example.com/owl/families> <http://example.com/owl/families-v1>
      Import: <http://ex.com/owl2/families.owl>
      Annotations: creator John,
                   Annotations: rdfs:comment "Creation Year"
                     creationYear 2008,
                   mainClass Person

      ObjectProperty: hasWife
        Annotations: ...
        Characteristics: Functional, InverseFunctional, Reflexive, Irreflexive, Asymmetric, Transitive
        Domain: Annotations: rdfs:comment "General domain",
                             creator John
                  Person,
                Annotations: rdfs:comment "More specific domain"
                  Man
        Range: Person, Woman
        SubPropertyOf: hasSpouse, loves
        EquivalentTo: isMarriedTo ,...
        DisjointWith: hates ,...
        InverseOf: hasSpouse, inverse hasSpouse
        SubPropertyChain: Annotations: ... hasChild o hasParent o...

      DataProperty: hasAge
        Annotations: ...
        Characteristics: Functional
        Domain: Person ,...
        Range: integer ,...
        SubPropertyOf: hasVerifiedAge ,...
        EquivalentTo: hasAgeInYears ,...
        DisjointWith: hasSSN ,...

      AnnotationProperty: creator
        Annotations: ...
        Domain: Person ,...
        Range: integer ,...
        SubPropertyOf: initialCreator ,...

      Datatype: NegInt
        Annotations: ...
        EquivalentTo: integer[< 0]

      Class: Person
        Annotations: ...
        SubClassOf: owl:Thing that hasFirstName exactly 1 and hasFirstName only string[minLength 1]  ,...
        SubClassOf: hasAge exactly 1 and hasAge only not NegInt,...
        SubClassOf: hasGender exactly 1 and hasGender only {female , male} ,...
        SubClassOf: hasSSN max 1, hasSSN min 1
        SubClassOf: not hates Self, ...
        EquivalentTo: g:People ,...
        DisjointWith: g:Rock , g:Mineral ,...
        DisjointUnionOf: Annotations: ... Child, Adult
        HasKey: Annotations: ... hasSSN

      Individual: John
        Annotations: ...
        Types: Person , hasFirstName value "John" or hasFirstName value "Jack"^^xsd:string
        Facts: hasWife Mary, not hasChild Susan, hasAge 33, hasChild _:child1
        SameAs: Jack ,...
        DifferentFrom: Susan ,...

      Individual: _:child1
        Annotations: ...
        Types: Person ,...
        Facts: hasChild Susan ,...

      DisjointClasses: Annotations: ... g:Rock, g:Scissor, g:Paper
      EquivalentProperties: Annotations: ... hates, loathes, despises
      DisjointProperties: Annotations: ... hates, loves, indifferent
      EquivalentProperties: Annotations: ... favoriteNumber, g:favouriteNumber, g:favouriteInteger
      DisjointProperties: Annotations: ... favoriteInteger, favouriteReal
      SameIndividual: Annotations: ... John, Jack, Joe, Jim
      DifferentIndividuals: Annotations: ... John, Susan, Mary, Jill
"""


mansynt_class = """
    /**
    * @rdfs:comment A vegetarian pizza is a pizza that only has cheese toppings
    * and tomato toppings.
    *
    * @rdfs:label Pizza [en]
    * @rdfs:label Pizza [pt]
    */
    Class: VegetarianPizza
    EquivalentTo:
    Pizza and
    not (hasTopping some FishTopping) and
    not (hasTopping some MeatTopping)
    DisjointWith:
    NonVegetarianPizza
"""


def test_generateqname_using_conjunctivegraph() -> None:
    g = ConjunctiveGraph()
    g.bind("ex", EXNS)

    assert (
        generate_qname(g, URIRef("http://example.org/vocab/ontology")) == "ex:ontology"
    )


def test_generateqname_using_dataset() -> None:
    g = Dataset()
    g.bind("ex", EXNS)

    assert (
        generate_qname(g, URIRef("http://example.org/vocab/ontology")) == "ex:ontology"
    )


def test_generateqname_using_graph() -> None:
    g = Graph()
    g.bind("ex", EXNS)

    assert (
        generate_qname(g, URIRef("http://example.org/vocab/ontology")) == "ex:ontology"
    )


def test_generateqname_using_graph_and_uriref() -> None:
    g = Graph()
    g.bind("ex", EXNS)

    res = generate_qname(g, URIRef("http://example.org/vocab/ontology"))

    assert res == "ex:ontology"


def test_generateqname_using_graph_and_bnode() -> None:
    g = Graph()
    g.bind("ex", EXNS)

    res = generate_qname(g, BNode("http://example.org/vocab/ontology"))

    assert res == "ex:ontology"

    res = generate_qname(g, BNode("urn:example:foo"))

    assert res == "ns1:foo"


def test_generateqname_using_graph_and_property() -> None:
    g = Graph()
    g.bind("ex", EXNS)

    iswoman_property = Property(identifier=EXNS.iswoman, graph=g)

    res = generate_qname(g, iswoman_property)

    assert res == "ex:iswoman"


def test_class_or_term() -> None:
    uriref_term = URIRef("http://example.org/vocab/D")
    bnode_term = BNode("http://example.org/vocab/D")
    literal_term = Literal("http://example.org/vocab/D")

    assert classOrTerm(Class(EXNS.D)) == uriref_term
    assert classOrTerm(uriref_term) == uriref_term
    assert classOrTerm(bnode_term) == bnode_term
    assert classOrTerm(literal_term) == literal_term


def test_property_or_identifier() -> None:

    g = Graph()
    g.bind("ex", EXNS)

    is_a_woman = Property(identifier=EXNS.iswoman, graph=g)

    assert propertyOrIdentifier(is_a_woman) == URIRef(
        "http://example.org/vocab/iswoman"
    )

    uriref_term = URIRef("http://example.org/vocab/D")

    assert propertyOrIdentifier(uriref_term) == URIRef("http://example.org/vocab/D")
