URI Loading
===========

.. admonition:: Status

   Accepted

Context
-------

RDFLib provides no direct means for users to control URI loading.

Several issues relating to this has been raised:

- [rdflib-1844]_: `URLInputSource can be abused to retrieve arbitrary documents if used naïvely <https://github.com/RDFLib/rdflib/issues/1844>`_
- [rdflib-1650]_: `Load a remote context via an unsupported network protocol <https://github.com/RDFLib/rdflib/issues/1650>`_

[rdflib-1844]_ has also been raised as a security vulnerability [SNYK-PYTHON-RDFLIB-1324490]_.

Additionally, there is a `test.utils.iri.URIMapper`_ class in the RDFLib test
suite which is used to map remote URIs to local file URIs, and this is
specifically used for loading test data from the local file-system using remote
URIs.

The listed issues and functionality can be fulfilled by a URI loading mechanism
that provides the following functionality:

- URI allow/deny-listing
- URI remapping
- URI loading

.. RDFLib should provide a way for users to control URI loading that address all
.. these issues and requirements.

.. A mechanism that allows users to control URI loading can be used to
.. address the referenced issues and also to do the remote to local mapping in the RDFLib test suite.

Prior-art
^^^^^^^^^

This section describes how the mechanisms that other RDF libraries use for URI
loading.

Apache Jena
"""""""""""

`Apache Jena <https://jena.apache.org/>`_ uses `org.apache.jena.riot.system.stream.StreamManager
<https://jena.apache.org/documentation/javadoc/arq/org.apache.jena.arq/org/apache/jena/riot/system/stream/StreamManager.html>`_
for loading URIs.

A custom ``StreamManager`` can be supplied to a `org.apache.jena.riot.RDFParser
<https://jena.apache.org/documentation/javadoc/arq/org.apache.jena.arq/org/apache/jena/riot/RDFParser.html>`_
by using `org.apache.jena.riot.RDFParserBuilder <https://jena.apache.org/documentation/javadoc/arq/org.apache.jena.arq/org/apache/jena/riot/RDFParserBuilder.html>`_.

A ``StreamManager`` provides an ``InputStream`` for a URI, and also does URI to
URI translation with `org.apache.jena.riot.system.stream.LocationMapper
<https://jena.apache.org/documentation/javadoc/arq/org.apache.jena.arq/org/apache/jena/riot/system/stream/LocationMapper.html>`_
which can map both specific URIs and URIs based on prefix. The URI mapping
functionality could be used to map ``http`` URLs to ``file`` URIs.

RDF4J
^^^^^

It does not seem like `RDF4J <https://rdf4j.org/>`_ has a general mechanism for
URI loading and mapping, there is however a JSON-LD specific mechanism for this
provided by JSONLD Java in `com.github.jsonldjava.core.DocumentLoader
<https://javadoc.io/static/com.github.jsonld-java/jsonld-java/0.13.4/com/github/jsonldjava/core/DocumentLoader.html>`_.
This mechanism can be controlled using
`org.eclipse.rdf4j.rio.helpers.JSONLDSettings
<https://rdf4j.org/javadoc/4.1.0/org/eclipse/rdf4j/rio/helpers/JSONLDSettings.html>`_

Oxigraph / Rio
^^^^^^^^^^^^^^

Rio_ is the component that Oxigraph_ uses for RDF parsing.

It does not seem like `Rio`_ or `Oxigraph`_ currently has a generic mechanism
for URI loading, mapping or deny/allow-listing.

Decision
--------

Validator / Vetter / Verifier / Arbiter / Authorizer


.. kroki::
   :caption: URI Loading Classes
   :type: plantuml

    @startuml
    skinparam shadowing false
    skinparam monochrome true
    skinparam packageStyle rectangle
    skinparam backgroundColor FFFFFE
    
    class URILoader
    
    @enduml


Consequences
------------



References
----------

.. [rdflib-1844] `URLInputSource can be abused to retrieve arbitrary documents if used naïvely <https://github.com/RDFLib/rdflib/issues/1844>`_
.. [rdflib-1650] `Load a remote context via an unsupported network protocol <https://github.com/RDFLib/rdflib/issues/1650>`_
.. [SNYK-PYTHON-RDFLIB-1324490] `Server-Side Request Forgery (SSRF) Affecting rdflib package, versions [0,] <https://security.snyk.io/vuln/SNYK-PYTHON-RDFLIB-1324490>`_


.. _test.utils.iri.URIMapper: https://github.com/RDFLib/rdflib/blob/bcd05e93c0325854b2c44447996cb4bf91cc830c/test/utils/iri.py#L103
.. _Oxigraph: https://github.com/oxigraph/oxigraph
.. _Rio: https://github.com/oxigraph/rio
