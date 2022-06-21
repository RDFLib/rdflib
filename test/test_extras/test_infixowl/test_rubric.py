from rdflib import Namespace

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

"""
class Infix:
    def __init__(self, function):
    def __rlshift__(self, other):
    def __rshift__(self, other):
    def __rmatmul__(self, other):
    def __matmul__(self, other):
    def __call__(self, value1, value2):

def generateQName(graph, uri):  # noqa: N802

def classOrTerm(thing):  # noqa: N802

def classOrIdentifier(thing):  # noqa: N802

def propertyOrIdentifier(thing):  # noqa: N802

def manchesterSyntax(  # noqa: N802

def GetIdentifiedClasses(graph):  # noqa: N802

class TermDeletionHelper:
    def someFunc(func):  # noqa: N802

def termDeletionDecorator(prop):  # noqa: N802
    def __init__(self, prop):
    def __call__(self, f):

class Individual(object):
    def serialize(self, graph):
    def __init__(self, identifier=None, graph=None):
    def clearInDegree(self):  # noqa: N802
    def clearOutDegree(self):  # noqa: N802
    def delete(self):
    def replace(self, other):
    def _get_type(self):
    def _set_type(self, kind):
    def _delete_type(self):
    def _get_identifier(self):
    def _set_identifier(self, i):
    def _get_sameAs(self):  # noqa: N802
    def _set_sameAs(self, term):  # noqa: N802
    def _delete_sameAs(self):  # noqa: N802

class AnnotatableTerms(Individual):
    def __init__(
    def handleAnnotation(self, val):  # noqa: N802
    def setupACEAnnotations(self):  # noqa: N802
    def _get_comment(self):
    def _set_comment(self, comment):
    def _del_comment(self):
    def _get_seeAlso(self):  # noqa: N802
    def _set_seeAlso(self, seeAlsos):  # noqa: N802, N803
    def _del_seeAlso(self):  # noqa: N802
    def _get_label(self):
    def _set_label(self, label):
    def _delete_label(self):

class Ontology(AnnotatableTerms):
    def __init__(self, identifier=None, imports=None, comment=None, graph=None):
    def setVersion(self, version):  # noqa: N802
    def _get_imports(self):
    def _set_imports(self, other):
    def _del_imports(self):

def AllClasses(graph):  # noqa: N802

def AllProperties(graph):  # noqa: N802

class ClassNamespaceFactory(Namespace):
    def term(self, name):
    def __getitem__(self, key, default=None):
    def __getattr__(self, name):

def ComponentTerms(cls):  # noqa: N802

def DeepClassClear(classToPrune):  # noqa: N802, N803
    def deepClearIfBNode(_class):  # noqa: N802

class MalformedClassError(Exception):
    def __init__(self, msg):
    def __repr__(self):

def CastClass(c, graph=None):  # noqa: N802

class Class(AnnotatableTerms):
    def _serialize(self, graph):
    def serialize(self, graph):
    def setupNounAnnotations(self, nounAnnotations):  # noqa: N802, N803
    def __init__(
    def _get_extent(self, graph=None):
    def _set_extent(self, other):
    def _del_type(self):
    def _get_annotation(self, term=RDFS.label):
    def _get_extentQuery(self):  # noqa: N802
    def _set_extentQuery(self, other):  # noqa: N802
    def __hash__(self):
    def __eq__(self, other):
    def __iadd__(self, other):
    def __isub__(self, other):
    def __invert__(self):
    def __or__(self, other):
    def __and__(self, other):
    def _get_subClassOf(self):  # noqa: N802
    def _set_subClassOf(self, other):  # noqa: N802
    def _del_subClassOf(self):  # noqa: N802
    def _get_equivalentClass(self):  # noqa: N802
    def _set_equivalentClass(self, other):  # noqa: N802
    def _del_equivalentClass(self):  # noqa: N802
    def _get_disjointWith(self):  # noqa: N802
    def _set_disjointWith(self, other):  # noqa: N802
    def _del_disjointWith(self):  # noqa: N802
    def _get_complementOf(self):  # noqa: N802
    def _set_complementOf(self, other):  # noqa: N802
    def _del_complementOf(self):  # noqa: N802
    def _get_parents(self):
    def isPrimitive(self):  # noqa: N802
    def subSumpteeIds(self):  # noqa: N802
    def __repr__(self, full=False, normalization=True):


class OWLRDFListProxy(object):
    def __init__(self, rdfList, members=None, graph=None):  # noqa: N803
    def __eq__(self, other):
    def __len__(self):
    def index(self, item):
    def __getitem__(self, key):
    def __setitem__(self, key, value):
    def __delitem__(self, key):
    def clear(self):
    def __iter__(self):
    def __contains__(self, item):
    def append(self, item):
    def __iadd__(self, other):

class EnumeratedClass(OWLRDFListProxy, Class):
    def isPrimitive(self):  # noqa: N802
    def __init__(self, identifier=None, members=None, graph=None):
    def __repr__(self):
    def serialize(self, graph):


class BooleanClassExtentHelper:
    def __init__(self, operator):
    def __call__(self, f):

class Callable:
    def __init__(self, anycallable):

class BooleanClass(OWLRDFListProxy, Class):
    def getIntersections():  # type: ignore[misc]  # noqa: N802
    def getUnions():  # type: ignore[misc]  # noqa: N802
    def __init__(
    def copy(self):
    def serialize(self, graph):
    def isPrimitive(self):  # noqa: N802
    def changeOperator(self, newOperator):  # noqa: N802, N803
    def __repr__(self):
    def __or__(self, other):

def AllDifferent(members):  # noqa: N802

class Restriction(Class):
    def __init__(
    def serialize(self, graph):
    def isPrimitive(self):  # noqa: N802
    def __hash__(self):
    def __eq__(self, other):
    def _get_onProperty(self):  # noqa: N802
    def _set_onProperty(self, prop):  # noqa: N802
    def _del_onProperty(self):  # noqa: N802
    def _get_allValuesFrom(self):  # noqa: N802
    def _set_allValuesFrom(self, other):  # noqa: N802
    def _del_allValuesFrom(self):  # noqa: N802
    def _get_someValuesFrom(self):  # noqa: N802
    def _set_someValuesFrom(self, other):  # noqa: N802
    def _del_someValuesFrom(self):  # noqa: N802
    def _get_hasValue(self):  # noqa: N802
    def _set_hasValue(self, other):  # noqa: N802
    def _del_hasValue(self):  # noqa: N802
    def _get_cardinality(self):
    def _set_cardinality(self, other):
    def _del_cardinality(self):
    def _get_maxCardinality(self):  # noqa: N802
    def _set_maxCardinality(self, other):  # noqa: N802
    def _del_maxCardinality(self):  # noqa: N802
    def _get_minCardinality(self):  # noqa: N802
    def _set_minCardinality(self, other):  # noqa: N802
    def _del_minCardinality(self):  # noqa: N802
    def restrictionKind(self):  # noqa: N802
    def __repr__(self):

class Property(AnnotatableTerms):
    def setupVerbAnnotations(self, verbAnnotations):  # noqa: N802, N803
    def __init__(
    def serialize(self, graph):
    def _get_extent(self, graph=None):
    def _set_extent(self, other):
    def __repr__(self):
    def _get_subPropertyOf(self):  # noqa: N802
    def _set_subPropertyOf(self, other):  # noqa: N802
    def _del_subPropertyOf(self):  # noqa: N802
    def _get_inverseOf(self):  # noqa: N802
    def _set_inverseOf(self, other):  # noqa: N802
    def _del_inverseOf(self):  # noqa: N802
    def _get_domain(self):
    def _set_domain(self, other):
    def _del_domain(self):
    def _get_range(self):
    def _set_range(self, ranges):
    def _del_range(self):
    def replace(self, other):

def CommonNSBindings(graph, additionalNS={}):  # noqa: N802, N803

"""
