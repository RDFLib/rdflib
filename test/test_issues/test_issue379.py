"""
Tests for GitHub Issue 379: https://github.com/RDFLib/rdflib/issues/379
"""

import pytest

import rdflib


@pytest.fixture
def prefix_data():
    return """
           @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
           @prefix : <http://www.example.com#> .

           <http://www.example.com#prefix> a rdf:class ."""


@pytest.fixture
def base_data():
    return """
           @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
           @base <http://www.example.com#> .

           <http://www.example.com#base> a rdf:class .
           """


@pytest.fixture
def graph():
    return rdflib.Graph()


def test_parse_successful_prefix_with_hash(graph, prefix_data):
    """
    Test parse of '@prefix' namespace directive to allow a trailing hash '#', as is
    permitted for an IRIREF:
    http://www.w3.org/TR/2014/REC-turtle-20140225/#grammar-production-prefixID
    """
    graph.parse(data=prefix_data, format="n3")
    assert isinstance(next(graph.subjects()), rdflib.URIRef)


def test_parse_successful_base_with_hash(graph, base_data):
    """
    Test parse of '@base' namespace directive to allow a trailing hash '#', as is
    permitted for an '@prefix' since both allow an IRIREF:
    http://www.w3.org/TR/2014/REC-turtle-20140225/#grammar-production-base
    """
    graph.parse(data=base_data, format="n3")
    assert isinstance(next(graph.subjects()), rdflib.URIRef)
