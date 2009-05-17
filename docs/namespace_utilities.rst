.. _namespace_utilities:

===================
Namespace Utilities
===================

RDFLib provides mechanisms for managing Namespaces.  In particular, there is a [http://svn.rdflib.net/trunk/rdflib/Namespace.py Namespace] class which takes (as its only argument) the Base URI of the namespace.  Fully qualified URIs in the namespace can be constructed by attribute / dictionary access on Namespace instances:

.. code-block:: pycon

    >>> from rdflib.namespace import Namespace
    >>> fuxi = Namespace('http://metacognition.info/ontologies/FuXi.n3#')
    >>> fuxi.ruleBase
    u'http://metacognition.info/ontologies/FuXi.n3#ruleBase'
    >>> fuxi['ruleBase']
    u'http://metacognition.info/ontologies/FuXi.n3#ruleBase'

.. automodule:: rdflib.namespace

Contents
--------

.. autoclass:: rdflib.namespace.Namespace
    :members: