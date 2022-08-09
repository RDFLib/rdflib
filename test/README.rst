
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

EARL test reports are generated using the EARL reporter plugin from
``test/utils/earl.py``.

This plugin is enabled by default and writes test reports to
``test_reports/*-HEAD.ttl`` without timestamps by default.

For EARL reporter plugin options see the output of ``pytest --help``.

To write reports with timestamps:

.. code-block:: bash

    pytest \
      --earl-add-datetime \
      --earl-output-suffix=-timestamped \
      test/test_w3c_spec/
