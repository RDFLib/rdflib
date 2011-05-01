# -*- coding: UTF-8 -*-
"""
The ``Description`` class wraps a ``Graph`` and a resource reference (i.e. an
``URIRef`` or ``BNode``), to support a resource oriented way of working with a
graph.

It contains methods directly corresponding to those methods of the Graph
interface that relate to reading and writing data. The difference is that a
Description also binds a current subject, making it possible to work without
tracking both the graph and a current subject. This makes Description "resource
oriented", as compared to the triple orientation of the Graph API.

Resulting generators are also wrapped so that any resource reference values are
in turn wrapped in Descriptions.

Here are some examples. Start by importing things we need and defining some
namespaces::

    >>> from rdflib import *
    >>> FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    >>> CV = Namespace("http://purl.org/captsolo/resume-rdf/0.2/cv#")

Load some RDF data::

    >>> graph = Graph().parse(format='n3', data='''
    ... @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    ... @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
    ... @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    ... @prefix cv: <http://purl.org/captsolo/resume-rdf/0.2/cv#> .
    ...
    ... @base <http://example.org/> .
    ...
    ... </person/some1#self> a foaf:Person;
    ...     rdfs:comment "Just a Python & RDF hacker."@en;
    ...     foaf:depiction </images/person/some1.jpg>;
    ...     foaf:homepage <http://example.net/>;
    ...     foaf:name "Some Body" .
    ...
    ... </images/person/some1.jpg> a foaf:Image;
    ...     rdfs:label "some 1"@en;
    ...     rdfs:comment "Just an image"@en;
    ...     foaf:thumbnail </images/person/some1-thumb.jpg> .
    ...
    ... </images/person/some1-thumb.jpg> a foaf:Image .
    ...
    ... [] a cv:CV;
    ...     cv:aboutPerson </person/some1#self>;
    ...     cv:hasWorkHistory [ cv:employedIn </#company>;
    ...             cv:startDate "2009-09-04"^^xsd:date ] .
    ... ''')

Create a Description::

    >>> person = Description(graph, URIRef("http://example.org/person/some1#self"))

Retrieve some basic facts::

    >>> person.identifier
    rdflib.term.URIRef('http://example.org/person/some1#self')

    >>> person.value(FOAF.name)
    rdflib.term.Literal(u'Some Body')

    >>> person.value(RDFS.comment)
    rdflib.term.Literal(u'Just a Python & RDF hacker.', lang=u'en')

Resource references are also Descriptions, so you can easily get e.g. a qname
for the type of a resource, like::

    >>> person.value(RDF.type).qname()
    u'foaf:Person'

Or for the predicates of a resource::

    >>> sorted(p.qname() for p in person.predicates())
    [u'foaf:depiction', u'foaf:homepage', u'foaf:name', u'rdf:type', u'rdfs:comment']

Follow relations and get more data from their Descriptions as well::

    >>> for pic in person.objects(FOAF.depiction):
    ...     print pic.identifier
    ...     print pic.value(RDF.type).qname()
    ...     print pic.label()
    ...     print pic.comment()
    ...     print pic.value(FOAF.thumbnail).identifier
    http://example.org/images/person/some1.jpg
    foaf:Image
    some 1
    Just an image
    http://example.org/images/person/some1-thumb.jpg

    >>> for cv in person.subjects(CV.aboutPerson):
    ...     work = list(cv.objects(CV.hasWorkHistory))[0]
    ...     print work.value(CV.employedIn).identifier
    ...     print work.value(CV.startDate)
    http://example.org/#company
    2009-09-04

It's just as easy to work with the predicates of a resource::

    >>> for s, p in person.subject_predicates():
    ...     print s.value(RDF.type).qname()
    ...     print p.qname()
    ...     for s, o in p.subject_objects():
    ...         print s.value(RDF.type).qname()
    ...         print o.value(RDF.type).qname()
    cv:CV
    cv:aboutPerson
    cv:CV
    foaf:Person

This is useful for e.g. inspection::

    >>> thumb_ref = URIRef("http://example.org/images/person/some1-thumb.jpg")
    >>> thumb = Description(graph, thumb_ref)
    >>> for p, o in thumb.predicate_objects():
    ...     print p.qname()
    ...     print o.qname()
    rdf:type
    foaf:Image

Similarly, adding, setting and removing data is easy::

    >>> thumb.add(RDFS.label, Literal("thumb"))
    >>> print thumb.label()
    thumb
    >>> thumb.set(RDFS.label, Literal("thumbnail"))
    >>> print thumb.label()
    thumbnail
    >>> thumb.remove(RDFS.label)
    >>> list(thumb.objects(RDFS.label))
    []


With this artificial schema data::

    >>> graph2 = Graph().parse(format='n3', data='''
    ... @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    ... @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    ... @prefix owl: <http://www.w3.org/2002/07/owl#> .
    ... @prefix v: <http://example.org/def/v#> .
    ...
    ... v:Artifact a owl:Class .
    ...
    ... v:Document a owl:Class;
    ...     rdfs:subClassOf v:Artifact .
    ...
    ... v:Paper a owl:Class;
    ...     rdfs:subClassOf v:Document .
    ...
    ... v:Choice owl:oneOf (v:One v:Other) .
    ...
    ... v:Stuff a rdf:Seq; rdf:_1 v:One; rdf:_2 v:Other .
    ...
    ... ''')

From this class::

    >>> artifact = Description(graph2, URIRef("http://example.org/def/v#Artifact"))

we can get at subclasses::

    >>> subclasses = list(artifact.transitive_subjects(RDFS.subClassOf))
    >>> [c.qname() for c in subclasses]
    [u'v:Artifact', u'v:Document', u'v:Paper']

and superclasses from the last subclass::

    >>> [c.qname() for c in subclasses[-1].transitive_objects(RDFS.subClassOf)]
    [u'v:Paper', u'v:Document', u'v:Artifact']

Get items from the Choice::

    >>> choice = Description(graph2, URIRef("http://example.org/def/v#Choice"))
    >>> [it.qname() for it in choice.value(OWL.oneOf).items()]
    [u'v:One', u'v:Other']

And the sequence of Stuff::

    >>> stuff = Description(graph2, URIRef("http://example.org/def/v#Stuff"))
    >>> [it.qname() for it in stuff.seq()]
    [u'v:One', u'v:Other']

Equality is based on the identifier::

    >>> t1 = Description(Graph(), URIRef("http://example.org/thing"))
    >>> t2 = Description(Graph(), URIRef("http://example.org/thing"))
    >>> t3 = Description(Graph(), URIRef("http://example.org/other"))
    >>> t1 is t2
    False
    >>> t1 == t2
    True
    >>> t1 != t2
    False
    >>> t1 == t3
    False
    >>> t1 != t3
    True

That's it!
"""

