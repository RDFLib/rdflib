
Various unit tests for rdflib

Graph tests
===========

(Graphs are mostly tested through the store tests - detailed below)

test_aggregate_graphs - special tests for the ReadOnlyGraphAggregate class

Store tests
===========

These tests test all stores plugins that are registered, i.e. you may test more than just core rdflib:

test_graph - all stores
test_graph_context - only context aware stores
test_graph_formula - only formula aware stores


Syntax tests
============

test_n3 - test misc n3 features
test_n3_suite - n3 test-cases in n3/*

test_nt_misc - test misc nt features

test_rdfxml - rdf-wg RDF/XML test-cases in rdf/*

test_trix - trix test-cases in trix/*

test_nquads - nquads test-cases in nquads/*

test_roundtrip - roundtrip testing of all files nt/*
                 All parser/serializer pairs that are registered are tested, i.e you may test more than just core rdflib.

Misc tests
==========

test_finalnewline - test that all serializers produce output with a final newline

test_conneg - test content negotiation when reading remote graphs


EARL Test Reports
=================

EARL test reports can be generated using the EARL reporter plugin from ``earl.py``.

When this plugin is enabled it will create an ``earl:Assertion`` for every test that has a ``rdf_test_uri`` parameter which can be either a string or an ``URIRef``.

To enable the EARL reporter plugin an output file path must be supplied to pytest with ``--earl-output-file``. The report will be written to this location in turtle format.

Some examples of generating test reports:

.. code-block:: bash

   pytest \
      --earl-assertor-homepage=http://example.com \
      --earl-assertor-name 'Example Name' \
      --earl-output-file=/var/tmp/earl/earl-jsonld-local.ttl \
      test/jsonld/test_localsuite.py

   pytest \
      --earl-assertor-homepage=http://example.com \
      --earl-assertor-name 'Example Name' \
      --earl-output-file=/var/tmp/earl/earl-jsonld-v1.1.ttl \
      test/jsonld/test_onedotone.py

   pytest \
      --earl-assertor-homepage=http://example.com \
      --earl-assertor-name 'Example Name' \
      --earl-output-file=/var/tmp/earl/earl-jsonld-v1.0.ttl \
      test/jsonld/test_testsuite.py

   pytest \
      --earl-assertor-homepage=http://example.com \
      --earl-assertor-name 'Example Name' \
      --earl-output-file=/var/tmp/earl/earl-sparql.ttl \
      test/test_w3c_spec/test_sparql_w3c.py

   pytest \
      --earl-assertor-homepage=http://example.com \
      --earl-assertor-name 'Example Name' \
      --earl-output-file=/var/tmp/earl/earl-nquads.ttl \
      test/test_w3c_spec/test_nquads_w3c.py

   pytest \
      --earl-assertor-homepage=http://example.com \
      --earl-assertor-name 'Example Name' \
      --earl-output-file=/var/tmp/earl/earl-nt.ttl \
      test/test_w3c_spec/test_nt_w3c.py

   pytest \
      --earl-assertor-homepage=http://example.com \
      --earl-assertor-name 'Example Name' \
      --earl-output-file=/var/tmp/earl/earl-trig.ttl \
      test/test_w3c_spec/test_trig_w3c.py

   pytest \
      --earl-assertor-homepage=http://example.com \
      --earl-assertor-name 'Example Name' \
      --earl-output-file=/var/tmp/earl/earl-turtle.ttl \
      test/test_w3c_spec/test_turtle_w3c.py
