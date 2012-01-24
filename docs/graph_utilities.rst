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
    :noindex:

This function is a generator of triples that match the pattern given by the arguments.  The arguments of these are RDF terms that restrict the triples that are returned.  Terms that are :data:`None` are treated as a wildcard.

Managing Triples
----------------

Adding Triples
^^^^^^^^^^^^^^
Triples can be added in two ways:

* They may be added with with the :meth:`parse` function.

    .. automethod:: rdflib.graph.Graph.parse
                  :noindex:

    The first argument can be a *source* of many kinds, but the most common is the serialization (in various formats: RDF/XML, Notation 3, NTriples of an RDF graph as a string.  The ``format`` parameter is one of ``n3``, ``xml``, or ``ntriples``.  ``publicID`` is the name of the graph into which the RDF serialization will be parsed.

* Triples can also be added with the :meth:`add` function: 

    .. automethod:: rdflib.graph.Graph.add
                  :noindex:

Removing Triples
^^^^^^^^^^^^^^^^

Similarly, triples can be removed by a call to :meth:`remove`:

.. automethod:: rdflib.graph.Graph.remove
              :noindex:


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

Merging graphs
--------------

.. note:: A merge of a set of RDF graphs is defined as follows. If the graphs in the set have no blank nodes in common, then the union of the graphs is a merge; if they do share blank nodes, then it is the union of a set of graphs that is obtained by replacing the graphs in the set by equivalent graphs that share no blank nodes. This is often described by saying that the blank nodes have been 'standardized apart'. It is easy to see that any two merges are equivalent, so we will refer to the merge, following the convention on equivalent graphs. Using the convention on equivalent graphs and identity, any graph in the original set is considered to be a subgraph of the merge.

    One does not, in general, obtain the merge of a set of graphs by concatenating their corresponding N-Triples documents and constructing the graph described by the merged document. If some of the documents use the same node identifiers, the merged document will describe a graph in which some of the blank nodes have been 'accidentally' identified. To merge N-Triples documents it is necessary to check if the same nodeID is used in two or more documents, and to replace it with a distinct nodeID in each of them, before merging the documents. Similar cautions apply to merging graphs described by RDF/XML documents which contain nodeIDs

(copied directly from http://www.w3.org/TR/rdf-mt/#graphdefs)

.. code-block:: pycon

    """
    Tutorial 9 - demonstrate graph operations

    (not really quite graph operations since rdflib cannot merge models like 
    Jena, but this examples shows you can load two different RDF files and 
    rdflib will merge the two together into one model)

    Copyright (C) 2005 Sylvia Wong <sylvia at whileloop dot org>

    This program is free software; you can redistribute it and/or modify it 
    under the terms of the GNU General Public License as published by the 
    Free Software Foundation; either version 2 of the License, or (at your 
    option) any later version.

    This program is distributed in the hope that it will be useful, but 
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
    General Public License for more details.

    You should have received a copy of the GNU General Public License along 
    with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
    """

    >>> data1 = """\
    ... @prefix vCard: <http://www.w3.org/2001/vcard-rdf/3.0#> .
    ... 
    ... <http://somewhere/JohnSmith/> vCard:FN "John Smith";
    ...     vCard:N [ vCard:Family "Smith";
    ...             vCard:Given "John" ] .
    ... """
    >>> data2 = """\
    ... @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    ... @prefix vCard: <http://www.w3.org/2001/vcard-rdf/3.0#> .
    ... 
    ... <http://somewhere/JohnSmith/> vCard:EMAIL [ a vCard:internet;
    ...             rdf:value "John@somewhere.com" ];
    ...     vCard:FN "John Smith" .
    ... """
    >>> from rdflib import Graph
    >>> store = Graph()
    >>> store.parse(data=data1, format="n3") #doctest :ellipsis
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> store.parse(data=data2, format="n3") #doctest :ellipsis
    <Graph identifier=... (<class 'rdflib.graph.Graph'>)>
    >>> print(store.serialize(format="n3"))
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix vCard: <http://www.w3.org/2001/vcard-rdf/3.0#> .

    <http://somewhere/JohnSmith/> vCard:EMAIL [ a vCard:internet;
                rdf:value "John@somewhere.com" ];
        vCard:FN "John Smith";
        vCard:N [ vCard:Family "Smith";
                vCard:Given "John" ] .

(edited for inclusion in rdflib documentation)

