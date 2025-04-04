Plugins
=======

.. toctree::
   :maxdepth: 1

   plugin_parsers
   plugin_serializers
   plugin_stores
   plugin_query_results

.. image:: /_static/plugins-diagram.*
   :alt: RDFLib plugin architecture
   :width: 450px
   :target: _static/plugins-diagram.svg

RDFLib uses Python **entry points** to automatically discover plugins.  
This approach allows you to extend RDFLib's functionality by adding custom parsers, serializers, stores, query processors, and result handlers.

Plugins can also be registered manually using :func:`rdf.plugin.register`.

Supported entry point groups
----------------------------
- ``rdf.plugins.parser``: custom RDF parsers (:class:`rdflib.parser.Parser` subclasses)
- ``rdf.plugins.serializer``: custom RDF serializers (:class:`rdflib.serializer.Serializer` subclasses)
- ``rdf.plugins.store``: custom store implementations (:class:`rdflib.store.Store` subclasses)
- ``rdf.plugins.queryprocessor``: custom SPARQL query processors (:class:`rdflib.query.Processor` subclasses)
- ``rdf.plugins.updateprocessor``: custom SPARQL update processors (:class:`rdflib.query.UpdateProcessor` subclasses)
- ``rdf.plugins.resultparser``: custom SPARQL result parsers (:class:`rdflib.query.ResultParser` subclasses)
- ``rdf.plugins.resultserializer``: custom SPARQL result serializers (:class:`rdflib.query.ResultSerializer` subclasses)
- ``rdf.plugins.queryresult``: custom SPARQL query result classes (:class:`rdflib.query.Result` subclasses)

Example ``pyproject.toml`` using a PEP 621-compliant tool, e.g. uv:

.. code-block:: toml

    [project.entry-points."rdf.plugins.parser"]
    nt = "rdf.plugins.parsers.ntriples:NTParser"
    "application/n-triples" = "rdf.plugins.parsers.ntriples:NTParser"

    [project.entry-points."rdf.plugins.serializer"]
    nt = "rdf.plugins.serializers.NTSerializer:NTSerializer"
    "application/n-triples" = "rdf.plugins.parsers.ntriples:NTSerializer"

`Learn more about using package metadata for creating and discovering plugins <https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata>`_.
