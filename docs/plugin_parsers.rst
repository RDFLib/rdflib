.. _plugin_parsers: Plugin parsers

==============
Plugin parsers
==============

The currently-available plug-in parsers are listed in 
`rdfextras plugins <http://rdfextras.readthedocs.org/en/latest>`_

.. code-block:: python

    register('n3', Parser, 
             'rdflib.plugins.parsers.notation3', 'N3Parser')
    register('nquads', Parser, 
             'rdflib.plugins.parsers.nquads', 'NQuadsParser')
    register('nt', Parser, 
             'rdflib.plugins.parsers.nt', 'NTParser')
    register('trix', Parser, 
             'rdflib.plugins.parsers.trix', 'TriXParser')
    register('application/rdf+xml', Parser,
             'rdflib.plugins.parsers.rdfxml', 'RDFXMLParser')
    register('xml', Parser, 
             'rdflib.plugins.parsers.rdfxml', 'RDFXMLParser')
    register('rdfa', Parser, 
             'rdflib.plugins.parsers.rdfa', 'RDFaParser')
    register('text/html', Parser,
             'rdflib.plugins.parsers.rdfa', 'RDFaParser')
    register('application/xhtml+xml', Parser,
             'rdflib.plugins.parsers.rdfa', 'RDFaParser')


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

.. code-block:: python

    ConjunctiveGraph().parse(data=data, format="rdfa")

.. automodule:: rdflib.plugins.parsers.rdfa
.. autoclass::  rdflib.plugins.parsers.rdfa.RDFaParser
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


