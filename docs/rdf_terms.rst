.. _rdf_terms: RDF terms in rdflib

===================
RDF terms in rdflib
===================

Terms are the kinds of objects that can appear in a quoted/asserted triple. Those that are part of core  RDF concepts are: ``Blank Node``, ``URI Reference`` and ``Literal``, the latter consisting of a literal value and either a `datatype <http://www.w3.org/TR/2001/REC-xmlschema-2-20010502/#built-in-datatypes>`_ or an `rfc3066 <http://tools.ietf.org/html/rfc3066>`_ language tag.

BNodes
======

    In RDF, a blank node (also called bnode) is a node in an RDF graph representing a resource for which a URI or literal is not given. The resource represented by a blank node is also called an anonymous resource. By RDF standard a blank node can only be used as subject or object in an RDF triple, although in some syntaxes like Notation 3 [1] it is acceptable to use a blank node as a predicate. If a blank node has a node ID (not all blank nodes are labeled in all RDF serializations), it is limited in scope to a serialization of a particular RDF graph, i.e. the node p1 in the subsequent example does not represent the same node as a node named p1 in any other graph  --`wikipedia`__


.. __: http://en.wikipedia.org/wiki/Blank_node

.. autoclass:: rdflib.term.BNode
    :noindex:

.. code-block:: pycon

    >>> from rdflib import BNode
    >>> anode = BNode()
    >>> anode
    rdflib.term.BNode('AFwALAKU0')
    >>> anode.n3()
    u'_:AFwALAKU0'

URIRefs
=======

    A URI reference within an RDF graph is a Unicode string that does not contain any control characters ( #x00 - #x1F, #x7F-#x9F) and would produce a valid URI character sequence representing an absolute URI with optional fragment identifier -- `W3 RDF Concepts`__

.. __: http://www.w3.org/TR/rdf-concepts/#section-Graph-URIref

.. autoclass:: rdflib.term.URIRef
    :noindex:

.. code-block:: pycon

    >>> from rdflib import URIRef
    >>> aref = URIRef()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: __new__() takes at least 2 arguments (1 given)
    >>> aref = URIRef('')
    >>> aref
    rdflib.term.URIRef(u'')
    >>> aref = URIRef('http://example.com')
    >>> aref
    rdflib.term.URIRef(u'http://example.com')
    >>> aref.n3()
    u'<http://example.com>'


Literals
========

.. autoclass:: rdflib.term.Literal
    :noindex:

    A literal in an RDF graph contains one or two named components.
    
    All literals have a lexical form being a Unicode string, which SHOULD be in Normal Form C.
    
    Plain literals have a lexical form and optionally a language tag as defined by RFC-3066, normalized to lowercase.
    
    Typed literals have a lexical form and a datatype URI being an RDF URI reference.
    
    Note: Literals in which the lexical form begins with a composing character (as defined by CHARMOD)are allowed however they may cause interoperability problems, particularly with XML version 1.1.
    
    Note: When using the language tag, care must be taken not to confuse language with locale. The language tag relates only to human language text. Presentational issues should be addressed in end-user applications.
    
    Note: The case normalization of language tags is part of the description of the abstract syntax, and consequently the abstract behaviour of RDF applications. It does not constrain an RDF implementation to actually normalize the case. Crucially, the result of comparing two language tags should not be sensitive to the case of the original input. -- `RDF Concepts and Abstract Syntax`__

.. __: http://www.w3.org/TR/rdf-concepts/#section-Graph-URIref

Python support
--------------
RDFLib Literals essentially behave like unicode characters with an XML Schema datatype or language attribute.  


The class provides a mechanism to both convert Python literals (and their built-ins such as time/date/datetime) into equivalent RDF Literals and (conversely) convert Literals to their Python equivalent.  There is some support of considering datatypes in comparing Literal instances, implemented as an override to :meth:`__eq__`.  This mapping to and from Python literals is achieved with the following dictionaries:

.. code-block:: python

    PythonToXSD = {
        basestring : (None,None),
        float      : (None,XSD_NS+u'float'),
        int        : (None,XSD_NS+u'int'),
        long       : (None,XSD_NS+u'long'),    
        bool       : (None,XSD_NS+u'boolean'),
        date       : (lambda i:i.isoformat(),XSD_NS+u'date'),
        time       : (lambda i:i.isoformat(),XSD_NS+u'time'),
        datetime   : (lambda i:i.isoformat(),XSD_NS+u'dateTime'),
    }

Maps Python instances to WXS datatyped Literals (the parse_time, _date and _datetime
functions are imports from the `isodate <http://pypi.python.org/pypi/isodate/>`_ 
package).

.. code-block:: python

     XSDToPython = {
        URIRef(_XSD_PFX+'time')               : parse_time,
        URIRef(_XSD_PFX+'date')               : parse_date,
        URIRef(_XSD_PFX+'dateTime')           : parse_datetime,
        URIRef(_XSD_PFX+'string')             : None,
        URIRef(_XSD_PFX+'normalizedString')   : None,
        URIRef(_XSD_PFX+'token')              : None,
        URIRef(_XSD_PFX+'language')           : None,
        URIRef(_XSD_PFX+'boolean')            : lambda i:i.lower() in ['1','true'],
        URIRef(_XSD_PFX+'decimal')            : float,
        URIRef(_XSD_PFX+'integer')            : long,
        URIRef(_XSD_PFX+'nonPositiveInteger') : int,
        URIRef(_XSD_PFX+'long')               : long,
        URIRef(_XSD_PFX+'nonNegativeInteger') : int,
        URIRef(_XSD_PFX+'negativeInteger')    : int,
        URIRef(_XSD_PFX+'int')                : long,
        URIRef(_XSD_PFX+'unsignedLong')       : long,
        URIRef(_XSD_PFX+'positiveInteger')    : int,
        URIRef(_XSD_PFX+'short')              : int,
        URIRef(_XSD_PFX+'unsignedInt')        : long,
        URIRef(_XSD_PFX+'byte')               : int,
        URIRef(_XSD_PFX+'unsignedShort')      : int,
        URIRef(_XSD_PFX+'unsignedByte')       : int,
        URIRef(_XSD_PFX+'float')              : float,
        URIRef(_XSD_PFX+'double')             : float,
        URIRef(_XSD_PFX+'base64Binary')       : lambda s: base64.b64decode(py3compat.b(s)),
        URIRef(_XSD_PFX+'anyURI')             : None,
    }

Maps WXS datatyped Literals to Python.  This mapping is used by the :meth:`toPython` method defined on all Literal instances.

.. image:: /_static/datatype-hierarchy.gif
   :alt: datatype hierarchy
   :align: center
   :width: 629
   :height: 717

