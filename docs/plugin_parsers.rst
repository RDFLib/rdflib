.. _plugin_parsers: Plugin parsers

==============
Plugin parsers
==============

The currently-available plug-in parsers are listed in 
`rdfextras plugins <http://rdfextras.readthedocs.org/en/latest>`_

.. code-block:: python

    register('application/rdf+xml', Parser,
                'rdflib.plugins.parsers.rdfxml', 'RDFXMLParser')
    register('xml', Parser,
                'rdflib.plugins.parsers.rdfxml', 'RDFXMLParser')
    register('n3', Parser,
                'rdflib.plugins.parsers.notation3', 'N3Parser')
    register('turtle', Parser,
                'rdflib.plugins.parsers.notation3', 'TurtleParser')
    register('nt', Parser,
                'rdflib.plugins.parsers.nt', 'NTParser')
    register('nquads', Parser,
                'rdflib.plugins.parsers.nquads', 'NQuadsParser')
    register('trix', Parser,
                'rdflib.plugins.parsers.trix', 'TriXParser')

    # The basic parsers: RDFa (by default, 1.1), microdata, and embedded
    # turtle (a.k.a. hturtle)

    register('hturtle', Parser,
                'rdflib.plugins.parsers.hturtle', 'HTurtleParser')
    register('rdfa', Parser,
                'rdflib.plugins.parsers.structureddata', 'RDFaParser')
    register('mdata', Parser,
                'rdflib.plugins.parsers.structureddata', 'MicrodataParser')
    register('microdata', Parser,
                'rdflib.plugins.parsers.structureddata', 'MicrodataParser')
    
    # A convenience for using the RDFa 1.0 syntax if required (although this
    # parse method can be invoked with an rdfa_version keyword, too)

    register('rdfa1.0', Parser,
                'rdflib.plugins.parsers.structureddata', 'RDFa10Parser')
    
    # For completeness/consistency

    register('rdfa1.1', Parser,
                'rdflib.plugins.parsers.structureddata', 'RDFaParser')

    # An HTML file may contain microdata, rdfa, or turtle. If the user
    # wants all of them, the parser below simply invokes all:

    register('html', Parser,
                'rdflib.plugins.parsers.structureddata', 'StructuredDataParser')

    # Some media types are also bound to RDFa

    register('application/svg+xml', Parser,
                'rdflib.plugins.parsers.structureddata', 'RDFaParser')
    register('application/xhtml+xml', Parser,
                'rdflib.plugins.parsers.structureddata', 'RDFaParser')

    # 'text/html' media type should be equivalent to html:

    register('text/html', Parser,
                'rdflib.plugins.parsers.structureddata', 'StructuredDataParser')


Notation 3
-----------

.. code-block:: python

    ConjunctiveGraph().parse(data=data, format="n3")

.. module:: rdflib.plugins.parsers.notation3
.. autoclass::  rdflib.plugins.parsers.notation3.N3Parser
    :members:

NQuads
-------

.. code-block:: python

    ConjunctiveGraph().parse(data=data, format="nquads")

.. module:: rdflib.plugins.parsers.nquads
.. autoclass::  rdflib.plugins.parsers.nquads.NQuadsParser
    :members:

NTriples
--------

.. code-block:: python

    ConjunctiveGraph().parse(data=data, format="nt")

.. module:: rdflib.plugins.parsers.nt
.. autoclass::  rdflib.plugins.parsers.nt.NTParser
    :members:

RDFa
-----

RDFa 1.0
^^^^^^^^

.. warning:: The RDFa parser is now 1.1 by default (2012-11-07)

.. code-block:: python

    ConjunctiveGraph().parse(data=data, format="rdfa1.0")

.. automodule:: rdflib.plugins.parsers.structureddata
.. autoclass::  rdflib.plugins.parsers.structureddata.RDFa10Parser'
    :members:

RDFa 1.1
^^^^^^^^

.. code-block:: python

    ConjunctiveGraph().parse(data=data, format="rdfa1.1")

.. automodule:: rdflib.plugins.parsers.structureddata
.. autoclass::  rdflib.plugins.parsers.structureddata.RDFaParser'
    :members:

RDF/XML
--------

.. code-block:: python

    ConjunctiveGraph().parse(data=data, format="application/rdf+xml")

.. autoclass::  rdflib.plugins.parsers.rdfxml.RDFXMLParser
    :members:

TriX
-----

.. code-block:: python

    ConjunctiveGraph().parse(data=data, format="trix")

.. module:: rdflib.plugins.parsers.trix
.. autoclass::  rdflib.plugins.parsers.trix.TriXParser
    :members:


