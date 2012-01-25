.. _plugin_serializers: Plugin serializers

==================
Plugin serializers
==================

The plug-in serializers are listed in :mod:`rdfextras.plugins`:

.. code-block:: python

    register('n3', Serializer, 
             'rdflib.plugins.serializers.n3','N3Serializer')
    register('turtle', Serializer, 
             'rdflib.plugins.serializers.turtle', 'TurtleSerializer')
    register('nt', Serializer, 
             'rdflib.plugins.serializers.nt', 'NTSerializer')
    register('xml', Serializer, 
             'rdflib.plugins.serializers.rdfxml', 'XMLSerializer')
    register('pretty-xml', Serializer,
             'rdflib.plugins.serializers.rdfxml', 'PrettyXMLSerializer')
    register('trix', Serializer,
             'rdflib.plugins.serializers.trix', 'TriXSerializer')
    register('nquads', Serializer, 
             'rdflib.plugins.serializers.nquads', 'NQuadsSerializer')

Notation 3
----------

.. code-block:: python

    ConjunctiveGraph().parse(data=s, format='n3')

.. module:: rdflib.plugins.serializers.n3
.. autoclass::  rdflib.plugins.serializers.n3.N3Serializer
    :members:

NQuads
-------
.. code-block:: python

    ConjunctiveGraph().parse(data=s, format='nquads')

.. module:: rdflib.plugins.serializers.nquads
.. autoclass::  rdflib.plugins.serializers.nquads.NQuadsSerializer
    :members:

NTriples
---------
.. code-block:: python

    ConjunctiveGraph().parse(data=s, format='nt')

.. module:: rdflib.plugins.serializers.nt
.. autoclass::  rdflib.plugins.serializers.nt.NTSerializer
    :members:

RDF/XML
--------
.. code-block:: python

    ConjunctiveGraph().parse(data=s, format='xml')

.. module:: rdflib.plugins.serializers.rdfxml
.. autoclass::  rdflib.plugins.serializers.rdfxml.XMLSerializer
    :members:

TriX
-----
.. code-block:: python

    ConjunctiveGraph().parse(data=s, format='trix')

.. module:: rdflib.plugins.serializers.trix
.. autoclass::  rdflib.plugins.serializers.trix.TriXSerializer
    :members:

Turtle
------
.. code-block:: python

    ConjunctiveGraph().parse(data=s, format='turtle')

.. module:: rdflib.plugins.serializers.turtle
.. autoclass::  rdflib.plugins.serializers.turtle.TurtleSerializer
    :members:

XML
---
.. code-block:: python

    ConjunctiveGraph().parse(data=s, format='pretty-xml')

.. module:: rdflib.plugins.serializers.xmlwriter
.. autoclass::  rdflib.plugins.serializers.xmlwriter.XMLWriter
    :members:
