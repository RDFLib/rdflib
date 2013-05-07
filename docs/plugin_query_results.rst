.. _plugin_query_results: Plugin Query Results

====================
Plugin Query Results
====================

Plugins for reading and writing of (SPARQL) :class:`~rdflib.querye.QueryResult` - pass ``name`` to either :meth:`~rdflib.query.QueryResult.parse` or :meth:`~rdflib.query.QueryResult.serialize` 


Parsers
-------

==== ====================================================================
Name Class                                                               
==== ====================================================================
csv  :class:`~rdflib.plugins.sparql.results.csvresults.CSVResultParser`
json :class:`~rdflib.plugins.sparql.results.jsonresults.JSONResultParser`
tsv  :class:`~rdflib.plugins.sparql.results.tsvresults.TSVResultParser`
xml  :class:`~rdflib.plugins.sparql.results.xmlresults.XMLResultParser`
==== ====================================================================

Serializers
-----------

==== ========================================================================
Name Class                                                                   
==== ========================================================================
csv  :class:`~rdflib.plugins.sparql.results.csvresults.CSVResultSerializer`
json :class:`~rdflib.plugins.sparql.results.jsonresults.JSONResultSerializer`
xml  :class:`~rdflib.plugins.sparql.results.xmlresults.XMLResultSerializer`
==== ========================================================================
