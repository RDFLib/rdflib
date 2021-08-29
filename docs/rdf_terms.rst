.. _rdf_terms: RDF terms in rdflib

===================
RDF terms in rdflib
===================

Terms are the kinds of objects that can appear in a quoted/asserted triples. Those that are part of core  RDF concepts are: ``Blank Node``, ``URI Reference`` and ``Literal``, the latter consisting of a literal value and either a `datatype <https://www.w3.org/TR/xmlschema-2/#built-in-datatypes>`_ or an :rfc:`3066` language tag.

All terms in RDFLib are sub-classes of the :class:`rdflib.term.Identifier` class.

Nodes are a subset of the Terms that the underlying store actually persists.
The set of such Terms depends on whether or not the store is formula-aware. 
Stores that aren't formula-aware only persist those terms core to the
RDF Model but those that are formula-aware also persist the N3
extensions. However, utility terms that only serve the purpose of
matching nodes by term-patterns will probably only be terms and not nodes.


URIRefs
=======

A *URI reference* within an RDF graph is a Unicode string that does not contain any control characters ( #x00 - #x1F, #x7F-#x9F)
and would produce a valid URI character sequence representing an absolute URI with optional fragment
identifier -- `W3 RDF Concepts`__

.. __: http://www.w3.org/TR/rdf-concepts/#section-Graph-URIref

.. autoclass:: rdflib.term.URIRef
    :noindex:

.. code-block:: python

    >>> from rdflib import URIRef
    >>> uri = URIRef()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: __new__() missing 1 required positional argument: 'value'
    >>> uri = URIRef('')
    >>> uri
    rdflib.term.URIRef('')
    >>> uri = URIRef('http://example.com')
    >>> uri
    rdflib.term.URIRef('http://example.com')
    >>> uri.n3()
    '<http://example.com>'


.. _rdflibliterals:

Literals
========

Literals are attribute values in RDF, for instance, a person's name, the date of birth, height, etc. Literals can have a datatype (i.e. this is a *double*) or a language tag (this label is in *English*).

.. autoclass:: rdflib.term.Literal
    :noindex:

    A literal in an RDF graph contains one or two named components.
    
    All literals have a lexical form being a Unicode string, which SHOULD be in Normal Form C.
    
    Plain literals have a lexical form and optionally a language tag as defined by :rfc:`3066`, normalized to lowercase. An exception will be raised if illegal language-tags are passed to :meth:`rdflib.term.Literal.__init__`.
    
    Typed literals have a lexical form and a datatype URI being an RDF URI reference.
    
.. note:: When using the language tag, care must be taken not to confuse language with locale. The language tag relates only to human language text. Presentational issues should be addressed in end-user applications.
    
.. note:: The case normalization of language tags is part of the description of the abstract syntax, and consequently the abstract behaviour of RDF applications. It does not constrain an RDF implementation to actually normalize the case. Crucially, the result of comparing two language tags should not be sensitive to the case of the original input. -- `RDF Concepts and Abstract Syntax`__



.. __: http://www.w3.org/TR/rdf-concepts/#section-Graph-URIref

BNodes
======

In RDF, a blank node (also called BNode) is a node in an RDF graph representing a resource for which a URI or literal is not given. The resource represented by a blank node is also called an anonymous resource. According to the RDF standard, a blank node can only be used as subject or object in a triple, although in some syntaxes like Notation 3 it is acceptable to use a blank node as a predicate. If a blank node has a node ID (not all blank nodes are labelled in all RDF serializations), it is limited in scope to a particular serialization of the RDF graph, i.e. the node p1 in the subsequent example does not represent the same node as a node named p1 in any other graph  --`wikipedia`__


.. __: http://en.wikipedia.org/wiki/Blank_node

.. autoclass:: rdflib.term.BNode
    :noindex:

.. code-block:: python

    >>> from rdflib import BNode
    >>> bn = BNode()
    >>> bn
    rdflib.term.BNode('AFwALAKU0')
    >>> bn.n3()
    '_:AFwALAKU0'


Python support
--------------
RDFLib Literals essentially behave like unicode characters with an XML Schema datatype or language attribute. 

.. image:: /_static/datatype_hierarchy.png
   :alt: datatype hierarchy
   :align: center
   :width: 629
   :height: 717


The class provides a mechanism to both convert Python literals (and their built-ins such as time/date/datetime) into equivalent RDF Literals and (conversely) convert Literals to their Python equivalent.  This mapping to and from Python literals is done as follows:

====================== ===========
XML Datatype           Python type
====================== ===========
None                   None [#f1]_
xsd:time               time [#f2]_
xsd:date               date
xsd:dateTime           datetime
xsd:string             None
xsd:normalizedString   None
xsd:token              None
xsd:language           None
xsd:boolean            boolean
xsd:decimal            Decimal
xsd:integer            long
xsd:nonPositiveInteger int
xsd:long               long
xsd:nonNegativeInteger int
xsd:negativeInteger    int
xsd:int                long
xsd:unsignedLong       long
xsd:positiveInteger    int
xsd:short              int
xsd:unsignedInt        long
xsd:byte               int
xsd:unsignedShort      int
xsd:unsignedByte       int
xsd:float              float
xsd:double             float
xsd:base64Binary       :mod:`base64`
xsd:anyURI             None
rdf:XMLLiteral         :class:`xml.dom.minidom.Document` [#f3]_
rdf:HTML               :class:`xml.dom.minidom.DocumentFragment`
====================== ===========

.. [#f1] plain literals map directly to value space

.. [#f2] Date, time and datetime literals are mapped to Python
         instances using the `isodate <http://pypi.python.org/pypi/isodate/>`_
         package).

.. [#f3] this is a bit dirty - by accident the ``html5lib`` parser
         produces ``DocumentFragments``, and the xml parser ``Documents``,
         letting us use this to decide what datatype when round-tripping.

An appropriate data-type and lexical representation can be found using:

.. autofunction:: rdflib.term._castPythonToLiteral

and the other direction with 

.. autofunction:: rdflib.term._castLexicalToPython

All this happens automatically when creating ``Literal`` objects by passing Python objects to the constructor, and you never have to do this manually. 

You can add custom data-types with :func:`rdflib.term.bind`, see also :mod:`examples.custom_datatype`