from rdflib.term import BNode, URIRef
from rdflib.namespace import RDF


class Description(object):

    def __init__(self, graph, subject):
        self.graph = graph
        self.identifier = subject

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __ne__(self, other):
        return not self == other

    def add(self, p, o):
        self.graph.add((self.identifier, p, o))

    def remove(self, p, o=None):
        self.graph.remove((self.identifier, p, o))

    def set(self, predicate, object):
        self.graph.set((self.identifier, predicate, object))

    def subjects(self, predicate=None): # rev
        return self._descriptions(self.graph.subjects(predicate, self.identifier))

    def predicates(self, object=None):
        return self._descriptions(self.graph.predicates(self.identifier, object))

    def objects(self, predicate=None):
        return self._descriptions(self.graph.objects(self.identifier, predicate))

    def subject_predicates(self):
        return self._description_pairs(
                self.graph.subject_predicates(self.identifier))

    def subject_objects(self):
        return self._description_pairs(
                self.graph.subject_objects(self.identifier))

    def predicate_objects(self):
        return self._description_pairs(
                self.graph.predicate_objects(self.identifier))

    def value(self, predicate=RDF.value, object=None, default=None, any=True):
        return self._cast(
            self.graph.value(self.identifier, predicate, object, default, any))

    def label(self):
        return self.graph.label(self.identifier)

    def comment(self):
        return self.graph.comment(self.identifier)

    def items(self):
        return self._descriptions(self.graph.items(self.identifier))

    def transitive_objects(self, property, remember=None):
        return self._descriptions(self.graph.transitive_objects(
            self.identifier, property, remember))

    def transitive_subjects(self, predicate, remember=None):
        return self._descriptions(self.graph.transitive_subjects(
            predicate, self.identifier, remember))

    def seq(self):
        return self._descriptions(self.graph.seq(self.identifier))

    def qname(self):
        return self.graph.qname(self.identifier)

    def _description_pairs(self, pairs):
        for s1, s2 in pairs:
            yield self._cast(s1), self._cast(s2)

    def _descriptions(self, nodes):
        for node in nodes:
            yield self._cast(node)

    def _cast(self, node):
        return _is_ref(node) and self._new(node) or node

    def _new(self, subject):
        return type(self)(self.graph, subject)


def _is_ref(node):
    return isinstance(node, (BNode, URIRef))


