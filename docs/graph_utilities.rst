.. _graph_utilities:

===============
Graph utilities
===============


Graphs as Iterators
-------------------

RDFLib graphs also override :meth:`__iter__` in order to support iteration over the contained triples:

.. code-block:: python

    for subject,predicate,obj_ in someGraph:
       assert (subject,predicate,obj_) in someGraph, "Iterator / Container Protocols are Broken!!"

Set Operations on RDFLib Graphs 
-------------------------------

:meth:`__iadd__` and :meth:`__isub__` are overridden to support adding and subtracting Graphs to/from each other (in place):

* G1 += G1
* G2 -= G2

Basic Triple Matching
---------------------

RDFLib graphs support basic triple pattern matching with a :meth:`triples` function.

.. automethod:: rdflib.graph.Graph.triples

This function is a generator of triples that match the pattern given by the arguments.  The arguments of these are RDF terms that restrict the triples that are returned.  Terms that are :data:`None` are treated as a wildcard.

Managing Triples
----------------

Adding Triples
^^^^^^^^^^^^^^
Triples can be added in two ways:

* They may be added with with the :meth:`parse` function.

    .. automethod:: rdflib.graph.Graph.parse

    The first argument can be a *source* of many kinds, but the most common is the serialization (in various formats: RDF/XML, Notation 3, NTriples of an RDF graph as a string.  The :keyword:`format` parameter is one of ``n3``, ``xml``, or ``ntriples``.  :keyword:`publicID` is the name of the graph into which the RDF serialization will be parsed.
* Triples can also be added with the :meth:`add` function: 

    .. automethod:: rdflib.graph.Graph.add

Removing Triples
^^^^^^^^^^^^^^^^

Similarly, triples can be removed by a call to :meth:`remove`:

.. automethod:: rdflib.graph.Graph.remove


RDF Literal Support
-------------------

RDFLib Literals essentially behave like unicode characters with an XML Schema datatype or language attribute.  The class provides a mechanism to both convert Python literals (and their built-ins such as time/date/datetime) into equivalent RDF Literals and (conversely) convert Literals to their Python equivalent.  There is some support of considering datatypes in comparing Literal instances, implemented as an override to :meth:`__eq__`.  This mapping to and from Python literals is achieved with the following dictionaries:

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

Maps Python instances to WXS datatyped Literals

.. code-block:: python

    XSDToPython = {  
        XSD_NS+u'time'               : (None,_strToTime),
        XSD_NS+u'date'               : (None,_strToDate),
        XSD_NS+u'dateTime'           : (None,_strToDateTime),    
        XSD_NS+u'string'             : (None,None),
        XSD_NS+u'normalizedString'   : (None,None),
        XSD_NS+u'token'              : (None,None),
        XSD_NS+u'language'           : (None,None),
        XSD_NS+u'boolean'            : (None, lambda i:i.lower() in ['1','true']),
        XSD_NS+u'decimal'            : (float,None), 
        XSD_NS+u'integer'            : (long ,None),
        XSD_NS+u'nonPositiveInteger' : (int,None),
        XSD_NS+u'long'               : (long,None),
        XSD_NS+u'nonNegativeInteger' : (int, None),
        XSD_NS+u'negativeInteger'    : (int, None),
        XSD_NS+u'int'                : (int, None),
        XSD_NS+u'unsignedLong'       : (long, None),
        XSD_NS+u'positiveInteger'    : (int, None),
        XSD_NS+u'short'              : (int, None),
        XSD_NS+u'unsignedInt'        : (long, None),
        XSD_NS+u'byte'               : (int, None),
        XSD_NS+u'unsignedShort'      : (int, None),
        XSD_NS+u'unsignedByte'       : (int, None),
        XSD_NS+u'float'              : (float, None),
        XSD_NS+u'double'             : (float, None),
        XSD_NS+u'base64Binary'       : (base64.decodestring, None),
        XSD_NS+u'anyURI'             : (None,None),
    }

Maps WXS datatyped Literals to Python.  This mapping is used by the :meth:`toPython` method defined on all Literal instances.


