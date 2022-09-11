URI Loading
===========

.. admonition:: Status

   Accepted

Context
-------



Prior-art
^^^^^^^^^

This section describes how URI loading is implemented by other RDF libraries.

Apache Jena
"""""""""""

Apache Jena uses `org.apache.jena.riot.system.stream.StreamManager
<https://jena.apache.org/documentation/javadoc/arq/org.apache.jena.arq/org/apache/jena/riot/system/stream/StreamManager.html>`_
for loading URIs.

A custom ``StreamManager`` can be supplied to a `org.apache.jena.riot.RDFParser
<https://jena.apache.org/documentation/javadoc/arq/org.apache.jena.arq/org/apache/jena/riot/RDFParser.html>`_
by using `org.apache.jena.riot.RDFParserBuilder
 <https://jena.apache.org/documentation/javadoc/arq/org.apache.jena.arq/org/apache/jena/riot/RDFParserBuilder.html>`_.

A stream manager can be used to obtain an ``InputStream`` from a URI, and also does
URI to URI mapping which can be used for mapping remote URIs to file URIs for
example.


https://jena.apache.org/documentation/javadoc/arq/org.apache.jena.arq/org/apache/jena/riot/RDFParser.html


RDF4J
^^^^^

It does not seem like RDF4J has a general 

https://github.com/eclipse/rdf4j/tree/4.1.1
https://rdf4j.org/javadoc/latest/
https://github.com/jsonld-java/jsonld-java/blob/master/core/src/main/java/com/github/jsonldjava/core/DocumentLoader.java



Prior-art: oxigraph
^^^^^^^^^^^^^^^^^^^

https://github.com/oxigraph/oxigraph/tree/v0.3.6

Decision
--------


Consequences
------------



References
----------

